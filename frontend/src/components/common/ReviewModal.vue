<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">
          {{ editingReview ? 'Edit Review' : 'Write a Review' }}
        </h3>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Content -->
      <form @submit.prevent="submitReview" class="p-6 space-y-6">
        <!-- Review Type Display (read-only) -->
        <div v-if="!editingReview">
          <label class="block text-sm font-medium text-gray-700 mb-2">Review Type</label>
          <div class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md text-sm text-gray-700">
            {{ targetType === 'product' ? 'Product Review' : targetType === 'farmer' ? 'Farmer Review' : 'Review' }}
          </div>
        </div>
      
        <!-- Rating -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Rating</label>
          <div class="flex items-center space-x-2">
            <button v-for="star in 5" :key="star" type="button"
                    @click="form.rating = star"
                    :class="star <= form.rating ? 'text-yellow-400' : 'text-gray-300'"
                    class="text-2xl hover:text-yellow-400 transition-colors">
              ★
            </button>
            <span class="text-sm text-gray-600 ml-2">{{ form.rating }}/5</span>
          </div>
        </div>

        <!-- Comment -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Comment</label>
          <textarea v-model="form.comment" rows="4" 
                    class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                    placeholder="Share your experience..."></textarea>
        </div>

        <!-- Photo Upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Photos (optional)</label>
          <input type="file" multiple accept="image/*" @change="handlePhotoUpload" 
                 class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100">
          
          <!-- Photo Previews -->
          <div v-if="form.review_photos.length > 0" class="mt-3 flex space-x-2 overflow-x-auto">
            <div v-for="(photo, index) in form.review_photos" :key="index" class="relative flex-shrink-0">
              <img :src="photo" :alt="`Photo ${index + 1}`" class="w-20 h-20 object-cover rounded-lg">
              <button type="button" @click="removePhoto(index)"
                      class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600">
                ×
              </button>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button type="button" @click="closeModal" 
                  class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
            Cancel
          </button>
          <button type="submit" :disabled="loading || !isFormValid"
                  class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50">
            {{ loading ? 'Saving...' : (editingReview ? 'Update Review' : 'Submit Review') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { reviewsAPI, ordersAPI } from '@/services/api'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  editingReview: {
    type: Object,
    default: null
  },
  targetType: {
    type: String,
    default: ''
  },
  targetId: {
    type: String,
    default: ''
  },
  orderItem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'success'])

const loading = ref(false)
const error = ref('')
const availableOrderItems = ref([])

const form = ref({
  target_type: 'product', // Default to product review
  target_id: props.targetId || '',
  order_item: props.orderItem?.order_item_id || '',
  rating: 5,
  comment: '',
  review_photos: []
})

const isFormValid = computed(() => {
  return form.value.rating >= 1 && form.value.rating <= 5 &&
         form.value.comment.trim().length > 0
         form.value.value.target_type &&
         (form.value.target_id || props.targetId)
})

// Watch for editing review changes
watch(() => props.editingReview, (newValue) => {
  if (newValue) {
    form.value = {
      target_type: newValue.target_type,
      target_id: newValue.target_id,
      order_item: newValue.order_item || '',
      rating: parseFloat(newValue.rating) || 5,
      comment: newValue.comment || '',
      review_photos: newValue.review_photos || []
    }
  }
}, { immediate: true })

const handlePhotoUpload = (event) => {
  const files = Array.from(event.target.files)
  files.forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        form.value.review_photos.push(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  })
}

const removePhoto = (index) => {
  form.value.review_photos.splice(index, 1)
}

const submitReview = async () => {
  if (!isFormValid.value) return

  loading.value = true
  error.value = ''

  try {
    const reviewData = {
      target_type: form.value.target_type,
      target_id: form.value.target_id || props.targetId,
      rating: parseFloat(form.value.rating),
      comment: form.value.comment.trim(),
      review_photos: form.value.review_photos
    }

    // Add order_item if available
    if (props.orderItem?.order_item_id) {
      reviewData.order_item = props.orderItem.order_item_id
    }

    //debug logging
    console.log('Submitting review data:', reviewData)
    console.log('Props:', {
      targetType: props.targetType,
      targetId: props.targetId,
      orderItem: props.orderItem
    })

    let result
    if (props.editingReview) {
      result = await reviewsAPI.updateReview(props.editingReview.review_id, reviewData)
    } else {
      result = await reviewsAPI.createReview(reviewData)
    }

    emit('success', result)
    closeModal()
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Failed to submit review'
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  form.value = {
    target_type: props.targetType || 'product',
    target_id: props.targetId || '',
    order_item: '',
    rating: 5,
    comment: '',
    review_photos: []
  }
  error.value = ''
  emit('close')
}
</script>