<template>
  <div v-if="order" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
      <!-- Header -->
      <div class="border-b px-6 py-4 flex justify-between items-center">
        <h2 class="text-lg font-semibold text-gray-900">Update Payment Status</h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <XMarkIcon class="h-6 w-6" />
        </button>
      </div>

      <!-- Content -->
      <div class="p-6">
        <div class="mb-4 p-3 bg-gray-50 rounded-md">
          <div class="text-sm text-gray-600">Order: <span class="font-medium">{{ order.order_number }}</span></div>
          <div class="text-sm text-gray-600">Customer: <span class="font-medium">{{ order.customer?.first_name }} {{ order.customer?.last_name }}</span></div>
          <div class="text-sm text-gray-600">Amount: <span class="font-medium">KES {{ formatCurrency(order.total_amount) }}</span></div>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Current Payment Status: <span class="font-semibold">{{ formatPaymentStatus(order.payment_status) }}</span>
          </label>
          <select
            v-model="newPaymentStatus"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select new payment status</option>
            <option v-for="status in paymentStatusOptions" :key="status.value" :value="status.value">
              {{ status.label }}
            </option>
          </select>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Payment Reference (Optional)
          </label>
          <input
            v-model="paymentReference"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter payment reference or transaction ID"
          />
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Notes (Optional)
          </label>
          <textarea
            v-model="notes"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Add notes about this payment status change..."
          ></textarea>
        </div>

        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <!-- Warning for certain status changes -->
        <div v-if="showWarning" class="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
          <div class="flex">
            <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400 mr-2 mt-0.5" />
            <p class="text-sm text-yellow-700">
              <strong>Warning:</strong> {{ warningMessage }}
            </p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="border-t px-6 py-4 flex justify-end space-x-3">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          :disabled="loading"
        >
          Cancel
        </button>
        <button
          @click="updatePaymentStatus"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          :disabled="!newPaymentStatus || loading"
        >
          <span v-if="loading">Updating...</span>
          <span v-else>Update Payment Status</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { XMarkIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { adminOrdersAPI } from '@/services/api'

const props = defineProps({
  order: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const newPaymentStatus = ref('')
const paymentReference = ref('')
const notes = ref('')
const loading = ref(false)
const error = ref(null)

const paymentStatusOptions = [
  { value: 'pending', label: 'Pending' },
  { value: 'paid', label: 'Paid' },
  { value: 'failed', label: 'Failed' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'refunded', label: 'Refunded' }
]

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatPaymentStatus = (status) => {
  const statusMap = {
    'pending': 'Pending',
    'paid': 'Paid',
    'failed': 'Failed',
    'cancelled': 'Cancelled',
    'refunded': 'Refunded'
  }
  return statusMap[status] || status
}

const showWarning = computed(() => {
  return newPaymentStatus.value === 'refunded' || 
         (props.order?.payment_status === 'paid' && newPaymentStatus.value === 'failed')
})

const warningMessage = computed(() => {
  if (newPaymentStatus.value === 'refunded') {
    return 'This will initiate a refund process. Make sure you have processed the actual refund before updating this status.'
  }
  if (props.order?.payment_status === 'paid' && newPaymentStatus.value === 'failed') {
    return 'Changing from paid to failed may require refund processing. Please verify this change is necessary.'
  }
  return ''
})

const resetForm = () => {
  newPaymentStatus.value = ''
  paymentReference.value = ''
  notes.value = ''
  error.value = null
  loading.value = false
}

const updatePaymentStatus = async () => {
  if (!newPaymentStatus.value || !props.order?.order_id) return

  loading.value = true
  error.value = null

  try {
    await adminOrdersAPI.updatePaymentStatus(props.order.order_id, newPaymentStatus.value)
    
    emit('save', props.order.order_id, newPaymentStatus.value)
    
    emit('close')
  } catch (err) {
    console.error('Error updating payment status:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to update payment status'
  } finally {
    loading.value = false
  }
}

watch(() => props.order, (newOrder) => {
  if (newOrder) {
    resetForm()
  }
})
</script> 