<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="!order" class="text-center py-12">
        <svg class="mx-auto h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8V4m0 4v4m0 0v4m0-4h4m-4 0H8"></path>
        </svg>
        <h2 class="mt-4 text-2xl font-semibold text-gray-900">Order not found</h2>
        <p class="mt-2 text-gray-600">The order you're looking for doesn't exist or has been removed.</p>
        <router-link to="/orders" class="mt-6 btn-primary inline-block">
          Back to Orders
        </router-link>
      </div>

      <!-- Order Content -->
      <div v-else>
        <!-- Header with Navigation -->
        <div class="mb-8">
          <nav class="flex mb-4" aria-label="Breadcrumb">
            <ol class="flex items-center space-x-4">
              <li>
                <router-link to="/orders" class="text-gray-400 hover:text-gray-500">
                  <svg class="flex-shrink-0 h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                  </svg>
                  <span class="sr-only">Back to orders</span>
                </router-link>
              </li>
              <li>
                <div class="flex items-center">
                  <svg class="flex-shrink-0 h-5 w-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                  </svg>
                  <span class="ml-4 text-sm font-medium text-gray-500">Order #{{ order.order_id }}</span>
                </div>
              </li>
            </ol>
          </nav>

          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Order #{{ order.order_id }}</h1>
              <p class="mt-2 text-gray-600">
                Placed on {{ formatDate(order.created_at) }}
              </p>
            </div>
            
            <div class="mt-4 sm:mt-0 flex items-center space-x-4">
              <span :class="getStatusClass(order.order_status)" class="px-4 py-2 rounded-full text-sm font-medium">
                {{ formatStatus(order.order_status) }}
              </span>
              <span :class="getPaymentStatusClass(order.payment_status)" class="px-4 py-2 rounded-full text-sm font-medium">
                {{ formatPaymentStatus(order.payment_status) }}
              </span>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Main Content -->
          <div class="lg:col-span-2 space-y-8">
            <!-- Order Progress Timeline -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-xl font-semibold text-gray-900 mb-6">Order Status</h2>
              
              <div class="flow-root">
                <ul class="-mb-8">
                  <li v-for="(status, index) in orderTimeline" :key="status.step" class="relative">
                    <div v-if="index !== orderTimeline.length - 1" 
                         :class="[
                           'absolute left-4 top-4 -ml-px h-full w-0.5',
                           status.completed ? 'bg-green-600' : 'bg-gray-300'
                         ]"
                         aria-hidden="true"></div>
                    
                    <div class="relative flex items-start space-x-3">
                      <div class="relative">
                        <div :class="[
                          'h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white',
                          status.completed ? 'bg-green-600' : status.current ? 'bg-yellow-600' : 'bg-gray-300'
                        ]">
                          <svg v-if="status.completed" class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                          </svg>
                          <div v-else-if="status.current" class="h-2.5 w-2.5 bg-white rounded-full"></div>
                          <div v-else class="h-2.5 w-2.5 bg-gray-100 rounded-full"></div>
                        </div>
                      </div>
                      
                      <div class="min-w-0 flex-1">
                        <div>
                          <div class="text-sm">
                            <span :class="[
                              'font-medium',
                              status.completed ? 'text-gray-900' : status.current ? 'text-yellow-800' : 'text-gray-500'
                            ]">
                              {{ status.title }}
                            </span>
                          </div>
                          <p class="mt-0.5 text-sm text-gray-500">{{ status.description }}</p>
                          <p v-if="status.timestamp" class="mt-0.5 text-xs text-gray-400">
                            {{ formatDate(status.timestamp) }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Order Items -->
            <div class="bg-white rounded-lg shadow">
              <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-xl font-semibold text-gray-900">Order Items</h2>
              </div>
              
              <div class="divide-y divide-gray-200">
                <div
                  v-for="item in order.items"
                  :key="item.order_item_id"
                  class="px-6 py-4"
                >
                  <div class="flex items-center space-x-4">
                    <!-- Product Image -->
                    <div class="flex-shrink-0">
                      <img
                        v-if="item.listing_details && item.listing_details.photos && item.listing_details.photos.length"
                        :src="item.listing_details.photos[0]"
                        :alt="item.listing_details.product_name"
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
                        {{ item.listing_details?.product_name || 'Product' }}
                      </h3>
                      <p class="text-sm text-gray-500">
                        From {{ item.listing_details?.farm_name || item.farmer_name }}
                      </p>
                      <p class="text-sm text-gray-600 mt-1">
                        {{ item.quantity }} {{ item.listing_details?.product_unit || 'units' }} × KSh {{ item.price_at_purchase }}
                      </p>
                      
                      <!-- Item Status -->
                      <div class="mt-2 flex items-center justify-between">
                        <span :class="getItemStatusClass(item.item_status)" class="px-3 py-1 rounded-full text-xs font-medium">
                          {{ formatItemStatus(item.item_status) }}
                        </span>
                        
                        <!-- Review Button -->
                        <button
                          v-if="order.order_status === 'delivered'"
                          @click="openReviewModal(item)"
                          class="text-sm text-green-600 hover:text-green-800 font-medium"
                        >
                          {{ item.order_item_id && orderItemToReviewMap[item.order_item_id] ? 'View Review' : 'Write Review' }}
                        </button>
                      </div>
                    </div>
                    
                    <!-- Subtotal -->
                    <div class="text-right">
                      <div class="text-lg font-medium text-gray-900">
                        KSh {{ item.subtotal }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Order Summary Sidebar -->
          <div class="space-y-8">
            <!-- Order Summary -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-xl font-semibold text-gray-900 mb-6">Order Summary</h2>
              
              <div class="space-y-3">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-600">Subtotal</span>
                  <span class="font-medium">KSh {{ (parseFloat(order.total_amount) - parseFloat(order.delivery_fee || 0)).toFixed(2) }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-600">Delivery Fee</span>
                  <span class="font-medium">KSh {{ order.delivery_fee || '0.00' }}</span>
                </div>
                <div class="border-t pt-3">
                  <div class="flex justify-between text-lg font-bold">
                    <span>Total</span>
                    <span>KSh {{ order.total_amount }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Delivery Information -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-xl font-semibold text-gray-900 mb-6">Delivery Information</h2>
              
              <div class="space-y-4">
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ order.delivery_address?.full_name }}</p>
                  <p class="text-sm text-gray-600">{{ order.delivery_address?.phone_number }}</p>
                </div>
                
                <div>
                  <p class="text-sm font-medium text-gray-700">Address</p>
                  <p class="text-sm text-gray-600">{{ order.delivery_address?.detailed_address }}</p>
                  <p class="text-sm text-gray-500">{{ order.delivery_address?.location_name }}</p>
                </div>
                
                <div v-if="order.special_instructions">
                  <p class="text-sm font-medium text-gray-700">Special Instructions</p>
                  <p class="text-sm text-gray-600">{{ order.special_instructions }}</p>
                </div>
              </div>
            </div>

            <!-- Payment Information -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-xl font-semibold text-gray-900 mb-6">Payment Information</h2>
              
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Payment Method</span>
                  <span class="text-sm font-medium">{{ formatPaymentMethod(order.payment_method) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Payment Status</span>
                  <span :class="getPaymentStatusClass(order.payment_status)" class="px-2 py-1 rounded text-xs font-medium">
                    {{ formatPaymentStatus(order.payment_status) }}
                  </span>
                </div>
                <div v-if="order.payment_reference" class="flex justify-between">
                  <span class="text-sm text-gray-600">Reference</span>
                  <span class="text-sm font-medium">{{ order.payment_reference }}</span>
                </div>
              </div>
            </div>

            <!-- Order Actions -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-xl font-semibold text-gray-900 mb-6">Actions</h2>
              
              <div class="space-y-3">
                <button
                  v-if="order.order_status === 'pending'"
                  @click="cancelOrder"
                  :disabled="cancellingOrder"
                  class="w-full btn-secondary text-red-600 border-red-300 hover:bg-red-50"
                >
                  <span v-if="cancellingOrder">Cancelling...</span>
                  <span v-else>Cancel Order</span>
                </button>
                
                <button
                  @click="reorderItems"
                  class="w-full btn-secondary"
                >
                  Order Again
                </button>
                
                <button
                  v-if="order.order_status === 'delivered'"
                  @click="downloadReceipt"
                  class="w-full btn-secondary"
                >
                  Download Receipt
                </button>
                
                <router-link
                  to="/support"
                  class="w-full btn-secondary text-center block"
                >
                  Contact Support
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Review Modal -->
  <ReviewModal
    :isOpen="showReviewModal"
    :editingReview="selectedItem?.existingReview"
    :targetType="'product'"
    :targetId="selectedItem?.listing_details?.product?.product_id || selectedItem?.listing_details?.listing_id || selectedItem?.listing || ''"
    :orderItem="selectedItem"
    @close="closeReviewModal"
    @success="onReviewSuccess"
  />
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ordersAPI, cartAPI, reviewsAPI } from '@/services/api'
import ReviewModal from '@/components/common/ReviewModal.vue'

export default {
  name: 'OrderDetail',
  components: {
    ReviewModal
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const loading = ref(true)
    const order = ref(null)
    const cancellingOrder = ref(false)
    const showReviewModal = ref(false)
    const selectedItem = ref(null)
    const userReviews = ref([])
    const orderItemToReviewMap = computed(() => {
      const map = {}
      userReviews.value.forEach(review => {
        if (review.order_item) {
          map[review.order_item] = review
        }
      })
      return map
    })

    // Computed
    const orderTimeline = computed(() => {
      if (!order.value) return []

      const status = order.value.order_status
      const timeline = [
        {
          step: 'pending',
          title: 'Order Placed',
          description: 'Your order has been received and is being processed',
          completed: true,
          current: status === 'pending',
          timestamp: order.value.created_at
        },
        {
          step: 'confirmed',
          title: 'Order Confirmed',
          description: 'Farmers have confirmed your order and are preparing items',
          completed: ['confirmed', 'processing', 'out_for_delivery', 'delivered'].includes(status),
          current: status === 'confirmed',
          timestamp: order.value.confirmed_at
        },
        {
          step: 'processing',
          title: 'Processing',
          description: 'Items are being harvested and packed for delivery',
          completed: ['processing', 'out_for_delivery', 'delivered'].includes(status),
          current: status === 'processing',
          timestamp: order.value.processing_at
        },
        {
          step: 'out_for_delivery',
          title: 'Out for Delivery',
          description: 'Your order is on the way to your delivery address',
          completed: ['out_for_delivery', 'delivered'].includes(status),
          current: status === 'out_for_delivery',
          timestamp: order.value.shipped_at
        },
        {
          step: 'delivered',
          title: 'Delivered',
          description: 'Your order has been successfully delivered',
          completed: status === 'delivered',
          current: status === 'delivered',
          timestamp: order.value.delivered_at
        }
      ]

      // Handle cancelled orders
      if (status === 'cancelled') {
        timeline.push({
          step: 'cancelled',
          title: 'Order Cancelled',
          description: 'This order has been cancelled',
          completed: true,
          current: true,
          timestamp: order.value.cancelled_at
        })
      }

      return timeline
    })

    // Methods
    const loadOrder = async () => {
      loading.value = true
      
      try {
        const orderResponse = await ordersAPI.getOrderById(route.params.id)
        order.value = orderResponse

        // Fetch user's reviews to check if this order item has been reviewed
        const reviewsResponse = await reviewsAPI.getMyReviews()
        userReviews.value = reviewsResponse
        
      } catch (error) {
        console.error('Failed to load order or reviews:', error)
        order.value = null
        userReviews.value = []
      } finally {
        loading.value = false
      }
    }

    const cancelOrder = async () => {
      if (!confirm('Are you sure you want to cancel this order?')) {
        return
      }

      cancellingOrder.value = true

      try {
        await ordersAPI.cancelOrder(order.value.order_id)
        await loadOrder()
        alert('Order cancelled successfully')
      } catch (error) {
        console.error('Failed to cancel order:', error)
        alert('Failed to cancel order. Please try again.')
      } finally {
        cancellingOrder.value = false
      }
    }

    const reorderItems = async () => {
      try {
        for (const item of order.value.items) {
          await cartAPI.addToCart(item.listing_id, item.quantity)
        }
        
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        alert('Items added to cart!')
        router.push('/cart')
        
      } catch (error) {
        console.error('Failed to reorder items:', error)
        alert('Failed to add items to cart. Some items may no longer be available.')
      }
    }

    const downloadReceipt = () => {
      // Implementation for receipt download
      alert('Receipt download feature coming soon!')
    }

    const openReviewModal = (item) => {
      const existingReview = item.order_item_id ? orderItemToReviewMap.value[item.order_item_id] : null;
      if (existingReview) {
        selectedItem.value = { ...item, existingReview }; // Pass existing review data
      } else {
        selectedItem.value = item;
      }
      showReviewModal.value = true;
      console.log('Opening review modal for item:', item);
      console.log('Full selected item data:', item); // Log the entire item object
      console.log('Product ID:', item?.listing_details?.product_id);
      console.log('Listing ID:', item?.listing_id);
      console.log('Order Item ID:', item?.order_item_id);
    }

    const closeReviewModal = () => {
      showReviewModal.value = false
      selectedItem.value = null
    }

    const onReviewSuccess = () => {
      console.log('Review submitted successfully')
      closeReviewModal()
      loadOrder() // Reload order to show new reviews
      alert('Thank you for your review!')
    }

    // Utility functions
    const formatDate = (dateString) => {
      if (!dateString) return 'Not available'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatStatus = (status) => {
      const statusMap = {
        'pending': 'Pending',
        'confirmed': 'Confirmed',
        'processing': 'Processing',
        'out_for_delivery': 'Out for Delivery',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled'
      }
      return statusMap[status] || status
    }

    const formatItemStatus = (status) => {
      const statusMap = {
        'pending': 'Pending',
        'harvested': 'Harvested',
        'packed': 'Packed',
        'shipped': 'Shipped',
        'delivered': 'Delivered'
      }
      return statusMap[status] || status
    }

    const formatPaymentStatus = (status) => {
      const statusMap = {
        'pending': 'Payment Pending',
        'paid': 'Paid',
        'failed': 'Payment Failed',
        'refunded': 'Refunded'
      }
      return statusMap[status] || status
    }

    const formatPaymentMethod = (method) => {
      const methodMap = {
        'mpesa': 'M-Pesa',
        'cash_on_delivery': 'Cash on Delivery',
        'card': 'Credit/Debit Card'
      }
      return methodMap[method] || method
    }

    const getStatusClass = (status) => {
      const statusClasses = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'confirmed': 'bg-blue-100 text-blue-800',
        'processing': 'bg-purple-100 text-purple-800',
        'out_for_delivery': 'bg-orange-100 text-orange-800',
        'delivered': 'bg-green-100 text-green-800',
        'cancelled': 'bg-red-100 text-red-800'
      }
      return statusClasses[status] || 'bg-gray-100 text-gray-800'
    }

    const getItemStatusClass = (status) => {
      const statusClasses = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'harvested': 'bg-blue-100 text-blue-800',
        'packed': 'bg-purple-100 text-purple-800',
        'shipped': 'bg-orange-100 text-orange-800',
        'delivered': 'bg-green-100 text-green-800'
      }
      return statusClasses[status] || 'bg-gray-100 text-gray-800'
    }

    const getPaymentStatusClass = (status) => {
      const statusClasses = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'paid': 'bg-green-100 text-green-800',
        'failed': 'bg-red-100 text-red-800',
        'refunded': 'bg-purple-100 text-purple-800'
      }
      return statusClasses[status] || 'bg-gray-100 text-gray-800'
    }

    // Lifecycle
    onMounted(() => {
      loadOrder()
    })

    return {
      loading,
      order,
      cancellingOrder,
      orderTimeline,
      showReviewModal,
      selectedItem,
      cancelOrder,
      reorderItems,
      downloadReceipt,
      openReviewModal,
      closeReviewModal,
      onReviewSuccess,
      formatDate,
      formatStatus,
      formatItemStatus,
      formatPaymentStatus,
      formatPaymentMethod,
      getStatusClass,
      getItemStatusClass,
      getPaymentStatusClass,
      userReviews, // Expose userReviews
      orderItemToReviewMap // Expose orderItemToReviewMap
    }
  }
}
</script>
