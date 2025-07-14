<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-3 sm:px-4 py-6 sm:py-12">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 sm:mb-8 space-y-4 sm:space-y-0">
        <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <div class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
          <button 
            @click="refreshData"
            :disabled="loading"
            class="btn-secondary w-full sm:w-auto justify-center sm:justify-start"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            Refresh Data
          </button>
          <div class="text-xs sm:text-sm text-gray-500 text-center sm:text-left">
            Last updated: {{ formatDateTime(lastUpdated) }}
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-white rounded-lg shadow p-8 sm:p-12 text-center">
        <div class="animate-spin rounded-full h-8 w-8 sm:h-12 sm:w-12 border-b-2 border-green-600 mx-auto"></div>
        <p class="mt-4 text-gray-500 text-sm sm:text-base">Loading dashboard data...</p>
      </div>

      <div v-else>
        <!-- Key Metrics Overview -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <div class="flex flex-col sm:flex-row sm:items-center">
              <div class="p-2 bg-blue-100 rounded-lg mb-3 sm:mb-0 w-fit">
                <svg class="h-6 w-6 sm:h-8 sm:w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                </svg>
              </div>
              <div class="sm:ml-4">
                <p class="text-xs sm:text-sm font-medium text-gray-600">Total Users</p>
                <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ stats.total_users || 0 }}</p>
                <p class="text-xs text-gray-500">
                  {{ stats.active_users || 0 }} active this month
                </p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <div class="flex flex-col sm:flex-row sm:items-center">
              <div class="p-2 bg-green-100 rounded-lg mb-3 sm:mb-0 w-fit">
                <svg class="h-6 w-6 sm:h-8 sm:w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
                </svg>
              </div>
              <div class="sm:ml-4">
                <p class="text-xs sm:text-sm font-medium text-gray-600">Total Orders</p>
                <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ stats.total_orders || 0 }}</p>
                <p class="text-xs text-gray-500">
                  {{ stats.pending_orders || 0 }} pending
                </p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <div class="flex flex-col sm:flex-row sm:items-center">
              <div class="p-2 bg-yellow-100 rounded-lg mb-3 sm:mb-0 w-fit">
                <svg class="h-6 w-6 sm:h-8 sm:w-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="sm:ml-4">
                <p class="text-xs sm:text-sm font-medium text-gray-600">Revenue</p>
                <p class="text-sm sm:text-2xl font-bold text-gray-900">
                  KSh {{ formatNumber(stats.total_revenue || 0) }}
                </p>
                <p class="text-xs text-gray-500">
                  This month: KSh {{ formatNumber(stats.monthly_revenue || 0) }}
                </p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <div class="flex flex-col sm:flex-row sm:items-center">
              <div class="p-2 bg-purple-100 rounded-lg mb-3 sm:mb-0 w-fit">
                <svg class="h-6 w-6 sm:h-8 sm:w-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>
                </svg>
              </div>
              <div class="sm:ml-4">
                <p class="text-xs sm:text-sm font-medium text-gray-600">Deliveries</p>
                <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ stats.total_deliveries || 0 }}</p>
                <p class="text-xs text-gray-500">
                  {{ stats.active_deliveries || 0 }} in progress
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- User Distribution and Order Status -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <h3 class="text-base sm:text-lg font-semibold text-gray-900 mb-4">User Distribution</h3>
            <div class="space-y-3 sm:space-y-4">
              <div class="flex justify-between items-center">
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
                  <span class="text-xs sm:text-sm text-gray-600">Customers</span>
                </div>
                <span class="text-xs sm:text-sm font-medium text-gray-900">
                  {{ stats.customers_count || 0 }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                  <span class="text-xs sm:text-sm text-gray-600">Farmers</span>
                </div>
                <span class="text-xs sm:text-sm font-medium text-gray-900">
                  {{ stats.farmers_count || 0 }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-yellow-500 rounded-full mr-3"></div>
                  <span class="text-xs sm:text-sm text-gray-600">Riders</span>
                </div>
                <span class="text-xs sm:text-sm font-medium text-gray-900">
                  {{ stats.riders_count || 0 }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-purple-500 rounded-full mr-3"></div>
                  <span class="text-xs sm:text-sm text-gray-600">Admins</span>
                </div>
                <span class="text-xs sm:text-sm font-medium text-gray-900">
                  {{ stats.admins_count || 0 }}
                </span>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <h3 class="text-base sm:text-lg font-semibold text-gray-900 mb-4">Order Status Overview</h3>
            <div class="space-y-3 sm:space-y-4">
              <div class="flex justify-between items-center">
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-yellow-500 rounded-full mr-3"></div>
                  <span class="text-xs sm:text-sm text-gray-600">Pending Payment</span>
                </div>
                <span class="text-xs sm:text-sm font-medium text-gray-900">
                  {{ stats.orders_pending_payment || 0 }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
                  <span class="text-xs sm:text-sm text-gray-600">Confirmed</span>
                </div>
                <span class="text-xs sm:text-sm font-medium text-gray-900">
                  {{ stats.orders_confirmed || 0 }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-purple-500 rounded-full mr-3"></div>
                  <span class="text-xs sm:text-sm text-gray-600">Processing</span>
                </div>
                <span class="text-xs sm:text-sm font-medium text-gray-900">
                  {{ stats.orders_processing || 0 }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-orange-500 rounded-full mr-3"></div>
                  <span class="text-xs sm:text-sm text-gray-600">Out for Delivery</span>
                </div>
                <span class="text-xs sm:text-sm font-medium text-gray-900">
                  {{ stats.orders_out_for_delivery || 0 }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                  <span class="text-xs sm:text-sm text-gray-600">Delivered</span>
                </div>
                <span class="text-xs sm:text-sm font-medium text-gray-900">
                  {{ stats.orders_delivered || 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <h3 class="text-base sm:text-lg font-semibold text-gray-900 mb-4">Recent Orders</h3>
            <div class="space-y-2 sm:space-y-3">
              <div v-if="recentOrders.length === 0" class="text-center py-6 sm:py-8 text-gray-500 text-sm">
                No recent orders
              </div>
              <div 
                v-else
                v-for="order in recentOrders.slice(0, 5)" 
                :key="order.order_id"
                class="flex flex-col sm:flex-row sm:justify-between sm:items-center p-3 bg-gray-50 rounded-lg space-y-2 sm:space-y-0"
              >
                <div class="flex-1">
                  <p class="text-sm font-medium text-gray-900">
                    Order #{{ order.order_number }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ order.customer_name }} • {{ formatDate(order.order_date) }}
                  </p>
                </div>
                <div class="flex justify-between sm:block sm:text-right items-center">
                  <p class="text-sm font-bold text-green-600">
                    KSh {{ order.total_amount }}
                  </p>
                  <span 
                    :class="getOrderStatusBadgeClass(order.order_status)"
                    class="px-2 py-1 rounded-full text-xs font-medium"
                  >
                    {{ getOrderStatusLabel(order.order_status) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="mt-4 text-center">
              <router-link to="/admin/orders" class="text-green-600 hover:text-green-700 text-sm font-medium">
                View All Orders →
              </router-link>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <h3 class="text-base sm:text-lg font-semibold text-gray-900 mb-4">Recent Users</h3>
            <div class="space-y-2 sm:space-y-3">
              <div v-if="recentUsers.length === 0" class="text-center py-6 sm:py-8 text-gray-500 text-sm">
                No recent users
              </div>
              <div 
                v-else
                v-for="user in recentUsers.slice(0, 5)" 
                :key="user.user_id"
                class="flex flex-col sm:flex-row sm:justify-between sm:items-center p-3 bg-gray-50 rounded-lg space-y-2 sm:space-y-0"
              >
                <div class="flex-1">
                  <p class="text-sm font-medium text-gray-900">
                    {{ user.full_name || user.phone_number }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ getUserRoleLabel(user.user_role) }} • {{ formatDate(user.date_joined) }}
                  </p>
                </div>
                <div class="flex justify-end">
                  <span 
                    :class="getUserRoleBadgeClass(user.user_role)"
                    class="px-2 py-1 rounded-full text-xs font-medium"
                  >
                    {{ getUserRoleLabel(user.user_role) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="mt-4 text-center">
              <router-link to="/admin/users" class="text-green-600 hover:text-green-700 text-sm font-medium">
                View All Users →
              </router-link>
            </div>
          </div>
        </div>

        <!-- Management Links -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-4 sm:mb-6">
          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <div class="flex items-center mb-2">
              <svg class="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
              </svg>
              <h3 class="text-base sm:text-lg font-medium text-gray-900">User Management</h3>
            </div>
            <p class="text-gray-600 mb-4 text-sm">Manage users and permissions</p>
            <router-link to="/admin/users" class="btn-primary inline-flex w-full justify-center">
              Manage Users
            </router-link>
          </div>
          
          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <div class="flex items-center mb-2">
              <svg class="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
              </svg>
              <h3 class="text-base sm:text-lg font-medium text-gray-900">Orders Management</h3>
            </div>
            <p class="text-gray-600 mb-4 text-sm">Oversee all platform orders</p>
            <router-link to="/admin/orders" class="btn-primary inline-flex w-full justify-center">
              View Orders
            </router-link>
          </div>
          
          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <div class="flex items-center mb-2">
              <svg class="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>
              </svg>
              <h3 class="text-base sm:text-lg font-medium text-gray-900">Delivery Management</h3>
            </div>
            <p class="text-gray-600 mb-4 text-sm">Monitor delivery operations</p>
            <router-link to="/admin/deliveries" class="btn-primary inline-flex w-full justify-center">
              View Deliveries
            </router-link>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <div class="flex items-center mb-2">
              <svg class="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
              </svg>
              <h3 class="text-base sm:text-lg font-medium text-gray-900">Reviews Management</h3>
            </div>
            <p class="text-gray-600 mb-4 text-sm">Moderate user reviews and ratings</p>
            <router-link to="/admin/reviews" class="btn-primary inline-flex w-full justify-center">
              Manage Reviews
            </router-link>
          </div>
          
          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <div class="flex items-center mb-2">
              <svg class="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <h3 class="text-base sm:text-lg font-medium text-gray-900">Payouts Management</h3>
            </div>
            <p class="text-gray-600 mb-4 text-sm">Process farmer and rider payouts</p>
            <router-link to="/admin/payouts" class="btn-primary inline-flex w-full justify-center">
              Manage Payouts
            </router-link>
          </div>
          
          <div class="bg-white rounded-lg shadow p-4 sm:p-6">
            <div class="flex items-center mb-2">
              <svg class="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              <h3 class="text-base sm:text-lg font-medium text-gray-900">System Settings</h3>
            </div>
            <p class="text-gray-600 mb-4 text-sm">Configure platform settings</p>
            <router-link to="/admin/settings" class="btn-primary inline-flex w-full justify-center">
              Settings
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/services/api'

export default {
  name: 'AdminDashboard',
  setup() {
    const loading = ref(true)
    const stats = ref({})
    const recentOrders = ref([])
    const recentUsers = ref([])
    const lastUpdated = ref(new Date())

    const loadDashboardData = async () => {
      loading.value = true
      try {
        // Load dashboard statistics
        const [statsResponse, ordersResponse, usersResponse] = await Promise.all([
          adminAPI.getDashboardStats().catch(() => ({ data: {} })),
          adminAPI.getRecentOrders().catch(() => ({ data: [] })),
          adminAPI.getRecentUsers().catch(() => ({ data: [] }))
        ])
        
        stats.value = statsResponse.data || statsResponse
        recentOrders.value = ordersResponse.data || ordersResponse
        recentUsers.value = usersResponse.data || usersResponse
        lastUpdated.value = new Date()
        
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
        // Set default values
        stats.value = {
          total_users: 0,
          total_orders: 0,
          total_revenue: 0,
          total_deliveries: 0
        }
        recentOrders.value = []
        recentUsers.value = []
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      loadDashboardData()
    }

    const formatNumber = (number) => {
      return new Intl.NumberFormat('en-KE').format(number)
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const formatDateTime = (date) => {
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const getOrderStatusLabel = (status) => {
      const labels = {
        'pending_payment': 'Pending Payment',
        'confirmed': 'Confirmed',
        'processing': 'Processing',
        'out_for_delivery': 'Out for Delivery',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled'
      }
      return labels[status] || status
    }

    const getOrderStatusBadgeClass = (status) => {
      const classes = {
        'pending_payment': 'bg-yellow-100 text-yellow-800',
        'confirmed': 'bg-blue-100 text-blue-800',
        'processing': 'bg-purple-100 text-purple-800',
        'out_for_delivery': 'bg-orange-100 text-orange-800',
        'delivered': 'bg-green-100 text-green-800',
        'cancelled': 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }

    const getUserRoleLabel = (role) => {
      const labels = {
        'customer': 'Customer',
        'farmer': 'Farmer',
        'rider': 'Rider',
        'admin': 'Admin'
      }
      return labels[role] || role
    }

    const getUserRoleBadgeClass = (role) => {
      const classes = {
        'customer': 'bg-blue-100 text-blue-800',
        'farmer': 'bg-green-100 text-green-800',
        'rider': 'bg-yellow-100 text-yellow-800',
        'admin': 'bg-purple-100 text-purple-800'
      }
      return classes[role] || 'bg-gray-100 text-gray-800'
    }

    onMounted(() => {
      loadDashboardData()
    })

    return {
      loading,
      stats,
      recentOrders,
      recentUsers,
      lastUpdated,
      refreshData,
      formatNumber,
      formatDate,
      formatDateTime,
      getOrderStatusLabel,
      getOrderStatusBadgeClass,
      getUserRoleLabel,
      getUserRoleBadgeClass
    }
  }
}
</script>

<style scoped>
.btn-primary {
  background-color: #059669;
  color: white;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: background-color 0.2s;
  font-size: 0.875rem;
}

.btn-primary:hover {
  background-color: #047857;
}

.btn-secondary {
  background-color: white;
  color: #374151;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
  transition: background-color 0.2s;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}

.btn-secondary:hover {
  background-color: #f9fafb;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style> 