<template>
  <div v-if="order" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
        <h2 class="text-xl font-semibold text-gray-900">Order Details</h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <XMarkIcon class="h-6 w-6" />
        </button>
      </div>

      <!-- Order Content -->
      <div class="p-6 space-y-6">
        <!-- Order Overview -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="bg-gray-50 rounded-lg p-4">
            <h3 class="font-semibold text-gray-900 mb-3">Order Information</h3>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Order Number:</span>
                <span class="font-medium">{{ order.order_number }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Date:</span>
                <span>{{ formatDate(order.created_at) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Status:</span>
                <span class="px-2 py-1 rounded-full text-xs font-medium"
                      :class="getStatusBadgeClass(order.order_status)">
                  {{ formatOrderStatus(order.order_status) }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Total Amount:</span>
                <span class="font-semibold text-green-600">KES {{ formatCurrency(order.total_amount) }}</span>
              </div>
            </div>
          </div>

          <div class="bg-gray-50 rounded-lg p-4">
            <h3 class="font-semibold text-gray-900 mb-3">Customer Information</h3>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Name:</span>
                <span>{{ order.customer?.first_name }} {{ order.customer?.last_name }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Phone:</span>
                <span>{{ order.customer?.phone_number }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Email:</span>
                <span>{{ order.customer?.email || 'Not provided' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Address:</span>
                <span class="text-right max-w-40 truncate">{{ order.delivery_address || 'Not provided' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Payment Information -->
        <div class="bg-gray-50 rounded-lg p-4">
          <h3 class="font-semibold text-gray-900 mb-3">Payment Information</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Payment Method:</span>
              <span>{{ order.payment_method?.payment_type || 'Not specified' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Payment Status:</span>
              <span class="px-2 py-1 rounded-full text-xs font-medium"
                    :class="getPaymentStatusBadgeClass(order.payment_status)">
                {{ formatPaymentStatus(order.payment_status) }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Amount:</span>
              <span class="font-semibold">KES {{ formatCurrency(order.total_amount) }}</span>
            </div>
          </div>
        </div>

        <!-- Order Items -->
        <div>
          <h3 class="font-semibold text-gray-900 mb-3">Order Items</h3>
          <div class="bg-white border rounded-lg overflow-hidden">
            <div class="max-h-60 overflow-y-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Farm</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="item in order.items" :key="item.order_item_id" class="hover:bg-gray-50">
                    <td class="px-4 py-3 text-sm">
                      <div class="flex items-center">
                        <img v-if="item.listing?.product?.image_url" 
                             :src="item.listing.product.image_url" 
                             alt="" 
                             class="h-10 w-10 rounded-lg object-cover mr-3">
                        <div class="h-10 w-10 bg-gray-200 rounded-lg mr-3 flex items-center justify-center" v-else>
                          <span class="text-gray-400 text-xs">No img</span>
                        </div>
                        <div>
                          <div class="font-medium text-gray-900">{{ item.listing?.product?.name || 'Unknown Product' }}</div>
                          <div class="text-gray-500 text-xs">{{ item.listing?.product?.category?.name || 'No Category' }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-600">
                      {{ item.listing?.farm?.name || 'Unknown Farm' }}
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-600">
                      {{ item.quantity }} {{ item.listing?.unit || 'units' }}
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-900">
                      KES {{ formatCurrency(item.price_at_purchase) }}
                    </td>
                    <td class="px-4 py-3 text-sm">
                      <span class="px-2 py-1 rounded-full text-xs font-medium"
                            :class="getItemStatusBadgeClass(item.item_status)">
                        {{ formatItemStatus(item.item_status) }}
                      </span>
                    </td>
                    <td class="px-4 py-3 text-sm font-semibold text-gray-900">
                      KES {{ formatCurrency(item.total_price) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Delivery Information -->
        <div v-if="order.delivery" class="bg-gray-50 rounded-lg p-4">
          <h3 class="font-semibold text-gray-900 mb-3">Delivery Information</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-600">Delivery Status:</span>
                <span class="px-2 py-1 rounded-full text-xs font-medium"
                      :class="getDeliveryStatusBadgeClass(order.delivery.delivery_status)">
                  {{ formatDeliveryStatus(order.delivery.delivery_status) }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Delivery Address:</span>
                <span class="text-right max-w-40">{{ order.delivery_address?.location_name || 'Not provided' }}</span>
              </div>
            </div>
            <div class="space-y-2" v-if="order.delivery.rider">
              <div class="flex justify-between">
                <span class="text-gray-600">Rider:</span>
                <span>{{ order.delivery.rider.first_name }} {{ order.delivery.rider.last_name }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Rider Phone:</span>
                <span>{{ order.delivery.rider.phone_number }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Admin Actions -->
        <div class="bg-blue-50 rounded-lg p-4">
          <h3 class="font-semibold text-gray-900 mb-3">Admin Actions</h3>
          <div class="flex flex-wrap gap-3">
            <button
              @click="openStatusModal"
              class="inline-flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700"
            >
              <PencilIcon class="h-4 w-4 mr-2" />
              Update Order Status
            </button>
            <button
              @click="openPaymentModal" 
              class="inline-flex items-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700"
            >
              <CurrencyDollarIcon class="h-4 w-4 mr-2" />
              Update Payment Status
            </button>
            <button
              @click="exportOrder"
              class="inline-flex items-center px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700"
            >
              <DocumentArrowDownIcon class="h-4 w-4 mr-2" />
              Export Order
            </button>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="sticky bottom-0 bg-gray-50 border-t px-6 py-4 flex justify-end space-x-3">
        <button @click="$emit('close')" 
                class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  XMarkIcon, 
  PencilIcon, 
  CurrencyDollarIcon, 
  DocumentArrowDownIcon 
} from '@heroicons/vue/24/outline'

const props = defineProps({
  order: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'update-status'])

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatOrderStatus = (status) => {
  const statusMap = {
    'pending': 'Pending',
    'confirmed': 'Confirmed',
    'processing': 'Processing',
    'out_for_delivery': 'Out for Delivery',
    'delivered': 'Delivered',
    'cancelled': 'Cancelled'
  }
  return statusMap[status] || status
}

const formatPaymentStatus = (status) => {
  const statusMap = {
    'pending': 'Pending',
    'paid': 'Paid',
    'failed': 'Failed',
    'refunded': 'Refunded',
    'cancelled': 'Cancelled'
  }
  return statusMap[status] || status
}

const formatItemStatus = (status) => {
  const statusMap = {
    'pending': 'Pending',
    'harvested': 'Harvested',
    'packed': 'Packed',
    'delivered': 'Delivered'
  }
  return statusMap[status] || status
}

const formatDeliveryStatus = (status) => {
  const statusMap = {
    'pending': 'Pending',
    'assigned': 'Assigned',
    'in_progress': 'In Progress',
    'delivered': 'Delivered'
  }
  return statusMap[status] || status
}

const getStatusBadgeClass = (status) => {
  const statusClasses = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'confirmed': 'bg-blue-100 text-blue-800',
    'processing': 'bg-indigo-100 text-indigo-800',
    'out_for_delivery': 'bg-purple-100 text-purple-800',
    'delivered': 'bg-green-100 text-green-800',
    'cancelled': 'bg-red-100 text-red-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const getPaymentStatusBadgeClass = (status) => {
  const statusClasses = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'paid': 'bg-green-100 text-green-800',
    'failed': 'bg-red-100 text-red-800',
    'refunded': 'bg-orange-100 text-orange-800',
    'cancelled': 'bg-gray-100 text-gray-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const getItemStatusBadgeClass = (status) => {
  const statusClasses = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'harvested': 'bg-blue-100 text-blue-800',
    'packed': 'bg-orange-100 text-orange-800',
    'delivered': 'bg-green-100 text-green-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const getDeliveryStatusBadgeClass = (status) => {
  const statusClasses = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'assigned': 'bg-blue-100 text-blue-800',
    'in_progress': 'bg-orange-100 text-orange-800',
    'delivered': 'bg-green-100 text-green-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const openStatusModal = () => {
  emit('update-status', 'status', props.order)
}

const openPaymentModal = () => {
  emit('update-status', 'payment', props.order)
}

const exportOrder = () => {
  if (!props.order) return
  
  const orderData = {
    order_number: props.order.order_number,
    customer: `${props.order.customer?.first_name} ${props.order.customer?.last_name}`,
    phone: props.order.customer?.phone_number,
    total_amount: props.order.total_amount,
    order_status: props.order.order_status,
    payment_status: props.order.payment_status,
    created_at: props.order.created_at,
    items: props.order.items?.map(item => ({
      product: item.listing?.product?.name,
      quantity: item.quantity,
      price: item.price_at_purchase,
      total: (item.quantity * item.price_at_purchase).toFixed(2)
    }))
  }
  
  const dataStr = JSON.stringify(orderData, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `order_${props.order.order_number}.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}
</script>