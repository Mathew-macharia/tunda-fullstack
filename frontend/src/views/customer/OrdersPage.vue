<template>
  <div class="min-h-screen bg-gray-50 py-4 sm:py-8">
    <div class="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
      <!-- Header -->
      <div class="mb-6 sm:mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">My Orders</h1>
        <p class="mt-1 sm:mt-2 text-sm sm:text-base text-gray-600">Track and manage your orders</p>
      </div>

      <!-- Order Stats - Mobile Optimized -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex flex-col sm:flex-row sm:items-center">
            <div class="p-2 sm:p-3 rounded-full bg-blue-100 self-start">
              <svg class="h-4 w-4 sm:h-6 sm:w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
              </svg>
            </div>
            <div class="mt-2 sm:mt-0 sm:ml-4">
              <p class="text-xs sm:text-sm font-medium text-gray-500">Total</p>
              <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ orderStats.total }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex flex-col sm:flex-row sm:items-center">
            <div class="p-2 sm:p-3 rounded-full bg-yellow-100 self-start">
              <svg class="h-4 w-4 sm:h-6 sm:w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="mt-2 sm:mt-0 sm:ml-4">
              <p class="text-xs sm:text-sm font-medium text-gray-500">Pending</p>
              <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ orderStats.pending }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex flex-col sm:flex-row sm:items-center">
            <div class="p-2 sm:p-3 rounded-full bg-green-100 self-start">
              <svg class="h-4 w-4 sm:h-6 sm:w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <div class="mt-2 sm:mt-0 sm:ml-4">
              <p class="text-xs sm:text-sm font-medium text-gray-500">Delivered</p>
              <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ orderStats.delivered }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex flex-col sm:flex-row sm:items-center">
            <div class="p-2 sm:p-3 rounded-full bg-red-100 self-start">
              <svg class="h-4 w-4 sm:h-6 sm:w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </div>
            <div class="mt-2 sm:mt-0 sm:ml-4">
              <p class="text-xs sm:text-sm font-medium text-gray-500">Cancelled</p>
              <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ orderStats.cancelled }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters - Mobile Optimized -->
      <div class="bg-white rounded-lg shadow p-4 sm:p-6 mb-6 sm:mb-8">
        <div class="space-y-4 sm:space-y-0 sm:grid sm:grid-cols-2 lg:grid-cols-4 sm:gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              v-model="filters.status"
              @change="loadOrders"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">All Orders</option>
              <option value="pending">Pending</option>
              <option value="confirmed">Confirmed</option>
              <option value="processing">Processing</option>
              <option value="out_for_delivery">Out for Delivery</option>
              <option value="delivered">Delivered</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
            <select
              v-model="filters.dateRange"
              @change="loadOrders"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">Last 3 Months</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
            <select
              v-model="filters.sortBy"
              @change="loadOrders"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="-created_at">Newest First</option>
              <option value="created_at">Oldest First</option>
              <option value="-total_amount">Highest Amount</option>
              <option value="total_amount">Lowest Amount</option>
            </select>
          </div>

          <div class="sm:flex sm:items-end">
            <button
              @click="resetFilters"
              class="w-full btn-secondary py-2 text-sm"
            >
              Reset Filters
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 sm:h-12 sm:w-12 border-b-2 border-green-600"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="orders.length === 0" class="text-center py-8 sm:py-12">
        <svg class="mx-auto h-16 w-16 sm:h-24 sm:w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
        </svg>
        <h2 class="mt-4 text-xl sm:text-2xl font-semibold text-gray-900">No orders found</h2>
        <p class="mt-2 text-sm sm:text-base text-gray-600 px-4">
          {{ filters.status ? 'No orders match your current filters.' : 'You haven\'t placed any orders yet.' }}
        </p>
        <router-link to="/products" class="mt-6 btn-primary inline-block text-sm sm:text-base px-4 py-2">
          Start Shopping
        </router-link>
      </div>

      <!-- Orders List - Mobile Optimized -->
      <div v-else class="space-y-4 sm:space-y-6">
        <div
          v-for="order in orders"
          :key="order.order_id"
          class="bg-white rounded-lg shadow overflow-hidden"
        >
          <!-- Order Header - Mobile Optimized -->
          <div class="px-4 sm:px-6 py-4 border-b border-gray-200">
            <div class="space-y-3 sm:space-y-0 sm:flex sm:items-center sm:justify-between">
              <div class="space-y-2 sm:space-y-0 sm:flex sm:items-center sm:space-x-4">
                <div>
                  <h3 class="text-base sm:text-lg font-medium text-gray-900">
                    Order #{{ order.order_id }}
                  </h3>
                  <p class="text-xs sm:text-sm text-gray-500">
                    {{ formatDate(order.created_at) }}
                  </p>
                </div>
                
                <!-- Status badges - Mobile optimized -->
                <div class="flex flex-wrap gap-2">
                  <span :class="getStatusClass(order.order_status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ formatStatus(order.order_status) }}
                  </span>
                  <span :class="getPaymentStatusClass(order.payment_status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ formatPaymentStatus(order.payment_status) }}
                  </span>
                </div>
              </div>
              
              <!-- Price and actions - Mobile stacked -->
              <div class="flex items-center justify-between sm:flex-col sm:items-end sm:space-y-2">
                <span class="text-lg sm:text-xl font-semibold text-gray-900">
                  KSh {{ order.total_amount }}
                </span>
                <router-link
                  :to="`/orders/${order.order_id}`"
                  class="btn-secondary px-3 py-1.5 text-sm"
                >
                  View Details
                </router-link>
              </div>
            </div>
          </div>

          <!-- Order Items Preview - Mobile Optimized -->
          <div class="px-4 sm:px-6 py-4">
            <div class="space-y-3 sm:space-y-0 sm:grid sm:grid-cols-2 lg:grid-cols-3 sm:gap-4">
              <div
                v-for="item in order.items.slice(0, 3)"
                :key="item.order_item_id"
                class="flex items-center space-x-3"
              >
                <img
                  v-if="item.listing_details && item.listing_details.photos && item.listing_details.photos.length"
                  :src="item.listing_details.photos[0]"
                  :alt="item.listing_details.product_name"
                  class="h-10 w-10 sm:h-12 sm:w-12 object-cover rounded-lg flex-shrink-0"
                />
                <div v-else class="h-10 w-10 sm:h-12 sm:w-12 bg-gray-200 rounded-lg flex-shrink-0"></div>
                
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ item.listing_details?.product_name || 'Product' }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ item.quantity }} × KSh {{ item.price_at_purchase }}
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Show more items indicator -->
            <div v-if="order.items.length > 3" class="mt-3 sm:mt-0 sm:col-span-full text-center sm:text-left">
              <span class="text-sm text-gray-500">
                +{{ order.items.length - 3 }} more items
              </span>
            </div>
          </div>

          <!-- Quick Actions - Mobile Optimized -->
          <div class="px-4 sm:px-6 py-4 bg-gray-50 border-t border-gray-200">
            <div class="space-y-3 sm:space-y-0 sm:flex sm:justify-between sm:items-center">
              <div class="text-sm text-gray-600">
                <span class="font-medium">Delivery:</span>
                <span class="block sm:inline sm:ml-1">
                  {{ order.delivery_address?.detailed_address || 'Address not provided' }}
                </span>
              </div>
              
              <div class="flex flex-col sm:flex-row gap-2 sm:gap-3">
                <button
                  v-if="order.order_status === 'pending'"
                  @click="cancelOrder(order)"
                  :disabled="cancellingOrder === order.order_id"
                  class="btn-secondary px-4 py-2 text-sm text-red-600 border-red-300 hover:bg-red-50 disabled:opacity-50"
                >
                  <span v-if="cancellingOrder === order.order_id">Cancelling...</span>
                  <span v-else>Cancel Order</span>
                </button>
                
                <button
                  @click="reorderItems(order)"
                  class="btn-secondary px-4 py-2 text-sm"
                >
                  Reorder
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination - Mobile Optimized -->
      <div v-if="totalPages > 1" class="mt-6 sm:mt-8 flex justify-center">
        <nav class="flex items-center space-x-1 sm:space-x-2">
          <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-2 sm:px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span class="hidden sm:inline">Previous</span>
            <span class="sm:hidden">Prev</span>
          </button>
          
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="changePage(page)"
            :class="[
              'px-2 sm:px-3 py-2 text-sm font-medium rounded-md',
              page === currentPage
                ? 'text-white bg-green-600 border border-green-600'
                : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50'
            ]"
          >
            {{ page }}
          </button>
          
          <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="px-2 sm:px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span class="hidden sm:inline">Next</span>
            <span class="sm:hidden">Next</span>
          </button>
        </nav>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ordersAPI, cartAPI } from '@/services/api'

