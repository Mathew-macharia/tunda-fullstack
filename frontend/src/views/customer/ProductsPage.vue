<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
        <div class="md:flex md:items-center md:justify-between">
          <div class="flex-1 min-w-0">
            <h1 class="text-xl font-bold leading-7 text-primary sm:text-2xl lg:text-3xl">
              Fresh Products
            </h1>
            <p class="mt-1 text-sm text-gray-500">
              Discover fresh produce from local farmers
            </p>
          </div>
          <!-- Mobile filter toggle -->
          <button
            @click="showFilters = !showFilters"
            class="md:hidden mt-3 inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            Filters
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
      <div class="lg:grid lg:grid-cols-4 lg:gap-8">
        <!-- Mobile Filters Overlay -->
        <div
          v-if="showFilters"
          class="fixed inset-0 z-40 md:hidden"
          @click="showFilters = false"
        >
          <div class="absolute inset-0 bg-black bg-opacity-50"></div>
          <div class="relative bg-white h-full max-w-xs shadow-xl overflow-y-auto">
            <div class="px-4 py-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-medium text-gray-900">Filters</h3>
                <button
                  @click="showFilters = false"
                  class="text-gray-400 hover:text-gray-500"
                >
                  <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div class="space-y-6">
                <!-- Mobile filter content (same as desktop) -->
                <div>
                  <label for="mobile-search" class="form-label">Search Products</label>
                  <input
                    id="mobile-search"
                    type="text"
                    v-model="filters.search"
                    @input.stop="debouncedSearch"
                    @click.stop
                    class="form-input"
                    placeholder="Search for products..."
                  />
                  <button @click.stop="debouncedSearch" class="absolute right-2 top-2.5 text-gray-400 hover:text-gray-600">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </button>
                </div>
                
                <div>
                  <label class="form-label">Categories</label>
                  <div class="space-y-2 mt-2">
                    <label class="flex items-center" @click.stop>
                      <input
                        type="radio"
                        value=""
                        v-model="filters.category"
                        @change="resetAndLoadProducts"
                        class="form-radio text-primary"
                      />
                      <span class="ml-2 text-sm text-gray-700">All Categories</span>
                    </label>
                    <label v-for="category in categories" :key="category.category_id" class="flex items-center" @click.stop>
                      <input
                        type="radio"
                        :value="category.category_id"
                        v-model="filters.category"
                        @change="resetAndLoadProducts"
                        class="form-radio text-primary"
                      />
                      <span class="ml-2 text-sm text-gray-700">{{ category.category_name }}</span>
                    </label>
                  </div>
                </div>
                
                <div>
                  <label class="form-label">Availability</label>
                  <div class="space-y-2 mt-2">
                    <label class="flex items-center" @click.stop>
                      <input
                        type="checkbox"
                        v-model="filters.availableOnly"
                        @change="resetAndLoadProducts"
                        class="form-checkbox text-primary"
                      />
                      <span class="ml-2 text-sm text-gray-700">Available Now</span>
                    </label>
                    <label class="flex items-center" @click.stop>
                      <input
                        type="checkbox"
                        v-model="filters.organicOnly"
                        @change="resetAndLoadProducts"
                        class="form-checkbox text-primary"
                      />
                      <span class="ml-2 text-sm text-gray-700">Organic Certified</span>
                    </label>
                  </div>
                </div>
                
                <div>
                  <label for="mobile-sort" class="form-label">Sort By</label>
                  <select
                    id="mobile-sort"
                    v-model="filters.sortBy"
                    @change="resetAndLoadProducts"
                    @click.stop
                    class="form-input"
                  >
                    <option value="">Default</option>
                    <option value="price_asc">Price: Low to High</option>
                    <option value="price_desc">Price: High to Low</option>
                    <option value="name_asc">Name: A to Z</option>
                    <option value="name_desc">Name: Z to A</option>
                    <option value="newest">Newest First</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Desktop Filters Sidebar -->
        <div class="hidden lg:block lg:col-span-1">
          <div class="bg-white rounded-lg shadow p-6 sticky top-24">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Filters</h3>
            
            <!-- Search -->
            <div class="mb-6">
              <label for="search" class="form-label">Search Products</label>
              <input
                id="search"
                type="text"
                v-model="filters.search"
                @input="debouncedSearch"
                class="form-input"
                placeholder="Search for products..."
              />
            </div>
            
            <!-- Categories -->
            <div class="mb-6">
              <label class="form-label">Categories</label>
              <div class="space-y-2 mt-2">
                <label class="flex items-center">
                  <input
                    type="radio"
                    value=""
                    v-model="filters.category"
                    @change="resetAndLoadProducts"
                    class="form-radio text-primary"
                  />
                  <span class="ml-2 text-sm text-gray-700">All Categories</span>
                </label>
                <label v-for="category in categories" :key="category.category_id" class="flex items-center">
                  <input
                    type="radio"
                    :value="category.category_id"
                    v-model="filters.category"
                    @change="resetAndLoadProducts"
                    class="form-radio text-primary"
                  />
                  <span class="ml-2 text-sm text-gray-700">{{ category.category_name }}</span>
                </label>
              </div>
            </div>
            
            <!-- Availability -->
            <div class="mb-6">
              <label class="form-label">Availability</label>
              <div class="space-y-2 mt-2">
                <label class="flex items-center">
                  <input
                    type="checkbox"
                    v-model="filters.availableOnly"
                    @change="resetAndLoadProducts"
                    class="form-checkbox text-primary"
                  />
                  <span class="ml-2 text-sm text-gray-700">Available Now</span>
                </label>
                <label class="flex items-center">
                  <input
                    type="checkbox"
                    v-model="filters.organicOnly"
                    @change="resetAndLoadProducts"
                    class="form-checkbox text-primary"
                  />
                  <span class="ml-2 text-sm text-gray-700">Organic Certified</span>
                </label>
              </div>
            </div>
            
            <!-- Sort -->
            <div>
              <label for="sort" class="form-label">Sort By</label>
              <select
                id="sort"
                v-model="filters.sortBy"
                @change="resetAndLoadProducts"
                class="form-input"
              >
                <option value="">Default</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="name_asc">Name: A to Z</option>
                <option value="name_desc">Name: Z to A</option>
                <option value="newest">Newest First</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- Products Grid -->
        <div class="lg:col-span-3 mt-6 lg:mt-0">
          <!-- Mobile Quick Sort -->
          <div class="md:hidden mb-4 flex items-center justify-between">
            <span class="text-sm text-gray-500">
              {{ products.length }} products
            </span>
            <select
              v-model="filters.sortBy"
              @change="resetAndLoadProducts"
              class="text-sm border-gray-300 rounded-md focus:ring-primary focus:border-primary"
            >
              <option value="">Sort by</option>
              <option value="price_asc">Price ↑</option>
              <option value="price_desc">Price ↓</option>
              <option value="name_asc">Name A-Z</option>
              <option value="newest">Newest</option>
            </select>
          </div>

          <!-- Loading -->
          <div v-if="loading" class="flex justify-center items-center h-64">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
          
          <!-- Empty State -->
          <div v-else-if="!products.length" class="text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No products found</h3>
            <p class="mt-1 text-sm text-gray-500">
              Try adjusting your search or filter criteria.
            </p>
          </div>
          
          <!-- Products Grid -->
          <div v-else class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-6">
            <div
              v-for="listing in products"
              :key="listing.listing_id"
              class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
              @click="viewProduct(listing)"
            >
              <!-- Product Image -->
              <div class="aspect-w-1 aspect-h-1 bg-gray-200 rounded-t-lg overflow-hidden relative">
                <img
                  v-if="(listing.photos && listing.photos.length)"
                  :src="listing.photos[0]"
                  :alt="listing.product_name"
                  class="w-full h-32 sm:h-40 lg:h-48 object-cover"
                />
                <div v-else class="w-full h-32 sm:h-40 lg:h-48 bg-gray-200 flex items-center justify-center">
                  <svg class="h-8 w-8 sm:h-12 sm:w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                </div>
                
                <!-- Status Badge -->
                <div class="absolute top-1 left-1 sm:top-2 sm:left-2">
                  <span
                    :class="{
                      'bg-green-100 text-green-800': listing.listing_status === 'available',
                      'bg-yellow-100 text-yellow-800': listing.listing_status === 'pre_order',
                      'bg-red-100 text-red-800': listing.listing_status === 'sold_out'
                    }"
                    class="inline-flex items-center px-1.5 py-0.5 sm:px-2.5 rounded-full text-xs font-medium"
                  >
                    {{ getStatusDisplay(listing.listing_status) }}
                  </span>
                </div>
                
                <!-- Organic Badge -->
                <div v-if="listing.is_organic_certified" class="absolute top-1 right-1 sm:top-2 sm:right-2">
                  <span class="bg-primary text-white px-1.5 py-0.5 sm:px-2 sm:py-1 rounded-full text-xs font-medium">
                    Organic
                  </span>
                </div>
              </div>
              
              <!-- Product Info -->
              <div class="p-2 sm:p-4">
                <div class="mb-2">
                  <h3 class="text-sm sm:text-base lg:text-lg font-medium text-gray-900 line-clamp-1 mb-1">
                    {{ listing.product_name }}
                  </h3>
                  <div class="flex items-center justify-between">
                    <div>
                      <div class="text-base sm:text-lg font-bold text-gray-900">
                        KSh {{ listing.current_price }}
                      </div>
                      <div class="text-xs sm:text-sm text-gray-500">
                        per {{ listing.product_unit_display }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Compact Rating -->
                <div v-if="listing.review_count > 0" class="flex items-center text-xs text-gray-600 mb-2">
                  <svg class="h-3 w-3 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.538 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.783.57-1.838-.197-1.538-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.929 8.72c-.783-.57-.38-1.81.588-1.81h3.462a1 1 0 00.95-.69l1.07-3.292z"></path>
                  </svg>
                  <span class="font-medium mr-1">{{ listing.average_rating ? listing.average_rating.toFixed(1) : '0.0' }}</span>
                  <span class="text-gray-400">•</span>
                  <span class="ml-1">{{ listing.review_count }} reviews</span>
                </div>

                <div class="flex items-center text-xs sm:text-sm text-gray-500 mb-2">
                  <svg class="h-3 w-3 sm:h-4 sm:w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                  <span class="truncate">{{ listing.farm_name }}</span>
                </div>
                
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
                  <div class="text-xs sm:text-sm text-gray-500">
                    {{ listing.quantity_available }} {{ listing.product_unit_display }} available
                  </div>
                  
                  <button
                    v-if="listing.listing_status === 'available'"
                    @click.stop="addToCart(listing)"
                    :disabled="addingToCart === listing.listing_id"
                    class="btn-primary text-xs sm:text-sm py-1 px-2 sm:px-3 w-full sm:w-auto"
                  >
                    <span v-if="addingToCart === listing.listing_id">Adding...</span>
                    <span v-else>Add to Cart</span>
                  </button>
                  
                  <!-- No longer "Login to Buy" for unauthenticated users, just "Add to Cart" -->
                  <!-- The button above handles both authenticated and unauthenticated -->
                </div>
              </div>
            </div>
          </div>
          
          <!-- Infinite Scroll Trigger / Loading Indicator -->
          <div v-if="nextPageUrl" ref="loadMoreTrigger" class="mt-6 sm:mt-8 flex justify-center">
            <div v-if="loading" class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
          <div v-else-if="products.length > 0 && !loading" class="mt-6 sm:mt-8 text-center text-gray-500">
            You've reached the end of the product list.
          </div>
        </div>
      </div>
    </div>

    <!-- Notification Message -->
    <transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="transform opacity-0 translate-y-full sm:translate-y-0 sm:translate-x-full"
      enter-to-class="transform opacity-100 translate-y-0 sm:translate-x-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="transform opacity-100 translate-y-0 sm:translate-x-0"
      leave-to-class="transform opacity-0 translate-y-full sm:translate-y-0 sm:translate-x-full"
    >
      <div
        v-if="showNotification"
        class="fixed bottom-4 right-4 sm:top-4 sm:right-4 bg-primary text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center space-x-3"
      >
        <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <p class="font-medium">{{ notificationMessage }}</p>
        <button @click="showNotification = false" class="ml-auto -mr-1 p-1 rounded-full hover:bg-primary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { isAuthenticated, isCustomer, addGuestCartItem } from '@/stores/auth'
import { productsAPI, cartAPI } from '@/services/api'

export default {
  name: 'ProductsPage',
  setup() {
    const router = useRouter()
    const route = useRoute() // Initialize useRoute
    const loading = ref(false)
    const products = ref([])
    const categories = ref([])
    const nextPageUrl = ref(null) // For infinite scroll
    const addingToCart = ref(null)
    const showFilters = ref(false)
    const showNotification = ref(false)
    const notificationMessage = ref('')
    const loadMoreTrigger = ref(null) // Ref for the intersection observer target
    
    const filters = reactive({
      search: route.query.search || '',
      category: route.query.category || '',
      farmer_id: route.query.farmer_id || '',
      availableOnly: false,
      organicOnly: false,
      sortBy: ''
    })
    
    // Debounced search
    let searchTimeout
    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        resetAndLoadProducts()
      }, 500)
    }
    
    // Methods
    const loadCategories = async () => {
      try {
        const response = await productsAPI.getCategories()
        categories.value = response.results || response
      } catch (error) {
        console.error('Failed to load categories:', error)
      }
    }
    
    const loadProducts = async () => {
      if (loading.value) return // Prevent multiple simultaneous loads
      loading.value = true
      
      try {
        let response
        if (nextPageUrl.value) {
          // Use the next URL for subsequent loads
          response = await productsAPI.get(nextPageUrl.value)
        } else {
          // Initial load or after filter change
          const params = {
            page_size: 12,
            ...(filters.search && { search: filters.search }),
            ...(filters.category && { category: filters.category }),
            ...(filters.farmer_id && { farmer_id: filters.farmer_id }),
            ...(filters.availableOnly ? { status: 'available' } : {}),
            ...(filters.organicOnly && { organic: 'true' }),
            ...(filters.sortBy && { ordering: getSortOrder(filters.sortBy) })
          }
          response = await productsAPI.getListings(params)
        }
        
        if (response.results) {
          products.value = [...products.value, ...response.results]
          nextPageUrl.value = response.next
        } else if (Array.isArray(response)) {
          products.value = [...products.value, ...response]
          nextPageUrl.value = null // No more pages if it's a plain array
        } else {
          // Handle cases where response might be empty or unexpected
          products.value = products.value // Keep existing products
          nextPageUrl.value = null
        }
      } catch (error) {
        console.error('Failed to load products:', error)
      } finally {
        loading.value = false
      }
    }
    
    const getSortOrder = (sortBy) => {
      const sortMap = {
        'price_asc': 'current_price',
        'price_desc': '-current_price',
        'name_asc': 'product__product_name',
        'name_desc': '-product__product_name',
        'newest': '-created_at'
      }
      return sortMap[sortBy] || ''
    }
    
    const getStatusDisplay = (status) => {
      const statusMap = {
        'available': 'Available',
        'pre_order': 'Pre-order',
        'sold_out': 'Sold Out',
        'inactive': 'Inactive'
      }
      return statusMap[status] || status
    }
    
    const viewProduct = (listing) => {
      router.push(`/products/${listing.listing_id}`)
    }
    
    const addToCart = async (listing) => {
      addingToCart.value = listing.listing_id
      
      try {
        if (isAuthenticated.value && isCustomer.value) {
          await cartAPI.addToCart(listing.listing_id, listing.min_order_quantity || 1)
          console.log(`${listing.product_name} added to authenticated cart!`)
        } else {
          addGuestCartItem(listing, listing.min_order_quantity || 1)
          console.log(`${listing.product_name} added to guest cart!`)
        }
        
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        
        notificationMessage.value = `${listing.product_name} added to cart!`
        showNotification.value = true
        setTimeout(() => {
          showNotification.value = false
        }, 3000)
        
      } catch (error) {
        console.error('Failed to add to cart:', error)
        notificationMessage.value = 'Failed to add item to cart. Please try again.'
        showNotification.value = true
        setTimeout(() => {
          showNotification.value = false
        }, 3000)
      } finally {
        addingToCart.value = null
      }
    }
    
    const resetAndLoadProducts = () => {
      products.value = [] // Clear existing products
      nextPageUrl.value = null // Reset next page URL
      loadProducts()
      showFilters.value = false
    }
    
    // Lifecycle
    onMounted(() => {
      loadCategories()
      loadProducts()
      
      // Set up Intersection Observer
      const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && nextPageUrl.value && !loading.value) {
          loadProducts()
        }
      }, {
        rootMargin: '0px',
        threshold: 0.1
      })
      
      if (loadMoreTrigger.value) {
        observer.observe(loadMoreTrigger.value)
      }
    })

    // Watch for changes in the route's search query
    watch(() => route.query.search, (newSearchQuery) => {
      filters.search = newSearchQuery || '';
      resetAndLoadProducts();
    });

    // Watch for changes in the route's category query
    watch(() => route.query.category, (newCategory) => {
      filters.category = newCategory || '';
      resetAndLoadProducts();
    });

    // Watch for changes in the route's farmer_id query
    watch(() => route.query.farmer_id, (newFarmerId) => {
      filters.farmer_id = newFarmerId || '';
      resetAndLoadProducts();
    });
    
    return {
      loading,
      products,
      categories,
      filters,
      addingToCart,
      showFilters,
      isAuthenticated,
      isCustomer,
      showNotification,
      notificationMessage,
      loadMoreTrigger, // Expose ref to template
      
      // Methods
      debouncedSearch,
      loadProducts,
      resetAndLoadProducts,
      getStatusDisplay,
      viewProduct,
      addToCart,
    }
  }
}
</script>

<style scoped>
.line-clamp-1 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  line-clamp: 1;
}

.form-radio:checked {
  color: #059669;
}

.form-checkbox:checked {
  color: #059669;
}

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
