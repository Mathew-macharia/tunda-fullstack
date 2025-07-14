<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div class="flex-1 min-w-0">
            <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold leading-7 text-gray-900">
              Welcome back, {{ getUserName }}!
            </h1>
            <p class="mt-1 text-sm text-gray-500">
              Here's what's happening with your account
            </p>
          </div>
          <div class="mt-3 sm:mt-0 sm:ml-4">
            <router-link to="/products" class="btn-primary w-full sm:w-auto inline-flex justify-center">
              Browse Products
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8">
      <!-- Quick Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 sm:h-6 sm:w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
                </svg>
              </div>
              <div class="ml-2 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">
                    Total Orders
                  </dt>
                  <dd class="text-sm sm:text-lg font-medium text-gray-900">
                    {{ stats.totalOrders }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 sm:h-6 sm:w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                </svg>
              </div>
              <div class="ml-2 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">
                    Total Spent
                  </dt>
                  <dd class="text-xs sm:text-lg font-medium text-gray-900">
                    KSh {{ stats.totalSpent.toLocaleString() }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 sm:h-6 sm:w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </div>
              <div class="ml-2 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">
                    Pending
                  </dt>
                  <dd class="text-sm sm:text-lg font-medium text-gray-900">
                    {{ stats.pendingOrders }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 sm:h-6 sm:w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
                </svg>
              </div>
              <div class="ml-2 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">
                    Cart Items
                  </dt>
                  <dd class="text-sm sm:text-lg font-medium text-gray-900">
                    {{ stats.cartItems }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-white shadow rounded-lg mb-6 sm:mb-8">
        <div class="px-3 py-4 sm:px-6 sm:py-6">
          <h3 class="text-base sm:text-lg leading-6 font-medium text-gray-900 mb-3 sm:mb-4">
            Quick Actions
          </h3>
          <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <router-link to="/products" class="quick-action-card">
              <div class="flex flex-col sm:flex-row items-center text-center sm:text-left">
                <div class="flex-shrink-0 mb-2 sm:mb-0">
                  <svg class="h-6 w-6 text-green-600 mx-auto sm:mx-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                  </svg>
                </div>
                <div class="sm:ml-3">
                  <p class="text-xs sm:text-sm font-medium text-gray-900">Browse Products</p>
                  <p class="text-xs text-gray-500 hidden sm:block">Find fresh produce</p>
                </div>
              </div>
            </router-link>

            <router-link v-if="stats.cartItems > 0" to="/cart" class="quick-action-card">
              <div class="flex flex-col sm:flex-row items-center text-center sm:text-left">
                <div class="flex-shrink-0 mb-2 sm:mb-0">
                  <svg class="h-6 w-6 text-blue-600 mx-auto sm:mx-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
                  </svg>
                </div>
                <div class="sm:ml-3">
                  <p class="text-xs sm:text-sm font-medium text-gray-900">View Cart</p>
                  <p class="text-xs text-gray-500">{{ stats.cartItems }} items</p>
                </div>
              </div>
            </router-link>

            <router-link to="/orders" class="quick-action-card">
              <div class="flex flex-col sm:flex-row items-center text-center sm:text-left">
                <div class="flex-shrink-0 mb-2 sm:mb-0">
                  <svg class="h-6 w-6 text-purple-600 mx-auto sm:mx-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                </div>
                <div class="sm:ml-3">
                  <p class="text-xs sm:text-sm font-medium text-gray-900">Order History</p>
                  <p class="text-xs text-gray-500 hidden sm:block">Track your orders</p>
                </div>
              </div>
            </router-link>

            <router-link to="/profile" class="quick-action-card">
              <div class="flex flex-col sm:flex-row items-center text-center sm:text-left">
                <div class="flex-shrink-0 mb-2 sm:mb-0">
                  <svg class="h-6 w-6 text-gray-600 mx-auto sm:mx-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                </div>
                <div class="sm:ml-3">
                  <p class="text-xs sm:text-sm font-medium text-gray-900">Profile</p>
                  <p class="text-xs text-gray-500 hidden sm:block">Update your info</p>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </div>

      <div class="space-y-6 lg:space-y-0 lg:grid lg:grid-cols-2 lg:gap-8">
        <!-- Recent Orders -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-3 py-4 sm:px-6 sm:py-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-base sm:text-lg leading-6 font-medium text-gray-900">
                Recent Orders
              </h3>
              <router-link to="/orders" class="text-sm font-medium text-green-600 hover:text-green-500">
                View all
              </router-link>
            </div>
            
            <div v-if="loadingOrders" class="flex justify-center py-4">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
            </div>
            
            <div v-else-if="!recentOrders.length" class="text-center py-6">
              <p class="text-sm text-gray-500 mb-2">No orders yet</p>
              <router-link to="/products" class="text-sm font-medium text-green-600 hover:text-green-500">
                Start shopping
              </router-link>
            </div>
            
            <div v-else class="space-y-3">
              <div
                v-for="order in recentOrders"
                :key="order.order_id"
                class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 bg-gray-50 rounded-lg space-y-2 sm:space-y-0"
              >
                <div class="flex-1">
                  <p class="text-sm font-medium text-gray-900">
                    Order #{{ order.order_number }}
                  </p>
                  <p class="text-xs sm:text-sm text-gray-500">
                    {{ formatDate(order.order_date) }}
                  </p>
                </div>
                <div class="flex items-center justify-between sm:flex-col sm:items-end sm:text-right">
                  <p class="text-sm font-medium text-gray-900">
                    KSh {{ order.total_amount }}
                  </p>
                  <span
                    :class="getOrderStatusClass(order.order_status)"
                    class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                  >
                    {{ getOrderStatusDisplay(order.order_status) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Account Summary -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-3 py-4 sm:px-6 sm:py-6">
            <h3 class="text-base sm:text-lg leading-6 font-medium text-gray-900 mb-4">
              Account Summary
            </h3>
            
            <div class="space-y-3 sm:space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-500">Account Status</span>
                <span class="text-sm font-medium text-green-600">Active</span>
              </div>
              
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-500">Member Since</span>
                <span class="text-sm text-gray-900">{{ formatDate(user?.created_at) }}</span>
              </div>
              
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-500">Phone Verified</span>
                <span :class="user?.is_verified ? 'text-green-600' : 'text-yellow-600'" class="text-sm font-medium">
                  {{ user?.is_verified ? 'Yes' : 'Pending' }}
                </span>
              </div>
              
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-500">Language</span>
                <span class="text-sm text-gray-900 capitalize">{{ user?.preferred_language }}</span>
              </div>
              
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-500">Notifications</span>
                <span class="text-sm text-gray-900">
                  {{ user?.sms_notifications ? 'SMS' : '' }}
                  {{ user?.email_notifications ? (user?.sms_notifications ? ' & Email' : 'Email') : '' }}
                </span>
              </div>
            </div>
            
            <div class="mt-6">
              <router-link to="/profile" class="btn-secondary w-full text-center block">
                Update Profile
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { user, getUserName } from '@/stores/auth'
import { ordersAPI, cartAPI } from '@/services/api'

export default {
  name: 'CustomerDashboard',
  setup() {
    const loadingOrders = ref(false)
    const recentOrders = ref([])
    
    const stats = reactive({
      totalOrders: 0,
      totalSpent: 0,
      pendingOrders: 0,
      cartItems: 0
    })
    
    const loadDashboardData = async () => {
      await Promise.all([
        loadStats(),
        loadRecentOrders(),
        loadCartInfo()
      ])
    }
    
    const loadStats = async () => {
      try {
        const response = await ordersAPI.getOrders({ page_size: 1000 })
        console.log('Orders API response:', response) // Debug log
        
        // Handle different response structures
        let orders = []
        if (Array.isArray(response)) {
          orders = response
        } else if (response && response.results && Array.isArray(response.results)) {
          orders = response.results
        } else if (response && response.data && Array.isArray(response.data)) {
          orders = response.data
        } else if (response && typeof response === 'object') {
          // If response is an object but not expected format, check all properties
          console.warn('Unexpected response format:', response)
          const possibleArrays = Object.values(response).filter(val => Array.isArray(val))
          if (possibleArrays.length > 0) {
            orders = possibleArrays[0]
            console.log('Using array from response:', orders)
          } else {
            orders = []
          }
        } else {
          console.warn('Orders response is not in expected format:', response)
          orders = []
        }
        
        stats.totalOrders = orders.length
        stats.totalSpent = orders.reduce((sum, order) => sum + parseFloat(order.total_amount || 0), 0)
        stats.pendingOrders = orders.filter(order => 
          ['pending', 'confirmed', 'processing', 'out_for_delivery'].includes(order.order_status)
        ).length
      } catch (error) {
        console.error('Failed to load stats:', error)
        stats.totalOrders = 0
        stats.totalSpent = 0
        stats.pendingOrders = 0
      }
    }
    
    const loadRecentOrders = async () => {
      loadingOrders.value = true
      try {
        const response = await ordersAPI.getOrders({ page_size: 5, ordering: '-created_at' })
        recentOrders.value = response.results || response
      } catch (error) {
        console.error('Failed to load recent orders:', error)
        recentOrders.value = []
      } finally {
        loadingOrders.value = false
      }
    }
    
    const loadCartInfo = async () => {
      try {
        const cart = await cartAPI.getCart()
        stats.cartItems = cart.items_count || 0
      } catch (error) {
        console.error('Failed to load cart info:', error)
      }
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
    
    const getOrderStatusDisplay = (status) => {
      const statusMap = {
        'pending_payment': 'Pending Payment',
        'confirmed': 'Confirmed',
        'processing': 'Processing',
        'out_for_delivery': 'Out for Delivery',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled',
        'refunded': 'Refunded'
      }
      return statusMap[status] || status
    }
    
    const getOrderStatusClass = (status) => {
      const classMap = {
        'pending_payment': 'bg-yellow-100 text-yellow-800',
        'confirmed': 'bg-blue-100 text-blue-800',
        'processing': 'bg-purple-100 text-purple-800',
        'out_for_delivery': 'bg-indigo-100 text-indigo-800',
        'delivered': 'bg-green-100 text-green-800',
        'cancelled': 'bg-red-100 text-red-800',
        'refunded': 'bg-gray-100 text-gray-800'
      }
      return classMap[status] || 'bg-gray-100 text-gray-800'
    }
    
    onMounted(() => {
      loadDashboardData()
    })
    
    return {
      user,
      getUserName,
      stats,
      loadingOrders,
      recentOrders,
      formatDate,
      getOrderStatusDisplay,
      getOrderStatusClass
    }
  }
}
</script>

<style scoped>
.quick-action-card {
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
  transition: background-color 0.2s;
  touch-action: manipulation;
}

.quick-action-card:hover {
  background-color: #f3f4f6;
}

.btn-primary {
  background-color: #059669;
  color: white;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #047857;
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #111827;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

/* Ensure touch targets are at least 44px */
@media (max-width: 640px) {
  .quick-action-card {
    min-height: 44px;
  }
}
</style>