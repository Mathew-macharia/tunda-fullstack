<template>
  <div class="min-h-screen bg-gray-50 py-4 sm:py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-6 sm:mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Order Management</h1>
        <p class="mt-2 text-sm sm:text-base text-gray-600">Manage and track all your customer orders</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex items-center">
            <div class="p-2 sm:p-3 rounded-full bg-yellow-100">
              <ClockIcon class="h-4 w-4 sm:h-6 sm:w-6 text-yellow-600" />
            </div>
            <div class="ml-3 sm:ml-4">
              <p class="text-xs sm:text-sm font-medium text-gray-500">Pending</p>
              <p class="text-lg sm:text-2xl font-semibold text-gray-900">{{ orderCounts.pending }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex items-center">
            <div class="p-2 sm:p-3 rounded-full bg-blue-100">
              <CheckCircleIcon class="h-4 w-4 sm:h-6 sm:w-6 text-blue-600" />
            </div>
            <div class="ml-3 sm:ml-4">
              <p class="text-xs sm:text-sm font-medium text-gray-500">Harvested</p>
              <p class="text-lg sm:text-2xl font-semibold text-gray-900">{{ orderCounts.harvested }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex items-center">
            <div class="p-2 sm:p-3 rounded-full bg-indigo-100">
              <ArchiveBoxIcon class="h-4 w-4 sm:h-6 sm:w-6 text-indigo-600" />
            </div>
            <div class="ml-3 sm:ml-4">
              <p class="text-xs sm:text-sm font-medium text-gray-500">Packed</p>
              <p class="text-lg sm:text-2xl font-semibold text-gray-900">{{ orderCounts.packed }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex items-center">
            <div class="p-2 sm:p-3 rounded-full bg-green-100">
              <TruckIcon class="h-4 w-4 sm:h-6 sm:w-6 text-green-600" />
            </div>
            <div class="ml-3 sm:ml-4">
              <p class="text-xs sm:text-sm font-medium text-gray-500">Delivered</p>
              <p class="text-lg sm:text-2xl font-semibold text-gray-900">{{ orderCounts.delivered }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-lg shadow p-4 sm:p-6 mb-6 sm:mb-8">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select 
              v-model="filters.status" 
              @change="loadOrders"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="harvested">Harvested</option>
              <option value="packed">Packed</option>
              <option value="delivered">Delivered</option>
            </select>
          </div>

          <div class="sm:col-span-1 lg:col-span-1">
            <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Search orders..."
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Date From</label>
            <input
              v-model="filters.dateFrom"
              @change="loadOrders"
              type="date"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Date To</label>
            <input
              v-model="filters.dateTo"
              @change="loadOrders"
              type="date"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm"
            />
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
        <div class="flex">
          <ExclamationTriangleIcon class="h-5 w-5 text-red-400 flex-shrink-0" />
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error loading orders</h3>
            <p class="mt-1 text-sm text-red-700">{{ error }}</p>
            <button 
              @click="loadOrders"
              class="mt-2 text-sm text-red-600 hover:text-red-500 underline"
            >
              Try again
            </button>
          </div>
        </div>
      </div>

      <!-- Orders List -->
      <div v-else class="space-y-4">
        <div v-if="orders.length === 0" class="bg-white rounded-lg shadow p-8 text-center">
          <ShoppingBagIcon class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900">No orders found</h3>
          <p class="mt-1 text-sm text-gray-500">
            You haven't received any orders yet or no orders match your current filters.
          </p>
        </div>

        <!-- Desktop Table View -->
        <div v-else class="hidden lg:block bg-white rounded-lg shadow overflow-hidden">
          <!-- Table Header -->
          <div class="px-6 py-3 bg-gray-50 border-b border-gray-200">
            <div class="grid grid-cols-12 gap-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
              <div class="col-span-3">Product</div>
              <div class="col-span-2">Order</div>
              <div class="col-span-1">Quantity</div>
              <div class="col-span-1">Amount</div>
              <div class="col-span-2">Payment Status</div>
              <div class="col-span-2">Item Status</div>
              <div class="col-span-1">Actions</div>
            </div>
          </div>

          <!-- Table Body -->
          <div class="divide-y divide-gray-200">
            <div
              v-for="order in orders"
              :key="order.order_item_id"
              class="px-6 py-4 hover:bg-gray-50"
            >
              <div class="grid grid-cols-12 gap-4 items-center">
                <!-- Product -->
                <div class="col-span-3">
                  <div class="flex items-center space-x-3">
                    <img 
                      :src="order.listing_details?.photos?.[0] || '/api/placeholder/40/40'"
                      :alt="order.listing_details?.product_name"
                      class="h-10 w-10 rounded-lg object-cover"
                    />
                    <div>
                      <p class="text-sm font-medium text-gray-900">
                        {{ order.listing_details?.product_name }}
                      </p>
                      <p class="text-xs text-gray-500">
                        {{ order.listing_details?.farm_name }}
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Order Info -->
                <div class="col-span-2">
                  <p class="text-sm font-medium text-gray-900">
                    #{{ order.order_details?.order_number }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ formatDate(order.created_at) }}
                  </p>
                </div>

                <!-- Quantity -->
                <div class="col-span-1">
                  <p class="text-sm text-gray-900">
                    {{ order.quantity }} {{ order.listing_details?.product_unit }}
                  </p>
                  <p class="text-xs text-gray-500">
                    @ KES {{ formatCurrency(order.price_at_purchase) }}
                  </p>
                </div>

                <!-- Amount -->
                <div class="col-span-1">
                  <p class="text-sm font-medium text-gray-900">
                    KES {{ formatCurrency(order.total_price) }}
                  </p>
                </div>

                <!-- Payment Status -->
                <div class="col-span-2">
                  <span :class="getPaymentStatusBadgeClass(order.order_details?.payment_status)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                    {{ getPaymentStatusDisplayName(order.order_details?.payment_status) }}
                  </span>
                  <p class="text-xs text-gray-500 mt-1">
                    {{ getPaymentMethodDisplayName(order.order_details?.payment_method?.payment_type) }}
                  </p>
                </div>

                <!-- Item Status -->
                <div class="col-span-2">
                  <span :class="getItemStatusBadgeClass(order.item_status)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                    {{ getItemStatusDisplayName(order.item_status) }}
                  </span>
                  <p class="text-xs text-gray-500 mt-1">
                    Updated {{ formatRelativeTime(order.updated_at) }}
                  </p>
                </div>

                <!-- Actions -->
                <div class="col-span-1">
                  <div class="flex items-center space-x-2">
                    <button
                      v-if="canAdvanceStatus(order)"
                      @click="updateOrderStatus(order)"
                      :disabled="updatingStatus === order.order_item_id || !canUpdateStatus(order)"
                      :title="getStatusUpdateTooltip(order)"
                      :class="[
                        'inline-flex items-center p-2 border border-transparent rounded-full shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500',
                        canUpdateStatus(order) 
                          ? 'text-white bg-green-600 hover:bg-green-700' 
                          : 'text-gray-400 bg-gray-300 cursor-not-allowed'
                      ]"
                    >
                      <ArrowRightIcon v-if="updatingStatus !== order.order_item_id" class="h-4 w-4" />
                      <div v-else class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    </button>
                    
                    <button
                      @click="viewOrderDetails(order)"
                      class="inline-flex items-center p-2 border border-gray-300 rounded-full shadow-sm text-gray-400 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                    >
                      <EyeIcon class="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Mobile Card View -->
        <div v-else class="lg:hidden space-y-4">
          <div
            v-for="order in orders"
            :key="order.order_item_id"
            class="bg-white rounded-lg shadow p-4"
          >
            <!-- Product Info -->
            <div class="flex items-start space-x-3 mb-4">
              <img 
                :src="order.listing_details?.photos?.[0] || '/api/placeholder/48/48'"
                :alt="order.listing_details?.product_name"
                class="h-12 w-12 rounded-lg object-cover flex-shrink-0"
              />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ order.listing_details?.product_name }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ order.listing_details?.farm_name }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  Order #{{ order.order_details?.order_number }}
                </p>
              </div>
            </div>

            <!-- Order Details Grid -->
            <div class="grid grid-cols-2 gap-4 mb-4">
              <!-- Quantity & Price -->
              <div>
                <p class="text-xs text-gray-500">Quantity</p>
                <p class="text-sm font-medium text-gray-900">
                  {{ order.quantity }} {{ order.listing_details?.product_unit }}
                </p>
                <p class="text-xs text-gray-500">
                  @ KES {{ formatCurrency(order.price_at_purchase) }}
                </p>
              </div>

              <!-- Total Amount -->
              <div>
                <p class="text-xs text-gray-500">Total</p>
                <p class="text-sm font-semibold text-gray-900">
                  KES {{ formatCurrency(order.total_price) }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ formatDate(order.created_at) }}
                </p>
              </div>
            </div>

            <!-- Status Badges -->
            <div class="flex flex-wrap gap-2 mb-4">
              <span :class="getItemStatusBadgeClass(order.item_status)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                {{ getItemStatusDisplayName(order.item_status) }}
              </span>
              <span :class="getPaymentStatusBadgeClass(order.order_details?.payment_status)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                {{ getPaymentStatusDisplayName(order.order_details?.payment_status) }}
              </span>
            </div>

            <!-- Payment Method -->
            <div class="text-xs text-gray-500 mb-4">
              <span>{{ getPaymentMethodDisplayName(order.order_details?.payment_method?.payment_type) }}</span>
              <span class="mx-2">•</span>
              <span>Updated {{ formatRelativeTime(order.updated_at) }}</span>
            </div>

            <!-- Actions -->
            <div class="flex space-x-3">
              <button
                v-if="canAdvanceStatus(order)"
                @click="updateOrderStatus(order)"
                :disabled="updatingStatus === order.order_item_id || !canUpdateStatus(order)"
                :class="[
                  'flex-1 inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500',
                  canUpdateStatus(order) 
                    ? 'text-white bg-green-600 hover:bg-green-700' 
                    : 'text-gray-400 bg-gray-300 cursor-not-allowed'
                ]"
              >
                <ArrowRightIcon v-if="updatingStatus !== order.order_item_id" class="h-4 w-4 mr-2" />
                <div v-else class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                {{ getNextStatusButtonText(order.item_status) }}
              </button>
              
              <button
                @click="viewOrderDetails(order)"
                class="inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <EyeIcon class="h-4 w-4 mr-2" />
                View
              </button>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.total_pages > 1" class="bg-white rounded-lg shadow px-4 sm:px-6 py-3">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-700">
              <span class="hidden sm:inline">Showing {{ (pagination.current_page - 1) * pagination.page_size + 1 }} to 
              {{ Math.min(pagination.current_page * pagination.page_size, pagination.total_count) }} of </span>
              <span class="font-medium">{{ pagination.total_count }}</span> results
            </div>
            <div class="flex space-x-2">
              <button
                @click="goToPage(pagination.current_page - 1)"
                :disabled="pagination.current_page <= 1"
                class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                @click="goToPage(pagination.current_page + 1)"
                :disabled="pagination.current_page >= pagination.total_pages"
                class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Order Details Modal -->
    <OrderDetailsModal
      v-if="selectedOrder"
      :order="selectedOrder"
      @close="selectedOrder = null"
      @status-updated="handleStatusUpdate"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { farmerOrdersAPI } from '@/services/api'
