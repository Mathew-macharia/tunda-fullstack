<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 lg:py-6">
        <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Shopping Cart</h1>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 lg:py-8">
      <div v-if="loading" class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
      
      <div v-else-if="!cart || !cart.items || cart.items.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">Your cart is empty</h3>
        <p class="mt-1 text-sm text-gray-500">Start shopping to add items to your cart.</p>
        <div class="mt-6">
          <router-link to="/products" class="btn-primary">
            Browse Products
          </router-link>
        </div>
      </div>
      
      <div v-else class="space-y-6 lg:grid lg:grid-cols-12 lg:gap-x-12 lg:space-y-0">
        <!-- Cart Items -->
        <div class="space-y-4 lg:col-span-8">
          <div
            v-for="item in cart.items"
            :key="item.cart_item_id"
            class="bg-white rounded-lg shadow p-4 sm:p-6"
          >
            <!-- Mobile Layout -->
            <div class="sm:hidden">
              <!-- Product Image and Basic Info -->
              <div class="flex space-x-3 mb-3">
                <div class="flex-shrink-0">
                  <img
                    v-if="item.photos && item.photos.length"
                    :src="item.photos[0]"
                    :alt="item.product_name"
                    class="h-16 w-16 object-cover rounded-lg"
                  />
                  <div v-else class="h-16 w-16 bg-gray-200 rounded-lg flex items-center justify-center">
                    <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                  </div>
                </div>
                
                <div class="flex-1 min-w-0">
                  <h3 class="font-medium text-gray-900 text-sm leading-tight">
                    {{ item.product_name }}
                  </h3>
                  <p class="text-xs text-gray-500 mt-1">
                    From {{ item.farm_name }}
                  </p>
                  <p class="text-xs text-gray-500">
                    KSh {{ item.current_price }} per {{ item.product_unit }}
                  </p>
                </div>
                
                <!-- Remove Button (Top Right) -->
                <button
                  @click="removeItem(item)"
                  :disabled="removingItem === (isAuthenticated ? item.cart_item_id : item.listing_id)"
                  class="text-red-500 text-xs px-2 py-1"
                >
                  Remove
                </button>
              </div>
              
              <!-- Warnings (simplified for guest cart, as full details like price_changed/availability_status are from backend) -->
              <div v-if="!isAuthenticated && item.quantity > item.quantity_available" class="mb-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                ⚠️ Quantity exceeds available stock ({{ item.quantity_available }} {{ item.product_unit }} available)
              </div>
              
              <!-- Quantity and Total Row -->
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <span class="text-sm text-gray-600">Qty:</span>
                                  <button
                  @click="updateQuantity(item, parseFloat(item.quantity) - 1)"
                  :disabled="parseFloat(item.quantity) <= (parseFloat(item.min_order_quantity) || 1) || updatingItem === (isAuthenticated ? item.cart_item_id : item.listing_id)"
                  class="p-1 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
                  </svg>
                </button>
                
                <span class="px-2 py-1 border border-gray-300 rounded text-sm min-w-8 text-center">
                  {{ item.quantity }}
                </span>
                
                <button
                  @click="updateQuantity(item, parseFloat(item.quantity) + 1)"
                  :disabled="parseFloat(item.quantity) >= parseFloat(item.quantity_available) || updatingItem === (isAuthenticated ? item.cart_item_id : item.listing_id)"
                  class="p-1 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                    </svg>
                  </button>
                </div>
                
                <div class="text-right">
                  <div class="font-medium text-gray-900">
                    KSh {{ (item.current_price * item.quantity).toFixed(2) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Desktop Layout -->
            <div class="hidden sm:flex sm:items-center sm:space-x-4">
              <!-- Product Image -->
              <div class="flex-shrink-0">
                <img
                  v-if="item.photos && item.photos.length"
                  :src="item.photos[0]"
                  :alt="item.product_name"
                  class="h-20 w-20 object-cover rounded-lg"
                />
                <div v-else class="h-20 w-20 bg-gray-200 rounded-lg flex items-center justify-center">
                  <svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                </div>
              </div>
              
              <!-- Product Info -->
              <div class="flex-1 min-w-0">
                <h3 class="text-lg font-medium text-gray-900">
                  {{ item.product_name }}
                </h3>
                <p class="text-sm text-gray-500">
                  From {{ item.farm_name }}
                </p>
                <p class="text-sm text-gray-500">
                  KSh {{ item.current_price }} per {{ item.product_unit }}
                </p>
                
                <!-- Price Change Warning -->
                <div v-if="isAuthenticated && item.price_changed" class="mt-2 text-sm text-yellow-600">
                  ⚠️ Price has changed to KSh {{ item.current_price }}
                </div>
                
                <!-- Availability Warning -->
                <div v-if="isAuthenticated && item.availability_status !== 'Available'" class="mt-2 text-sm text-red-600">
                  ⚠️ {{ item.availability_status }}
                </div>
                <div v-else-if="!isAuthenticated && item.quantity > item.quantity_available" class="mt-2 text-sm text-red-600">
                  ⚠️ Quantity exceeds available stock ({{ item.quantity_available }} {{ item.product_unit }} available)
                </div>
              </div>
              
              <!-- Quantity Controls -->
              <div class="flex items-center space-x-2">
                <button
                  @click="updateQuantity(item, parseFloat(item.quantity) - 1)"
                  :disabled="parseFloat(item.quantity) <= (parseFloat(item.min_order_quantity) || 1) || updatingItem === (isAuthenticated ? item.cart_item_id : item.listing_id)"
                  class="p-1 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
                  </svg>
                </button>
                
                <span class="px-3 py-1 border border-gray-300 rounded-md text-center min-w-12">
                  {{ item.quantity }}
                </span>
                
                <button
                  @click="updateQuantity(item, parseFloat(item.quantity) + 1)"
                  :disabled="parseFloat(item.quantity) >= parseFloat(item.quantity_available) || updatingItem === (isAuthenticated ? item.cart_item_id : item.listing_id)"
                  class="p-1 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                  </svg>
                </button>
              </div>
              
              <!-- Subtotal -->
              <div class="text-right">
                <div class="text-lg font-medium text-gray-900">
                  KSh {{ (item.current_price * item.quantity).toFixed(2) }}
                </div>
                <button
                  @click="removeItem(item)"
                  :disabled="removingItem === (isAuthenticated ? item.cart_item_id : item.listing_id)"
                  class="mt-1 text-sm text-red-600 hover:text-red-500"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Order Summary -->
        <div class="lg:col-span-4">
          <div class="bg-white rounded-lg shadow p-4 sm:p-6 lg:sticky lg:top-24">
            <h2 class="text-lg font-medium text-gray-900 mb-4">Order Summary</h2>
            
            <div class="space-y-2 mb-4">
              <div class="flex justify-between text-sm sm:text-base">
                <span class="text-gray-600">Items ({{ cart.total_items }})</span>
                <span class="font-medium">KSh {{ cart.total_cost }}</span>
              </div>
              <div class="flex justify-between text-sm sm:text-base">
                <span class="text-gray-600">Estimated Delivery</span>
                <span class="font-medium">KSh {{ isAuthenticated ? (cart.estimated_delivery_fee || '50.00') : '50.00' }}</span>
              </div>
              <div class="text-xs text-blue-600 mt-1">
                💡 Final delivery fee will be calculated based on your address during checkout
              </div>
              <hr class="my-2">
              <div class="flex justify-between text-lg font-bold">
                <span>Total</span>
                <span>KSh {{ isAuthenticated ? (cart.total_with_delivery || (parseFloat(cart.total_cost || 0) + 50).toFixed(2)) : (parseFloat(cart.total_cost || 0) + 50).toFixed(2) }}</span>
              </div>
            </div>
            
            <router-link
              to="/checkout"
              class="w-full btn-primary py-3 text-center block text-sm sm:text-base"
            >
              Proceed to Checkout
            </router-link>
            
            <router-link
              to="/products"
              class="w-full btn-secondary py-2 text-center block mt-3 text-sm sm:text-base"
            >
              Continue Shopping
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { cartAPI } from '@/services/api'
import { isAuthenticated, guestCartItems, updateGuestCartItem, removeGuestCartItem } from '@/stores/auth'

export default {
  name: 'CartPage',
  setup() {
    const loading = ref(true)
    const authenticatedCart = ref(null) // For authenticated user's cart
    const updatingItem = ref(null)
    const removingItem = ref(null)
    
    // Computed property to determine which cart to display
    const cart = computed(() => {
      return isAuthenticated.value ? authenticatedCart.value : { items: guestCartItems.value, total_items: guestCartItems.value.length, total_cost: calculateGuestCartTotal() }
    })

    const calculateGuestCartTotal = () => {
      return guestCartItems.value.reduce((total, item) => total + (parseFloat(item.quantity) * parseFloat(item.current_price)), 0).toFixed(2);
    }
    
    const loadCart = async () => {
      loading.value = true
      try {
        if (isAuthenticated.value) {
          const response = await cartAPI.getCart()
          authenticatedCart.value = response
        } else {
          // Guest cart is already reactive via guestCartItems from auth store
          // No API call needed, just ensure guestCartItems is loaded (handled by auth store init)
        }
      } catch (error) {
        console.error('Failed to load cart:', error)
        authenticatedCart.value = null // Clear authenticated cart on error
      } finally {
        loading.value = false
      }
    }
    
    const updateQuantity = async (item, newQuantity) => {
      // Note: min_order_quantity and quantity_available are not available in guestCartItems directly.
      // This might lead to issues for guest users if not handled.
      // For now, we'll assume basic quantity updates.
      
      updatingItem.value = item.listing_id || item.cart_item_id // Use listing_id for guest, cart_item_id for auth
      
      try {
        if (isAuthenticated.value) {
          await cartAPI.updateCartItem(item.cart_item_id, newQuantity)
          await loadCart() // Reload authenticated cart
        } else {
          updateGuestCartItem(item.listing_id, newQuantity)
          // No need to reload, guestCartItems is reactive
        }
        
        window.dispatchEvent(new CustomEvent('cartUpdated'))
      } catch (error) {
        console.error('Failed to update quantity:', error)
        if (error.response?.data) {
          console.error('Error details:', error.response.data)
        }
        alert('Failed to update quantity. Please try again.')
      } finally {
        updatingItem.value = null
      }
    }
    
    const removeItem = async (item) => {
      removingItem.value = item.listing_id || item.cart_item_id // Use listing_id for guest, cart_item_id for auth
      
      try {
        if (isAuthenticated.value) {
          await cartAPI.removeFromCart(item.cart_item_id)
          await loadCart() // Reload authenticated cart
        } else {
          removeGuestCartItem(item.listing_id)
          // No need to reload, guestCartItems is reactive
        }
        
        window.dispatchEvent(new CustomEvent('cartUpdated'))
      } catch (error) {
        console.error('Failed to remove item:', error)
        alert('Failed to remove item. Please try again.')
      } finally {
        removingItem.value = null
      }
    }
    
    onMounted(() => {
      loadCart()
    })
    
    return {
      loading,
      cart,
      updatingItem,
      removingItem,
      isAuthenticated, // Export for template conditionals
      updateQuantity,
      removeItem
    }
  }
}
</script>