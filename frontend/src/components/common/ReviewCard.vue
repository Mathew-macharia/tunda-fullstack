<template>
  <div class="bg-white border border-gray-200 rounded-lg p-4 mb-4">
    <!-- Review Header -->
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-full flex items-center justify-center" :style="{ backgroundColor: getReviewerColor(review.reviewer) }">
          <span class="text-white font-medium text-sm">
            {{ review.reviewer_username?.charAt(0)?.toUpperCase() || 'A' }}
          </span>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <!-- Star Rating -->
            <div class="flex items-center">
              <svg v-for="star in 5" :key="star"
                   :class="star <= review.rating ? 'text-yellow-400' : 'text-gray-300'"
                   class="w-4 h-4 fill-current" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
            </div>
            <span class="text-sm text-gray-500">{{ Math.floor(review.rating) }}/5</span>
          </div>
          <h4 class="font-medium text-gray-900 mt-1">— Anonymous</h4>
          <p class="text-xs text-gray-500 mt-1">
            <span v-if="review.is_verified_purchase" class="inline-flex items-center text-green-600 mr-2">
              <div class="relative w-3 h-3 bg-green-500 rounded-full flex items-center justify-center mr-1">
                <svg class="h-2 w-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                </svg>
              </div>
              Verified Purchase
            </span>
            {{ formatDate(review.review_date) }}
          </p>
        </div>
      </div>
      
      <!-- Admin Actions -->
      <div v-if="showAdminActions && user?.user_role === 'admin'" class="flex items-center space-x-2">
        <button
          @click="toggleVisibility"
          :class="review.is_visible ? 'text-red-600 hover:text-red-700' : 'text-green-600 hover:text-green-700'"
          class="text-sm font-medium"
        >
          {{ review.is_visible ? 'Hide' : 'Show' }}
        </button>
      </div>
    </div>

    <!-- Review Content -->
    <div v-if="review.comment" class="mb-3">
      <p class="text-gray-700 leading-relaxed">{{ review.comment }}</p>
    </div>

    <!-- Review Photos -->
    <div v-if="review.review_photos && review.review_photos.length > 0" class="mb-3">
      <div class="flex space-x-2 overflow-x-auto">
        <img v-for="(photo, index) in review.review_photos" :key="index"
             :src="photo" :alt="`Review photo ${index + 1}`"
             class="w-20 h-20 object-cover rounded-lg flex-shrink-0">
      </div>
    </div>

    <!-- Action Buttons -->
    <div v-if="showActions" class="flex items-center space-x-2">
      <button v-if="canEdit" @click="$emit('edit', review)"
              class="text-sm text-green-600 hover:text-green-700 font-medium">
        Edit
      </button>
      <button v-if="canDelete" @click="$emit('delete', review)"
              class="text-sm text-red-600 hover:text-red-700 font-medium">
        Delete
      </button>
    </div>
    <span v-if="!review.is_visible && showAdminActions" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 mt-2">
      Hidden
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { user } from '@/stores/auth' // Directly import user
import { reviewsAPI } from '@/services/api'

const props = defineProps({
  review: {
    type: Object,
    required: true
  },
  showActions: {
    type: Boolean,
    default: false
  },
  showAdminActions: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit', 'delete', 'updated'])

// No need for authStore if user is directly imported
// const authStore = useAuthStore()
// const user = computed(() => authStore.user)

const canEdit = computed(() => {
  return user.value && (
    user.value.user_id === props.review.reviewer ||
    user.value.user_role === 'admin'
  )
})

const canDelete = computed(() => {
  return user.value && (
    user.value.user_id === props.review.reviewer ||
    user.value.user_role === 'admin'
  )
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getTargetTypeLabel = (type) => {
  const labels = {
    product: 'Product Review',
    farmer: 'Farmer Review', 
  }
  return labels[type] || type
}

const getTargetTypeClass = (type) => {
  const classes = {
    product: 'bg-blue-100 text-blue-800',
    farmer: 'bg-green-100 text-green-800',
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const colorPalette = [
  '#EF4444', // Red-500
  '#F97316', // Orange-500
  '#EAB308', // Yellow-500
  '#22C55E', // Green-500
  '#10B981', // Emerald-500
  '#06B6D4', // Cyan-500
  '#3B82F6', // Blue-500
  '#6366F1', // Indigo-500
  '#8B5CF6', // Violet-500
  '#EC4899', // Pink-500
];

const getReviewerColor = (reviewerId) => {
  if (!reviewerId) return '#9CA3AF'; // Gray-400 for default/unknown

  // Simple hash function to get a deterministic color based on reviewerId
  let hash = 0;
  const idString = String(reviewerId);
  for (let i = 0; i < idString.length; i++) {
    hash = idString.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash % colorPalette.length);
  return colorPalette[index];
};

const toggleVisibility = async () => {
  try {
    const updatedReview = await reviewsAPI.moderateReview(props.review.review_id, {
      is_visible: !props.review.is_visible
    })
    emit('updated', updatedReview)
  } catch (error) {
    console.error('Failed to moderate review:', error)
  }
}
</script>