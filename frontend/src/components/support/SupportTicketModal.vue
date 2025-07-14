<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-3 sm:p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900 pr-4 leading-tight">
          {{ editingTicket ? 'Edit Support Ticket' : 'Create Support Ticket' }}
        </h3>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600 p-1 touch-manipulation">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Content -->
      <form @submit.prevent="submitTicket" class="p-4 sm:p-6 space-y-4 sm:space-y-6">
        <!-- Subject -->
        <div>
          <label class="form-label">Subject *</label>
          <input
            v-model="form.subject"
            type="text"
            class="form-input"
            placeholder="Brief description of your issue"
            required
          />
          <div v-if="errors.subject" class="mt-1 text-sm text-red-600">
            {{ errors.subject }}
          </div>
        </div>

        <!-- Category -->
        <div>
          <label class="form-label">Category *</label>
          <select
            v-model="form.category"
            class="form-input"
            required
            @change="updateSubcategories"
          >
            <option value="">Select a category</option>
            <option v-for="category in categories" :key="category.value" :value="category.value">
              {{ category.label }}
            </option>
          </select>
          <div v-if="errors.category" class="mt-1 text-sm text-red-600">
            {{ errors.category }}
          </div>
        </div>

        <!-- Priority -->
        <div>
          <label class="form-label">Priority</label>
          <div class="mt-2 space-y-2">
            <label v-for="priority in priorities" :key="priority.value" class="flex items-center">
              <input
                v-model="form.priority"
                :value="priority.value"
                type="radio"
                class="form-radio"
                :disabled="editingTicket && user?.user_role !== 'admin'"
              />
              <span class="ml-2 text-sm text-gray-700" :class="{ 'opacity-50': editingTicket && user?.user_role !== 'admin' }">
                {{ priority.label }}
                <span class="text-gray-500">- {{ priority.description }}</span>
              </span>
            </label>
          </div>
        </div>

        <!-- Related Order -->
        <div v-if="showOrderSelection">
          <label class="form-label">Related Order (Optional)</label>
          <select v-model="form.order" class="form-input">
            <option value="">Select an order (if applicable)</option>
            <option v-for="order in userOrders" :key="order.order_id" :value="order.order_id">
              Order #{{ order.order_number }} - {{ formatDate(order.created_at) }}
            </option>
          </select>
        </div>

        <!-- Description -->
        <div>
          <label class="form-label">Description *</label>
          <textarea
            v-model="form.description"
            rows="6"
            class="form-input"
            placeholder="Please describe your issue in detail. Include any relevant information that might help us assist you."
            required
          ></textarea>
          <div v-if="errors.description" class="mt-1 text-sm text-red-600">
            {{ errors.description }}
          </div>
          <p class="mt-1 text-xs text-gray-500">
            {{ form.description.length }} characters (minimum 10 required) - Be as specific as possible to help us resolve your issue quickly.
          </p>
        </div>

        <!-- File Attachments -->
        <div>
          <label class="form-label">Attachments (Optional)</label>
          <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
            <div class="space-y-1 text-center">
              <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              <div class="flex text-sm text-gray-600">
                <label class="relative cursor-pointer bg-white rounded-md font-medium text-green-600 hover:text-green-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-green-500">
                  <span>Upload files</span>
                  <input
                    type="file"
                    multiple
                    accept="image/*,.pdf,.doc,.docx"
                    @change="handleFileUpload"
                    class="sr-only"
                  />
                </label>
                <p class="pl-1">or drag and drop</p>
              </div>
              <p class="text-xs text-gray-500">
                PNG, JPG, PDF up to 10MB each
              </p>
            </div>
          </div>
          
          <!-- File Preview -->
          <div v-if="form.attachments.length > 0" class="mt-3 space-y-2">
            <div v-for="(file, index) in form.attachments" :key="index" class="flex items-center justify-between p-2 bg-gray-50 rounded-md">
              <div class="flex items-center">
                <svg class="h-5 w-5 text-gray-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                </svg>
                <span class="text-sm text-gray-700">{{ file.name }}</span>
              </div>
              <button type="button" @click="removeFile(index)" class="text-red-600 hover:text-red-700">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <!-- Actions -->
        <div class="flex flex-col sm:flex-row justify-end space-y-3 sm:space-y-0 sm:space-x-3 pt-4 border-t border-gray-200">
          <button type="button" @click="closeModal" class="btn-secondary w-full sm:w-auto order-2 sm:order-1 touch-manipulation">
            Cancel
          </button>
          <button type="submit" :disabled="loading || !isFormValid" class="btn-primary w-full sm:w-auto order-1 sm:order-2 touch-manipulation">
            {{ loading ? 'Submitting...' : (editingTicket ? 'Update Ticket' : 'Create Ticket') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { communicationAPI, ordersAPI } from '@/services/api'
import { user } from '@/stores/auth'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  editingTicket: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'success'])

const loading = ref(false)
const error = ref('')
const errors = ref({})
const userOrders = ref([])

const form = ref({
  subject: '',
  category: '',
  priority: 'medium',
  description: '',
  order: '',
  attachments: []
})

