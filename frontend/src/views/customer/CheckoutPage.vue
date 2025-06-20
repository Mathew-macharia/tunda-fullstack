<template>
  <div class="min-h-screen bg-gray-50 py-4 sm:py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-6 sm:mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Checkout</h1>
        <p class="mt-1 sm:mt-2 text-sm sm:text-base text-gray-600">Complete your order to fresh farm produce</p>
      </div>

      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>

      <div v-else-if="!cart || cart.total_items === 0" class="text-center py-12">
        <svg class="mx-auto h-16 sm:h-24 w-16 sm:w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
        </svg>
        <h2 class="mt-4 text-xl sm:text-2xl font-semibold text-gray-900">Your cart is empty</h2>
        <p class="mt-2 text-sm sm:text-base text-gray-600">Add some items to your cart before checking out.</p>
        <router-link to="/products" class="mt-6 btn-primary inline-block">
          Browse Products
        </router-link>
      </div>

      <div v-else class="space-y-6 lg:grid lg:grid-cols-3 lg:gap-8 lg:space-y-0">
        <!-- Order Summary - Mobile First -->
        <div class="lg:hidden">
          <div class="bg-white rounded-lg shadow p-4">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Order Summary</h2>
            
            <!-- Collapsed Items View for Mobile -->
            <div class="mb-4">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">{{ cart.total_items }} item{{ cart.total_items > 1 ? 's' : '' }}</span>
                <button @click="showItems = !showItems" class="text-sm text-green-600 font-medium">
                  {{ showItems ? 'Hide' : 'Show' }} details
                </button>
              </div>
              
              <!-- Expandable Items List -->
              <div v-show="showItems" class="mt-3 space-y-2">
                <div v-for="item in cart.items" :key="item.cart_item_id" class="flex items-center space-x-2 text-sm">
                  <img
                    v-if="item.photos && item.photos.length"
                    :src="item.photos[0]"
                    :alt="item.product_name"
                    class="h-8 w-8 object-cover rounded"
                  />
                  <div v-else class="h-8 w-8 bg-gray-200 rounded"></div>
                  
                  <div class="flex-1">
                    <p class="font-medium text-gray-900 text-xs leading-tight">{{ item.product_name }}</p>
                    <p class="text-xs text-gray-500">{{ item.quantity }} × KSh {{ item.price_at_addition }}</p>
                  </div>
                  
                  <div class="text-xs font-medium">KSh {{ item.subtotal }}</div>
                </div>
              </div>
            </div>

            <!-- Totals -->
            <div class="border-t pt-3 space-y-1">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Subtotal</span>
                <span class="font-medium">KSh {{ cart.total_cost }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Delivery Fee</span>
                <span class="font-medium">KSh {{ deliveryFee }}</span>
              </div>
              <div class="flex justify-between font-bold border-t pt-2">
                <span>Total</span>
                <span>KSh {{ (parseFloat(cart.total_cost || 0) + deliveryFee).toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Checkout Form -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Delivery Information -->
          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <h2 class="text-lg sm:text-xl font-semibold text-gray-900 mb-4 sm:mb-6">Delivery Information</h2>
            
            <form @submit.prevent="submitOrder" class="space-y-4 sm:space-y-6">
              <!-- Contact Information -->
              <div class="space-y-4 sm:grid sm:grid-cols-2 sm:gap-4 sm:space-y-0">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                    Full Name *
                  </label>
                  <input
                    v-model="orderForm.delivery_address.full_name"
                    type="text"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm sm:text-base"
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                    Phone Number *
                  </label>
                  <input
                    v-model="orderForm.delivery_address.phone_number"
                    type="tel"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm sm:text-base"
                    placeholder="+254712345678"
                  />
                </div>
              </div>

              <!-- Location Selection -->
              <div class="space-y-4 sm:grid sm:grid-cols-2 sm:gap-4 sm:space-y-0">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                    County *
                  </label>
                  <select
                    v-model="selectedCounty"
                    @change="loadSubCounties"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm sm:text-base"
                  >
                    <option value="">Select County</option>
                    <option v-for="county in counties" :key="county.county_id" :value="county.county_id">
                      {{ county.county_name }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                    Sub-County *
                  </label>
                  <select
                    v-model="orderForm.delivery_address.location"
                    required
                    :disabled="!selectedCounty || loadingSubCounties"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 text-sm sm:text-base"
                  >
                    <option value="">
                      {{ loadingSubCounties ? 'Loading sub-counties...' : 'Select Sub-County' }}
                    </option>
                    <option v-for="subCounty in subCounties" :key="subCounty.sub_county_id" :value="subCounty.sub_county_id">
                      {{ subCounty.sub_county_name }}
                    </option>
                  </select>
                </div>
              </div>

              <!-- Detailed Address -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                  Detailed Address *
                </label>
                <textarea
                  v-model="orderForm.delivery_address.detailed_address"
                  required
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm sm:text-base"
                  placeholder="House number, street name, landmark, etc."
                ></textarea>
              </div>

              <!-- Special Instructions -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                  Special Delivery Instructions (Optional)
                </label>
                <textarea
                  v-model="orderForm.special_instructions"
                  rows="2"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm sm:text-base"
                  placeholder="Any special instructions for delivery..."
                ></textarea>
              </div>
            </form>
          </div>

          <!-- Payment Method -->
          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <h2 class="text-lg sm:text-xl font-semibold text-gray-900 mb-4 sm:mb-6">Payment Method</h2>
            
            <div class="space-y-3 sm:space-y-4">
              <!-- M-Pesa Option -->
              <div class="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50" 
                   @click="orderForm.payment_method = 'mpesa'">
                <input
                  id="mpesa"
                  v-model="orderForm.payment_method"
                  type="radio"
                  value="mpesa"
                  class="mt-1 h-4 w-4 text-green-600 focus:ring-green-500"
                />
                <div class="flex-1">
                  <label for="mpesa" class="block text-sm font-medium text-gray-900 cursor-pointer">
                    M-Pesa
                  </label>
                  <p class="text-xs text-gray-500 mt-1">Secure mobile money payment</p>
                </div>
                <div class="flex items-center">
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Recommended
                  </span>
                </div>
              </div>
              
              <!-- Cash on Delivery Option - Disabled with explanation -->
              <div class="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg bg-gray-50 opacity-75">
                <input
                  id="cash"
                  type="radio"
                  value="cash_on_delivery"
                  disabled
                  class="mt-1 h-4 w-4 text-gray-400 cursor-not-allowed"
                />
                <div class="flex-1">
                  <label for="cash" class="block text-sm font-medium text-gray-500 cursor-not-allowed">
                    Cash on Delivery
                  </label>
                  <p class="text-xs text-gray-400 mt-1">Currently unavailable - Coming soon!</p>
                </div>
                <div class="flex items-center">
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                    Coming Soon
                  </span>
                </div>
              </div>
            </div>

            <!-- Payment Instructions -->
            <div class="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
              <div class="flex items-start space-x-3">
                <svg class="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div class="flex-1">
                  <p class="text-sm text-green-800 font-semibold mb-2">How M-Pesa Payment Works:</p>
                  <div class="space-y-2 text-xs text-green-700">
                    <div class="flex items-start space-x-2">
                      <span class="inline-flex items-center justify-center w-4 h-4 bg-green-600 text-white rounded-full text-xs font-bold mt-0.5">1</span>
                      <p>Click "Place Order" to confirm your order details</p>
                    </div>
                    <div class="flex items-start space-x-2">
                      <span class="inline-flex items-center justify-center w-4 h-4 bg-green-600 text-white rounded-full text-xs font-bold mt-0.5">2</span>
                      <p>Send <span class="font-semibold">KSh {{ (parseFloat(cart?.total_cost || 0) + deliveryFee).toFixed(2) }}</span> to M-Pesa number: <span class="font-bold text-green-900">0745 758 422</span></p>
                    </div>
                    <div class="flex items-start space-x-2">
                      <span class="inline-flex items-center justify-center w-4 h-4 bg-green-600 text-white rounded-full text-xs font-bold mt-0.5">3</span>
                      <p>We'll call you within <span class="font-semibold">30 minutes</span> to confirm payment and delivery</p>
                    </div>
                    <div class="flex items-start space-x-2">
                      <span class="inline-flex items-center justify-center w-4 h-4 bg-green-600 text-white rounded-full text-xs font-bold mt-0.5">4</span>
                      <p>Your fresh produce will be prepared and delivered</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Trust Building Message -->
            <div class="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div class="flex items-start space-x-2">
                <svg class="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div>
                  <p class="text-xs text-blue-800 font-medium">Why M-Pesa only?</p>
                  <p class="text-xs text-blue-700 mt-1">
                    We're starting with M-Pesa to ensure fast, secure transactions. Cash on delivery will be available as we expand our delivery network.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Mobile Place Order Button -->
          <div class="lg:hidden">
            <button
              @click="submitOrder"
              :disabled="submittingOrder || !isFormValid"
              class="w-full btn-primary py-3 text-sm sm:text-base disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="submittingOrder">Confirming Order...</span>
              <span v-else>Confirm Order - KSh {{ (parseFloat(cart.total_cost || 0) + deliveryFee).toFixed(2) }}</span>
            </button>
            <div class="mt-3 text-xs text-gray-500 text-center space-y-1">
              <p>After confirming, send payment to <span class="font-semibold text-gray-700">0745 758 422</span></p>
              <p>By placing this order, you agree to our Terms of Service and Privacy Policy.</p>
            </div>
          </div>
        </div>

        <!-- Desktop Order Summary -->
        <div class="hidden lg:block">
          <div class="bg-white rounded-lg shadow p-6 sticky top-8">
            <h2 class="text-xl font-semibold text-gray-900 mb-6">Order Summary</h2>
            
            <!-- Items -->
            <div class="space-y-4 mb-6">
              <div v-for="item in cart.items" :key="item.cart_item_id" class="flex items-center space-x-3">
                <img
                  v-if="item.photos && item.photos.length"
                  :src="item.photos[0]"
                  :alt="item.product_name"
                  class="h-12 w-12 object-cover rounded-lg"
                />
                <div v-else class="h-12 w-12 bg-gray-200 rounded-lg"></div>
                
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ item.product_name }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ item.quantity }} {{ item.product_unit }} × KSh {{ item.price_at_addition }}
                  </p>
                </div>
                
                <div class="text-sm font-medium text-gray-900">
                  KSh {{ item.subtotal }}
                </div>
              </div>
            </div>

            <!-- Totals -->
            <div class="border-t pt-4 space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Subtotal</span>
                <span class="font-medium">KSh {{ cart.total_cost }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Delivery Fee</span>
                <span class="font-medium">KSh {{ deliveryFee }}</span>
              </div>
              <div class="flex justify-between text-lg font-bold border-t pt-2">
                <span>Total</span>
                <span>KSh {{ (parseFloat(cart.total_cost || 0) + deliveryFee).toFixed(2) }}</span>
              </div>
            </div>

            <!-- Place Order Button -->
            <button
              @click="submitOrder"
              :disabled="submittingOrder || !isFormValid"
              class="w-full mt-6 btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="submittingOrder">Confirming Order...</span>
              <span v-else>Confirm Order</span>
            </button>

            <div class="mt-4 text-xs text-gray-500 text-center space-y-1">
              <p>After confirming, send payment to <span class="font-semibold text-gray-700">0745 758 422</span></p>
              <p>By placing this order, you agree to our Terms of Service and Privacy Policy.</p>
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
import { cartAPI, ordersAPI, locationsAPI } from '@/services/api'
import { user, isAuthenticated, mergeGuestCartToUserCart, guestCartItems } from '@/stores/auth' // Import isAuthenticated, mergeGuestCartToUserCart, guestCartItems

export default {
  name: 'CheckoutPage',
  setup() {
    const router = useRouter()
    
    const loading = ref(true)
    const authenticatedCart = ref(null) // For authenticated user's cart
    const counties = ref([])
    const subCounties = ref([])
    const selectedCounty = ref('')
    const submittingOrder = ref(false)
    const loadingSubCounties = ref(false)
    const deliveryFee = ref(50)
    const showItems = ref(false)
    
    const orderForm = ref({
      delivery_address: {
        full_name: '',
        phone_number: '',
        location: '',
        detailed_address: ''
      },
      payment_method: 'mpesa', // Default to mpesa since it's the primary option
      special_instructions: ''
    })

    // Computed property to determine which cart to display
    const cart = computed(() => {
      if (isAuthenticated.value) {
        return authenticatedCart.value
      } else {
        // For guest users, we need to calculate total_cost and total_items from guestCartItems
        const total_items = guestCartItems.value.reduce((sum, item) => sum + item.quantity, 0);
        // Note: We cannot accurately calculate total_cost for guest cart here as we don't have product prices.
        // This will be handled on the backend when the cart is merged.
        // For display, we'll show 0 or a placeholder.
        const total_cost = '0.00'; 
        return { items: guestCartItems.value, total_items, total_cost };
      }
    })

    // Computed
    const isFormValid = computed(() => {
      const addr = orderForm.value.delivery_address
      return addr.full_name && 
             addr.phone_number && 
             addr.location && 
             addr.detailed_address &&
             orderForm.value.payment_method === 'mpesa' // Only allow mpesa for now
    })

    // Methods
    const loadCart = async () => {
      try {
        if (isAuthenticated.value) {
          const response = await cartAPI.getCart()
          authenticatedCart.value = response
        } else {
          // If not authenticated, cart data comes from guestCartItems (reactive)
          // We might need to fetch product details for display if guestCartItems only has IDs
          // For now, we assume guestCartItems has enough info for basic display (listing_id, quantity)
          // The full details will be available after merge on backend.
        }
      } catch (error) {
        console.error('Failed to load cart:', error)
        authenticatedCart.value = null // Clear authenticated cart on error
      }
    }

    const loadCounties = async () => {
      try {
        console.log('Loading counties...')
        const response = await locationsAPI.getCounties()
        console.log('Counties response:', response)
        counties.value = response.results || response
        console.log('Counties set to:', counties.value)
      } catch (error) {
        console.error('Failed to load counties:', error)
      }
    }

    const loadSubCounties = async () => {
      // Clear the current subcounty selection when county changes
      orderForm.value.delivery_address.location = ''
      
      if (!selectedCounty.value) {
        subCounties.value = []
        loadingSubCounties.value = false
        return
      }
      
      loadingSubCounties.value = true
      
      try {
        console.log('Loading sub-counties for county:', selectedCounty.value)
        const response = await locationsAPI.getSubCounties(selectedCounty.value)
        console.log('Sub-counties response:', response)
        subCounties.value = response.results || response
        console.log('Sub-counties set to:', subCounties.value)
      } catch (error) {
        console.error('Failed to load sub-counties:', error)
        subCounties.value = []
      } finally {
        loadingSubCounties.value = false
      }
    }

    const submitOrder = async () => {
      if (!isFormValid.value) {
        alert('Please fill in all required fields')
        return
      }

      // Ensure only M-Pesa is allowed for now
      if (orderForm.value.payment_method !== 'mpesa') {
        alert('Only M-Pesa payment is currently available')
        return
      }

      submittingOrder.value = true

      try {
        const orderData = {
          ...orderForm.value,
          expected_total: parseFloat(cart.value.total_cost) + deliveryFee.value
        }

        const order = await ordersAPI.createOrder(orderData)
        
        // Clear cart after successful order
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        
        // Redirect to order confirmation
        router.push(`/orders/${order.order_id}`)
        
      } catch (error) {
        console.error('Failed to create order:', error)
        alert('Failed to place order. Please try again.')
      } finally {
        submittingOrder.value = false
      }
    }

    // Initialize form with user data
    const initializeForm = () => {
      if (user.value) {
        orderForm.value.delivery_address.full_name = `${user.value.first_name || ''} ${user.value.last_name || ''}`.trim()
        orderForm.value.delivery_address.phone_number = user.value.phone_number || ''
      }
    }

    // Lifecycle
    onMounted(async () => {
      // Authentication gate: If not authenticated and guest cart is not empty, redirect to login
      if (!isAuthenticated.value && guestCartItems.value.length > 0) {
        router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } });
        return; // Stop further execution
      } else if (!isAuthenticated.value && guestCartItems.value.length === 0) {
        // If not authenticated and cart is empty, redirect to products page
        router.push({ name: 'products' });
        return; // Stop further execution
      }

      await Promise.all([
        loadCart(),
        loadCounties()
      ])
      initializeForm()
      loading.value = false
    })

    return {
      loading,
      cart,
      counties,
      subCounties,
      selectedCounty,
      submittingOrder,
      loadingSubCounties,
      deliveryFee,
      orderForm,
      isFormValid,
      showItems,
      loadSubCounties,
      submitOrder,
      isAuthenticated // Export isAuthenticated for template
    }
  }
}
</script>
