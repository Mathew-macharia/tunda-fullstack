<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Reviews & Ratings</h1>
        <p class="mt-2 text-gray-600">Share your experience and read reviews from other customers</p>
      </div>
      <button @click="showReviewModal = true"
              class="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors">
        Write Review
      </button>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="-mb-px flex space-x-8">
        <button v-for="tab in tabs" :key="tab.key"
                @click="activeTab = tab.key"
                :class="activeTab === tab.key ? 'border-green-500 text-green-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                class="py-2 px-1 border-b-2 font-medium text-sm">
          {{ tab.label }}
          <span v-if="tab.count !== null" class="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2.5 rounded-full text-xs">
            {{ tab.count }}
          </span>
        </button>
      </nav>
    </div>

    <!-- My Reviews Tab -->
    <div v-if="activeTab === 'my_reviews'">
      <!-- Filters -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Review Type</label>
            <select v-model="myReviewsFilters.target_type" 
                    class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
              <option value="">All Types</option>
              <option value="product">Products</option>
              <option value="farmer">Farmers</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Rating</label>
            <select v-model="myReviewsFilters.rating" 
                    class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
              <option value="">All Ratings</option>
              <option value="5">5 Stars</option>
              <option value="4">4 Stars</option>
              <option value="3">3 Stars</option>
              <option value="2">2 Stars</option>
              <option value="1">1 Star</option>
            </select>
          </div>
          <div class="flex items-end">
            <button @click="loadMyReviews" 
                    class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      <!-- My Reviews List -->
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        <p class="mt-2 text-gray-600">Loading your reviews...</p>
      </div>

      <div v-else-if="myReviews.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.001 8.001 0 01-7.93-6.93c-.04-.54-.04-1.1 0-1.64A8.001 8.001 0 018.5 2.5L21 12z"></path>
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">No reviews yet</h3>
        <p class="mt-2 text-gray-600">You haven't written any reviews. Share your experience with other customers!</p>
        <button @click="showReviewModal = true" 
                class="mt-4 bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors">
          Write Your First Review
        </button>
      </div>

      <div v-else class="space-y-4">
        <div v-for="review in myReviews" :key="review.review_id" class="bg-white border border-gray-200 rounded-lg p-4">
          <!-- Review Header -->
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                <span class="text-white font-medium text-sm">
                  {{ review.reviewer_username?.charAt(0)?.toUpperCase() || 'U' }}
                </span>
              </div>
              <div>
                <h4 class="font-medium text-gray-900">{{ review.reviewer_username || 'Anonymous' }}</h4>
                <div class="flex items-center space-x-2">
                  <div class="flex items-center">
                    <svg v-for="star in 5" :key="star"
                         :class="star <= review.rating ? 'text-yellow-400' : 'text-gray-300'"
                         class="w-4 h-4 fill-current" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                  </div>
                  <span class="text-sm text-gray-500">{{ review.rating }}/5</span>
                </div>
                <p class="text-xs text-gray-500 mt-1">
                  {{ new Date(review.review_date).toLocaleDateString() }}
                  <span v-if="review.is_verified_purchase" class="ml-2 text-green-600">✓ Verified Purchase</span>
                </p>
              </div>
            </div>
          </div>

          <!-- Review Content -->
          <div v-if="review.comment" class="mb-3">
            <p class="text-gray-700 leading-relaxed">{{ review.comment }}</p>
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center justify-between">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="review.target_type === 'product' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'">
              {{ review.target_type === 'product' ? 'Product Review' : 'Farmer Review' }}
            </span>
            
            <div class="flex items-center space-x-2">
              <button @click="editReview(review)"
                      class="text-sm text-blue-600 hover:text-blue-700 font-medium">
                Edit
              </button>
              <button @click="deleteReview(review)"
                      class="text-sm text-red-600 hover:text-red-700 font-medium">
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- All Reviews Tab -->
    <div v-if="activeTab === 'all_reviews'">
      <!-- Filters -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Review Type</label>
            <select v-model="allReviewsFilters.target_type" 
                    class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
              <option value="">All Types</option>
              <option value="product">Products</option>
              <option value="farmer">Farmers</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Rating</label>
            <select v-model="allReviewsFilters.rating" 
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
            <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input v-model="allReviewsFilters.search" type="text" 
                   placeholder="Search reviews..."
                   class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
          </div>
          <div class="flex items-end">
            <button @click="loadAllReviews" 
                    class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      <!-- All Reviews List -->
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        <p class="mt-2 text-gray-600">Loading reviews...</p>
      </div>

      <div v-else-if="allReviews.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.001 8.001 0 01-7.93-6.93c-.04-.54-.04-1.1 0-1.64A8.001 8.001 0 018.5 2.5L21 12z"></path>
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">No reviews found</h3>
        <p class="mt-2 text-gray-600">No reviews match your current filters.</p>
      </div>

      <div v-else class="space-y-4">
        <div v-for="review in allReviews" :key="review.review_id" class="bg-white border border-gray-200 rounded-lg p-4">
          <!-- Review Header -->
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                <span class="text-white font-medium text-sm">
                  {{ review.reviewer_username?.charAt(0)?.toUpperCase() || 'U' }}
                </span>
              </div>
              <div>
                <h4 class="font-medium text-gray-900">{{ review.reviewer_username || 'Anonymous' }}</h4>
                <div class="flex items-center space-x-2">
                  <div class="flex items-center">
                    <svg v-for="star in 5" :key="star"
                         :class="star <= review.rating ? 'text-yellow-400' : 'text-gray-300'"
                         class="w-4 h-4 fill-current" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                  </div>
                  <span class="text-sm text-gray-500">{{ review.rating }}/5</span>
                </div>
                <p class="text-xs text-gray-500 mt-1">
                  {{ new Date(review.review_date).toLocaleDateString() }}
                  <span v-if="review.is_verified_purchase" class="ml-2 text-green-600">✓ Verified Purchase</span>
                </p>
              </div>
            </div>
          </div>

          <!-- Review Content -->
          <div v-if="review.comment" class="mb-3">
            <p class="text-gray-700 leading-relaxed">{{ review.comment }}</p>
          </div>

          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="review.target_type === 'product' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'">
            {{ review.target_type === 'product' ? 'Product Review' : 'Farmer Review' }}
          </span>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="allReviewsPagination.total > allReviewsPagination.pageSize" class="mt-8 flex justify-center">
        <nav class="flex items-center space-x-2">
          <button @click="goToPage(allReviewsPagination.page - 1)"
                  :disabled="allReviewsPagination.page === 1"
                  class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50">
            Previous
          </button>
          <span class="px-3 py-1 text-sm text-gray-700">
            Page {{ allReviewsPagination.page }} of {{ Math.ceil(allReviewsPagination.total / allReviewsPagination.pageSize) }}
          </span>
          <button @click="goToPage(allReviewsPagination.page + 1)"
                  :disabled="allReviewsPagination.page >= Math.ceil(allReviewsPagination.total / allReviewsPagination.pageSize)"
                  class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50">
            Next
          </button>
        </nav>
      </div>
    </div>

    <!-- Review Modal -->
    <ReviewModal
      :isOpen="showReviewModal"
      context="reviews-page"
      :editing-review="editingReview"
      @close="closeReviewModal"
      @success="handleReviewSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { reviewsAPI } from '@/services/api'