// Role-based categories
const categoryMap = {
  customer: [
    { value: 'order_issue', label: 'Order Issues' },
    { value: 'payment_problem', label: 'Payment Problems' },
    { value: 'delivery_issue', label: 'Delivery Issues' },
    { value: 'product_quality', label: 'Product Quality' },
    { value: 'technical_support', label: 'Technical Support' },
    { value: 'other', label: 'Other' }
  ],
  farmer: [
    { value: 'order_issue', label: 'Order Management' },
    { value: 'payment_problem', label: 'Payment & Payouts' },
    { value: 'product_quality', label: 'Product Listings' },
    { value: 'technical_support', label: 'Technical Support' },
    { value: 'other', label: 'Business Support' }
  ],
  rider: [
    { value: 'delivery_issue', label: 'Delivery Operations' },
    { value: 'payment_problem', label: 'Payment Issues' },
    { value: 'technical_support', label: 'Technical Support' },
    { value: 'other', label: 'Safety & Security' }
  ]
}

const priorities = [
  { value: 'low', label: 'Low', description: 'General inquiries, feature requests' },
  { value: 'medium', label: 'Medium', description: 'Account issues, minor problems' },
  { value: 'high', label: 'High', description: 'Order problems, payment issues' },
  { value: 'urgent', label: 'Urgent', description: 'Service outages, critical issues' }
]

const categories = computed(() => {
  return categoryMap[user.value?.user_role] || categoryMap.customer
})

const showOrderSelection = computed(() => {
  return user.value?.user_role === 'customer' && ['order_issue', 'delivery_issue', 'product_quality'].includes(form.value.category)
})

const isFormValid = computed(() => {
  return form.value.subject.trim().length > 0 &&
         form.value.category &&
         form.value.description.trim().length > 10
})

// Watch for editing ticket changes
watch(() => props.editingTicket, (newValue) => {
  if (newValue) {
    form.value = {
      subject: newValue.subject || '',
      category: newValue.category || '',
      priority: newValue.priority || 'medium',
      description: newValue.description || '',
      order: newValue.order || '',
      attachments: []
    }
  }
}, { immediate: true })

// Load user orders if customer
onMounted(() => {
  if (user.value?.user_role === 'customer') {
    loadUserOrders()
  }
})

const loadUserOrders = async () => {
  try {
    const response = await ordersAPI.getOrders({ page_size: 20, ordering: '-created_at' })
    userOrders.value = response.results || response || []
  } catch (err) {
    console.error('Failed to load user orders:', err)
  }
}

const updateSubcategories = () => {
  // Clear order selection if category doesn't support it
  if (!showOrderSelection.value) {
    form.value.order = ''
  }
}

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  files.forEach(file => {
    if (file.size <= 10 * 1024 * 1024) { // 10MB limit
      form.value.attachments.push(file)
    }
  })
}

const removeFile = (index) => {
  form.value.attachments.splice(index, 1)
}

const validateForm = () => {
  errors.value = {}
  
  if (!form.value.subject.trim()) {
    errors.value.subject = 'Subject is required'
  }
  
  if (!form.value.category) {
    errors.value.category = 'Category is required'
  }
  
  if (!form.value.description.trim()) {
    errors.value.description = 'Description is required'
  } else if (form.value.description.trim().length < 10) {
    errors.value.description = 'Description must be at least 10 characters'
  }
  
  return Object.keys(errors.value).length === 0
}

// Watch form fields to clear errors as user types
watch(() => form.value.subject, () => {
  if (errors.value.subject) {
    delete errors.value.subject
  }
})

watch(() => form.value.category, () => {
  if (errors.value.category) {
    delete errors.value.category
  }
})

watch(() => form.value.description, () => {
  if (errors.value.description && form.value.description.trim().length >= 10) {
    delete errors.value.description
  }
})

const submitTicket = async () => {
  if (!validateForm()) return

  loading.value = true
  error.value = ''

  try {
    let ticketData = {
      subject: form.value.subject.trim(),
      category: form.value.category,
      description: form.value.description.trim()
    }

    // For new tickets or admin users, include priority and order
    if (!props.editingTicket || user.value?.user_role === 'admin') {
      ticketData.priority = form.value.priority;
      if (form.value.order) {
        ticketData.order = form.value.order;
      }
    }

    // Handle file attachments if any
    if (form.value.attachments.length > 0) {
      // TODO: Implement file upload logic
      console.log('Files to upload:', form.value.attachments)
    }

    let result
    if (props.editingTicket) {
      result = await communicationAPI.updateSupportTicket(props.editingTicket.ticket_id, ticketData)
    } else {
      result = await communicationAPI.createSupportTicket(ticketData)
    }

    emit('success', result)
    closeModal()
  } catch (err) {
    console.error('Failed to submit ticket:', err)
    
    // Handle validation errors from server
    if (err.response?.data && typeof err.response.data === 'object') {
      const serverErrors = err.response.data
      Object.keys(serverErrors).forEach(key => {
        if (errors.value.hasOwnProperty(key)) {
          errors.value[key] = Array.isArray(serverErrors[key]) 
            ? serverErrors[key][0] 
            : serverErrors[key]
        }
      })
      
      // If there are validation errors, don't show generic error
      if (Object.keys(errors.value).length > 0) {
        error.value = ''
      } else {
        error.value = serverErrors.detail || 'Failed to submit ticket. Please try again.'
      }
    } else {
      error.value = err.response?.data?.detail || 'Failed to submit ticket. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  form.value = {
    subject: '',
    category: '',
    priority: 'medium',
    description: '',
    order: '',
    attachments: []
  }
  errors.value = {}
  error.value = ''
  emit('close')
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script>
