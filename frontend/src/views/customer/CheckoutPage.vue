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
        <!-- Checkout Form (Delivery Information and Payment Method) -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Delivery Information -->
          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <h2 class="text-lg sm:text-xl font-semibold text-gray-900 mb-4 sm:mb-6">Delivery Information</h2>
            
            <form @submit.prevent="createOrderManually" class="space-y-4 sm:space-y-6">
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
                    :class="['w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm sm:text-base', {'border-red-500': formSubmitted && !orderForm.delivery_address.full_name}]"
                    placeholder="John Doe"
                  />
                  <p v-if="formSubmitted && !orderForm.delivery_address.full_name" class="mt-1 text-xs text-red-500">Full Name is required.</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                    Phone Number *
                  </label>
                  <input
                    v-model="orderForm.delivery_address.phone_number"
                    type="tel"
                    required
                    :class="['w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm sm:text-base', {'border-red-500': formSubmitted && !orderForm.delivery_address.phone_number}]"
                    placeholder="+254712345678"
                  />
                  <p v-if="formSubmitted && !orderForm.delivery_address.phone_number" class="mt-1 text-xs text-red-500">Phone Number is required.</p>
                </div>
              </div>

              <!-- Location Selection -->
              <div class="space-y-4 sm:grid sm:grid-cols-2 sm:gap-4 sm:space-y-0">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                    County *
                  </label>
                  <select
                    v-model="orderForm.delivery_address.county_id"
                    @change="loadSubCounties"
                    required
                    :class="['w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm sm:text-base', {'border-red-500': formSubmitted && !orderForm.delivery_address.county_id}]"
                  >
                    <option value="">Select County</option>
                    <option v-for="county in counties" :key="county.county_id" :value="county.county_id">
                      {{ county.county_name }}
                    </option>
                  </select>
                  <p v-if="formSubmitted && !orderForm.delivery_address.county_id" class="mt-1 text-xs text-red-500">County is required.</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                    Sub-County *
                  </label>
                  <select
                    v-model="orderForm.delivery_address.subcounty_id"
                    required
                    :disabled="!orderForm.delivery_address.county_id || loadingSubCounties"
                    :class="['w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 text-sm sm:text-base', {'border-red-500': formSubmitted && !orderForm.delivery_address.subcounty_id}]"
                  >
                    <option value="">
                      {{ loadingSubCounties ? 'Loading sub-counties...' : 'Select Sub-County' }}
                    </option>
                    <option v-for="subCounty in subCounties" :key="subCounty.sub_county_id" :value="subCounty.sub_county_id">
                      {{ subCounty.sub_county_name }}
                    </option>
                  </select>
                  <p v-if="formSubmitted && !orderForm.delivery_address.subcounty_id" class="mt-1 text-xs text-red-500">Sub-County is required.</p>
                </div>
              </div>

              <!-- Detailed Address with Validation -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                  Detailed Address *
                </label>
                <div class="relative">
                  <textarea
                    v-model="orderForm.delivery_address.detailed_address"
                    @input="onAddressInput"
                    required
                    rows="3"
                    :class="['w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm sm:text-base', {'border-red-500': formSubmitted && !orderForm.delivery_address.detailed_address}]"
                    placeholder="House number, street name, landmark, etc."
                  ></textarea>
                  
                  <!-- Address Autocomplete Dropdown -->
                  <div v-if="addressSuggestions.length > 0" class="absolute z-10 w-full bg-white border border-gray-300 rounded-md shadow-lg mt-1 max-h-48 overflow-y-auto">
                    <div
                      v-for="suggestion in addressSuggestions"
                      :key="suggestion.text"
                      @click="selectAddressSuggestion(suggestion)"
                      :class="[
                        'px-3 py-2 text-sm',
                        suggestion.loading ? 'text-gray-500 cursor-default' : 'hover:bg-gray-100 cursor-pointer'
                      ]"
                    >
                      <div v-if="suggestion.loading" class="flex items-center space-x-2">
                        <div class="animate-spin rounded-full h-3 w-3 border-b border-blue-600"></div>
                        <span class="text-blue-600">{{ suggestion.text }}</span>
                      </div>
                      <div v-else>
                        <div class="font-medium">{{ suggestion.text }}</div>
                        <div v-if="suggestion.description" class="text-xs text-gray-500">{{ suggestion.description }}</div>
                      </div>
                    </div>
                  </div>
                </div>
                <p v-if="formSubmitted && !orderForm.delivery_address.detailed_address" class="mt-1 text-xs text-red-500">Detailed Address is required.</p>
                
                <!-- Address Validation Status -->
                <div v-if="addressValidation" class="mt-2 space-y-1">
                  <!-- Loading State -->
                  <div v-if="addressValidation.loading" class="flex items-center space-x-2 text-sm text-blue-600">
                    <div class="animate-spin rounded-full h-3 w-3 border-b border-blue-600"></div>
                    <span>Validating address...</span>
                  </div>
                  
                  <!-- Validation Warnings -->
                  <div v-else-if="addressValidation.warnings.length > 0" class="space-y-1">
                    <div v-for="warning in addressValidation.warnings" :key="warning" class="flex items-start space-x-2 text-sm text-orange-600">
                      <svg class="h-4 w-4 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                      </svg>
                      <span>{{ warning }}</span>
                    </div>
                  </div>
                  
                  <!-- Success State -->
                  <div v-else-if="!addressValidation.loading && addressValidation.is_valid" class="flex items-center space-x-2 text-sm text-green-600">
                    <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                    </svg>
                    <span>Address validated successfully</span>
                  </div>
                </div>
                

                
                <!-- Address Validation Suggestions -->
                <div v-if="addressValidation && addressValidation.suggestions.length > 0" class="mt-2 space-y-1">
                  <div v-for="suggestion in addressValidation.suggestions" :key="suggestion" class="flex items-start space-x-2 text-sm text-blue-600">
                    <svg class="h-4 w-4 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                    </svg>
                    <span>{{ suggestion }}</span>
                  </div>
                </div>
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
            <div class="mt-4">
              <MpesaPaymentCard :totalAmount="totalAmount" />
            </div>

            <!-- Trust Building Message -->
            <div class="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div class="flex items-start space-x-2">
                <svg class="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                  <path fill-rule="evenodd" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" clip-rule="evenodd"></path>
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

          <!-- Mobile Pay with M-Pesa Button -->
          <div class="lg:hidden">
            <button
              @click="createOrderManually"
              :disabled="processingPayment || !isFormValid"
              class="w-full btn-primary py-3 text-sm sm:text-base disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <svg v-if="processingPayment" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-if="processingPayment">Processing Order...</span>
              <span v-else>Create Order - KSh {{ totalAmount }}</span>
            </button>
            <div class="mt-3 text-xs text-gray-500 text-center space-y-1">
              <p>Your order will be confirmed by an admin once payment is received.</p>
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
                <span class="text-gray-600">
                  Delivery Fee
                  <span v-if="deliveryDistance" class="text-xs text-gray-500">({{ deliveryDistance }} km)</span>
                </span>
                <div class="flex items-center space-x-2">
                  <span v-if="estimatingDeliveryFee" class="text-xs text-blue-600">Calculating...</span>
                  <span class="font-medium">KSh {{ actualDeliveryFee.toFixed(2) }}</span>
                </div>
              </div>
              <div v-if="deliveryFeeError" class="text-xs text-orange-600 mt-1">
                {{ deliveryFeeError }}
              </div>
              <div class="flex justify-between text-lg font-bold border-t pt-2">
                <span>Total</span>
                <span>KSh {{ totalAmount }}</span>
              </div>
            </div>

            <!-- Pay with M-Pesa Button -->
            <button
              @click="createOrderManually"
              :disabled="processingPayment || !isFormValid"
              class="w-full mt-6 btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <svg v-if="processingPayment" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-if="processingPayment">Processing Order...</span>
              <span v-else>Create Order</span>
            </button>

            <div class="mt-4 text-xs text-gray-500 text-center space-y-1">
              <p>Your order will be confirmed by an admin once payment is received.</p>
              <p>By placing this order, you agree to our Terms of Service and Privacy Policy.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { cartAPI, ordersAPI, locationsAPI, paymentsAPI } from '@/services/api'
