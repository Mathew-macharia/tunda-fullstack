<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <!-- Shop by Categories -->
      <div class="mb-8 sm:mb-12">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl sm:text-3xl font-bold text-gray-900">Shop by Category</h2>
          <router-link 
            to="/products" 
            class="text-green-600 hover:text-green-700 text-sm font-medium flex items-center space-x-1"
          >
            <span>View All</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </router-link>
        </div>
        
        <!-- Loading State -->
        <div v-if="loadingCategories" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 sm:gap-6">
          <div v-for="n in 5" :key="n" class="bg-white rounded-2xl p-6 shadow-sm animate-pulse">
            <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-gray-200 mx-auto mb-4"></div>
            <div class="h-4 bg-gray-200 rounded"></div>
          </div>
        </div>
        
        <!-- Categories Scrollable List -->
        <div v-else class="relative">
          <div class="flex space-x-4 overflow-x-auto pb-2 -mb-2 scrollbar-hide scroll-fade">
            <div
              v-for="category in categories"
              :key="category.category_id"
              @click="filterByCategory(category.category_id)"
              class="flex-shrink-0 w-32 sm:w-40 bg-white rounded-2xl p-4 sm:p-6 shadow-sm hover:shadow-lg transition-all duration-300 cursor-pointer text-center border border-gray-100 hover:border-green-200 transform hover:-translate-y-1"
            >
              <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl overflow-hidden mx-auto mb-3 sm:mb-4 shadow-md">
                <img 
                  :src="getCategoryImage(category.category_name)"
                  :alt="category.category_name"
                  class="w-full h-full object-cover"
                />
              </div>
              <h3 class="text-sm sm:text-base font-semibold text-gray-900 line-clamp-2">
                {{ category.category_name }}
              </h3>
            </div>
          </div>
        </div>
      </div>

      <!-- Today's Fresh Picks -->
      <div class="mb-8 sm:mb-12">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl sm:text-3xl font-bold text-gray-900">Today's Fresh Picks</h2>
          <router-link 
            to="/products" 
            class="text-green-600 hover:text-green-700 text-sm font-medium flex items-center space-x-1"
          >
            <span>View All</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </router-link>
        </div>
        
        <!-- Loading State -->
        <div v-if="loadingFreshPicks" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 sm:gap-6">
          <div v-for="n in 5" :key="n" class="bg-white rounded-2xl shadow-sm animate-pulse">
            <div class="h-40 sm:h-48 bg-gray-200 rounded-t-2xl"></div>
            <div class="p-4">
              <div class="h-4 bg-gray-200 rounded mb-2"></div>
              <div class="h-3 bg-gray-200 rounded w-2/3"></div>
            </div>
          </div>
        </div>
        
        <!-- Fresh Picks Grid -->
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 sm:gap-6">
          <div
            v-for="listing in freshPicks"
            :key="listing.listing_id"
            class="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
            @click="viewProduct(listing)"
          >
            <!-- Product Image -->
            <div class="relative overflow-hidden rounded-t-2xl">
              <img
                v-if="listing.photos && listing.photos.length"
                :src="listing.photos[0]"
                :alt="listing.product_name"
                class="w-full h-40 sm:h-48 object-cover"
              />
              <div v-else class="w-full h-40 sm:h-48 bg-gray-200 flex items-center justify-center">
                <svg class="h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
              </div>
              
              <!-- Status Badge -->
              <div class="absolute top-3 left-3">
                <span
                  :class="{
                    'bg-green-100 text-green-800': listing.listing_status === 'available',
                    'bg-yellow-100 text-yellow-800': listing.listing_status === 'pre_order',
                    'bg-red-100 text-red-800': listing.listing_status === 'sold_out'
                  }"
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium shadow-sm"
                >
                  {{ getStatusDisplay(listing.listing_status) }}
                </span>
              </div>
              
              <!-- Organic Badge -->
              <div v-if="listing.is_organic_certified" class="absolute top-3 right-3">
                <span class="bg-green-600 text-white px-2.5 py-1 rounded-full text-xs font-medium shadow-sm">
                  Organic
                </span>
              </div>
            </div>
            
            <!-- Product Info -->
            <div class="p-4">
              <h3 class="text-sm font-semibold text-gray-900 line-clamp-1 mb-2">
                {{ listing.product_name }}
              </h3>
              
              <div class="flex items-center justify-between mb-2">
                <div class="text-lg font-bold text-gray-900">
                  KSh {{ listing.current_price }}
                </div>
                <div class="text-xs text-gray-500">
                  per {{ listing.product_unit_display }}
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
              
              <div class="flex items-center text-xs text-gray-500 mb-3">
                <svg class="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <span class="truncate">{{ listing.farm_name }}</span>
              </div>
              
              <div class="flex items-center justify-between">
                <div class="text-xs text-gray-500">
                  {{ listing.quantity_available }} {{ listing.product_unit_display }} left
                </div>
                
                <button
                  v-if="listing.listing_status === 'available'"
                  @click.stop="addToCart(listing)"
                  :disabled="addingToCart === listing.listing_id"
                  class="bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
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
      </div>

      <!-- Health Tip Card -->
      <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-6 sm:p-8 border border-green-100">
        <div class="flex flex-col sm:flex-row items-start sm:space-x-4 space-y-4 sm:space-y-0">
          <div class="flex-shrink-0 w-24 h-24 sm:w-32 sm:h-32 bg-green-100 rounded-full flex items-center justify-center mx-auto sm:mx-0">
            <img src="@/assets/illustrations/healthylifestyle.svg" alt="Healthy Lifestyle" class="w-full h-full object-contain" />
          </div>
          <div class="flex-1 text-center sm:text-left">
            <h3 class="text-lg sm:text-xl font-bold text-gray-900 mb-2">Today's Health Tip</h3>
            <p class="text-gray-700 text-sm sm:text-base leading-relaxed mb-4">
              {{ currentHealthTip }}
            </p>
            <div class="flex items-center justify-center sm:justify-start text-sm text-green-600 font-medium">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>Eat fresh, live healthy!</span>
            </div>
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
        class="fixed bottom-4 right-4 sm:top-4 sm:right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center space-x-3"
      >
        <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <p class="font-medium">{{ notificationMessage }}</p>
        <button @click="showNotification = false" class="ml-auto -mr-1 p-1 rounded-full hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { isAuthenticated, isCustomer, addGuestCartItem } from '@/stores/auth'