import { debounce } from 'lodash-es'
import {
  ClockIcon,
  CheckCircleIcon,
  ArchiveBoxIcon,
  TruckIcon,
  ShoppingBagIcon,
  ExclamationTriangleIcon,
  ArrowRightIcon,
  EyeIcon
} from '@heroicons/vue/24/outline'
import OrderDetailsModal from '@/components/farmer/OrderDetailsModal.vue'

// State
const loading = ref(true)
const error = ref(null)
const orders = ref([])
const selectedOrder = ref(null)
const updatingStatus = ref(null)

const filters = ref({
  status: '',
  search: '',
  dateFrom: '',
  dateTo: ''
})

const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_count: 0,
  page_size: 20
})

// Computed
const orderCounts = computed(() => {
  const counts = { pending: 0, harvested: 0, packed: 0, delivered: 0 }
  orders.value.forEach(order => {
    if (counts.hasOwnProperty(order.item_status)) {
      counts[order.item_status]++
    }
  })
  return counts
})

// Methods
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatRelativeTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = Math.floor((now - date) / (1000 * 60 * 60))
  
  if (diffInHours < 1) return 'Just now'
  if (diffInHours < 24) return `${diffInHours}h ago`
  
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) return `${diffInDays}d ago`
  
  return formatDate(dateString)
}

const getItemStatusBadgeClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    harvested: 'bg-blue-100 text-blue-800',
    packed: 'bg-indigo-100 text-indigo-800',
    delivered: 'bg-green-100 text-green-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getItemStatusDisplayName = (status) => {
  const names = {
    pending: 'Pending',
    harvested: 'Harvested',
    packed: 'Packed',
    delivered: 'Delivered'
  }
  return names[status] || status
}

const getPaymentStatusBadgeClass = (status) => {
  const classes = {
    pending: 'bg-orange-100 text-orange-800',
    paid: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getPaymentStatusDisplayName = (status) => {
  const names = {
    pending: 'Payment Pending',
    paid: 'Payment Confirmed',
    failed: 'Payment Failed',
    cancelled: 'Payment Cancelled'
  }
  return names[status] || status || 'Unknown'
}

const getPaymentMethodDisplayName = (method) => {
  const names = {
    Mpesa: 'M-Pesa',
    CashOnDelivery: 'Cash on Delivery',
    BankTransfer: 'Bank Transfer'
  }
  return names[method] || method || 'Not Set'
}

const canAdvanceStatus = (order) => {
  return order.item_status !== 'delivered'
}

const canUpdateStatus = (order) => {
  const paymentMethod = order.order_details?.payment_method?.payment_type
  const paymentStatus = order.order_details?.payment_status
  const itemStatus = order.item_status
  
  // For non-cash orders, payment must be confirmed
  if (paymentMethod !== 'CashOnDelivery') {
    return paymentStatus === 'paid'
  }
  
  // For cash on delivery orders
  if (paymentMethod === 'CashOnDelivery') {
    // Can update up to packed without payment confirmation
    if (itemStatus === 'packed' && getNextStatus(itemStatus) === 'delivered') {
      // To mark as delivered, need delivery status to be delivered
      // Since we don't have delivery status in the order item, we'll allow it for now
      // The backend will validate this
      return true
    }
    return true
  }
  
  return false
}

const getStatusUpdateTooltip = (order) => {
  const paymentMethod = order.order_details?.payment_method?.payment_type
  const paymentStatus = order.order_details?.payment_status
  const itemStatus = order.item_status
  
  if (!canUpdateStatus(order)) {
    if (paymentMethod !== 'CashOnDelivery' && paymentStatus !== 'paid') {
      return 'Cannot update status until payment is confirmed'
    }
  }
  
  const nextStatus = getNextStatus(itemStatus)
  return nextStatus ? `Update to ${getItemStatusDisplayName(nextStatus)}` : 'Cannot advance further'
}

const getNextStatus = (currentStatus) => {
  const statusFlow = {
    pending: 'harvested',
    harvested: 'packed',
    packed: 'delivered'
  }
  return statusFlow[currentStatus]
}

const getNextStatusButtonText = (currentStatus) => {
  const nextStatus = getNextStatus(currentStatus)
  const statusTexts = {
    harvested: 'Mark Harvested',
    packed: 'Mark Packed',
    delivered: 'Mark Delivered'
  }
  return statusTexts[nextStatus] || 'Update Status'
}

const updateOrderStatus = async (order) => {
  const nextStatus = getNextStatus(order.item_status)
  if (!nextStatus) return

  // Double-check permissions before sending request
  if (!canUpdateStatus(order)) {
    const tooltip = getStatusUpdateTooltip(order)
    error.value = tooltip
    return
  }

  updatingStatus.value = order.order_item_id
  
  try {
    const updatedOrder = await farmerOrdersAPI.updateOrderItemStatus(order.order_item_id, nextStatus)
    
    // Update the order in the local list
    const orderIndex = orders.value.findIndex(o => o.order_item_id === order.order_item_id)
    if (orderIndex !== -1) {
      orders.value[orderIndex].item_status = nextStatus
      orders.value[orderIndex].updated_at = new Date().toISOString()
    }
    
    // Clear any previous errors
    error.value = null
    
  } catch (err) {
    console.error('Error updating order status:', err)
    
    // Handle specific error messages from backend validation
    const errorMessage = err.response?.data?.non_field_errors?.[0] || 
                         err.response?.data?.item_status?.[0] ||
                         err.response?.data?.detail || 
                         'Failed to update order status'
    
    error.value = errorMessage
    
    // Auto-clear error after 5 seconds
    setTimeout(() => {
      if (error.value === errorMessage) {
        error.value = null
      }
    }, 5000)
    
  } finally {
    updatingStatus.value = null
  }
}

const viewOrderDetails = (order) => {
  selectedOrder.value = order
}

const handleStatusUpdate = (updatedOrder) => {
  const orderIndex = orders.value.findIndex(o => o.order_item_id === updatedOrder.order_item_id)
  if (orderIndex !== -1) {
    orders.value[orderIndex] = updatedOrder
  }
}

const loadOrders = async (page = 1) => {
  loading.value = true
  error.value = null
  
  try {
    const params = {
      page,
      page_size: pagination.value.page_size,
      ordering: '-created_at'
    }
    
    if (filters.value.status) {
      params.item_status = filters.value.status
    }
    
    if (filters.value.search) {
      params.search = filters.value.search
    }
    
    if (filters.value.dateFrom) {
      params.created_at__gte = filters.value.dateFrom
    }
    
    if (filters.value.dateTo) {
      params.created_at__lte = filters.value.dateTo
    }
    
    const response = await farmerOrdersAPI.getOrderItems(params)
    
    if (Array.isArray(response)) {
      orders.value = response
      pagination.value = {
        current_page: 1,
        total_pages: 1,
        total_count: response.length,
        page_size: 20
      }
    } else {
      orders.value = response.results || []
      pagination.value = {
        current_page: page,
        total_pages: Math.ceil((response.count || 0) / pagination.value.page_size),
        total_count: response.count || 0,
        page_size: pagination.value.page_size
      }
    }
    
  } catch (err) {
    console.error('Error loading orders:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load orders'
  } finally {
    loading.value = false
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    loadOrders(page)
  }
}

const debouncedSearch = debounce(() => {
  loadOrders(1)
}, 500)

onMounted(() => {
  loadOrders()
})
</script>