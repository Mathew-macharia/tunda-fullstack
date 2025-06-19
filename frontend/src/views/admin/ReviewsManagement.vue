<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Reviews Management</h1>
        <p class="mt-2 text-gray-600">Moderate and manage user reviews across the platform</p>
      </div>
      <div class="flex space-x-3">
        <button @click="exportReviews" 
                class="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
          Export Data
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <dt class="text-sm font-medium text-gray-500 truncate">Total Reviews</dt>
        <dd class="text-2xl font-bold text-gray-900">{{ stats.total }}</dd>
      </div>
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <dt class="text-sm font-medium text-gray-500 truncate">Visible Reviews</dt>
        <dd class="text-2xl font-bold text-green-600">{{ stats.visible }}</dd>
      </div>
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <dt class="text-sm font-medium text-gray-500 truncate">Hidden Reviews</dt>
        <dd class="text-2xl font-bold text-red-600">{{ stats.hidden }}</dd>
      </div>
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <dt class="text-sm font-medium text-gray-500 truncate">Average Rating</dt>
        <dd class="text-2xl font-bold text-yellow-600">{{ stats.averageRating.toFixed(1) }}</dd>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Review Type</label>
          <select v-model="filters.target_type" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
            <option value="">All Types</option>
            <option value="product">Products</option>
            <option value="farmer">Farmers</option>
            <option value="rider">Riders</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Rating</label>
          <select v-model="filters.rating" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
            <option value="">All Ratings</option>
            <option value="5">5 Stars</option>
            <option value="4">4 Stars</option>
            <option value="3">3 Stars</option>
            <option value="2">2 Stars</option>
            <option value="1">1 Star</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select v-model="filters.is_visible" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
            <option value="">All Status</option>
            <option value="true">Visible</option>
            <option value="false">Hidden</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input v-model="filters.search" type="text" 
                 placeholder="Search reviews..."
                 class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
        </div>
        <div class="flex items-end space-x-2">
          <button @click="loadReviews" 
                  class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
            Apply Filters
          </button>
          <button @click="resetFilters" 
                  class="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors">
            Reset
          </button>
        </div>
      </div>
    </div>

    <!-- Bulk Actions -->
    <div v-if="selectedReviews.length > 0" class="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <span class="text-sm font-medium text-blue-900">
            {{ selectedReviews.length }} review(s) selected
          </span>
          <button @click="clearSelection" 
                  class="text-blue-600 hover:text-blue-700 text-sm font-medium">
            Clear Selection
          </button>
        </div>
        <div class="flex space-x-2">
          <button @click="bulkHideReviews" 
                  class="bg-red-600 text-white px-3 py-2 rounded-md text-sm hover:bg-red-700">
            Hide Selected
          </button>
          <button @click="bulkShowReviews" 
                  class="bg-green-600 text-white px-3 py-2 rounded-md text-sm hover:bg-green-700">
            Show Selected
          </button>
        </div>
      </div>
    </div>

    <!-- Reviews Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        <p class="mt-2 text-gray-600">Loading reviews...</p>
      </div>

      <div v-else-if="reviews.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.001 8.001 0 01-7.93-6.93c-.04-.54-.04-1.1 0-1.64A8.001 8.001 0 218.5 2.5L21 12z"></path>
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">No reviews found</h3>
        <p class="mt-2 text-gray-600">No reviews match your current filters.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="w-4 px-6 py-3">
                <input type="checkbox" 
                       :checked="isAllSelected" 
                       @change="toggleSelectAll"
                       class="rounded border-gray-300 text-green-600 focus:ring-green-500">
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Review
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rating
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="review in reviews" :key="review.review_id" 
                :class="selectedReviews.includes(review.review_id) ? 'bg-blue-50' : 'hover:bg-gray-50'">
              <td class="px-6 py-4">
                <input type="checkbox" 
                       :value="review.review_id"
                       v-model="selectedReviews"
                       class="rounded border-gray-300 text-green-600 focus:ring-green-500">
              </td>
              <td class="px-6 py-4">
                <div class="flex items-start space-x-3">
                  <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <span class="text-white font-medium text-xs">
                      {{ review.reviewer_username?.charAt(0)?.toUpperCase() || 'U' }}
                    </span>
                  </div>
                  <div class="min-w-0 flex-1">
                    <p class="text-sm font-medium text-gray-900">{{ review.reviewer_username }}</p>
                    <p class="text-sm text-gray-600 truncate max-w-xs">{{ review.comment || 'No comment' }}</p>
                    <span v-if="review.is_verified_purchase" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 mt-1">
                      Verified Purchase
                    </span>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getTargetTypeClass(review.target_type)">
                  {{ getTargetTypeLabel(review.target_type) }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center">
                  <div class="flex items-center">
                    <svg v-for="star in 5" :key="star"
                         :class="star <= review.rating ? 'text-yellow-400' : 'text-gray-300'"
                         class="w-4 h-4 fill-current" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                  </div>
                  <span class="ml-2 text-sm text-gray-600">{{ review.rating }}/5</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <span v-if="review.is_visible" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Visible
                </span>
                <span v-else class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  Hidden
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-600">
                {{ formatDate(review.review_date) }}
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center space-x-2">
                  <button @click="viewReview(review)" 
                          class="text-blue-600 hover:text-blue-700 text-sm font-medium">
                    View
                  </button>
                  <button @click="toggleReviewVisibility(review)"
                          :class="review.is_visible ? 'text-red-600 hover:text-red-700' : 'text-green-600 hover:text-green-700'"
                          class="text-sm font-medium">
                    {{ review.is_visible ? 'Hide' : 'Show' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.total > pagination.pageSize" class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <p class="text-sm text-gray-700">
              Showing {{ ((pagination.page - 1) * pagination.pageSize) + 1 }} to {{ Math.min(pagination.page * pagination.pageSize, pagination.total) }} of {{ pagination.total }} results
            </p>
          </div>
          <div class="flex items-center space-x-2">
            <button @click="goToPage(pagination.page - 1)"
                    :disabled="pagination.page === 1"
                    class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50">
              Previous
            </button>
            <span class="px-3 py-1 text-sm text-gray-700">
              Page {{ pagination.page }} of {{ Math.ceil(pagination.total / pagination.pageSize) }}
            </span>
            <button @click="goToPage(pagination.page + 1)"
                    :disabled="pagination.page >= Math.ceil(pagination.total / pagination.pageSize)"
                    class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50">
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Review Details Modal -->
    <div v-if="selectedReview" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Review Details</h3>
          <button @click="selectedReview = null" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="p-6">
          <ReviewCard :review="selectedReview" :show-admin-actions="true" 
                      @updated="handleReviewUpdated" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { reviewsAPI } from '@/services/api'
import ReviewCard from '@/components/common/ReviewCard.vue'

const loading = ref(false)
const reviews = ref([])
const selectedReview = ref(null)
const selectedReviews = ref([])

const stats = ref({
  total: 0,
  visible: 0,
  hidden: 0,
  averageRating: 0
})

const filters = ref({
  target_type: '',
  rating: '',
  is_visible: '',
  search: ''
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const isAllSelected = computed(() => {
  return reviews.value.length > 0 && selectedReviews.value.length === reviews.value.length
})

onMounted(() => {
  loadReviews()
  loadStats()
})

const loadReviews = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      page_size: pagination.value.pageSize,
      all: true // Admin can see all reviews including hidden ones
    }
    
    Object.keys(filters.value).forEach(key => {
      if (filters.value[key]) params[key] = filters.value[key]
    })

    const response = await reviewsAPI.getReviews(params)
    
    if (response.results) {
      reviews.value = response.results
      pagination.value.total = response.count || 0
      pagination.value.page = page
    } else {
      reviews.value = Array.isArray(response) ? response : []
    }
  } catch (error) {
    console.error('Failed to load reviews:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await reviewsAPI.getReviews({ all: true })
    const allReviews = Array.isArray(response) ? response : (response.results || [])
    
    stats.value.total = allReviews.length
    stats.value.visible = allReviews.filter(r => r.is_visible).length
    stats.value.hidden = allReviews.filter(r => !r.is_visible).length
    
    if (allReviews.length > 0) {
      const totalRating = allReviews.reduce((sum, r) => sum + parseFloat(r.rating), 0)
      stats.value.averageRating = totalRating / allReviews.length
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const resetFilters = () => {
  filters.value = {
    target_type: '',
    rating: '',
    is_visible: '',
    search: ''
  }
  loadReviews(1)
}

const goToPage = (page) => {
  loadReviews(page)
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedReviews.value = []
  } else {
    selectedReviews.value = reviews.value.map(review => review.review_id)
  }
}

const clearSelection = () => {
  selectedReviews.value = []
}

const bulkHideReviews = async () => {
  try {
    await Promise.all(
      selectedReviews.value.map(reviewId => {
        const review = reviews.value.find(r => r.review_id === reviewId)
        if (review?.is_visible) {
          return reviewsAPI.moderateReview(reviewId, { is_visible: false })
        }
      })
    )
    
    selectedReviews.value = []
    loadReviews(pagination.value.page)
    loadStats()
  } catch (error) {
    console.error('Failed to hide reviews:', error)
  }
}

const bulkShowReviews = async () => {
  try {
    await Promise.all(
      selectedReviews.value.map(reviewId => {
        const review = reviews.value.find(r => r.review_id === reviewId)
        if (!review?.is_visible) {
          return reviewsAPI.moderateReview(reviewId, { is_visible: true })
        }
      })
    )
    
    selectedReviews.value = []
    loadReviews(pagination.value.page)
    loadStats()
  } catch (error) {
    console.error('Failed to show reviews:', error)
  }
}

const viewReview = (review) => {
  selectedReview.value = review
}

const toggleReviewVisibility = async (review) => {
  try {
    const updatedReview = await reviewsAPI.moderateReview(review.review_id, {
      is_visible: !review.is_visible
    })
    
    // Update local state
    const index = reviews.value.findIndex(r => r.review_id === review.review_id)
    if (index !== -1) {
      reviews.value[index] = updatedReview
    }
    
    loadStats()
  } catch (error) {
    console.error('Failed to toggle review visibility:', error)
  }
}

const handleReviewUpdated = (updatedReview) => {
  const index = reviews.value.findIndex(r => r.review_id === updatedReview.review_id)
  if (index !== -1) {
    reviews.value[index] = updatedReview
  }
  selectedReview.value = updatedReview
  loadStats()
}

const exportReviews = async () => {
  try {
    // This would need to be implemented in the backend
    const params = { ...filters.value, format: 'csv' }
    // For now, just download current reviews as JSON
    const dataStr = JSON.stringify(reviews.value, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `reviews_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export reviews:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getTargetTypeLabel = (type) => {
  const labels = {
    product: 'Product',
    farmer: 'Farmer', 
    rider: 'Rider'
  }
  return labels[type] || type
}

const getTargetTypeClass = (type) => {
  const classes = {
    product: 'bg-blue-100 text-blue-800',
    farmer: 'bg-green-100 text-green-800',
    rider: 'bg-purple-100 text-purple-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}
</script> 