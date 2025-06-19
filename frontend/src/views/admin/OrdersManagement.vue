<template>
  <div class="min-h-screen bg-gray-50 py-4 sm:py-8">
    <div class="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
      <!-- Header -->
      <div class="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0 mb-6 sm:mb-8">
        <div class="min-w-0 flex-1">
          <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Orders Management</h1>
          <p class="mt-1 sm:mt-2 text-sm sm:text-base text-gray-600">Manage all orders in the system</p>
        </div>
        <div class="flex flex-col space-y-2 sm:flex-row sm:space-y-0 sm:space-x-3 sm:ml-4">
          <button
            @click="exportOrders"
            class="inline-flex items-center justify-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <DocumentArrowDownIcon class="-ml-1 mr-2 h-4 w-4 sm:h-5 sm:w-5" />
            Export Orders
          </button>
          <button
            @click="refreshData"
            class="inline-flex items-center justify-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            <ArrowPathIcon class="-ml-1 mr-2 h-4 w-4 sm:h-5 sm:w-5" />
            Refresh
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
        <div class="bg-white overflow-hidden shadow-sm rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <ShoppingBagIcon class="h-5 w-5 sm:h-6 sm:w-6 text-gray-400" />
              </div>
              <div class="ml-3 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Total Orders</dt>
                  <dd class="text-base sm:text-lg font-medium text-gray-900">{{ orderStats.orders?.total || 0 }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow-sm rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <ClockIcon class="h-5 w-5 sm:h-6 sm:w-6 text-yellow-400" />
              </div>
              <div class="ml-3 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Pending</dt>
                  <dd class="text-base sm:text-lg font-medium text-gray-900">{{ orderStats.orders?.pending || 0 }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow-sm rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <CheckCircleIcon class="h-5 w-5 sm:h-6 sm:w-6 text-green-400" />
              </div>
              <div class="ml-3 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Delivered</dt>
                  <dd class="text-base sm:text-lg font-medium text-gray-900">{{ orderStats.orders?.delivered || 0 }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow-sm rounded-lg col-span-2 lg:col-span-1">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <CurrencyDollarIcon class="h-5 w-5 sm:h-6 sm:w-6 text-green-400" />
              </div>
              <div class="ml-3 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Total Revenue</dt>
                  <dd class="text-base sm:text-lg font-medium text-gray-900">KES {{ formatCurrency(orderStats.revenue?.total || 0) }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white shadow-sm rounded-lg p-4 sm:p-6 mb-4 sm:mb-6">
        <!-- Mobile: Collapsible Filters -->
        <div class="sm:hidden">
          <button
            @click="showMobileFilters = !showMobileFilters"
            class="w-full flex items-center justify-between px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <span>Filters</span>
            <svg 
              :class="{ 'rotate-180': showMobileFilters }"
              class="h-5 w-5 transform transition-transform"
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <div v-show="showMobileFilters" class="mt-4 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
              <input
                v-model="filters.search"
                type="text"
                placeholder="Search orders..."
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                @input="debouncedFilter"
              />
            </div>
            
            <div class="grid grid-cols-1 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Order Status</label>
                <select
                  v-model="filters.order_status"
                  @change="applyFilters"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                >
                  <option value="">All Status</option>
                  <option value="pending">Pending</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="processing">Processing</option>
                  <option value="out_for_delivery">Out for Delivery</option>
                  <option value="delivered">Delivered</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Payment Status</label>
                <select
                  v-model="filters.payment_status"
                  @change="applyFilters"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                >
                  <option value="">All Status</option>
                  <option value="pending">Pending</option>
                  <option value="paid">Paid</option>
                  <option value="failed">Failed</option>
                  <option value="refunded">Refunded</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Customer Type</label>
                <select
                  v-model="filters.customer_role"
                  @change="applyFilters"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                >
                  <option value="">All Customers</option>
                  <option value="customer">Customer</option>
                  <option value="farmer">Farmer</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
                <select
                  v-model="filters.date_range"
                  @change="applyFilters"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                >
                  <option value="">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                  <option value="year">This Year</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- Desktop: Regular Filters -->
        <div class="hidden sm:grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              v-model="filters.search"
              type="text"
              placeholder="Search orders..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              @input="debouncedFilter"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Order Status</label>
            <select
              v-model="filters.order_status"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="confirmed">Confirmed</option>
              <option value="processing">Processing</option>
              <option value="out_for_delivery">Out for Delivery</option>
              <option value="delivered">Delivered</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Payment Status</label>
            <select
              v-model="filters.payment_status"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="paid">Paid</option>
              <option value="failed">Failed</option>
              <option value="refunded">Refunded</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Customer Type</label>
            <select
              v-model="filters.customer_role"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Customers</option>
              <option value="customer">Customer</option>
              <option value="farmer">Farmer</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
            <select
              v-model="filters.date_range"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="year">This Year</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-10 w-10 sm:h-12 sm:w-12 border-b-2 border-indigo-600"></div>
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

      <!-- Orders Content -->
      <div v-else>
        <!-- Mobile: Card Layout -->
        <div class="sm:hidden space-y-4">
          <div
            v-for="order in orders"
            :key="order.order_id"
            class="bg-white shadow-sm rounded-lg border border-gray-200"
          >
            <div class="p-4">
              <div class="flex items-center justify-between mb-3">
                <div>
                  <h3 class="text-sm font-semibold text-gray-900">#{{ order.order_number }}</h3>
                  <p class="text-xs text-gray-500">{{ order.items?.length || 0 }} items</p>
                </div>
                <div class="text-right">
                  <p class="text-sm font-medium text-gray-900">KES {{ formatCurrency(order.total_amount) }}</p>
                  <p class="text-xs text-gray-500">{{ formatDate(order.created_at) }}</p>
                </div>
              </div>
              
              <div class="mb-3">
                <p class="text-sm font-medium text-gray-900">
                  {{ order.customer?.first_name }} {{ order.customer?.last_name }}
                </p>
                <p class="text-xs text-gray-500">{{ order.customer?.phone_number }}</p>
              </div>
              
              <div class="flex items-center justify-between mb-4">
                <div class="flex flex-col space-y-1">
                  <span :class="getOrderStatusClass(order.order_status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full w-fit">
                    {{ formatOrderStatus(order.order_status) }}
                  </span>
                  <span :class="getPaymentStatusClass(order.payment_status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full w-fit">
                    {{ formatPaymentStatus(order.payment_status) }}
                  </span>
                </div>
              </div>
              
              <div class="flex justify-end space-x-3 pt-3 border-t border-gray-100">
                <button
                  @click="viewOrder(order)"
                  class="flex items-center px-3 py-1.5 text-xs font-medium text-indigo-600 hover:text-indigo-700 border border-indigo-200 rounded-md hover:bg-indigo-50"
                >
                  <EyeIcon class="h-3 w-3 mr-1" />
                  View
                </button>
                <button
                  @click="editOrderStatus(order)"
                  class="flex items-center px-3 py-1.5 text-xs font-medium text-green-600 hover:text-green-700 border border-green-200 rounded-md hover:bg-green-50"
                >
                  <PencilIcon class="h-3 w-3 mr-1" />
                  Status
                </button>
                <button
                  @click="editPaymentStatus(order)"
                  class="flex items-center px-3 py-1.5 text-xs font-medium text-yellow-600 hover:text-yellow-700 border border-yellow-200 rounded-md hover:bg-yellow-50"
                >
                  <CurrencyDollarIcon class="h-3 w-3 mr-1" />
                  Payment
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Desktop: Table Layout -->
        <div class="hidden sm:block bg-white shadow-sm overflow-hidden rounded-lg">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Order
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Payment
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="order in orders" :key="order.order_id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">
                      #{{ order.order_number }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ order.items?.length || 0 }} items
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">
                      {{ order.customer?.first_name }} {{ order.customer?.last_name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ order.customer?.phone_number }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="getOrderStatusClass(order.order_status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                      {{ formatOrderStatus(order.order_status) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="getPaymentStatusClass(order.payment_status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                      {{ formatPaymentStatus(order.payment_status) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    KES {{ formatCurrency(order.total_amount) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDate(order.created_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex justify-end space-x-2">
                      <button
                        @click="viewOrder(order)"
                        class="text-indigo-600 hover:text-indigo-900"
                        title="View Details"
                      >
                        <EyeIcon class="h-4 w-4" />
                      </button>
                      <button
                        @click="editOrderStatus(order)"
                        class="text-green-600 hover:text-green-900"
                        title="Update Status"
                      >
                        <PencilIcon class="h-4 w-4" />
                      </button>
                      <button
                        @click="editPaymentStatus(order)"
                        class="text-yellow-600 hover:text-yellow-900"
                        title="Update Payment"
                      >
                        <CurrencyDollarIcon class="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-4 sm:mt-0 rounded-b-lg sm:rounded-b-none">
          <!-- Mobile Pagination -->
          <div class="flex-1 flex justify-between sm:hidden">
            <button
              @click="changePage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="relative inline-flex items-center px-3 py-2 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <div class="flex items-center space-x-1">
              <span class="text-xs text-gray-700">
                Page {{ currentPage }} of {{ totalPages }}
              </span>
            </div>
            <button
              @click="changePage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="relative inline-flex items-center px-3 py-2 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
          
          <!-- Desktop Pagination -->
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalOrders) }} of {{ totalOrders }} results
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  @click="changePage(page)"
                  :class="currentPage === page ? 'bg-indigo-50 border-indigo-500 text-indigo-600' : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'"
                  class="relative inline-flex items-center px-4 py-2 border text-sm font-medium first:rounded-l-md last:rounded-r-md"
                >
                  {{ page }}
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Order Details Modal -->
    <OrderDetailsModal
      v-if="showDetailsModal"
      :order="selectedOrder"
      @close="closeDetailsModal"
      @update-status="handleModalAction"
    />

    <!-- Order Status Update Modal -->
    <OrderStatusModal
      v-if="showStatusModal"
      :order="selectedOrder"
      @close="showStatusModal = false"
      @save="handleStatusUpdate"
    />

    <!-- Payment Status Update Modal -->
    <PaymentStatusModal
      v-if="showPaymentModal"
      :order="selectedOrder"
      @close="showPaymentModal = false"
      @save="handlePaymentUpdate"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { adminOrdersAPI } from '@/services/api'
import {
  DocumentArrowDownIcon,
  ArrowPathIcon,
  ShoppingBagIcon,
  ClockIcon,
  CheckCircleIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  PencilIcon
} from '@heroicons/vue/24/outline'
import OrderDetailsModal from '@/components/admin/OrderDetailsModal.vue'
import OrderStatusModal from '@/components/admin/OrderStatusModal.vue'
import PaymentStatusModal from '@/components/admin/PaymentStatusModal.vue'

// State
const loading = ref(true)
const error = ref(null)
const orders = ref([])
const selectedOrder = ref(null)
const showDetailsModal = ref(false)
const showStatusModal = ref(false)
const showPaymentModal = ref(false)
const showMobileFilters = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const totalOrders = ref(0)
const pageSize = 20

// Order Statistics
const orderStats = ref({
  orders: {},
  payments: {},
  revenue: {}
})

// Filters
const filters = ref({
  search: '',
  order_status: '',
  payment_status: '',
  customer_role: '',
  date_range: ''
})

// Computed
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// Methods
const loadOrders = async () => {
  loading.value = true
  error.value = null
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize,
      ordering: '-created_at'
    }
    
    // Apply filters
    Object.keys(filters.value).forEach(key => {
      if (filters.value[key]) {
        params[key] = filters.value[key]
      }
    })
    
    const response = await adminOrdersAPI.getOrders(params)
    
    if (response.results) {
      orders.value = response.results
      totalPages.value = Math.ceil(response.count / pageSize)
      totalOrders.value = response.count
    } else {
      orders.value = Array.isArray(response) ? response : []
    }
    
    await loadOrderStats()
    
  } catch (err) {
    console.error('Error loading orders:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load orders'
  } finally {
    loading.value = false
  }
}

const loadOrderStats = async () => {
  try {
    const response = await adminOrdersAPI.getOrderStats()
    orderStats.value = response
  } catch (err) {
    console.error('Error loading order stats:', err)
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatOrderStatus = (status) => {
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
    'pending': 'Pending',
    'paid': 'Paid',
    'failed': 'Failed',
    'refunded': 'Refunded'
  }
  return statusMap[status] || status
}

const getOrderStatusClass = (status) => {
  const statusClasses = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'confirmed': 'bg-blue-100 text-blue-800',
    'processing': 'bg-indigo-100 text-indigo-800',
    'out_for_delivery': 'bg-purple-100 text-purple-800',
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
    'refunded': 'bg-orange-100 text-orange-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const viewOrder = (order) => {
  selectedOrder.value = order
  showDetailsModal.value = true
}

const editOrderStatus = (order) => {
  selectedOrder.value = order
  showStatusModal.value = true
}

const editPaymentStatus = (order) => {
  selectedOrder.value = order
  showPaymentModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedOrder.value = null
}

const handleModalAction = (type, order) => {
  if (type === 'status') {
    editOrderStatus(order)
  } else if (type === 'payment') {
    editPaymentStatus(order)
  }
}

const handleStatusUpdate = async (orderId, newStatus) => {
  try {
    await adminOrdersAPI.updateOrderStatus(orderId, newStatus)
    showStatusModal.value = false
    showDetailsModal.value = false
    await loadOrders()
  } catch (err) {
    console.error('Error updating order status:', err)
    error.value = 'Failed to update order status'
  }
}

const handlePaymentUpdate = async (orderId, newStatus) => {
  try {
    await adminOrdersAPI.updatePaymentStatus(orderId, newStatus)
    showPaymentModal.value = false
    showDetailsModal.value = false
    await loadOrders()
  } catch (err) {
    console.error('Error updating payment status:', err)
    error.value = 'Failed to update payment status'
  }
}

const exportOrders = async () => {
  try {
    const response = await adminOrdersAPI.exportOrders(filters.value)
    // Handle CSV download
    const blob = new Blob([response], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `orders_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Error exporting orders:', err)
    error.value = 'Failed to export orders'
  }
}

const refreshData = () => {
  loadOrders()
}

const applyFilters = () => {
  currentPage.value = 1
  loadOrders()
}

// Debounced search
let searchTimeout
const debouncedFilter = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(applyFilters, 500)
}

const changePage = (page) => {
  currentPage.value = page
  loadOrders()
}

onMounted(() => {
  loadOrders()
})
</script>