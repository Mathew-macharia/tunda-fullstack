<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="text-center">
        <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-green-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading farmer profile...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <svg class="w-12 h-12 text-red-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-red-700 font-medium">{{ error }}</p>
        <button @click="$router.go(-1)" class="mt-4 text-green-600 hover:text-green-700 font-medium">
          ← Go Back
        </button>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="farmer" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- Breadcrumbs -->
      <nav class="flex mb-6" aria-label="Breadcrumb">
        <ol class="inline-flex items-center space-x-1 md:space-x-3">
          <li class="inline-flex items-center">
            <router-link to="/" class="text-gray-700 hover:text-green-600 inline-flex items-center">
              <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>
              </svg>
              Home
            </router-link>
          </li>
          <li>
            <div class="flex items-center">
              <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
              </svg>
              <span class="ml-1 text-gray-500 md:ml-2">Farmer Profile</span>
            </div>
          </li>
        </ol>
      </nav>

      <!-- Farmer Header Section -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden mb-8">
        <div class="relative h-48 bg-gradient-to-br from-green-100 via-green-50 to-blue-50"></div>
        
        <div class="px-6 pb-6 pt-6">
          <div class="flex flex-col sm:flex-row items-center sm:items-start -mt-32 sm:-mt-20">
            <!-- Profile Photo -->
            <div class="relative sm:flex-shrink-0">
              <img 
                v-if="farmer.profile_photo_url" 
                :src="farmer.profile_photo_url" 
                :alt="farmer.farmer_name"
                class="h-32 w-32 rounded-full object-cover border-4 border-white shadow-lg"
              />
              <div 
                v-else 
                class="h-32 w-32 rounded-full bg-green-600 flex items-center justify-center border-4 border-white shadow-lg"
              >
                <span class="text-4xl font-bold text-white">{{ getInitials(farmer.farmer_name) }}</span>
              </div>
            </div>

            <!-- Farmer Info -->
            <div class="mt-4 sm:mt-16 sm:ml-6 text-center sm:text-left flex-1">
              <h1 class="text-3xl font-bold text-gray-900">{{ farmer.farmer_name }}</h1>
              
              <div class="flex flex-wrap items-center justify-center sm:justify-start gap-4 mt-2">
                <!-- Location -->
                <div v-if="farmer.primary_location" class="flex items-center text-gray-600">
                  <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span>{{ farmer.primary_location }}</span>
                </div>

                <!-- Member Since -->
                <div class="flex items-center text-gray-600">
                  <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span>Member since {{ formatDate(farmer.member_since) }}</span>
                </div>
              </div>

              <!-- Rating -->
              <div class="flex items-center justify-center sm:justify-start mt-3">
                <div class="flex items-center">
                  <svg 
                    v-for="star in 5" 
                    :key="star"
                    class="w-5 h-5"
                    :class="star <= Math.round(farmer.average_rating) ? 'text-yellow-400' : 'text-gray-300'"
                    fill="currentColor" 
                    viewBox="0 0 20 20"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </div>
                <span class="ml-2 text-lg font-semibold text-gray-700">
                  {{ farmer.average_rating > 0 ? farmer.average_rating.toFixed(1) : 'New Farmer' }}
                </span>
                <span v-if="farmer.review_count > 0" class="ml-1 text-gray-500">
                  ({{ farmer.review_count }} {{ farmer.review_count === 1 ? 'review' : 'reviews' }})
                </span>
              </div>
            </div>

            <!-- View All Products Button -->
            <div class="mt-4 sm:mt-16 sm:ml-4">
              <router-link 
                :to="`/products?farmer_id=${farmer.farmer_id}`"
                class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-green-600 hover:bg-green-700 transition-colors"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
                View All Products
              </router-link>
            </div>
          </div>

          <!-- Statistics -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8">
            <div class="bg-green-50 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-green-600">{{ farmer.total_products }}</div>
              <div class="text-sm text-gray-600 mt-1">Active Products</div>
            </div>
            <div class="bg-blue-50 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-blue-600">{{ farmer.farms_count }}</div>
              <div class="text-sm text-gray-600 mt-1">Farms</div>
            </div>
            <div class="bg-yellow-50 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-yellow-600">{{ farmer.statistics.organic_products }}</div>
              <div class="text-sm text-gray-600 mt-1">Organic Products</div>
            </div>
            <div class="bg-purple-50 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-purple-600">{{ farmer.statistics.total_sales }}</div>
              <div class="text-sm text-gray-600 mt-1">Total Sales</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sample Products Section -->
      <div v-if="farmer.sample_products && farmer.sample_products.length > 0" class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-3">
          <div>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900">Featured Products</h2>
            <p class="text-xs sm:text-sm text-gray-600 mt-1">Fresh from {{ farmer.farmer_name.split(' ')[0] }}'s farm</p>
          </div>
          <router-link 
            :to="`/products?farmer_id=${farmer.farmer_id}`"
            class="text-green-600 hover:text-green-700 text-sm font-medium flex items-center self-start sm:self-auto"
          >
            <span class="whitespace-nowrap">View All ({{ farmer.total_products }})</span>
            <svg class="w-4 h-4 ml-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>
        
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 sm:gap-6">
          <div
            v-for="listing in farmer.sample_products"
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
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Related Farmers Section -->
      <div v-if="relatedFarmers.length > 0" class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-2">
          <div>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900">More Farmers Like This</h2>
            <p class="text-xs sm:text-sm text-gray-600 mt-1">Discover similar local producers</p>
          </div>
        </div>
        
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
          <FarmerCard 
            v-for="relatedFarmer in relatedFarmers" 
            :key="relatedFarmer.farmer_id"
            :farmer="relatedFarmer"
            @farmer-click="goToFarmer"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productsAPI, cartAPI } from '@/services/api'
