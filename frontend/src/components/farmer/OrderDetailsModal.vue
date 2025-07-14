<template>
  <div class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex min-h-screen items-end justify-center px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="$emit('close')"></div>

      <!-- Modal panel -->
      <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full sm:p-6">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900">Order Details</h3>
            <p class="text-sm text-gray-500">Order #{{ order.order_details?.order_number }}</p>
          </div>
          <button @click="$emit('close')" class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <!-- Order Information Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <!-- Product Information -->
          <div class="bg-gray-50 rounded-lg p-4">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Product Information</h4>
            <div class="space-y-2">
              <div class="flex items-center space-x-3">
                <img 
                  :src="order.listing_details?.photos?.[0] || '/api/placeholder/48/48'"
                  :alt="order.listing_details?.product_name"
                  class="h-12 w-12 rounded-lg object-cover"
                />
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ order.listing_details?.product_name }}</p>
                  <p class="text-xs text-gray-500">{{ order.listing_details?.farm_name }}</p>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span class="text-gray-500">Quantity:</span>
                  <span class="ml-1 font-medium">{{ order.quantity }} {{ order.listing_details?.product_unit }}</span>
                </div>
                <div>
                  <span class="text-gray-500">Unit Price:</span>
                  <span class="ml-1 font-medium">KES {{ formatCurrency(order.price_at_purchase) }}</span>
                </div>
                <div class="col-span-2">
                  <span class="text-gray-500">Total Amount:</span>
                  <span class="ml-1 font-medium text-green-600">KES {{ formatCurrency(order.total_price) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Payment Information -->
          <div class="bg-gray-50 rounded-lg p-4">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Payment Information</h4>
            <div class="space-y-3">
              <div>
                <span class="text-sm text-gray-500">Payment Status:</span>
                <span :class="getPaymentStatusBadgeClass(order.order_details?.payment_status)" class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                  {{ getPaymentStatusDisplayName(order.order_details?.payment_status) }}
                </span>
              </div>
              <div>
                <span class="text-sm text-gray-500">Payment Method:</span>
                <span class="ml-2 text-sm font-medium text-gray-900">
                  {{ getPaymentMethodDisplayName(order.order_details?.payment_method?.payment_type) }}
                </span>
              </div>
              <div>
                <span class="text-sm text-gray-500">Order Date:</span>
                <span class="ml-2 text-sm font-medium text-gray-900">
                  {{ formatDate(order.created_at) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Current Status and Actions -->
        <div class="bg-blue-50 rounded-lg p-4 mb-6">
          <h4 class="text-sm font-medium text-gray-900 mb-3">Order Item Status</h4>
          <div class="flex items-center justify-between">
            <div>
              <span :class="getItemStatusBadgeClass(order.item_status)" class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium">
                {{ getItemStatusDisplayName(order.item_status) }}
              </span>
              <p class="text-xs text-gray-500 mt-1">
                Last updated {{ formatRelativeTime(order.updated_at) }}
              </p>
            </div>
            
            <!-- Status Update Button -->
            <div v-if="canAdvanceStatus(order)">
              <button
                @click="updateStatus"
                :disabled="updating || !canUpdateStatus(order)"
                :title="getStatusUpdateTooltip(order)"
                :class="[
                  'inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500',
                  canUpdateStatus(order) 
                    ? 'text-white bg-green-600 hover:bg-green-700' 
                    : 'text-gray-400 bg-gray-200 cursor-not-allowed'
                ]"
              >
                <span v-if="!updating">
                  Update to {{ getItemStatusDisplayName(getNextStatus(order.item_status)) }}
                </span>
                <span v-else class="flex items-center">
                  <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Updating...
                </span>
              </button>
            </div>
          </div>
        </div>

        <!-- Payment Restriction Notice -->
        <div v-if="!canUpdateStatus(order) && order.item_status !== 'delivered'" class="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-6">
          <div class="flex">
            <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400" />
            <div class="ml-3">
              <h3 class="text-sm font-medium text-yellow-800">Status Update Restricted</h3>
              <div class="mt-2 text-sm text-yellow-700">
                <p v-if="order.order_details?.payment_method?.payment_type !== 'CashOnDelivery' && order.order_details?.payment_status !== 'paid'">
                  You cannot update the order status until the customer's payment is confirmed. 
                  Current payment status: <strong>{{ getPaymentStatusDisplayName(order.order_details?.payment_status) }}</strong>
                </p>
                <p v-else-if="order.order_details?.payment_method?.payment_type === 'CashOnDelivery' && order.item_status === 'packed'">
                  For Cash on Delivery orders, you can only mark items as delivered after the delivery is completed by the rider.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="flex justify-end space-x-3">
          <button
            @click="$emit('close')"
            class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { XMarkIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { farmerOrdersAPI } from '@/services/api'

const props = defineProps({
  order: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'status-updated'])

// State
const updating = ref(false)

// Helper functions (reused from parent component)
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatRelativeTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = Math.floor((now - date) / (1000 * 60 * 60))
  
  if (diffInHours < 1) return 'Just now'
  if (diffInHours < 24) return `${diffInHours}h ago`
  
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) return `${diffInDays}d ago`
  
  return formatDate(dateString)
}

const getItemStatusBadgeClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    harvested: 'bg-blue-100 text-blue-800',
    packed: 'bg-indigo-100 text-indigo-800',
    delivered: 'bg-green-100 text-green-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getItemStatusDisplayName = (status) => {
  const names = {
    pending: 'Pending',
    harvested: 'Harvested',
    packed: 'Packed',
    delivered: 'Delivered'
  }
  return names[status] || status
}

const getPaymentStatusBadgeClass = (status) => {
  const classes = {
    pending: 'bg-orange-100 text-orange-800',
    paid: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getPaymentStatusDisplayName = (status) => {
  const names = {
    pending: 'Payment Pending',
    paid: 'Payment Confirmed',
    failed: 'Payment Failed',
    cancelled: 'Payment Cancelled'
  }
  return names[status] || status || 'Unknown'
}

const getPaymentMethodDisplayName = (method) => {
  const names = {
    Mpesa: 'M-Pesa',
    CashOnDelivery: 'Cash on Delivery',
    BankTransfer: 'Bank Transfer'
  }
  return names[method] || method || 'Not Set'
}

const canAdvanceStatus = (order) => {
  // Farmers should not be able to mark an item as 'delivered'
  return order.item_status !== 'delivered' && order.item_status !== 'packed'
}

const canUpdateStatus = (order) => {
  const paymentMethod = order.order_details?.payment_method?.payment_type
  const paymentStatus = order.order_details?.payment_status
  const itemStatus = order.item_status
  
  // Farmers can only update status if the item is not yet 'delivered'
  if (itemStatus === 'delivered') {
    return false
  }

  // For non-cash orders, payment must be confirmed
  if (paymentMethod !== 'CashOnDelivery') {
    return paymentStatus === 'paid'
  }
  
  // For cash on delivery orders, farmers can update up to 'packed'
  // They cannot mark as 'delivered'
  return true
}

const getNextStatus = (currentStatus) => {
  const statusFlow = {
    pending: 'harvested',
    harvested: 'packed',
    // Farmers cannot set status to 'delivered'
  }
  return statusFlow[currentStatus]
}

const getStatusUpdateTooltip = (order) => {
  const paymentMethod = order.order_details?.payment_method?.payment_type
  const paymentStatus = order.order_details?.payment_status
  const itemStatus = order.item_status
  
  if (itemStatus === 'delivered') {
    return 'Item is already delivered'
  }

  if (!canUpdateStatus(order)) {
    if (paymentMethod !== 'CashOnDelivery' && paymentStatus !== 'paid') {
      return 'Cannot update status until payment is confirmed'
    }
  }
  
  const nextStatus = getNextStatus(itemStatus)
  return nextStatus ? `Update to ${getItemStatusDisplayName(nextStatus)}` : 'Cannot advance further'
}

const updateStatus = async () => {
  const nextStatus = getNextStatus(props.order.item_status)
  if (!nextStatus || !canUpdateStatus(props.order)) return

  updating.value = true
  
  try {
    await farmerOrdersAPI.updateOrderItemStatus(props.order.order_item_id, nextStatus)
    
    // Update the order object
    props.order.item_status = nextStatus
    props.order.updated_at = new Date().toISOString()
    
    // Emit status update to parent
    emit('status-updated', props.order)
    
  } catch (error) {
    console.error('Error updating status:', error)
    // Handle error - could show a toast or error message
  } finally {
    updating.value = false
  }
}
</script>
