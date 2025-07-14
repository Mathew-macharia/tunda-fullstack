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
              <div class="flex justify-between font-bold border-t pt-2">
                <span>Total</span>
                <span>KSh {{ totalAmount }}</span>
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
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm sm:text-base"
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
                      <p>Click "Pay with M-Pesa" to start the payment process</p>
                    </div>
                    <div class="flex items-start space-x-2">
                      <span class="inline-flex items-center justify-center w-4 h-4 bg-green-600 text-white rounded-full text-xs font-bold mt-0.5">2</span>
                      <p>You'll receive an <span class="font-semibold">STK Push</span> on your phone to pay <span class="font-semibold">KSh {{ totalAmount }}</span></p>
                    </div>
                    <div class="flex items-start space-x-2">
                      <span class="inline-flex items-center justify-center w-4 h-4 bg-green-600 text-white rounded-full text-xs font-bold mt-0.5">3</span>
                      <p>Enter your <span class="font-semibold">M-Pesa PIN</span> to complete the payment</p>
                    </div>
                    <div class="flex items-start space-x-2">
                      <span class="inline-flex items-center justify-center w-4 h-4 bg-green-600 text-white rounded-full text-xs font-bold mt-0.5">4</span>
                      <p>Your order will be confirmed and delivery scheduled automatically</p>
                    </div>
                  </div>
                </div>
              </div>
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
              @click="initiatePayment"
              :disabled="processingPayment || !isFormValid"
              class="w-full btn-primary py-3 text-sm sm:text-base disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <svg v-if="processingPayment" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-if="processingPayment">Processing Payment...</span>
              <span v-else>Pay with M-Pesa - KSh {{ totalAmount }}</span>
            </button>
            <div class="mt-3 text-xs text-gray-500 text-center space-y-1">
              <p>You'll receive an STK Push on your phone to complete payment</p>
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
              @click="initiatePayment"
              :disabled="processingPayment || !isFormValid"
              class="w-full mt-6 btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <svg v-if="processingPayment" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-if="processingPayment">Processing Payment...</span>
              <span v-else>Pay with M-Pesa</span>
            </button>

            <div class="mt-4 text-xs text-gray-500 text-center space-y-1">
              <p>You'll receive an STK Push on your phone to complete payment</p>
              <p>By placing this order, you agree to our Terms of Service and Privacy Policy.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- M-Pesa Payment Modal -->
    <div v-if="showMpesaModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-md w-full p-6">
        <div class="text-center">
          <!-- Initiating Payment -->
          <div v-if="mpesaPaymentStatus === 'initiating'" class="space-y-4">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
            <h3 class="text-lg font-semibold text-gray-900">Initiating Payment</h3>
            <p class="text-sm text-gray-600">Setting up your M-Pesa payment...</p>
          </div>
          
          <!-- Pending Payment -->
          <div v-else-if="mpesaPaymentStatus === 'pending'" class="space-y-4">
            <div class="flex items-center justify-center">
              <div class="bg-green-100 p-3 rounded-full">
                <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                </svg>
              </div>
            </div>
            <h3 class="text-lg font-semibold text-gray-900">Check Your Phone</h3>
            <p class="text-sm text-gray-600">
              We've sent an M-Pesa payment request to your phone. 
              Please enter your M-Pesa PIN to complete the payment.
            </p>
            <div class="flex items-center justify-center space-x-2 text-sm text-gray-500">
              <div class="animate-pulse w-2 h-2 bg-green-600 rounded-full"></div>
              <span>Waiting for payment confirmation...</span>
            </div>
          </div>
          
          <!-- Payment Completed -->
          <div v-else-if="mpesaPaymentStatus === 'completed'" class="space-y-4">
            <div class="flex items-center justify-center">
              <div class="bg-green-100 p-3 rounded-full">
                <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
            </div>
            <h3 class="text-lg font-semibold text-green-900">Payment Successful!</h3>
            <p class="text-sm text-gray-600">
              Your payment has been processed successfully.
            </p>
            <div v-if="mpesaReceiptNumber" class="bg-gray-50 p-3 rounded-lg">
              <p class="text-xs text-gray-500">M-Pesa Receipt Number</p>
              <p class="font-mono text-sm font-semibold">{{ mpesaReceiptNumber }}</p>
            </div>
            <p class="text-xs text-gray-500">Redirecting to your order details...</p>
          </div>
          
          <!-- Payment Failed -->
          <div v-else-if="mpesaPaymentStatus === 'failed'" class="space-y-4">
            <div class="flex items-center justify-center">
              <div class="bg-red-100 p-3 rounded-full">
                <svg class="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </div>
            </div>
            <h3 class="text-lg font-semibold text-red-900">Payment Failed</h3>
            <p class="text-sm text-gray-600">{{ mpesaErrorMessage }}</p>
            <div class="flex space-x-3">
              <button @click="retryPayment" class="btn-primary flex-1">
                Try Again
              </button>
              <button @click="closeMpesaModal" class="btn-secondary flex-1">
                Close
              </button>
            </div>
          </div>
          
          <!-- Payment Timeout -->
          <div v-else-if="mpesaPaymentStatus === 'timeout'" class="space-y-4">
            <div class="flex items-center justify-center">
              <div class="bg-yellow-100 p-3 rounded-full">
                <svg class="h-8 w-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
            </div>
            <h3 class="text-lg font-semibold text-yellow-900">Payment Verification Timeout</h3>
            <p class="text-sm text-gray-600">
              We couldn't verify your payment within the expected time. 
              Please check your M-Pesa messages for confirmation.
            </p>
            <div class="flex space-x-3">
              <button @click="retryPayment" class="btn-primary flex-1">
                Check Again
              </button>
              <button @click="closeMpesaModal" class="btn-secondary flex-1">
                Close
              </button>
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
    
    // M-Pesa payment state
    const showMpesaModal = ref(false)
    const mpesaPaymentStatus = ref('idle') // idle, initiating, pending, completed, failed, timeout
    const mpesaErrorMessage = ref('')
    const mpesaReceiptNumber = ref('')
    const currentTransaction = ref(null)
    const processingPayment = ref(false)
    const pollingInterval = ref(null); // ADDED: To store polling interval ID
    
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
      return subtotal + actualDeliveryFee.value
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

    const estimateDeliveryFee = async () => {
      // Only estimate if we have sufficient address information
      const addr = orderForm.value.delivery_address
      if (!addr.location || !addr.detailed_address) {
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
          sub_county: addr.location,
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

    const initiatePayment = async () => {
      if (!isFormValid.value) {
        alert('Please fill in all required fields')
        return
      }

      // Ensure only M-Pesa is allowed for now
      if (orderForm.value.payment_method !== 'mpesa') {
        alert('Only M-Pesa payment is currently available')
        return
      }

      processingPayment.value = true

      try {
        // Create payment session first
        const sessionData = {
          cart_items: cart.value.items.map(item => ({
            product_listing_id: item.product_listing_id || item.listing_id,
            quantity: item.quantity
          })),
          // CORRECTED: Structure delivery_details as expected by backend
          delivery_details: {
            full_name: orderForm.value.delivery_address.full_name,
            phone_number: orderForm.value.delivery_address.phone_number,
            county_id: selectedCounty.value, // Add county_id
            subcounty_id: orderForm.value.delivery_address.location, // Use subcounty_id
            detailed_address: orderForm.value.delivery_address.detailed_address,
            special_instructions: orderForm.value.special_instructions || '', // Move special_instructions here
            // You might also want to include estimated_delivery_date and delivery_time_slot if collected
            estimated_delivery_date: null, // Placeholder, update if you have a form field for this
            delivery_time_slot: null,     // Placeholder, update if you have a form field for this
          },
          payment_method: 'mpesa',
          expected_total: totalAmount.value
        }

        const session = await paymentsAPI.createPaymentSession(sessionData)
        
        // Now initiate M-Pesa payment
        await initiateMpesaPayment(session)
        
      } catch (error) {
        console.error('Failed to initiate payment:', error)
        alert('Failed to initiate payment. Please try again.')
        processingPayment.value = false
      }
    }

    const submitOrder = async () => {
      // This method is now deprecated - use initiatePayment instead
      await initiatePayment()
    }

    const initiateMpesaPayment = async (session) => {
      try {
        // Show M-Pesa payment modal
        showMpesaModal.value = true
        mpesaPaymentStatus.value = 'initiating'
        
        // Get phone number for M-Pesa payment
        const phoneNumber = orderForm.value.delivery_address.phone_number
        
        // Initiate M-Pesa STK Push using payment session
        const response = await paymentsAPI.initiateSessionPayment(session.session_id, {
          phone_number: phoneNumber
        })
        
        if (response.status === 'success') {
          mpesaPaymentStatus.value = 'pending'
          currentTransaction.value = {
            transaction_id: response.transaction_id,
            checkout_request_id: response.checkout_request_id,
            session_id: session.session_id
          }
          
          // Start polling for payment status
          pollPaymentStatus(response.transaction_id)
          
        } else {
          mpesaPaymentStatus.value = 'failed'
          mpesaErrorMessage.value = response.message || 'Failed to initiate payment'
        }
        
      } catch (error) {
        console.error('Failed to initiate M-Pesa payment:', error)
        mpesaPaymentStatus.value = 'failed'
        mpesaErrorMessage.value = error.response?.data?.message || 'Failed to initiate M-Pesa payment'
      } finally {
        processingPayment.value = false
      }
    }

    const pollPaymentStatus = async (transactionId) => {
      const maxAttempts = 30 // 5 minutes with 10-second intervals
      let attempts = 0
      
      // Clear any existing polling interval before starting a new one
      if (pollingInterval.value) {
        clearTimeout(pollingInterval.value);
      }

      const poll = async () => {
        try {
          const response = await paymentsAPI.getPaymentTransaction(transactionId)
          const status = response.payment_status
          
          if (status === 'completed') {
            mpesaPaymentStatus.value = 'completed'
            mpesaReceiptNumber.value = response.mpesa_receipt_number
            
            // Stop polling
            if (pollingInterval.value) clearTimeout(pollingInterval.value);
            
            // Redirect to order details after a short delay
            setTimeout(() => {
              router.push(`/orders/${response.order}`)
            }, 3000)
            
          } else if (status === 'failed') {
            mpesaPaymentStatus.value = 'failed'
            mpesaErrorMessage.value = response.failure_reason || 'Payment failed'
            // Stop polling
            if (pollingInterval.value) clearTimeout(pollingInterval.value);
            
          } else if (attempts < maxAttempts) {
            attempts++
            pollingInterval.value = setTimeout(poll, 10000) // Store interval ID
            
          } else {
            mpesaPaymentStatus.value = 'timeout'
            mpesaErrorMessage.value = 'Payment verification timed out. Please check your M-Pesa messages.'
            // Stop polling
            if (pollingInterval.value) clearTimeout(pollingInterval.value);
          }
          
        } catch (error) {
          console.error('Error checking payment status:', error)
          if (attempts < maxAttempts) {
            attempts++
            pollingInterval.value = setTimeout(poll, 10000) // Store interval ID
          } else {
            mpesaPaymentStatus.value = 'failed'
            mpesaErrorMessage.value = 'Unable to verify payment status'
            // Stop polling
            if (pollingInterval.value) clearTimeout(pollingInterval.value);
          }
        }
      }
      
      poll()
    }

    const retryPayment = async () => {
      if (currentTransaction.value && currentTransaction.value.session_id) {
        // Retry payment using the session
        try {
          const session = await paymentsAPI.getPaymentSession(currentTransaction.value.session_id)
          await initiateMpesaPayment(session)
        } catch (error) {
          console.error('Failed to retry payment:', error)
          alert('Failed to retry payment. Please try again.')
        }
      }
    }

    const closeMpesaModal = () => {
      showMpesaModal.value = false
      mpesaPaymentStatus.value = 'idle'
      mpesaErrorMessage.value = ''
      mpesaReceiptNumber.value = ''
      currentTransaction.value = null
      // Ensure any active polling is stopped when modal is closed
      if (pollingInterval.value) {
        clearTimeout(pollingInterval.value);
        pollingInterval.value = null;
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
      () => orderForm.value.delivery_address.location,
      () => orderForm.value.delivery_address.detailed_address
    ], () => {
      // Only trigger if both fields have values
      if (orderForm.value.delivery_address.location && orderForm.value.delivery_address.detailed_address) {
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
      submitOrder,
      initiatePayment,
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
      showMpesaModal,
      mpesaPaymentStatus,
      mpesaErrorMessage,
      mpesaReceiptNumber,
      processingPayment,
      retryPayment,
      closeMpesaModal
    }
  }
}
</script>