export default {
  name: 'OrdersPage',
  setup() {
    const router = useRouter()
    
    const loading = ref(true)
    const orders = ref([])
    const currentPage = ref(1)
    const totalPages = ref(1)
    const cancellingOrder = ref(null)
    
    const filters = reactive({
      status: '',
      dateRange: '',
      sortBy: '-created_at'
    })

    const orderStats = reactive({
      total: 0,
      pending: 0,
      delivered: 0,
      cancelled: 0
    })

    // Computed
    const visiblePages = computed(() => {
      const delta = 2
      const range = []
      
      for (let i = Math.max(1, currentPage.value - delta); 
           i <= Math.min(totalPages.value, currentPage.value + delta); 
           i++) {
        range.push(i)
      }
      
      return range
    })

    // Methods
    const loadOrders = async (page = 1) => {
      loading.value = true
      currentPage.value = page

      try {
        const params = {
          page,
          page_size: 10,
          ordering: filters.sortBy
        }

        if (filters.status) {
          params.order_status = filters.status
        }

        if (filters.dateRange) {
          params.date_range = filters.dateRange
        }

        const response = await ordersAPI.getOrders(params)
        
        if (response.results) {
          orders.value = response.results
          totalPages.value = Math.ceil(response.count / 10)
        } else {
          orders.value = response
        }

        // Calculate stats
        calculateOrderStats()
        
      } catch (error) {
        console.error('Failed to load orders:', error)
        orders.value = []
      } finally {
        loading.value = false
      }
    }

    const loadOrderStats = async () => {
      try {
        const response = await ordersAPI.getOrders({ page_size: 1000 })
        let allOrders = []
        
        // Handle different response structures
        if (Array.isArray(response)) {
          allOrders = response
        } else if (response && response.results && Array.isArray(response.results)) {
          allOrders = response.results
        } else if (response && response.data && Array.isArray(response.data)) {
          allOrders = response.data
        } else {
          console.warn('Unexpected response format:', response)
          allOrders = []
        }

        orderStats.total = allOrders.length
        orderStats.pending = allOrders.filter(o => ['pending', 'confirmed', 'processing'].includes(o.order_status)).length
        orderStats.delivered = allOrders.filter(o => o.order_status === 'delivered').length
        orderStats.cancelled = allOrders.filter(o => o.order_status === 'cancelled').length
        
      } catch (error) {
        console.error('Failed to load order stats:', error)
        orderStats.total = 0
        orderStats.pending = 0
        orderStats.delivered = 0
        orderStats.cancelled = 0
      }
    }

    const calculateOrderStats = () => {
      // Ensure orders.value is an array before filtering
      const ordersArray = Array.isArray(orders.value) ? orders.value : []
      
      orderStats.total = ordersArray.length
      orderStats.pending = ordersArray.filter(o => ['pending', 'confirmed', 'processing'].includes(o.order_status)).length
      orderStats.delivered = ordersArray.filter(o => o.order_status === 'delivered').length
      orderStats.cancelled = ordersArray.filter(o => o.order_status === 'cancelled').length
    }

    const cancelOrder = async (order) => {
      if (!confirm('Are you sure you want to cancel this order?')) {
        return
      }

      cancellingOrder.value = order.order_id

      try {
        await ordersAPI.cancelOrder(order.order_id)
        await loadOrders(currentPage.value)
        alert('Order cancelled successfully')
      } catch (error) {
        console.error('Failed to cancel order:', error)
        alert('Failed to cancel order. Please try again.')
      } finally {
        cancellingOrder.value = null
      }
    }

    const reorderItems = async (order) => {
      try {
        // Add each item to cart
        for (const item of order.items) {
          await cartAPI.addToCart(item.listing_id, item.quantity)
        }
        
        // Dispatch cart updated event
        window.dispatchEvent(new CustomEvent('cartUpdated'))
        
        alert('Items added to cart!')
        router.push('/cart')
        
      } catch (error) {
        console.error('Failed to reorder items:', error)
        alert('Failed to add items to cart. Some items may no longer be available.')
      }
    }

    const resetFilters = () => {
      filters.status = ''
      filters.dateRange = ''
      filters.sortBy = '-created_at'
      loadOrders()
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        loadOrders(page)
      }
    }

    // Utility functions
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
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

    const formatPaymentStatus = (status) => {
      const statusMap = {
        'pending': 'Payment Pending',
        'paid': 'Paid',
        'failed': 'Payment Failed',
        'refunded': 'Refunded'
      }
      return statusMap[status] || status
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
      loadOrders()
      loadOrderStats()
    })

    return {
      loading,
      orders,
      currentPage,
      totalPages,
      cancellingOrder,
      filters,
      orderStats,
      visiblePages,
      loadOrders,
      cancelOrder,
      reorderItems,
      resetFilters,
      changePage,
      formatDate,
      formatStatus,
      formatPaymentStatus,
      getStatusClass,
      getPaymentStatusClass
    }
  }
}
</script>