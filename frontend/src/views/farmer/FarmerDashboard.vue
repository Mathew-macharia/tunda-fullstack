<template>
  <div class="min-h-screen bg-gray-50 py-4 sm:py-8">
    <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-6 sm:mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Farmer Dashboard</h1>
        <p class="mt-2 text-sm sm:text-base text-gray-600">Welcome back, {{ farmerName }}! Manage your farm, products, and orders</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
        <div class="flex">
          <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error loading dashboard</h3>
            <p class="mt-1 text-sm text-red-700">{{ error }}</p>
            <button 
              @click="loadDashboardData"
              class="mt-2 text-sm text-red-600 hover:text-red-500 underline"
            >
              Try again
            </button>
          </div>
        </div>
      </div>

      <div v-else>
        <!-- Statistics Cards -->
        <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
          <div class="bg-white rounded-lg shadow p-3 sm:p-6">
            <div class="flex items-center">
              <div class="p-2 sm:p-3 rounded-full bg-green-100">
                <CurrencyDollarIcon class="h-5 w-5 sm:h-6 sm:w-6 text-green-600" />
              </div>
              <div class="ml-3 sm:ml-4">
                <p class="text-xs sm:text-sm font-medium text-gray-500">Gross Revenue</p>
                <p class="text-lg sm:text-2xl font-semibold text-gray-900">KES {{ formatCurrency(earnings.gross_revenue) }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-3 sm:p-6">
            <div class="flex items-center">
              <div class="p-2 sm:p-3 rounded-full bg-blue-100">
                <ShoppingBagIcon class="h-5 w-5 sm:h-6 sm:w-6 text-blue-600" />
              </div>
              <div class="ml-3 sm:ml-4">
                <p class="text-xs sm:text-sm font-medium text-gray-500">Pending Orders</p>
                <p class="text-lg sm:text-2xl font-semibold text-gray-900">{{ dashboardStats.pendingOrders }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-3 sm:p-6">
            <div class="flex items-center">
              <div class="p-2 sm:p-3 rounded-full bg-purple-100">
                <ClipboardDocumentListIcon class="h-5 w-5 sm:h-6 sm:w-6 text-purple-600" />
              </div>
              <div class="ml-3 sm:ml-4">
                <p class="text-xs sm:text-sm font-medium text-gray-500">Active Listings</p>
                <p class="text-lg sm:text-2xl font-semibold text-gray-900">{{ dashboardStats.activeListings }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-3 sm:p-6">
            <div class="flex items-center">
              <div class="p-2 sm:p-3 rounded-full bg-yellow-100">
                <HomeIcon class="h-5 w-5 sm:h-6 sm:w-6 text-yellow-600" />
              </div>
              <div class="ml-3 sm:ml-4">
                <p class="text-xs sm:text-sm font-medium text-gray-500">Total Farms</p>
                <p class="text-lg sm:text-2xl font-semibold text-gray-900">{{ dashboardStats.totalFarms }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-8">
          <!-- Main Content -->
          <div class="lg:col-span-2 space-y-4 sm:space-y-8">
            <!-- Quick Actions -->
            <div class="bg-white rounded-lg shadow p-4 sm:p-6">
              <h2 class="text-lg sm:text-xl font-semibold text-gray-900 mb-4 sm:mb-6">Quick Actions</h2>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <router-link to="/farmer/listings/create" class="group relative bg-green-50 p-4 sm:p-6 rounded-lg border-2 border-dashed border-green-300 hover:border-green-400 transition-colors">
                  <div class="flex items-center">
                    <PlusIcon class="h-6 w-6 sm:h-8 sm:w-8 text-green-600" />
                    <div class="ml-3 sm:ml-4">
                      <p class="text-base sm:text-lg font-medium text-gray-900">Add New Product</p>
                      <p class="text-xs sm:text-sm text-gray-500">Create a new product listing</p>
                    </div>
                  </div>
                </router-link>

                <router-link to="/farmer/orders" class="group relative bg-blue-50 p-4 sm:p-6 rounded-lg border-2 border-dashed border-blue-300 hover:border-blue-400 transition-colors">
                  <div class="flex items-center">
                    <ClipboardDocumentListIcon class="h-6 w-6 sm:h-8 sm:w-8 text-blue-600" />
                    <div class="ml-3 sm:ml-4">
                      <p class="text-base sm:text-lg font-medium text-gray-900">Manage Orders</p>
                      <p class="text-xs sm:text-sm text-gray-500">View and update order status</p>
                    </div>
                  </div>
                </router-link>

                <router-link to="/farmer/farms" class="group relative bg-purple-50 p-4 sm:p-6 rounded-lg border-2 border-dashed border-purple-300 hover:border-purple-400 transition-colors">
                  <div class="flex items-center">
                    <HomeIcon class="h-6 w-6 sm:h-8 sm:w-8 text-purple-600" />
                    <div class="ml-3 sm:ml-4">
                      <p class="text-base sm:text-lg font-medium text-gray-900">Manage Farms</p>
                      <p class="text-xs sm:text-sm text-gray-500">Update farm information</p>
                    </div>
                  </div>
                </router-link>

                <router-link to="/farmer/listings" class="group relative bg-orange-50 p-4 sm:p-6 rounded-lg border-2 border-dashed border-orange-300 hover:border-orange-400 transition-colors">
                  <div class="flex items-center">
                    <ListBulletIcon class="h-6 w-6 sm:h-8 sm:w-8 text-orange-600" />
                    <div class="ml-3 sm:ml-4">
                      <p class="text-base sm:text-lg font-medium text-gray-900">View Products</p>
                      <p class="text-xs sm:text-sm text-gray-500">Manage product listings</p>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>

            <!-- Recent Orders -->
            <div class="bg-white rounded-lg shadow">
              <div class="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 class="text-lg sm:text-xl font-semibold text-gray-900">Recent Orders</h2>
                <router-link to="/farmer/orders" class="text-green-600 hover:text-green-500 text-sm font-medium">
                  View All
                </router-link>
              </div>

              <div v-if="recentOrders.length === 0" class="p-4 sm:p-6 text-center text-gray-500">
                <ShoppingBagIcon class="mx-auto h-10 sm:h-12 w-10 sm:w-12 text-gray-400 mb-3 sm:mb-4" />
                <p>No recent orders found</p>
                <p class="text-sm">Start by creating product listings to receive orders.</p>
              </div>

              <div v-else class="divide-y divide-gray-200">
                <div
                  v-for="order in recentOrders"
                  :key="order.order_item_id"
                  class="px-4 sm:px-6 py-3 sm:py-4 hover:bg-gray-50"
                >
                  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
                    <div class="flex items-center space-x-3 sm:space-x-4">
                      <img 
                        :src="order.listing_details?.photos?.[0] || '/api/placeholder/40/40'"
                        :alt="order.listing_details?.product_name"
                        class="h-10 w-10 rounded-lg object-cover"
                      />
                      <div>
                        <p class="text-sm font-medium text-gray-900">
                          {{ order.listing_details?.product_name }}
                        </p>
                        <p class="text-xs sm:text-sm text-gray-500">
                          Order #{{ order.order?.order_number }}
                        </p>
                        <p class="text-xs text-gray-400">
                          {{ formatDate(order.created_at) }}
                        </p>
                      </div>
                    </div>
                    
                    <div class="flex items-center justify-between sm:justify-end sm:space-x-3">
                      <div class="text-right">
                        <p class="text-sm font-medium text-gray-900">
                          {{ order.quantity }} {{ order.listing_details?.product_unit }}
                        </p>
                        <p class="text-xs sm:text-sm text-gray-500">
                          KES {{ formatCurrency(order.total_price) }}
                        </p>
                      </div>
                      <span :class="getOrderItemStatusClass(order.item_status)" class="px-2 sm:px-3 py-1 rounded-full text-xs font-medium">
                        {{ formatOrderItemStatus(order.item_status) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Top Products -->
            <div class="bg-white rounded-lg shadow">
              <div class="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 class="text-lg sm:text-xl font-semibold text-gray-900">Your Product Listings</h2>
                <router-link to="/farmer/listings" class="text-green-600 hover:text-green-500 text-sm font-medium">
                  View All
                </router-link>
              </div>

              <div v-if="recentListings.length === 0" class="p-4 sm:p-6 text-center text-gray-500">
                <ClipboardDocumentListIcon class="mx-auto h-10 sm:h-12 w-10 sm:w-12 text-gray-400 mb-3 sm:mb-4" />
                <p>No product listings found</p>
                <router-link 
                  to="/farmer/listings/create"
                  class="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                >
                  Create Your First Listing
                </router-link>
              </div>

              <div v-else class="divide-y divide-gray-200">
                <div
                  v-for="listing in recentListings"
                  :key="listing.listing_id"
                  class="px-4 sm:px-6 py-3 sm:py-4"
                >
                  <div class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
                    <img 
                      :src="listing.photos?.[0] || '/api/placeholder/40/40'"
                      :alt="listing.product_name"
                      class="h-10 w-10 rounded-lg object-cover"
                    />
                    
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 truncate">
                        {{ listing.product_name }}
                      </p>
                      <p class="text-xs sm:text-sm text-gray-500">
                        {{ listing.farm_name }} • KES {{ formatCurrency(listing.current_price) }}/{{ listing.product_unit }}
                      </p>
                    </div>
                    
                    <div class="flex items-center justify-between sm:text-right">
                      <p class="text-sm font-medium text-gray-900">
                        {{ listing.quantity_available }} {{ listing.product_unit }}
                      </p>
                      <span :class="getListingStatusClass(listing.listing_status)" class="ml-2 inline-flex items-center px-2 sm:px-2.5 py-0.5 rounded-full text-xs font-medium">
                        {{ formatListingStatus(listing.listing_status) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="space-y-4 sm:space-y-8">
            <!-- Farm Overview -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-xl font-semibold text-gray-900 mb-6">Your Farms</h2>
              
              <div v-if="farms.length > 0" class="space-y-4">
                <div 
                  v-for="farm in farms.slice(0, 3)" 
                  :key="farm.farm_id"
                  class="border border-gray-200 rounded-lg p-4"
                >
                  <div class="flex items-center justify-between mb-2">
                    <p class="text-sm font-medium text-gray-900">{{ farm.farm_name }}</p>
                    <span v-if="farm.is_certified_organic" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                      Organic
                    </span>
                  </div>
                  <p class="text-xs text-gray-500">{{ farm.location_name }}</p>
                  <p class="text-xs text-gray-500">{{ farm.total_acreage }} acres</p>
                </div>
                
                <router-link 
                  to="/farmer/farms"
                  class="block text-center text-sm text-green-600 hover:text-green-500 py-2"
                >
                  View all farms
                </router-link>
              </div>
              
              <div v-else class="text-center">
                <HomeIcon class="mx-auto h-12 w-12 text-gray-400" />
                <p class="mt-2 text-sm text-gray-500">No farms registered</p>
            <router-link to="/farmer/farms" class="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700">
                  Create Farm Profile
                </router-link>
              </div>
            </div>

            <!-- Order Status Summary -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-xl font-semibold text-gray-900 mb-6">Order Status</h2>
              
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Pending</span>
                  <span class="text-sm font-medium text-yellow-600">{{ orderStatusCounts.pending }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Harvested</span>
                  <span class="text-sm font-medium text-blue-600">{{ orderStatusCounts.harvested }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Packed</span>
                  <span class="text-sm font-medium text-indigo-600">{{ orderStatusCounts.packed }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Delivered</span>
                  <span class="text-sm font-medium text-green-600">{{ orderStatusCounts.delivered }}</span>
                </div>
              </div>
            </div>

            <!-- Financial Overview -->
            <div class="bg-white rounded-lg shadow">
              <div class="p-6">
                <h2 class="text-xl font-semibold text-gray-900 mb-6">Financial Overview</h2>
                
                <!-- Balance Information -->
                <div>
                  <h3 class="text-sm font-medium text-gray-500 mb-4">Balance Information</h3>
                  
                  <div class="space-y-3">
                    <div class="flex justify-between">
                      <div class="flex items-center">
                        <span class="text-gray-900">Available Balance</span>
                        <QuestionMarkCircleIcon
                          class="h-4 w-4 text-gray-400 ml-1.5 cursor-help"
                          @mouseenter="showTooltip('availableBalance')"
                          @mouseleave="hideTooltip"
                        />
                      </div>
                      <span class="text-green-600 font-medium">KES {{ formatCurrency(earnings.available_balance) }}</span>
                    </div>

                    <div class="flex justify-between">
                      <div class="flex items-center">
                        <span class="text-gray-900">Pending Balance</span>
                        <QuestionMarkCircleIcon
                          class="h-4 w-4 text-gray-400 ml-1.5 cursor-help"
                          @mouseenter="showTooltip('pendingBalance')"
                          @mouseleave="hideTooltip"
                        />
                      </div>
                      <span class="text-yellow-600 font-medium">KES {{ formatCurrency(earnings.pending_balance) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Payout Request Button -->
                <button
                  v-if="earnings.available_balance > 0"
                  @click="showPayoutModalHandler"
                  class="mt-6 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  Request Payout
                </button>
                <p v-else class="mt-6 text-sm text-center text-gray-500">
                  No funds available for payout
                </p>

                <!-- Revenue Breakdown -->
                <div class="mt-8">
                  <h3 class="text-sm font-medium text-gray-500 mb-4">Revenue Breakdown</h3>
                  
                  <div class="space-y-3">
                    <div class="flex justify-between">
                      <div class="flex items-center">
                        <span class="font-medium text-gray-900">Net Proceeds</span>
                        <QuestionMarkCircleIcon
                          class="h-4 w-4 text-gray-400 ml-1.5 cursor-help"
                          @mouseenter="showTooltip('netProceeds')"
                          @mouseleave="hideTooltip"
                        />
                      </div>
                      <span class="text-green-600 font-medium">KES {{ formatCurrency(earnings.net_revenue) }}</span>
                    </div>

                    <div class="pt-3 border-t">
                      <div class="flex justify-between">
                        <div class="flex items-center">
                          <span class="text-gray-900">Gross Revenue</span>
                          <QuestionMarkCircleIcon
                            class="h-4 w-4 text-gray-400 ml-1.5 cursor-help"
                            @mouseenter="showTooltip('grossRevenue')"
                            @mouseleave="hideTooltip"
                          />
                        </div>
                        <span class="text-gray-900 font-medium">KES {{ formatCurrency(earnings.gross_revenue) }}</span>
                      </div>
                    </div>

                    <div class="flex justify-between text-gray-500">
                      <div class="flex items-center">
                        <span>Service Fee</span>
                        <QuestionMarkCircleIcon
                          class="h-4 w-4 text-gray-400 ml-1.5 cursor-help"
                          @mouseenter="showTooltip('platformFee')"
                          @mouseleave="hideTooltip"
                        />
                      </div>
                      <span class="text-red-600">-KES {{ formatCurrency(earnings.fees.platform_fee) }}</span>
                    </div>

                    <div class="flex justify-between text-gray-500">
                      <div class="flex items-center">
                        <span>VAT on Service Fee</span>
                        <QuestionMarkCircleIcon
                          class="h-4 w-4 text-gray-400 ml-1.5 cursor-help"
                          @mouseenter="showTooltip('vat')"
                          @mouseleave="hideTooltip"
                        />
                      </div>
                      <span class="text-red-600">-KES {{ formatCurrency(earnings.fees.vat) }}</span>
                    </div>

                    <div class="flex justify-between text-gray-500">
                      <div class="flex items-center">
                        <span>Transaction Fee</span>
                        <QuestionMarkCircleIcon
                          class="h-4 w-4 text-gray-400 ml-1.5 cursor-help"
                          @mouseenter="showTooltip('transactionFee')"
                          @mouseleave="hideTooltip"
                        />
                      </div>
                      <span class="text-red-600">-KES {{ formatCurrency(earnings.fees.transaction_fee) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tooltip -->
            <div
              v-if="tooltipVisible"
              class="absolute z-10 w-72 px-4 py-3 bg-gray-900 text-white text-sm rounded-lg shadow-lg"
              :style="tooltipStyle"
            >
              {{ tooltipContent }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Payout Request Modal -->
  <PayoutRequestModal
    :show="showPayoutModal"
    :availableBalance="earnings.available_balance"
    @close="closePayoutModal"
    @payoutRequested="handlePayoutRequested"
  />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { user } from '@/stores/auth'
import { 
  farmsAPI, 
  productsAPI, 
  farmerOrdersAPI,
  financeAPI
} from '@/services/api'
import {
  PlusIcon,
  HomeIcon,
  ShoppingBagIcon,
  ClockIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  ClipboardDocumentListIcon,
  ListBulletIcon,
  QuestionMarkCircleIcon
} from '@heroicons/vue/24/outline'
import { useToast } from 'vue-toastification'
import PayoutRequestModal from '@/components/farmer/PayoutRequestModal.vue'

// State
const loading = ref(true)
const error = ref(null)
const farms = ref([])
const recentOrders = ref([])
const recentListings = ref([])
const showPayoutModal = ref(false) // Control payout modal visibility

const dashboardStats = ref({
  totalRevenue: 0,
  pendingOrders: 0,
  activeListings: 0,
  totalFarms: 0
})

const orderStatusCounts = ref({
  pending: 0,
  harvested: 0,
  packed: 0,
  delivered: 0
})

const monthlyStats = ref({
  grossRevenue: 0,
  platformFee: 0,
  netRevenue: 0,
  ordersCompleted: 0,
  productsSold: 0,
  availableBalance: 0,
  pendingBalance: 0
})

const earnings = ref({
  gross_revenue: 0,
  fees: {
    vat: 0,
    transaction_fee: 0,
    platform_fee: 0,
    total_fees: 0
  },
  net_revenue: 0,
  available_balance: 0,
  pending_balance: 0
})

const toast = useToast()
const tooltipContent = ref('')
const tooltipVisible = ref(false)
const tooltipStyle = ref({ top: '0px', left: '0px' })
const tooltipMessages = ref({
  grossRevenue: 'Total value of all completed orders before fees and deductions',
  vat: 'Value Added Tax (16%) collected on behalf of KRA',
  transactionFee: 'Payment processing fee (2%) for handling transactions',
  platformFee: 'Platform usage fee (10%) for marketing, support, and maintenance',
  netProceeds: 'Final amount after deducting all fees and taxes',
  availableBalance: 'Funds available for withdrawal (from orders older than 48 hours)',
  pendingBalance: 'Funds from recent orders (less than 48 hours old) not yet available for withdrawal'
})

// Computed
const farmerName = computed(() => {
  return user.value?.first_name || user.value?.phone_number || 'Farmer'
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
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatOrderItemStatus = (status) => {
  const statusMap = {
    'pending': 'Pending',
    'harvested': 'Harvested',
    'packed': 'Packed',
    'delivered': 'Delivered'
  }
  return statusMap[status] || status
}

const getOrderItemStatusClass = (status) => {
  const statusClasses = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'harvested': 'bg-blue-100 text-blue-800',
    'packed': 'bg-indigo-100 text-indigo-800',
    'delivered': 'bg-green-100 text-green-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const formatListingStatus = (status) => {
  const statusMap = {
    'available': 'Available',
    'pre_order': 'Pre-Order',
    'sold_out': 'Sold Out',
    'inactive': 'Inactive'
  }
  return statusMap[status] || status
}

const getListingStatusClass = (status) => {
  const statusClasses = {
    'available': 'bg-green-100 text-green-800',
    'pre_order': 'bg-blue-100 text-blue-800',
    'sold_out': 'bg-red-100 text-red-800',
    'inactive': 'bg-gray-100 text-gray-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const loadDashboardData = async () => {
  loading.value = true
  error.value = null
  
  try {
    await Promise.all([
      loadFarms(),
      loadRecentOrders(),
      loadRecentListings(),
      loadStats()
    ])
  } catch (err) {
    console.error('Error loading dashboard data:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load dashboard data'
  } finally {
    loading.value = false
  }
}

const loadFarms = async () => {
  try {
    const response = await farmsAPI.getFarms()
    farms.value = Array.isArray(response) ? response : response.results || []
  } catch (err) {
    console.error('Error loading farms:', err)
  }
}

const loadRecentOrders = async () => {
  try {
    const response = await farmerOrdersAPI.getOrderItems({ ordering: '-created_at' })
    const orders = Array.isArray(response) ? response : response.results || []
    recentOrders.value = orders.slice(0, 5)
    
    // Calculate order status counts
    const counts = { pending: 0, harvested: 0, packed: 0, delivered: 0 }
    orders.forEach(order => {
      if (counts.hasOwnProperty(order.item_status)) {
        counts[order.item_status]++
      }
    })
    orderStatusCounts.value = counts
    
  } catch (err) {
    console.error('Error loading recent orders:', err)
  }
}

const loadRecentListings = async () => {
  try {
    const response = await productsAPI.getMyListings({ ordering: '-created_at' })
    const listings = Array.isArray(response) ? response : response.results || []
    recentListings.value = listings.slice(0, 5)
  } catch (err) {
    console.error('Error loading recent listings:', err)
  }
}

const loadStats = async () => {
  // Define default rates at a higher scope
  const defaultVatRate = 0.16;
  const defaultTransactionFeeRate = 0.015; // Updated to 1.5%
  const defaultPlatformFeeRate = 0.10;

  try {
    // Calculate total revenue from orders
    const ordersResponse = await farmerOrdersAPI.getOrderItems()
    const orders = Array.isArray(ordersResponse) ? ordersResponse : ordersResponse.results || []
    
    const totalRevenue = orders.reduce((sum, order) => sum + (parseFloat(order.total_price) || 0), 0)
    const pendingOrders = orders.filter(o => o.item_status === 'pending').length
    
    // Get listings stats
    const listingsResponse = await productsAPI.getMyListings()
    const listings = Array.isArray(listingsResponse) ? listingsResponse : listingsResponse.results || []
    const activeListings = listings.filter(l => l.listing_status === 'available' || l.listing_status === 'pre_order').length
    
    dashboardStats.value = {
      totalRevenue,
      pendingOrders,
      activeListings,
      totalFarms: farms.value.length
    }
    
    // Get earnings data
    try {
      const earningsResponse = await financeAPI.getFarmerEarnings()
      earnings.value = earningsResponse
    } catch (err) {
      console.error('Error loading earnings:', err)
      // Set default values if earnings fetch fails
      // Use the new rates for fallback calculations
      const defaultPlatformFeeAmount = totalRevenue * defaultPlatformFeeRate;
      const defaultVatAmount = defaultPlatformFeeAmount * defaultVatRate; // VAT on Platform Fee
      const defaultTransactionFeeAmount = totalRevenue * defaultTransactionFeeRate;
      const defaultTotalFees = defaultPlatformFeeAmount + defaultVatAmount + defaultTransactionFeeAmount;
      const defaultNetRevenue = totalRevenue - defaultTotalFees;

      earnings.value = {
        gross_revenue: totalRevenue,
        fees: {
          vat: defaultVatAmount,
          transaction_fee: defaultTransactionFeeAmount,
          platform_fee: defaultPlatformFeeAmount,
          total_fees: defaultTotalFees
        },
        net_revenue: defaultNetRevenue,
        available_balance: 0,
        pending_balance: 0
      }
    }
    
    // Calculate monthly stats (current month)
    const currentMonth = new Date().getMonth()
    const currentYear = new Date().getFullYear()
    
    const monthlyOrders = orders.filter(order => {
      const orderDate = new Date(order.created_at)
      return orderDate.getMonth() === currentMonth && orderDate.getFullYear() === currentYear
    })
    
    // Recalculate monthly stats with new logic for fees
    const monthlyGrossRevenue = monthlyOrders.reduce((sum, order) => sum + (parseFloat(order.total_price) || 0), 0);
    const monthlyPlatformFee = monthlyGrossRevenue * defaultPlatformFeeRate;
    const monthlyVat = monthlyPlatformFee * defaultVatRate;
    const monthlyTransactionFee = monthlyGrossRevenue * defaultTransactionFeeRate;
    const monthlyNetRevenue = monthlyGrossRevenue - (monthlyPlatformFee + monthlyVat + monthlyTransactionFee);

    monthlyStats.value = {
      grossRevenue: monthlyGrossRevenue,
      platformFee: monthlyPlatformFee,
      netRevenue: monthlyNetRevenue,
      ordersCompleted: monthlyOrders.filter(o => o.item_status === 'delivered').length,
      productsSold: monthlyOrders.reduce((sum, order) => sum + (parseFloat(order.quantity) || 0), 0),
      availableBalance: earnings.value.available_balance,
      pendingBalance: earnings.value.pending_balance
    }
    
  } catch (err) {
    console.error('Error loading stats:', err)
  }
}

const showPayoutModalHandler = () => {
  showPayoutModal.value = true
}

const closePayoutModal = () => {
  showPayoutModal.value = false
}

const handlePayoutRequested = async () => {
  await loadDashboardData() // Reload data after a payout request
}

const showTooltip = (key, event) => {
  tooltipContent.value = tooltipMessages.value[key]
  tooltipVisible.value = true
  // Position tooltip near the cursor
  tooltipStyle.value = {
    top: `${event.clientY + 10}px`,
    left: `${event.clientX + 10}px`
  }
}

const hideTooltip = () => {
  tooltipVisible.value = false
}

onMounted(() => {
  loadDashboardData()
})
</script>
