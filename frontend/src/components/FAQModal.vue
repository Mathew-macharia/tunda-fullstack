<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
    <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white" @click.stop>
      <!-- Header -->
      <div class="flex items-center justify-between pb-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">
          {{ isEditing ? 'Edit FAQ' : 'Create New FAQ' }}
        </h3>
        <button
          @click="closeModal"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <XMarkIcon class="w-6 h-6" />
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="saveFAQ" class="mt-6">
        <!-- Question -->
        <div class="mb-6">
          <label for="question" class="block text-sm font-medium text-gray-700 mb-2">
            Question <span class="text-red-500">*</span>
          </label>
          <textarea
            id="question"
            v-model="form.question"
            rows="3"
            :class="[
              'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none',
              errors.question ? 'border-red-300' : 'border-gray-300'
            ]"
            placeholder="Enter the frequently asked question..."
            required
          ></textarea>
          <p v-if="errors.question" class="mt-1 text-sm text-red-600">{{ errors.question }}</p>
          <p class="mt-1 text-xs text-gray-500">{{ form.question.length }}/500 characters</p>
        </div>

        <!-- Answer -->
        <div class="mb-6">
          <label for="answer" class="block text-sm font-medium text-gray-700 mb-2">
            Answer <span class="text-red-500">*</span>
          </label>
          <textarea
            id="answer"
            v-model="form.answer"
            rows="6"
            :class="[
              'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none',
              errors.answer ? 'border-red-300' : 'border-gray-300'
            ]"
            placeholder="Provide a comprehensive answer to this question..."
            required
          ></textarea>
          <p v-if="errors.answer" class="mt-1 text-sm text-red-600">{{ errors.answer }}</p>
        </div>

        <!-- Target Role -->
        <div class="mb-6">
          <label for="target_role" class="block text-sm font-medium text-gray-700 mb-2">
            Target Audience <span class="text-red-500">*</span>
          </label>
          <select
            id="target_role"
            v-model="form.target_role"
            :class="[
              'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              errors.target_role ? 'border-red-300' : 'border-gray-300'
            ]"
            required
          >
            <option value="">Select target audience</option>
            <option value="customer">Customers</option>
            <option value="farmer">Farmers</option>
            <option value="rider">Riders</option>
            <option value="all">All Users</option>
          </select>
          <p v-if="errors.target_role" class="mt-1 text-sm text-red-600">{{ errors.target_role }}</p>
          <p class="mt-1 text-xs text-gray-500">Choose who should see this FAQ</p>
        </div>

        <!-- Order Index -->
        <div class="mb-6">
          <label for="order_index" class="block text-sm font-medium text-gray-700 mb-2">
            Display Order
          </label>
          <input
            id="order_index"
            v-model.number="form.order_index"
            type="number"
            min="0"
            :class="[
              'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              errors.order_index ? 'border-red-300' : 'border-gray-300'
            ]"
            placeholder="0"
          />
          <p v-if="errors.order_index" class="mt-1 text-sm text-red-600">{{ errors.order_index }}</p>
          <p class="mt-1 text-xs text-gray-500">Lower numbers appear first (0 = highest priority)</p>
        </div>

        <!-- Active Status -->
        <div class="mb-6">
          <div class="flex items-center">
            <input
              id="is_active"
              v-model="form.is_active"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="is_active" class="ml-2 block text-sm text-gray-700">
              Active (visible to users)
            </label>
          </div>
          <p class="mt-1 text-xs text-gray-500">Inactive FAQs are hidden from users but can be reactivated later</p>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            @click="closeModal"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            :disabled="loading"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="loading"
          >
            <span v-if="loading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Saving...
            </span>
            <span v-else>
              {{ isEditing ? 'Update FAQ' : 'Create FAQ' }}
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { communicationAPI } from '@/services/api'

export default {
  name: 'FAQModal',
  components: {
    XMarkIcon
  },
  props: {
    faq: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const loading = ref(false)
    
    const form = reactive({
      question: '',
      answer: '',
      target_role: '',
      order_index: 0,
      is_active: true
    })

    const errors = reactive({
      question: '',
      answer: '',
      target_role: '',
      order_index: ''
    })

    const isEditing = computed(() => !!props.faq)

    const validateForm = () => {
      // Clear previous errors
      Object.keys(errors).forEach(key => {
        errors[key] = ''
      })

      let isValid = true

      // Question validation
      if (!form.question.trim()) {
        errors.question = 'Question is required'
        isValid = false
      } else if (form.question.length > 500) {
        errors.question = 'Question must be 500 characters or less'
        isValid = false
      }

      // Answer validation
      if (!form.answer.trim()) {
        errors.answer = 'Answer is required'
        isValid = false
      }

      // Target role validation
      if (!form.target_role) {
        errors.target_role = 'Target audience is required'
        isValid = false
      }

      // Order index validation
      if (form.order_index < 0) {
        errors.order_index = 'Order must be 0 or greater'
        isValid = false
      }

      return isValid
    }

    const saveFAQ = async () => {
      if (!validateForm()) {
        return
      }

      loading.value = true

      try {
        const faqData = {
          question: form.question.trim(),
          answer: form.answer.trim(),
          target_role: form.target_role,
          order_index: form.order_index,
          is_active: form.is_active
        }

        if (isEditing.value) {
                  await communicationAPI.updateFAQ(props.faq.faq_id, faqData)
      } else {
        await communicationAPI.createFAQ(faqData)
        }

        emit('saved')
      } catch (error) {
        console.error('Error saving FAQ:', error)
        
        // Handle validation errors from server
        if (error.response?.data) {
          const serverErrors = error.response.data
          Object.keys(serverErrors).forEach(key => {
            if (errors.hasOwnProperty(key)) {
              errors[key] = Array.isArray(serverErrors[key]) 
                ? serverErrors[key][0] 
                : serverErrors[key]
            }
          })
        }
      } finally {
        loading.value = false
      }
    }

    const closeModal = () => {
      emit('close')
    }

    // Initialize form data if editing
    onMounted(() => {
      if (props.faq) {
        form.question = props.faq.question || ''
        form.answer = props.faq.answer || ''
        form.target_role = props.faq.target_role || ''
        form.order_index = props.faq.order_index || 0
        form.is_active = props.faq.is_active !== false
      }
    })

    return {
      loading,
      form,
      errors,
      isEditing,
      saveFAQ,
      closeModal
    }
  }
}
</script> 