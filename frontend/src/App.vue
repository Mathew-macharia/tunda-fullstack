<script setup>
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
// Import your logo
import logoImage from '@/assets/tunda_logo.jpg' // Adjust the filename as needed
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white sticky top-0 z-50 border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- Logo and main navigation -->
          <div class="flex items-center">
            <router-link to="/" class="flex items-center space-x-2">
              <!-- Replace the green box with actual logo -->
              <div class="w-8 h-8 rounded-lg overflow-hidden flex items-center justify-center bg-gray-100">
                <img :src="logoImage" 
                     alt="Tunda Logo" 
                     class="w-full h-full object-contain">
              </div>
               <span class="text-xl font-bold">
                <span class="text-green-600">Tun</span>
                <span class="text-orange-500">da</span>
              </span>
            </router-link>
            
            <!-- Desktop navigation -->
            <div class="hidden md:ml-8 md:flex md:space-x-8">
              <!-- Products link - hidden from riders -->
              <router-link v-if="!isRider" to="/products" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Products</router-link>
              
              <!-- Cart link - visible for all non-rider/admin roles (including guests) -->
              <router-link v-if="!isRider && !isAdmin" to="/cart" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 flex items-center space-x-1">
                <span>Cart</span>
                <span v-if="cartItemsCount > 0" 
                      class="bg-green-600 text-white text-xs rounded-full px-2 py-1 min-w-5 text-center">
                  {{ cartItemsCount }}
                </span>
              </router-link>

              <template v-if="isAuthenticated">
                <!-- Customer navigation -->
                <template v-if="isCustomer">
                  <router-link to="/customer" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Dashboard</router-link>
                  <!-- Cart link moved above -->
                  <router-link to="/orders" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Orders</router-link>
                </template>
                
                <!-- Farmer navigation -->
                <template v-if="isFarmer">
                  <router-link to="/farmer" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Dashboard</router-link>
                  <router-link to="/farmer/farms" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Farms</router-link>
                  <router-link to="/farmer/listings" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Listings</router-link>
                  <router-link to="/farmer/orders" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Orders</router-link>
                </template>
                
                <!-- Rider navigation -->
                <template v-if="isRider">
                  <router-link to="/rider" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Dashboard</router-link>
                  <router-link to="/rider/deliveries" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Deliveries</router-link>
                </template>
                
                <!-- Admin navigation -->
                <template v-if="isAdmin">
                  <router-link to="/admin" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Dashboard</router-link>
                  <router-link to="/admin/users" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Users</router-link>
                  <router-link to="/admin/orders" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Orders</router-link>
                  <router-link to="/admin/settings" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">Settings</router-link>
                </template>
              </template>
            </div>
          </div>
          
          <!-- Right side navigation -->
          <div class="flex items-center space-x-4">
            <template v-if="isAuthenticated">
              <!-- User info and direct links -->
              <div class="hidden sm:flex items-center space-x-4">
                <div class="flex items-center space-x-2 text-gray-700">
                  <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-gray-700">
                      {{ getUserName.charAt(0).toUpperCase() }}
                    </span>
                  </div>
                  <div class="text-sm">
                    <div class="font-medium">{{ getUserName }}</div>
                    <div class="text-xs text-gray-500">{{ getUserRoleDisplay }}</div>
                  </div>
                </div>
                
                <router-link to="/profile" 
                             class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">
                  Profile
                </router-link>
                
                <button @click="() => { logout(); $router.push('/'); }" 
                        class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">
                  Logout
                </button>
              </div>
              
              <!-- Mobile user info -->
              <div class="sm:hidden flex items-center space-x-2 text-gray-700">
                <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span class="text-sm font-medium text-gray-700">
                    {{ getUserName.charAt(0).toUpperCase() }}
                  </span>
                </div>
                <span class="text-sm font-medium">{{ getUserName }}</span>
              </div>
            </template>
            
            <template v-else>
              <router-link to="/login" class="text-gray-700 hover:text-gray-900 px-4 py-2 rounded-md text-sm font-medium border border-gray-300 hover:border-gray-400 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2">Login</router-link>
              <router-link to="/register" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2">Register</router-link>
            </template>
            
            <!-- Mobile menu button -->
            <button @click="showMobileMenu = !showMobileMenu" 
                    class="md:hidden p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      :d="showMobileMenu ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'"></path>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Mobile menu -->
        <div v-if="showMobileMenu" class="md:hidden border-t border-gray-200 py-4">
          <div class="space-y-2">
            <!-- Products link - hidden from riders in mobile menu too -->
            <router-link v-if="!isRider" to="/products" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Products</router-link>
            
            <!-- Cart link - visible for all non-rider/admin roles (including guests) -->
            <router-link v-if="!isRider && !isAdmin" to="/cart" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">
              Cart <span v-if="cartItemsCount > 0" class="text-green-600">({{ cartItemsCount }})</span>
            </router-link>

            <template v-if="isAuthenticated">
              <!-- Customer mobile navigation -->
              <template v-if="isCustomer">
                <router-link to="/customer" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Dashboard</router-link>
                <!-- Cart link moved above -->
                <router-link to="/orders" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Orders</router-link>
              </template>
              
              <!-- Farmer mobile navigation -->
              <template v-if="isFarmer">
                <router-link to="/farmer" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Dashboard</router-link>
                <router-link to="/farmer/farms" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Farms</router-link>
                <router-link to="/farmer/listings" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Listings</router-link>
                <router-link to="/farmer/orders" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Orders</router-link>
              </template>
              
              <!-- Rider mobile navigation -->
              <template v-if="isRider">
                <router-link to="/rider" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Dashboard</router-link>
                <router-link to="/rider/deliveries" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Deliveries</router-link>
              </template>
              
              <!-- Admin mobile navigation -->
              <template v-if="isAdmin">
                <router-link to="/admin" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Dashboard</router-link>
                <router-link to="/admin/users" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Users</router-link>
                <router-link to="/admin/orders" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Orders</router-link>
                <router-link to="/admin/settings" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Settings</router-link>
              </template>
              
              <div class="border-t border-gray-200 pt-2 mt-2">
                <router-link to="/profile" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Profile</router-link>
                <button @click="() => { logout(); $router.push('/'); }" 
                        class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200 w-full text-left">Logout</button>
              </div>
            </template>
            
            <template v-else>
              <router-link to="/login" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Login</router-link>
              <router-link to="/register" class="block px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200">Register</router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Main content -->
    <main class="flex-1">
      <router-view />
    </main>
    
    <!-- Loading overlay -->
    <div v-if="isLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 flex items-center space-x-3">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
        <span class="text-gray-700">Loading...</span>
      </div>
    </div>
    
    <!-- Toast notifications -->
    <div class="fixed top-4 right-4 z-50 space-y-2">
      <div v-for="toast in toasts" 
           :key="toast.id"
           :class="`toast-${toast.type}`"
           class="max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto flex ring-1 ring-black ring-opacity-5">
        <div class="flex-1 w-0 p-4">
          <div class="flex items-start">
            <div class="ml-3 flex-1">
              <p class="text-sm font-medium text-gray-900">{{ toast.title }}</p>
              <p v-if="toast.message" class="mt-1 text-sm text-gray-500">{{ toast.message }}</p>
            </div>
          </div>
        </div>
        <div class="flex border-l border-gray-200">
          <button @click="removeToast(toast.id)" 
                  class="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-gray-600 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500">
            ×
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  user, 
  isAuthenticated, 
  isLoading, 
  isCustomer, 
  isFarmer, 
  isRider, 
  isAdmin,
  getUserName,
  getUserRoleDisplay,
  logout,
  guestCartItems // Import guestCartItems
} from '@/stores/auth'
import { cartAPI } from '@/services/api'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const showMobileMenu = ref(false)
    const cartItemsCount = ref(0)
    const toasts = ref([])
    
    // Load cart count based on authentication status
    const loadCartCount = async () => {
      if (isAuthenticated.value && isCustomer.value) {
        try {
          const cart = await cartAPI.getCart()
          cartItemsCount.value = cart.items_count || 0
        } catch (error) {
          console.error('Failed to load authenticated cart count:', error)
          cartItemsCount.value = 0 // Reset on error
        }
      } else {
        // For unauthenticated users, use the guest cart items count
        cartItemsCount.value = guestCartItems.value.length
      }
    }
    
    // Handle logout
    const handleLogout = async () => {
      console.log('Logout button clicked!')
      try {
        console.log('Calling logout function...')
        logout()
        console.log('Logout function completed')
        
        showMobileMenu.value = false
        cartItemsCount.value = 0 // Reset cart count immediately on logout
        
        console.log('Navigating to home...')
        await router.push('/')
        console.log('Navigation completed')
        
        showToast('success', 'Logged out successfully')
        console.log('Toast shown')
      } catch (error) {
        console.error('Error during logout:', error)
        showToast('error', 'Logout failed', 'Please try again')
      }
    }
    
    // Toast notifications
    let toastIdCounter = 0
    const showToast = (type, title, message = '', duration = 5000) => {
      const id = ++toastIdCounter
      toasts.value.push({ id, type, title, message })
      
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
    
    const removeToast = (id) => {
      const index = toasts.value.findIndex(toast => toast.id === id)
      if (index > -1) {
        toasts.value.splice(index, 1)
      }
    }
    
    // Global error handler
    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled promise rejection:', event.reason)
      showToast('error', 'Something went wrong', 'Please try again')
    })
    
    onMounted(() => {
      loadCartCount()
      
      // Listen for cart updates
      window.addEventListener('cartUpdated', loadCartCount)
    })
    
    onUnmounted(() => {
      window.removeEventListener('cartUpdated', loadCartCount)
    })
    
    // Watch for changes in guestCartItems to update cart count
    // This is important because guestCartItems is updated directly in auth.js
    // and other components might modify it without dispatching 'cartUpdated' event.
    // However, the current implementation of addGuestCartItem, updateGuestCartItem, removeGuestCartItem
    // in auth.js *do* dispatch 'cartUpdated', so this might be redundant but safe.
    // watch(guestCartItems, loadCartCount, { deep: true }); // Uncomment if needed
    
    return {
      // Auth state
      user,
      isAuthenticated,
      isLoading,
      isCustomer,
      isFarmer,
      isRider,
      isAdmin,
      getUserName,
      getUserRoleDisplay,
      logout,
      
      // UI state
      showMobileMenu,
      cartItemsCount,
      toasts,
      
      // Router
      $router: router,
      
      // Methods
      handleLogout,
      showToast,
      removeToast
    }
  }
}
</script>

<style scoped>
/* Clean styles without @apply directives */
</style>