import { user, isAuthenticated, mergeGuestCartToUserCart, guestCartItems } from '@/stores/auth' // Import isAuthenticated, mergeGuestCartToUserCart, guestCartItems
import MpesaPaymentCard from '@/components/customer/MpesaPaymentCard.vue' // Import the new component

export default {
  name: 'CheckoutPage',
  components: {
    MpesaPaymentCard // Register the new component
  },
  setup() {
    const router = useRouter()
    
    const loading = ref(true)
    const authenticatedCart = ref(null) // For authenticated user's cart
    const counties = ref([])
    const subCounties = ref([])
    const selectedCounty = computed(() => orderForm.value.delivery_address.county_id); // Changed to computed
    const submittingOrder = ref(false)
    const loadingSubCounties = ref(false)
    const deliveryFee = ref(50)
    const showItems = ref(false)
    const formSubmitted = ref(false) // New reactive property for form submission status
    
    // New variables for delivery fee estimation
    const estimatedDeliveryFee = ref(null)
    const estimatingDeliveryFee = ref(false)
    const deliveryFeeError = ref(null)
    const deliveryDistance = ref(null)
    
    // Address validation and autocomplete variables
    const addressValidation = ref(null)
    const addressSuggestions = ref([])
    const addressInputTimeout = ref(null)
    const addressResolution = ref(null)
    const deliveryFeeTimeout = ref(null)
    
    // M-Pesa payment state (removed for manual flow)
    const processingPayment = ref(false)
    
    const orderForm = ref({
      delivery_address: {
        full_name: '',
        phone_number: '',
        county_id: '', // New field for county ID
        subcounty_id: '', // New field for subcounty ID
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
    }); // Added semicolon to ensure proper statement termination

    // Computed delivery fee - use real-time estimation when available, fallback to cart estimation, then default
    const actualDeliveryFee = computed(() => {
      if (estimatedDeliveryFee.value !== null) {
        return parseFloat(estimatedDeliveryFee.value)
      }
      return cart.value?.estimated_delivery_fee ? parseFloat(cart.value.estimated_delivery_fee) : deliveryFee.value
    })

    // Computed total amount
    const totalAmount = computed(() => {
      const subtotal = parseFloat(cart.value?.total_cost || 0)
      return (subtotal + actualDeliveryFee.value).toFixed(2)
    })

    // Computed
    const isFormValid = computed(() => {
      const addr = orderForm.value.delivery_address
      return addr.full_name && 
             addr.phone_number && 
             addr.county_id && 
             addr.subcounty_id && 
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
      orderForm.value.delivery_address.subcounty_id = ''
      
      if (!orderForm.value.delivery_address.county_id) {
        subCounties.value = []
        loadingSubCounties.value = false
        return
      }
      
      loadingSubCounties.value = true
      
      try {
        console.log('Loading sub-counties for county:', orderForm.value.delivery_address.county_id)
        const response = await locationsAPI.getSubCounties(orderForm.value.delivery_address.county_id)
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

    const estimateDeliveryFee = async () => {
      // Only estimate if we have sufficient address information
      const addr = orderForm.value.delivery_address
      if (!addr.subcounty_id || !addr.detailed_address) {
        estimatedDeliveryFee.value = null
        deliveryDistance.value = null
        deliveryFeeError.value = null
        addressValidation.value = null
        return
      }

      estimatingDeliveryFee.value = true
      deliveryFeeError.value = null
      
      // Clear previous validation results while loading
      addressValidation.value = {
        is_valid: true,
        warnings: [],
        suggestions: [],
        confidence: 0,
        mismatch_detected: false,
        loading: true
      }

      try {
        const response = await cartAPI.estimateDeliveryFee({
          county: selectedCounty.value,
          sub_county: addr.subcounty_id,
          detailed_address: addr.detailed_address,
          full_name: addr.full_name,
          phone_number: addr.phone_number
        })

        estimatedDeliveryFee.value = response.delivery_fee
        deliveryDistance.value = response.distance_km
        
        // Store address validation results with additional info
        if (response.address_validation) {
          addressValidation.value = {
            ...response.address_validation,
            loading: false
          }
        }
        
        // Store address resolution details for transparency
        if (response.address_resolution) {
          addressResolution.value = response.address_resolution
        }
        
        console.log('Delivery fee estimated:', response)
      } catch (error) {
        console.error('Failed to estimate delivery fee:', error)
        deliveryFeeError.value = 'Unable to calculate delivery fee. Using standard rate.'
        estimatedDeliveryFee.value = null
        addressValidation.value = {
          is_valid: false,
          warnings: ['Unable to validate address. Please double-check your details.'],
          suggestions: [],
          confidence: 0,
          mismatch_detected: false,
          loading: false
        }
      } finally {
        estimatingDeliveryFee.value = false
      }
    }

    const createOrderManually = async () => {
      formSubmitted.value = true // Set formSubmitted to true on attempt
      if (!isFormValid.value) {
        return
      }

      // Ensure only M-Pesa is allowed for now
      if (orderForm.value.payment_method !== 'mpesa') {
        alert('Only M-Pesa payment is currently available')
        return
      }

      processingPayment.value = true

      try {
        const orderPayload = {
          cart_items: cart.value.items.map(item => ({
            product_listing_id: item.product_listing_id || item.listing_id,
            quantity: item.quantity
          })),
          delivery_address: {
            full_name: orderForm.value.delivery_address.full_name,
            phone_number: orderForm.value.delivery_address.phone_number,
            county_id: selectedCounty.value,
            subcounty_id: orderForm.value.delivery_address.subcounty_id,
            detailed_address: orderForm.value.delivery_address.detailed_address,
          },
          payment_method: 'mpesa',
          special_instructions: orderForm.value.special_instructions || '',
          expected_total: parseFloat(totalAmount.value).toFixed(2) // Ensure two decimal places
        }

        const response = await ordersAPI.createOrder(orderPayload)
        
        if (response.order_id) {
          router.push(`/orders/${response.order_id}`)
        } else {
          alert('Failed to create order. Please try again.')
        }
        
      } catch (error) {
        console.error('Failed to create order:', error)
        alert('Failed to create order. Please try again.')
      } finally {
        processingPayment.value = false
      }
    }

    // Address input handler for autocomplete and validation
    const onAddressInput = (event) => {
      const query = event.target.value
      
      // Clear previous timeout
      if (addressInputTimeout.value) {
        clearTimeout(addressInputTimeout.value)
      }
      
      // Clear suggestions if query is too short
      if (query.length < 2) {
        addressSuggestions.value = []
        return
      }
      
      // Show loading state for autocomplete
      addressSuggestions.value = [{ text: 'Loading suggestions...', loading: true }]
      
      // Debounce the autocomplete API call
      addressInputTimeout.value = setTimeout(async () => {
        try {
          const response = await cartAPI.getAddressAutocomplete(query)
          addressSuggestions.value = response.suggestions || []
        } catch (error) {
          console.error('Failed to get address suggestions:', error)
          addressSuggestions.value = []
        }
      }, 300)
    }

    // Debounced delivery fee estimation
    const debouncedEstimateDeliveryFee = () => {
      // Clear previous timeout
      if (deliveryFeeTimeout.value) {
        clearTimeout(deliveryFeeTimeout.value)
      }
      
      // Debounce the delivery fee estimation to prevent too many API calls
      deliveryFeeTimeout.value = setTimeout(() => {
        estimateDeliveryFee()
      }, 800) // Increased to 800ms for better UX
    }

    // Select an address suggestion
    const selectAddressSuggestion = (suggestion) => {
      // Don't select loading suggestions
      if (suggestion.loading) return
      
      orderForm.value.delivery_address.detailed_address = suggestion.text
      
      // Auto-select subcounty if available
      if (suggestion.subcounty && suggestion.county) {
        // Find matching county
        const county = counties.value.find(c => 
          c.county_name.toLowerCase().includes(suggestion.county.toLowerCase())
        )
        
        if (county) {
          selectedCounty.value = county.county_id
          loadSubCounties().then(() => {
            // Find matching subcounty
            const subcounty = subCounties.value.find(sc => 
              sc.sub_county_name.toLowerCase().includes(suggestion.subcounty.toLowerCase())
            )
            
            if (subcounty) {
              orderForm.value.delivery_address.location = subcounty.sub_county_id
            }
          })
        }
      }
      
      // Clear suggestions
      addressSuggestions.value = []
      
      // Trigger debounced delivery fee estimation
      debouncedEstimateDeliveryFee()
    }

    // Initialize form with user data
    const initializeForm = () => {
      if (user.value) {
        orderForm.value.delivery_address.full_name = `${user.value.first_name || ''} ${user.value.last_name || ''}`.trim()
        orderForm.value.delivery_address.phone_number = user.value.phone_number || ''
      }
    }

    // Watchers for real-time delivery fee estimation
    watch([
      () => orderForm.value.delivery_address.subcounty_id,
      () => orderForm.value.delivery_address.detailed_address
    ], () => {
      // Only trigger if both fields have values
      if (orderForm.value.delivery_address.subcounty_id && orderForm.value.delivery_address.detailed_address) {
        debouncedEstimateDeliveryFee()
      }
    }, { deep: true })

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
      estimateDeliveryFee,
      createOrderManually,
      totalAmount,
      actualDeliveryFee,
      estimatedDeliveryFee,
      estimatingDeliveryFee,
      deliveryFeeError,
      deliveryDistance,
      addressValidation,
      addressSuggestions,
      onAddressInput,
      selectAddressSuggestion,
      addressResolution,
      debouncedEstimateDeliveryFee,
      processingPayment,
      formSubmitted, // Expose formSubmitted
    }
  }
}
</script>
