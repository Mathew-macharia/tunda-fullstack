<template>
  <div class="min-h-screen bg-gray-50 py-4 sm:py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 sm:mb-8 space-y-4 sm:space-y-0">
        <div class="min-w-0 flex-1">
          <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Product Listings</h1>
          <p class="mt-1 sm:mt-2 text-sm sm:text-base text-gray-600">Manage your product listings and inventory</p>
        </div>
        <div class="flex justify-end">
          <router-link
            to="/farmer/listings/create"
            class="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 w-full sm:w-auto"
          >
            <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
            Add New Product
          </router-link>
        </div>
      </div>

      <!-- Mobile Filters Toggle -->
      <div class="sm:hidden mb-4">
        <button
          @click="showMobileFilters = !showMobileFilters"
          class="w-full flex items-center justify-between px-4 py-3 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          <span>Filters</span>
          <svg 
            :class="{ 'rotate-180': showMobileFilters }"
            class="h-5 w-5 transform transition-transform duration-200" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      <!-- Filters -->
      <div 
        :class="{ 'hidden': !showMobileFilters }"
        class="mb-6 bg-white rounded-lg shadow p-4 sm:p-6 sm:block"
      >
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="col-span-1 sm:col-span-2 lg:col-span-1">
            <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              v-model="filters.search"
              type="text"
              placeholder="Search products..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
              @input="debouncedFilter"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              v-model="filters.status"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
            >
              <option value="">All Status</option>
              <option value="available">Available</option>
              <option value="pre_order">Pre-Order</option>
              <option value="sold_out">Sold Out</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              v-model="filters.category"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
            >
              <option value="">All Categories</option>
              <option v-for="category in categories" :key="category.category_id" :value="category.category_id">
                {{ category.category_name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Farm</label>
            <select
              v-model="filters.farm"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
            >
              <option value="">All Farms</option>
              <option v-for="farm in farms" :key="farm.farm_id" :value="farm.farm_id">
                {{ farm.farm_name }}
              </option>
            </select>
          </div>
        </div>

        <!-- Mobile: Close filters button -->
        <div class="mt-4 sm:hidden">
          <button
            @click="showMobileFilters = false"
            class="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-200"
          >
            Apply Filters
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 sm:h-12 sm:w-12 border-b-2 border-green-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
        <div class="flex">
          <ExclamationTriangleIcon class="h-5 w-5 text-red-400 flex-shrink-0" />
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium text-red-800">Error loading listings</h3>
            <p class="mt-1 text-sm text-red-700 break-words">{{ error }}</p>
            <button 
              @click="loadListings"
              class="mt-2 text-sm text-red-600 hover:text-red-500 underline"
            >
              Try again
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile: List View for smaller screens -->
      <div v-else-if="listings.length > 0" class="block sm:hidden space-y-4">
        <div
          v-for="listing in listings"
          :key="listing.listing_id"
          class="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow duration-200"
        >
          <div class="flex">
            <!-- Image -->
            <div class="relative w-24 h-24 flex-shrink-0">
              <img
                :src="listing.photos?.[0] || '/api/placeholder/96/96'"
                :alt="listing.product_name"
                class="w-full h-full object-cover rounded-l-lg"
              />
              <div class="absolute -top-1 -right-1">
                <span :class="getStatusClass(listing.listing_status)" class="px-1.5 py-0.5 rounded-full text-xs font-medium">
                  {{ formatStatus(listing.listing_status) }}
                </span>
              </div>
            </div>

            <!-- Content -->
            <div class="flex-1 p-4 min-w-0">
              <div class="flex justify-between items-start mb-2">
                <h3 class="text-base font-medium text-gray-900 truncate pr-2">{{ listing.product_name }}</h3>
                <p class="text-base font-semibold text-gray-900 flex-shrink-0">
                  KES {{ formatCurrency(listing.current_price) }}
                </p>
              </div>

              <div class="space-y-1 mb-3">
                <div class="flex items-center text-xs text-gray-600">
                  <HomeIcon class="h-3 w-3 mr-1 text-gray-400 flex-shrink-0" />
                  <span class="truncate">{{ listing.farm_name }}</span>
                </div>
                <div class="flex items-center justify-between text-xs text-gray-600">
                  <div class="flex items-center min-w-0">
                    <TagIcon class="h-3 w-3 mr-1 text-gray-400 flex-shrink-0" />
                    <span class="truncate">{{ listing.product?.category_name || 'Uncategorized' }}</span>
                  </div>
                  <span class="flex-shrink-0 ml-2">{{ listing.quantity_available }} {{ listing.product_unit }}</span>
                </div>
              </div>

              <!-- Mobile Actions -->
              <div class="flex space-x-2">
                <button
                  @click="editListing(listing)"
                  class="flex-1 bg-white border border-gray-300 rounded-md px-2 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-green-500"
                >
                  Edit
                </button>
                <button
                  @click="toggleStatus(listing)"
                  :class="listing.listing_status === 'inactive' ? 'bg-green-600 hover:bg-green-700 text-white' : 'bg-gray-600 hover:bg-gray-700 text-white'"
                  class="flex-1 border border-transparent rounded-md px-2 py-1.5 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-offset-1"
                >
                  {{ listing.listing_status === 'inactive' ? 'Activate' : 'Deactivate' }}
                </button>
                <button
                  @click="deleteListing(listing)"
                  class="px-2 py-1.5 border border-red-300 rounded-md text-xs font-medium text-red-700 hover:bg-red-50 focus:outline-none focus:ring-1 focus:ring-red-500"
                >
                  <TrashIcon class="h-3 w-3" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Desktop: Grid View for larger screens -->
      <div v-else-if="listings.length > 0" class="hidden sm:grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="listing in listings"
          :key="listing.listing_id"
          class="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow duration-200"
        >
          <div class="relative">
            <img
              :src="listing.photos?.[0] || '/api/placeholder/300/200'"
              :alt="listing.product_name"
              class="w-full h-48 object-cover"
            />
            <div class="absolute top-2 right-2">
              <span :class="getStatusClass(listing.listing_status)" class="px-2 py-1 rounded-full text-xs font-medium">
                {{ formatStatus(listing.listing_status) }}
              </span>
            </div>
          </div>

          <div class="p-6">
            <!-- Product Info -->
            <div class="mb-4">
              <h3 class="text-lg font-medium text-gray-900 mb-2">{{ listing.product_name }}</h3>
              <p class="text-sm text-gray-600 line-clamp-2">{{ listing.notes || 'No description available' }}</p>
            </div>

            <!-- Farm and Category -->
            <div class="mb-4 space-y-1">
              <div class="flex items-center text-sm text-gray-600">
                <HomeIcon class="h-4 w-4 mr-2 text-gray-400" />
                <span>{{ listing.farm_name }}</span>
              </div>
              <div class="flex items-center text-sm text-gray-600">
                <TagIcon class="h-4 w-4 mr-2 text-gray-400" />
                <span>{{ listing.product?.category_name || 'Uncategorized' }}</span>
              </div>
            </div>

            <!-- Pricing and Quantity -->
            <div class="mb-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-lg font-semibold text-gray-900">
                    KES {{ formatCurrency(listing.current_price) }}
                    <span class="text-sm font-normal text-gray-600">/ {{ listing.product_unit }}</span>
                  </p>
                  <p class="text-sm text-gray-600">
                    {{ listing.quantity_available }} {{ listing.product_unit }} available
                  </p>
                </div>
                <div class="text-right">
                  <p class="text-sm text-gray-600">Quality: {{ formatQuality(listing.quality_grade) }}</p>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex space-x-2">
              <button
                @click="editListing(listing)"
                class="flex-1 bg-white border border-gray-300 rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <PencilIcon class="h-4 w-4 inline mr-1" />
                Edit
              </button>
              <button
                @click="toggleStatus(listing)"
                :class="listing.listing_status === 'inactive' ? 'bg-green-600 hover:bg-green-700 text-white' : 'bg-gray-600 hover:bg-gray-700 text-white'"
                class="flex-1 border border-transparent rounded-md px-3 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2"
              >
                {{ listing.listing_status === 'inactive' ? 'Activate' : 'Deactivate' }}
              </button>
              <button
                @click="deleteListing(listing)"
                class="px-3 py-2 border border-red-300 rounded-md text-sm font-medium text-red-700 hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                <TrashIcon class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <ClipboardDocumentListIcon class="mx-auto h-16 w-16 sm:h-24 sm:w-24 text-gray-400" />
        <h3 class="mt-4 sm:mt-6 text-base sm:text-lg font-medium text-gray-900">No product listings found</h3>
        <p class="mt-2 text-sm text-gray-500">Get started by creating your first product listing.</p>
        <div class="mt-4 sm:mt-6">
          <router-link
            to="/farmer/listings/create"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
            Create Your First Listing
          </router-link>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="mt-6 sm:mt-8">
        <!-- Mobile Pagination -->
        <div class="flex justify-between items-center sm:hidden">
          <button
            @click="changePage(Math.max(1, currentPage - 1))"
            :disabled="currentPage === 1"
            :class="currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'"
            class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            Previous
          </button>
          <span class="text-sm text-gray-700">
            Page {{ currentPage }} of {{ totalPages }}
          </span>
          <button
            @click="changePage(Math.min(totalPages, currentPage + 1))"
            :disabled="currentPage === totalPages"
            :class="currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'"
            class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            Next
          </button>
        </div>

        <!-- Desktop Pagination -->
        <nav class="hidden sm:flex justify-center">
          <div class="flex space-x-2">
            <button
              v-for="page in visiblePages"
              :key="page"
              @click="changePage(page)"
              :class="currentPage === page ? 'bg-green-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
              class="px-3 py-2 text-sm font-medium border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {{ page }}
            </button>
          </div>
        </nav>
      </div>
    </div>

    <!-- Edit Listing Modal -->
    <ProductListingModal
      v-if="showEditModal"
      :listing="selectedListing"
      :farms="farms"
      :categories="categories"
      @close="closeEditModal"
      @save="handleSaveListing"
    />

    <!-- Delete Confirmation -->
    <ConfirmModal
      v-if="showDeleteModal"
      title="Delete Product Listing"
      message="Are you sure you want to delete this product listing? This action cannot be undone."
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { productsAPI, farmsAPI } from '@/services/api'
import {
  PlusIcon,
  HomeIcon,
  TagIcon,
  PencilIcon,
  TrashIcon,
  ExclamationTriangleIcon,
  ClipboardDocumentListIcon
} from '@heroicons/vue/24/outline'
import ProductListingModal from '@/components/farmer/ProductListingModal.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const router = useRouter()

// State
const loading = ref(true)
const error = ref(null)
const listings = ref([])
const farms = ref([])
const categories = ref([])
const selectedListing = ref(null)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const showMobileFilters = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 12

// Filters
const filters = ref({
  search: '',
  status: '',
  category: '',
  farm: ''
})

// Computed
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// Methods
const loadListings = async () => {
  loading.value = true
  error.value = null
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize,
      ordering: '-created_at'
    }
    
    // Apply filters
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.status) params.listing_status = filters.value.status
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.farm) params.farm = filters.value.farm
    
    const response = await productsAPI.getMyListings(params)
    
    if (response.results) {
      listings.value = response.results
      totalPages.value = Math.ceil(response.count / pageSize)
    } else {
      listings.value = Array.isArray(response) ? response : []
    }
    
  } catch (err) {
    console.error('Error loading listings:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load listings'
  } finally {
    loading.value = false
  }
}

