<template>
  <div v-if="order" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
      <!-- Header -->
      <div class="border-b px-6 py-4 flex justify-between items-center">
        <h2 class="text-lg font-semibold text-gray-900">Update Order Status</h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <XMarkIcon class="h-6 w-6" />
        </button>
      </div>

      <!-- Content -->
      <div class="p-6">
        <div class="mb-4 p-3 bg-gray-50 rounded-md">
          <div class="text-sm text-gray-600">Order: <span class="font-medium">{{ order.order_number }}</span></div>
          <div class="text-sm text-gray-600">Customer: <span class="font-medium">{{ order.customer?.first_name }} {{ order.customer?.last_name }}</span></div>
          <div class="text-sm text-gray-600">Phone: <span class="font-medium">{{ order.customer?.phone_number }}</span></div>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Current Status: <span class="font-semibold">{{ formatOrderStatus(order.order_status) }}</span>
          </label>
          <select
            v-model="newStatus"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select new status</option>
            <option v-for="status in statusOptions" :key="status.value" :value="status.value">
              {{ status.label }}
            </option>
          </select>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Notes (Optional)
          </label>
          <textarea
            v-model="notes"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Add notes about this status change..."
          ></textarea>
        </div>

        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-600">{{ error }}</p>
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
          @click="updateStatus"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          :disabled="!newStatus || loading"
        >
          <span v-if="loading">Updating...</span>
          <span v-else>Update Status</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { adminOrdersAPI } from '@/services/api'

const props = defineProps({
  order: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const newStatus = ref('')
const notes = ref('')
const loading = ref(false)
const error = ref(null)

const statusOptions = [
  { value: 'pending', label: 'Pending' },
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'processing', label: 'Processing' },
  { value: 'out_for_delivery', label: 'Out for Delivery' },
  { value: 'delivered', label: 'Delivered' },
  { value: 'cancelled', label: 'Cancelled' }
]

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

const resetForm = () => {
  newStatus.value = ''
  notes.value = ''
  error.value = null
  loading.value = false
}

const updateStatus = async () => {
  if (!newStatus.value || !props.order?.order_id) return

  loading.value = true
  error.value = null

  try {
    await adminOrdersAPI.updateOrderStatus(props.order.order_id, newStatus.value)
    
    emit('save', props.order.order_id, newStatus.value)
    
    emit('close')
  } catch (err) {
    console.error('Error updating order status:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to update order status'
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