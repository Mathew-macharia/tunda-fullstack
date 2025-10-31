<template>
  <div class="min-h-screen bg-gray-50">
    <HeroSection />
    <SearchBar
      :categories="categories"
      :initialSearchQuery="searchQuery"
      @search="handleSearch"
    />
    <CategoryOverview />
    <ExploreSection />
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-0">
      <!-- Shop by Farmer -->
      <div class="mb-20 sm:mb-24 bg-white py-12 sm:py-20">
        <div class="text-center">
<p class="text-xl font-dancing-script text-gray-900 font-semibold tracking-wide uppercase">Discover your</p>
          <h2 class="mt-2 text-2xl font-extrabold text-primary tracking-tight sm:text-4xl">Favourite Farmer</h2>
        </div>
        <!-- Loading State -->
        <div v-if="loadingFarmers" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 sm:gap-6 mt-8 sm:mt-12">
          <div v-for="n in 6" :key="n" class="bg-white rounded-2xl p-4 sm:p-6 shadow-sm animate-pulse">
            <div class="w-full h-40 sm:h-48 bg-gray-200 rounded-t-2xl"></div>
            <div class="p-4">
              <div class="h-4 bg-gray-200 rounded mb-2"></div>
              <div class="h-3 bg-gray-200 rounded w-2/3"></div>
            </div>
          </div>
        </div>
        
        <!-- Farmers Grid -->
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 sm:gap-6 mt-10 sm:mt-12">
            <FarmerCard
              v-for="farmer in farmers"
              :key="farmer.farmer_id"
              :farmer="farmer"
            />
        </div>
        <div class="mt-8">
          <router-link 
            to="/farmers-marketplace" 
            class="text-primary hover:text-primary-700 text-sm font-medium flex items-center justify-center space-x-1"
          >
            <span>View All Farmers</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </router-link>
        </div>
      </div>

      <!-- Today's Fresh Picks -->
      <div class="mb-8 sm:mb-12">
        <div class="text-center">
<p class="text-xl font-dancing-script text-gray-900 font-semibold tracking-wide uppercase">Today's</p>
          <h2 class="mt-2 text-2xl font-extrabold text-primary tracking-tight sm:text-4xl">Fresh Picks</h2>
        </div>
        
        <!-- Loading State -->
        <div v-if="loadingFreshPicks" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 sm:gap-6 mt-8 sm:mt-12">
          <div v-for="n in 10" :key="n" class="bg-white rounded-2xl shadow-sm animate-pulse">
            <div class="h-40 sm:h-48 bg-gray-200 rounded-t-2xl"></div>
            <div class="p-4">
              <div class="h-4 bg-gray-200 rounded mb-2"></div>
              <div class="h-3 bg-gray-200 rounded w-2/3"></div>
            </div>
          </div>
        </div>
        
        <!-- Fresh Picks Grid -->
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 sm:gap-6 mt-8 sm:mt-12">
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
                <span class="bg-primary text-white px-2.5 py-1 rounded-full text-xs font-medium shadow-sm">
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 2 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
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
                  class="bg-primary text-white px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-darkGreen disabled:opacity-50 transition-colors"
                >
                  <span v-if="addingToCart === listing.listing_id">Adding...</span>
                  <span v-else>Add to Cart</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="mt-8">
          <router-link 
            to="/products" 
            class="text-green-600 hover:text-primary text-sm font-medium flex items-center justify-center space-x-1"
          >
            <span>View All Products</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </router-link>
        </div>
      </div>
    </div>

    <OurServicesSection />

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
import HeroSection from '@/components/HeroSection.vue'
import CategoryOverview from '@/components/CategoryOverview.vue'
import SearchBar from '@/components/SearchBar.vue'
import ExploreSection from '@/components/ExploreSection.vue'
import FarmerCard from '@/components/FarmerCard.vue'
import OurServicesSection from '@/components/OurServicesSection.vue' // Import the new component
import { useHomePageData } from '@/composables/useHomePageData'
import { useCartActions } from '@/composables/useCartActions'
import { isAuthenticated, isCustomer } from '@/stores/auth'

export default {
  name: 'HomePage',
  components: {
    HeroSection,
    CategoryOverview,
    SearchBar,
    ExploreSection,
    FarmerCard,
    OurServicesSection // Register the new component
  },
  setup() {
    const {
      categories,
      farmers,
      freshPicks,
      searchQuery,
      loadingFarmers,
      loadingFreshPicks,
      debouncedSearch,
      getStatusDisplay,
      filterByFarmer,
      getInitials,
      viewProduct,
      getFarmerDisplayImage
    } = useHomePageData()

    console.log('HomePage - farmers ref:', farmers.value);
    console.log('HomePage - loadingFarmers ref:', loadingFarmers.value);

    const handleSearch = ({ query, category }) => {
      console.log('Search triggered from HomePage:', query, category);
    };

    const {
      addingToCart,
      showNotification,
      notificationMessage,
      addToCart
    } = useCartActions()
    
    return {
      categories,
      farmers,
      freshPicks,
      searchQuery,
      loadingFarmers,
      loadingFreshPicks,
      addingToCart,
      showNotification,
      notificationMessage,
      addToCart,
      debouncedSearch,
      getStatusDisplay,
      filterByFarmer,
      getInitials,
      viewProduct,
      handleSearch,
      getFarmerDisplayImage,
      isAuthenticated,
      isCustomer
    }
  }
}
</script>

<style scoped>
.font-dancing-script {
  font-family: 'Dancing Script', cursive;
}

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

.scrollbar-hide::-webkit-scrollbar {
    display: none;
}

.scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

.scroll-fade {
  mask-image: linear-gradient(to right, transparent, black 20px, black calc(100% - 20px), transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, black 20px, black calc(100% - 20px), transparent);
}
</style>