const loadFarms = async () => {
  try {
    const response = await farmsAPI.getFarms()
    farms.value = Array.isArray(response) ? response : response.results || []
  } catch (err) {
    console.error('Error loading farms:', err)
  }
}

const loadCategories = async () => {
  try {
    const response = await productsAPI.getCategories()
    categories.value = Array.isArray(response) ? response : response.results || []
  } catch (err) {
    console.error('Error loading categories:', err)
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatStatus = (status) => {
  const statusMap = {
    'available': 'Available',
    'pre_order': 'Pre-Order',
    'sold_out': 'Sold Out',
    'inactive': 'Inactive'
  }
  return statusMap[status] || status
}

const formatQuality = (quality) => {
  const qualityMap = {
    'premium': 'Premium',
    'standard': 'Standard',
    'economy': 'Economy'
  }
  return qualityMap[quality] || quality
}

const getStatusClass = (status) => {
  const statusClasses = {
    'available': 'bg-green-100 text-green-800',
    'pre_order': 'bg-blue-100 text-blue-800',
    'sold_out': 'bg-red-100 text-red-800',
    'inactive': 'bg-gray-100 text-gray-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const editListing = (listing) => {
  selectedListing.value = listing
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  selectedListing.value = null
}

const handleSaveListing = async (listingData) => {
  try {
    await productsAPI.updateListing(selectedListing.value.listing_id, listingData)
    closeEditModal()
    await loadListings()
  } catch (err) {
    console.error('Error saving listing:', err)
    throw err
  }
}

const toggleStatus = async (listing) => {
  try {
    const newStatus = listing.listing_status === 'inactive' ? 'available' : 'inactive'
    await productsAPI.updateListing(listing.listing_id, { listing_status: newStatus })
    await loadListings()
  } catch (err) {
    console.error('Error updating status:', err)
    error.value = 'Failed to update listing status'
  }
}

const deleteListing = (listing) => {
  selectedListing.value = listing
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  try {
    await productsAPI.deleteListing(selectedListing.value.listing_id)
    showDeleteModal.value = false
    selectedListing.value = null
    await loadListings()
  } catch (err) {
    console.error('Error deleting listing:', err)
    error.value = 'Failed to delete listing'
  }
}

const applyFilters = () => {
  currentPage.value = 1
  showMobileFilters.value = false // Close mobile filters after applying
  loadListings()
}

// Debounced search
let searchTimeout
const debouncedFilter = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(applyFilters, 500)
}

const changePage = (page) => {
  currentPage.value = page
  loadListings()
}

onMounted(async () => {
  await Promise.all([
    loadListings(),
    loadFarms(),
    loadCategories()
  ])
})
</script>