import { productsAPI, cartAPI } from '@/services/api'

export default {
  name: 'HomePage',
  setup() {
    const router = useRouter()
    
    // State
    const categories = ref([])
    const freshPicks = ref([])
    const searchQuery = ref('')
    const addingToCart = ref(null)
    const showNotification = ref(false)
    const notificationMessage = ref('')
    
    // Loading states
    const loadingCategories = ref(false)
    const loadingFreshPicks = ref(false)
    
    // Health tips array
    const healthTips = [
      "Eating 5 servings of fruits and vegetables daily can reduce your risk of heart disease by 20%. Start your day with a colorful fruit salad!",
      "Dark leafy greens like spinach and kale are packed with iron and folate. Add them to your smoothies for an extra nutritional boost.",
      "Berries are nature's antioxidant powerhouses! Blueberries, strawberries, and blackberries help fight inflammation and boost brain health.",
      "Orange and yellow vegetables like carrots, sweet potatoes, and bell peppers are rich in beta-carotene, which supports healthy vision and immune function.",
      "Fresh herbs like basil, cilantro, and parsley not only add flavor but also provide essential vitamins and minerals. Grow your own herb garden for maximum freshness!",
      "Whole grains provide sustained energy and fiber for digestive health. Choose brown rice, quinoa, and oats over processed alternatives.",
      "Legumes like beans, lentils, and chickpeas are excellent sources of plant-based protein and fiber. They help maintain stable blood sugar levels.",
      "Stay hydrated by eating water-rich foods like cucumbers, watermelon, and tomatoes. They help maintain healthy skin and support kidney function."
    ]
    
    // Image mapping for categories with correct extensions
    const categoryImages = {
      'dairy': 'dairy.jpg',
      'fruits': 'fruits.webp',
      'grains': 'grains.jpg',
      'herbs & spices': 'herbs and spices.png',
      'honey & natural': 'honey.webp',
      'legumes': 'legumes.jpg',
      'meat & poultry': 'meat and poultry.jpg',
      'nuts & seeds': 'nuts.png',
      'processed foods': 'ProcessedFoods.jpg',
      'vegetables': 'vegetables.webp',
      'default': 'default.jpg' // Fallback default image
    }
    
    // Computed
    const currentHealthTip = computed(() => {
      const today = new Date()
      const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 86400000)
      return healthTips[dayOfYear % healthTips.length]
    })
    
    // Methods
    const getCategoryImage = (categoryName) => {
      const imagePath = categoryImages[categoryName.toLowerCase()] || categoryImages.default;
      return `/images/categories/${imagePath}`;
    }
    
    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        if (searchQuery.value.trim()) {
          router.push(`/products?search=${encodeURIComponent(searchQuery.value)}`)
        }
      }, 500)
    }
    
    const loadCategories = async () => {
      loadingCategories.value = true
      try {
        const response = await productsAPI.getCategories()
        categories.value = response.results || response
      } catch (error) {
        console.error('Failed to load categories:', error)
      } finally {
        loadingCategories.value = false
      }
    }
    
    const loadFreshPicks = async () => {
      loadingFreshPicks.value = true
      try {
        const response = await productsAPI.getListings({
          page_size: 5,
          listing_status: 'available',
          ordering: '-created_at'
        })
        
        if (response.results) {
          freshPicks.value = response.results
        } else if (Array.isArray(response)) {
          freshPicks.value = response.slice(0, 5)
        }
      } catch (error) {
        console.error('Failed to load fresh picks:', error)
      } finally {
        loadingFreshPicks.value = false
      }
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
    
    const filterByCategory = (categoryId) => {
      router.push(`/products?category=${categoryId}`)
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
          // Add to guest cart if not authenticated or not a customer
          addGuestCartItem(listing, listing.min_order_quantity || 1) // Pass the full listing object
          console.log(`${listing.product_name} added to guest cart!`)
        }
        
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        
        notificationMessage.value = `${listing.product_name} added to cart!`
        showNotification.value = true
        setTimeout(() => {
          showNotification.value = false
        }, 3000) // Hide after 3 seconds
        
      } catch (error) {
        console.error('Failed to add to cart:', error)
        notificationMessage.value = 'Failed to add item to cart. Please try again.'
        showNotification.value = true
        setTimeout(() => {
          showNotification.value = false
        }, 3000) // Hide after 3 seconds
      } finally {
        addingToCart.value = null
      }
    }
    
    // Lifecycle
    onMounted(() => {
      loadCategories()
      loadFreshPicks()
    })
    
    return {
      // State
      categories,
      freshPicks,
      searchQuery,
      addingToCart,
      
      // Loading states
      loadingCategories,
      loadingFreshPicks,
      
      // Computed
      isAuthenticated,
      isCustomer,
      currentHealthTip,
      showNotification,
      notificationMessage,
      
      // Methods
      getCategoryImage,
      debouncedSearch,
      getStatusDisplay,
      filterByCategory,
      viewProduct,
      addToCart
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

.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Hide scrollbar for Chrome, Safari and Opera */
.scrollbar-hide::-webkit-scrollbar {
    display: none;
}

/* Hide scrollbar for IE, Edge and Firefox */
.scrollbar-hide {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
}

.scroll-fade {
  mask-image: linear-gradient(to right, transparent, black 20px, black calc(100% - 20px), transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, black 20px, black calc(100% - 20px), transparent);
}
</style>