import ReviewModal from '@/components/common/ReviewModal.vue'

const loading = ref(false)
const activeTab = ref('my_reviews')
const showReviewModal = ref(false)
const editingReview = ref(null)

const myReviews = ref([])
const allReviews = ref([])

const myReviewsFilters = ref({
  target_type: '',
  rating: ''
})

const allReviewsFilters = ref({
  target_type: '',
  rating: '',
  search: ''
})

const allReviewsPagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

const tabs = ref([
  { 
    key: 'my_reviews', 
    label: 'My Reviews', 
    count: 0 
  },
  { 
    key: 'all_reviews', 
    label: 'All Reviews', 
    count: null 
  }
])

onMounted(() => {
  loadMyReviews()
})

const loadMyReviews = async () => {
  loading.value = true
  try {
    const response = await reviewsAPI.getMyReviews()
    myReviews.value = Array.isArray(response) ? response : (response.results || [])
    tabs.value[0].count = myReviews.value.length
    
    // Apply client-side filtering
    let filtered = myReviews.value
    if (myReviewsFilters.value.target_type) {
      filtered = filtered.filter(review => review.target_type === myReviewsFilters.value.target_type)
    }
    if (myReviewsFilters.value.rating) {
      filtered = filtered.filter(review => Math.floor(review.rating) === parseInt(myReviewsFilters.value.rating))
    }
    myReviews.value = filtered
  } catch (error) {
    console.error('Failed to load my reviews:', error)
  } finally {
    loading.value = false
  }
}

const loadAllReviews = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      page_size: allReviewsPagination.value.pageSize
    }
    
    if (allReviewsFilters.value.target_type) params.target_type = allReviewsFilters.value.target_type
    if (allReviewsFilters.value.rating) params.rating = allReviewsFilters.value.rating
    if (allReviewsFilters.value.search) params.search = allReviewsFilters.value.search

    const response = await reviewsAPI.getReviews(params)
    
    if (response.results) {
      allReviews.value = response.results
      allReviewsPagination.value.total = response.count || 0
      allReviewsPagination.value.page = page
    } else {
      allReviews.value = Array.isArray(response) ? response : []
    }
  } catch (error) {
    console.error('Failed to load all reviews:', error)
  } finally {
    loading.value = false
  }
}

const goToPage = (page) => {
  loadAllReviews(page)
}

const editReview = (review) => {
  editingReview.value = review
  showReviewModal.value = true
}

const deleteReview = async (review) => {
  if (confirm('Are you sure you want to delete this review?')) {
    try {
      await reviewsAPI.deleteReview(review.review_id)
      myReviews.value = myReviews.value.filter(r => r.review_id !== review.review_id)
      allReviews.value = allReviews.value.filter(r => r.review_id !== review.review_id)
    } catch (error) {
      console.error('Failed to delete review:', error)
    }
  }
}

const closeReviewModal = () => {
  showReviewModal.value = false
  editingReview.value = null
}

const handleReviewSuccess = (review) => {
  if (editingReview.value) {
    // Update existing review
    const index = myReviews.value.findIndex(r => r.review_id === editingReview.value.review_id)
    if (index !== -1) {
      myReviews.value[index] = review
    }
  } else {
    // Add new review
    myReviews.value.unshift(review)
    tabs.value[0].count = myReviews.value.length
  }
  
  // Refresh all reviews if we're on that tab
  if (activeTab.value === 'all_reviews') {
    loadAllReviews(allReviewsPagination.value.page)
  }
  
  closeReviewModal()
}
</script>