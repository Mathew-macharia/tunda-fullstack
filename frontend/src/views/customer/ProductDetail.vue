<template>
  <div class="min-h-screen bg-gray-50">
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
    </div>
    
    <div v-else-if="!product" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
      <h1 class="text-2xl font-bold text-gray-900">Product not found</h1>
      <router-link to="/products" class="btn-primary mt-4 inline-flex">
        Back to Products
      </router-link>
    </div>
    
    <div v-else class="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8 py-4 sm:py-8">
      <!-- Mobile-optimized Breadcrumb -->
      <nav class="mb-4 sm:mb-8">
        <ol class="flex items-center space-x-1 sm:space-x-2 text-xs sm:text-sm text-gray-500 overflow-x-auto">
          <li><router-link to="/" class="hover:text-gray-700 whitespace-nowrap">Home</router-link></li>
          <li>/</li>
          <li><router-link to="/products" class="hover:text-gray-700 whitespace-nowrap">Products</router-link></li>
          <li>/</li>
          <li class="text-gray-900 truncate">{{ product.product_name }}</li>
        </ol>
      </nav>
      
      <!-- Mobile-first layout: Image and info stack vertically -->
      <div class="space-y-6 lg:grid lg:grid-cols-2 lg:gap-8 lg:space-y-0">
        <!-- Product Image -->
        <div class="order-1">
          <div class="aspect-square bg-gray-200 rounded-lg overflow-hidden">
            <img
              v-if="product.photos && product.photos.length"
              :src="product.photos[0]"
              :alt="product.product_name"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full bg-gray-200 flex items-center justify-center">
              <svg class="h-16 w-16 sm:h-24 sm:w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
            </div>
          </div>
        </div>
        
        <!-- Product Info -->
        <div class="order-2">
          <!-- Header Section -->
          <div class="mb-4 sm:mb-6">
            <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 sm:gap-4">
              <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 leading-tight">
                {{ product.product_name }}
              </h1>
              <div v-if="product.is_organic_certified" class="flex-shrink-0">
                <span class="bg-green-600 text-white px-2 py-1 sm:px-3 rounded-full text-xs sm:text-sm font-medium">
                  Organic Certified
                </span>
              </div>
            </div>
            
            <!-- Price and unit -->
            <div class="mt-3 flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
              <span class="text-2xl sm:text-3xl font-bold text-gray-900">
                KSh {{ product.current_price }}
              </span>
              <span class="text-sm sm:text-lg text-gray-500">
                per {{ product.product_unit }}
              </span>
            </div>
            
            <!-- Status and availability -->
            <div class="mt-3 flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
              <span
                :class="{
                  'bg-green-100 text-green-800': product.listing_status === 'available',
                  'bg-yellow-100 text-yellow-800': product.listing_status === 'pre_order',
                  'bg-red-100 text-red-800': product.listing_status === 'sold_out'
                }"
                class="inline-flex items-center px-2 py-1 sm:px-3 rounded-full text-xs sm:text-sm font-medium w-fit"
              >
                {{ getStatusDisplay(product.listing_status) }}
              </span>
              
              <span class="text-xs sm:text-sm text-gray-500">
                {{ product.quantity_available }} {{ product.product_unit }} available
              </span>
            </div>
          </div>
          
          <!-- Farm Info - Compact mobile version -->
          <div class="mb-4 sm:mb-6 p-3 sm:p-4 bg-gray-50 rounded-lg">
            <h3 class="text-base sm:text-lg font-medium text-gray-900 mb-2">From the Farm</h3>
            <div class="space-y-1">
              <div class="flex items-center space-x-2 text-gray-600">
                <svg class="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <span class="text-sm sm:text-base font-medium">{{ product.farm_name }}</span>
              </div>
              <div class="text-xs sm:text-sm text-gray-500 ml-6">
                By {{ product.farmer_name }}
              </div>
            </div>
          </div>
          
          <!-- Add to Cart Section -->
          <div v-if="isAuthenticated && isCustomer" class="mb-6 sticky bottom-0 bg-white p-3 rounded-lg shadow-lg sm:static sm:bg-transparent sm:p-0 sm:shadow-none">
            <div class="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 mb-3 sm:mb-4">
              <label for="quantity" class="text-sm font-medium text-gray-700">Quantity:</label>
              <div class="flex items-center space-x-2">
                <input
                  id="quantity"
                  type="number"
                  v-model.number="quantity"
                  :min="product.min_order_quantity || 1"
                  :max="product.quantity_available"
                  class="w-16 sm:w-20 px-2 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500 text-center"
                />
                <span class="text-xs sm:text-sm text-gray-500">{{ product.product_unit }}</span>
              </div>
            </div>
            
            <button
              v-if="product.listing_status === 'available'"
              @click="addToCart"
              :disabled="addingToCart"
              class="w-full btn-primary py-3 text-sm sm:text-lg font-medium"
            >
              <span v-if="addingToCart">Adding...</span>
              <span v-else>Add to Cart - KSh {{ (product.current_price * quantity).toFixed(2) }}</span>
            </button>
            
            <div v-else class="w-full bg-gray-100 text-gray-500 py-3 px-4 rounded-md text-center text-sm sm:text-lg">
              Currently Unavailable
            </div>
          </div>
          
          <div v-else-if="!isAuthenticated" class="mb-6">
            <router-link to="/login" class="w-full btn-primary py-3 text-sm sm:text-lg text-center block">
              Login to Purchase
            </router-link>
          </div>
        </div>
      </div>
      
      <!-- Product Details Section - Full width on mobile -->
      <div class="mt-6 lg:mt-8 space-y-6">
        <div v-if="product.product.description" class="bg-white p-4 rounded-lg">
          <h3 class="text-lg font-medium text-gray-900 mb-3">Description</h3>
          <p class="text-gray-700 text-sm sm:text-base leading-relaxed">{{ product.product.description }}</p>
        </div>
        
        <div class="bg-white p-4 rounded-lg">
          <h3 class="text-lg font-medium text-gray-900 mb-3">Product Details</h3>
          <dl class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <div class="border-b border-gray-100 pb-2 sm:border-b-0 sm:pb-0">
              <dt class="text-xs sm:text-sm font-medium text-gray-500 mb-1">Unit of Measure</dt>
              <dd class="text-sm sm:text-base text-gray-900">{{ product.product_unit }}</dd>
            </div>
            <div class="border-b border-gray-100 pb-2 sm:border-b-0 sm:pb-0">
              <dt class="text-xs sm:text-sm font-medium text-gray-500 mb-1">Minimum Order</dt>
              <dd class="text-sm sm:text-base text-gray-900">
                {{ product.min_order_quantity }} {{ product.product_unit }}
              </dd>
            </div>
            <div class="border-b border-gray-100 pb-2 sm:border-b-0 sm:pb-0">
              <dt class="text-xs sm:text-sm font-medium text-gray-500 mb-1">Quality Grade</dt>
              <dd class="text-sm sm:text-base text-gray-900 capitalize">{{ product.quality_grade }}</dd>
            </div>
            <div v-if="product.harvest_date" class="border-b border-gray-100 pb-2 sm:border-b-0 sm:pb-0">
              <dt class="text-xs sm:text-sm font-medium text-gray-500 mb-1">Harvest Date</dt>
              <dd class="text-sm sm:text-base text-gray-900">{{ formatDate(product.harvest_date) }}</dd>
            </div>
            <div v-if="product.product.is_perishable" class="border-b border-gray-100 pb-2 sm:border-b-0 sm:pb-0">
              <dt class="text-xs sm:text-sm font-medium text-gray-500 mb-1">Shelf Life</dt>
              <dd class="text-sm sm:text-base text-gray-900">{{ product.product.shelf_life_days }} days</dd>
            </div>
          </dl>
        </div>
        
        <div v-if="product.notes" class="bg-white p-4 rounded-lg">
          <h3 class="text-lg font-medium text-gray-900 mb-3">Notes</h3>
          <p class="text-gray-700 text-sm sm:text-base leading-relaxed">{{ product.notes }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { isAuthenticated, isCustomer } from '@/stores/auth'
import { productsAPI, cartAPI } from '@/services/api'

export default {
  name: 'ProductDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const loading = ref(true)
    const product = ref(null)
    const quantity = ref(1)
    const addingToCart = ref(false)
    
    const loadProduct = async () => {
      try {
        const response = await productsAPI.getListingById(route.params.id)
        product.value = response
        quantity.value = response.min_order_quantity || 1
      } catch (error) {
        console.error('Failed to load product:', error)
      } finally {
        loading.value = false
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
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }
    
    const addToCart = async () => {
      addingToCart.value = true
      
      try {
        await cartAPI.addToCart(product.value.listing_id, quantity.value)
        
        // Dispatch cart updated event
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        
        // Show success message
        alert(`${product.value.product_name} added to cart!`)
        
        // Redirect to cart or stay on page
        // router.push('/cart')
        
      } catch (error) {
        console.error('Failed to add to cart:', error)
        alert('Failed to add item to cart. Please try again.')
      } finally {
        addingToCart.value = false
      }
    }
    
    onMounted(() => {
      loadProduct()
    })
    
    return {
      loading,
      product,
      quantity,
      addingToCart,
      isAuthenticated,
      isCustomer,
      getStatusDisplay,
      formatDate,
      addToCart
    }
  }
}
</script>