<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Report Problem</h3>
      </div>

      <form @submit.prevent="handleSubmit" class="px-6 py-4 space-y-4">
        <!-- Problem Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Problem Type <span class="text-red-500">*</span>
          </label>
          <select
            v-model="formData.problem_type"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select problem type</option>
            <option value="address_not_found">Address Not Found</option>
            <option value="customer_unavailable">Customer Unavailable</option>
            <option value="wrong_address">Wrong Address</option>
            <option value="vehicle_breakdown">Vehicle Breakdown</option>
            <option value="weather_conditions">Weather Conditions</option>
            <option value="product_damaged">Product Damaged</option>
            <option value="security_concern">Security Concern</option>
            <option value="other">Other</option>
          </select>
        </div>

        <!-- Problem Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Problem Description <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="formData.description"
            rows="4"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Please describe the problem in detail..."
          ></textarea>
        </div>

        <!-- Severity Level -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Severity Level <span class="text-red-500">*</span>
          </label>
          <select
            v-model="formData.severity"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select severity</option>
            <option value="low">Low - Minor issue, can proceed</option>
            <option value="medium">Medium - Needs attention</option>
            <option value="high">High - Cannot complete delivery</option>
            <option value="urgent">Urgent - Requires immediate help</option>
          </select>
        </div>

        <!-- Contact Customer Checkbox -->
        <div class="flex items-center">
          <input
            v-model="formData.contact_customer"
            type="checkbox"
            class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
          />
          <label class="ml-2 block text-sm text-gray-900">
            I have attempted to contact the customer
          </label>
        </div>

        <!-- Current Location -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Current Location/Landmark
          </label>
          <input
            v-model="formData.current_location"
            type="text"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Describe where you are currently located"
          />
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="submitting"
            class="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
          >
            {{ submitting ? 'Reporting...' : 'Report Problem' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const props = defineProps({
  deliveryId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['close', 'reported'])

const submitting = ref(false)

const formData = reactive({
  problem_type: '',
  description: '',
  severity: '',
  contact_customer: false,
  current_location: ''
})

const handleSubmit = async () => {
  submitting.value = true
  try {
    const problemReport = {
      delivery_id: props.deliveryId,
      problem_type: formData.problem_type,
      description: formData.description,
      severity: formData.severity,
      contact_customer: formData.contact_customer,
      current_location: formData.current_location || null,
      reported_at: new Date().toISOString()
    }

    emit('reported', problemReport)
    emit('close')
  } catch (error) {
    console.error('Error reporting problem:', error)
    alert('Failed to report problem. Please try again.')
  } finally {
    submitting.value = false
  }
}
</script>
