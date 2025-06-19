<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Quick Search Bar -->
    <div class="bg-white shadow-sm border-b sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-center">
          <div class="w-full max-w-2xl">
            <div class="relative">
              <input
                type="text"
                v-model="searchQuery"
                @input="debouncedSearch"
                class="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500 text-lg shadow-sm"
                placeholder="Search for fresh produce..."
              />
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center">
                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

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
        
        <!-- Categories Grid -->
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 sm:gap-6">
          <div
            v-for="category in categories.slice(0, 8)"
            :key="category.category_id"
            @click="filterByCategory(category.category_id)"
            class="bg-white rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all duration-300 cursor-pointer text-center border border-gray-100 hover:border-green-200 transform hover:-translate-y-1"
          >
            <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl overflow-hidden mx-auto mb-4 shadow-md">
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
              
              <div class="flex items-center justify-between mb-3">
                <div class="text-lg font-bold text-gray-900">
                  KSh {{ listing.current_price }}
                </div>
                <div class="text-xs text-gray-500">
                  per {{ listing.product_unit }}
                </div>
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
                  {{ listing.quantity_available }} {{ listing.product_unit }} left
                </div>
                
                <button
                  v-if="isAuthenticated && isCustomer && listing.listing_status === 'available'"
                  @click.stop="addToCart(listing)"
                  :disabled="addingToCart === listing.listing_id"
                  class="bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
                >
                  <span v-if="addingToCart === listing.listing_id">Adding...</span>
                  <span v-else>Add to Cart</span>
                </button>
                
                <router-link
                  v-else-if="!isAuthenticated"
                  to="/login"
                  @click.stop
                  class="bg-gray-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-gray-700 transition-colors"
                >
                  Login to Buy
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Health Tip Card -->
      <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-6 sm:p-8 border border-green-100">
        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0">
            <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
              </svg>
            </div>
          </div>
          <div class="flex-1">
            <h3 class="text-lg sm:text-xl font-bold text-gray-900 mb-2">Today's Health Tip</h3>
            <p class="text-gray-700 text-sm sm:text-base leading-relaxed mb-4">
              {{ currentHealthTip }}
            </p>
            <div class="flex items-center text-sm text-green-600 font-medium">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>Eat fresh, live healthy!</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { isAuthenticated, isCustomer, user } from '@/stores/auth'
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
    
    // Image mapping for categories
    const categoryImages = {
      'vegetables': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=200&h=200&fit=crop&crop=center',
      'fruits': 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=200&h=200&fit=crop&crop=center',
      'grains': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=200&h=200&fit=crop&crop=center',
      'herbs': 'https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=200&h=200&fit=crop&crop=center',
      'poultry': 'https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?w=200&h=200&fit=crop&crop=center',
      'animal products': 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=200&h=200&fit=crop&crop=center',
      'tubers': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=200&h=200&fit=crop&crop=center',
      'legumes': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=200&h=200&fit=crop&crop=center',
      'default': 'https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=200&h=200&fit=crop&crop=center'
    }
    
    // Computed
    const currentHealthTip = computed(() => {
      const today = new Date()
      const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 86400000)
      return healthTips[dayOfYear % healthTips.length]
    })
    
    // Methods
    const getCategoryImage = (categoryName) => {
      const lowerName = categoryName.toLowerCase()
      for (const [key, value] of Object.entries(categoryImages)) {
        if (lowerName.includes(key)) {
          return value
        }
      }
      return categoryImages.default
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
      if (!isCustomer.value) {
        router.push('/login')
        return
      }
      
      addingToCart.value = listing.listing_id
      
      try {
        await cartAPI.addToCart(listing.listing_id, listing.min_order_quantity || 1)
        
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        
        console.log(`${listing.product_name} added to cart!`)
        
      } catch (error) {
        console.error('Failed to add to cart:', error)
        alert('Failed to add item to cart. Please try again.')
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
      user,
      currentHealthTip,
      
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
</style>