import { isAuthenticated, isCustomer, addGuestCartItem } from '@/stores/auth'
import FarmerCard from '@/components/common/FarmerCard.vue'

export default {
  name: 'FarmerDetailPage',
  components: {
    FarmerCard
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const farmer = ref(null)
    const relatedFarmers = ref([])
    const loading = ref(true)
    const error = ref(null)
    const addingToCart = ref(null)

    const loadFarmerDetails = async () => {
      loading.value = true
      error.value = null
      
      try {
        const farmerId = route.params.id
        
        // Load farmer details
        farmer.value = await productsAPI.getFarmerDetail(farmerId)
        
        // Load related farmers
        try {
          relatedFarmers.value = await productsAPI.getRelatedFarmers(farmerId)
        } catch (err) {
          console.error('Failed to load related farmers:', err)
          // Don't fail the whole page if related farmers fail
          relatedFarmers.value = []
        }
      } catch (err) {
        console.error('Failed to load farmer details:', err)
        error.value = err.response?.data?.error || 'Failed to load farmer profile. Please try again.'
      } finally {
        loading.value = false
      }
    }

    const getInitials = (name) => {
      if (!name) return '?'
      const parts = name.trim().split(' ')
      if (parts.length === 1) {
        return parts[0].charAt(0).toUpperCase()
      }
      return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
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

    const goToFarmer = (farmerId) => {
      router.push(`/farmers/${farmerId}`)
      // Reload data for the new farmer
      loadFarmerDetails()
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
          addGuestCartItem(listing, listing.min_order_quantity || 1)
          console.log(`${listing.product_name} added to guest cart!`)
        }
        
        window.dispatchEvent(new CustomEvent('cartUpdated'))
      } catch (error) {
        console.error('Failed to add to cart:', error)
      } finally {
        addingToCart.value = null
      }
    }

    onMounted(() => {
      loadFarmerDetails()
    })

    return {
      farmer,
      relatedFarmers,
      loading,
      error,
      addingToCart,
      getInitials,
      formatDate,
      getStatusDisplay,
      goToFarmer,
      viewProduct,
      addToCart
    }
  }
}
</script>

<style scoped>
/* Any additional custom styles can go here */
</style>

