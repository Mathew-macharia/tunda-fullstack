<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import logoImage from '@/assets/tunda_logo.jpg'
import { 
  user, 
  isAuthenticated, 
  isCustomer, 
  isFarmer, 
  isRider, 
  isAdmin,
  getUserName,
  logout,
  guestCartItems
} from '@/stores/auth'
import { cartAPI, communicationAPI } from '@/services/api'

const router = useRouter()
const showUserDropdown = ref(false)
const showMobileMenu = ref(false)
const searchQuery = ref('')
const authenticatedCartCount = ref(0)
const activeTicketsCount = ref(0)

// Computed cart count for display
const cartCount = computed(() => {
  if (isAuthenticated.value && isCustomer.value) {
    return authenticatedCartCount.value
  } else {
    return guestCartItems.value.length
  }
})

// Load authenticated cart count
const loadCartCount = async () => {
  if (isAuthenticated.value && isCustomer.value) {
    try {
      const cart = await cartAPI.getCart()
      authenticatedCartCount.value = cart.total_items || 0
    } catch (error) {
      console.error('Failed to load cart count:', error)
      authenticatedCartCount.value = 0
    }
  }
}

// Load active tickets count for admin
const loadActiveTicketsCount = async () => {
  if (isAuthenticated.value && isAdmin.value) {
    try {
      const tickets = await communicationAPI.getUnassignedTickets()
      activeTicketsCount.value = tickets.length || 0
    } catch (error) {
      console.error('Failed to load active tickets count:', error)
      activeTicketsCount.value = 0
    }
  }
}

// Navigate to appropriate support page based on user role
const navigateToSupport = () => {
  if (isAdmin.value) {
    router.push('/admin/support')
  } else if (isFarmer.value) {
    router.push('/farmer/support')
  } else if (isRider.value) {
    router.push('/rider/support')
  } else if (isCustomer.value) {
    router.push('/support')
  }
}

// Listen for cart updates
const handleCartUpdate = () => {
  loadCartCount()
}

// Watch for authentication changes to load appropriate data
watch(isAuthenticated, (newValue) => {
  if (newValue) {
    loadCartCount()
    loadActiveTicketsCount()
  } else {
    authenticatedCartCount.value = 0
    activeTicketsCount.value = 0
  }
})

// Watch for admin role changes
watch(isAdmin, (newValue) => {
  if (newValue) {
    loadActiveTicketsCount()
  } else {
    activeTicketsCount.value = 0
  }
})

const handleLogout = async () => {
  try {
    await logout()
    showUserDropdown.value = false
    showMobileMenu.value = false
    window.location.href = '/'
  } catch (error) {
    console.error('Logout failed:', error)
  }
}

const handleSearch = () => {
  router.push({
    path: '/products',
    query: { search: searchQuery.value }
  })
  // Removed: searchQuery.value = '' to keep the search term in the input
}

const closeDropdowns = (event) => {
  // Close user dropdown if clicking outside
  if (showUserDropdown.value) {
    const userMenu = document.querySelector('#user-menu-button')
    const userDropdown = document.querySelector('#user-dropdown')
    if (!userMenu?.contains(event.target) && !userDropdown?.contains(event.target)) {
      showUserDropdown.value = false
    }
  }
  
  // Close mobile menu if clicking outside on mobile
  if (showMobileMenu.value) {
    const mobileMenu = document.querySelector('#mobile-menu')
    const mobileButton = document.querySelector('#mobile-menu-button')
    if (!mobileMenu?.contains(event.target) && !mobileButton?.contains(event.target)) {
      showMobileMenu.value = false
    }
  }
}

onMounted(() => {
  document.addEventListener('click', closeDropdowns)
  window.addEventListener('cartUpdated', handleCartUpdate)
  loadCartCount() // Load initial cart count
  loadActiveTicketsCount() // Load initial tickets count for admin
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdowns)
  window.removeEventListener('cartUpdated', handleCartUpdate)
})
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Left side - Logo and Navigation -->
          <div class="flex items-center shrink-0">
              <!-- Logo -->
            <RouterLink to="/" class="flex items-center">
              <img src="@/assets/tunda_logo.jpg" alt="Tunda Logo" class="h-8 w-auto mr-2">
              <span class="text-green-600 text-xl font-bold">Tun<span class="text-orange-500">da</span></span>
            </RouterLink>
            
            <!-- Desktop Navigation Links -->
            <div class="hidden md:ml-6 md:flex md:space-x-4">
              <RouterLink v-if="!isAuthenticated || isCustomer" 
                         to="/products" 
                         class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                Products
              </RouterLink>
            </div>
          </div>
          
          <!-- Mobile Search Bar - Centered -->
          <div v-if="!isAuthenticated || isCustomer" class="flex-grow flex justify-center md:hidden mx-1">
            <div class="relative w-full max-w-[120px]">
              <input type="text" 
                     v-model="searchQuery"
                     @keyup.enter="handleSearch"
                     placeholder="Search products..." 
                     class="w-full px-1.5 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-xs min-w-0">
              <button @click="handleSearch" 
                      class="absolute right-0.5 top-1 text-gray-400 hover:text-gray-600">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Right Side Navigation -->
          <div class="flex items-center space-x-0.5 shrink-0">
            <!-- Search Bar - Desktop Only -->
            <div v-if="!isAuthenticated || isCustomer" class="hidden md:flex items-center">
              <div class="relative">
                <input type="text" 
                       v-model="searchQuery"
                       @keyup.enter="handleSearch"
                       placeholder="Search products..." 
                       class="w-64 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent">
                <button @click="handleSearch" 
                        class="absolute right-2 top-2.5 text-gray-400 hover:text-gray-600">
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                </button>
              </div>
            </div>

            <!-- Cart Link - For Customers and Unauthenticated Users -->
            <RouterLink v-if="!isAuthenticated || isCustomer" 
                       to="/cart" 
                       class="text-gray-700 hover:text-gray-900 relative">
              <span class="sr-only">Shopping cart</span>
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <span v-if="cartCount > 0" 
                    class="absolute -top-1 -right-1 bg-red-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                {{ cartCount }}
              </span>
            </RouterLink>

            <!-- Support Button - For All Authenticated Users -->
            <button v-if="isAuthenticated" 
                    @click="navigateToSupport"
                    class="text-gray-700 hover:text-gray-900 relative p-2 rounded-md hover:bg-gray-100 transition-colors duration-200"
                    title="Support">
              <span class="sr-only">Support</span>
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <!-- Alert Badge for Admin -->
              <span v-if="isAdmin && activeTicketsCount > 0" 
                    class="absolute -top-1 -right-1 bg-red-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center animate-pulse">
                {{ activeTicketsCount > 99 ? '99+' : activeTicketsCount }}
              </span>
            </button>

            <!-- Desktop User Menu -->
            <div class="hidden md:block relative">
              <button v-if="isAuthenticated"
                      id="user-menu-button"
                      @click.stop="showUserDropdown = !showUserDropdown"
                      class="flex items-center space-x-2 text-sm px-3 py-2 bg-white hover:bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 border border-gray-200">
                <div class="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
                  <span class="text-sm font-medium text-gray-700">
                    {{ getUserName.charAt(0).toUpperCase() }}
                  </span>
                </div>
                <span class="text-gray-700">{{ getUserName }}</span>
                <!-- Dropdown Chevron -->
                <svg class="w-4 h-4 ml-1 text-gray-500" 
                     :class="{ 'transform rotate-180': showUserDropdown }"
                     fill="none" 
                     stroke="currentColor" 
                     viewBox="0 0 24 24">
                  <path stroke-linecap="round" 
                        stroke-linejoin="round" 
                        stroke-width="2" 
                        d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- Desktop Dropdown Menu -->
              <div v-if="showUserDropdown"
                   id="user-dropdown"
                   class="absolute right-0 mt-2 w-48 rounded-lg shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50 transform opacity-100 scale-100 transition ease-out duration-100">
                <div class="py-1">
                  <!-- Customer Links -->
                  <template v-if="isCustomer">
                    <RouterLink to="/customer"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Dashboard
                    </RouterLink>
                    <RouterLink to="/orders"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Orders
                    </RouterLink>
                  </template>

                  <!-- Farmer Links -->
                  <template v-if="isFarmer">
                    <RouterLink to="/farmer"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Dashboard
                    </RouterLink>
                    <RouterLink to="/farmer/farms"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Farms
                    </RouterLink>
                    <RouterLink to="/farmer/listings"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Listings
                    </RouterLink>
                    <RouterLink to="/farmer/orders"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Orders
                    </RouterLink>
                    <RouterLink to="/farmer/payouts"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Payouts
                    </RouterLink>
                  </template>

                  <!-- Rider Links -->
                  <template v-if="isRider">
                    <RouterLink to="/rider"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Dashboard
                    </RouterLink>
                    <RouterLink to="/rider/deliveries"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Deliveries
                    </RouterLink>
                  </template>

                  <!-- Admin Links -->
                  <template v-if="isAdmin">
                    <RouterLink to="/admin"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Dashboard
                    </RouterLink>
                    <RouterLink to="/admin/users"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Users
                    </RouterLink>
                    <RouterLink to="/admin/orders"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Orders
                    </RouterLink>
                    <RouterLink to="/admin/settings"
                               @click="showUserDropdown = false"
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      Settings
                    </RouterLink>
                  </template>

                  <!-- Common Links -->
                  <RouterLink to="/profile"
                             @click="showUserDropdown = false"
                             class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                    Profile
                  </RouterLink>
                  <div class="border-t border-gray-200 my-1"></div>
                  <button @click="handleLogout"
                          class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                    Logout
                  </button>
                </div>
              </div>
              
              <!-- Desktop Login/Register -->
              <div v-if="!isAuthenticated" class="flex items-center space-x-2">
                <RouterLink to="/login" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                  Login
                </RouterLink>
                <RouterLink to="/register" class="bg-green-600 text-white hover:bg-green-700 px-3 py-2 rounded-md text-sm font-medium">
                  Register
                </RouterLink>
              </div>
            </div>
            
            <!-- Mobile Menu Button -->
            <button @click.stop="showMobileMenu = !showMobileMenu"
                    class="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-green-500">
              <span class="sr-only">Open main menu</span>
              <!-- Hamburger Icon -->
              <svg class="h-6 w-6" 
                   :class="{'hidden': showMobileMenu, 'block': !showMobileMenu }"
                   stroke="currentColor" 
                   fill="none" 
                   viewBox="0 0 24 24">
                <path stroke-linecap="round" 
                      stroke-linejoin="round" 
                      stroke-width="2" 
                      d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <!-- Close Icon -->
              <svg class="h-6 w-6" 
                   :class="{'block': showMobileMenu, 'hidden': !showMobileMenu }"
                   stroke="currentColor" 
                   fill="none" 
                   viewBox="0 0 24 24">
                <path stroke-linecap="round" 
                      stroke-linejoin="round" 
                      stroke-width="2" 
                      d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Mobile Menu Panel -->
        <div v-show="showMobileMenu" 
             class="absolute top-16 inset-x-0 z-50 bg-white shadow-lg border-b border-gray-200 md:hidden">
          <div class="py-2">
            <!-- Unauthenticated Menu -->
            <template v-if="!isAuthenticated">
              <RouterLink to="/products"
                         @click="showMobileMenu = false"
                         class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                Products
              </RouterLink>
              <RouterLink to="/login"
                         @click="showMobileMenu = false"
                         class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                Login
              </RouterLink>
              <RouterLink to="/register"
                         @click="showMobileMenu = false"
                         class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 bg-green-600 text-white hover:bg-green-700 mx-4 rounded-md text-center">
                Register
              </RouterLink>
            </template>

            <!-- Authenticated Menu -->
            <template v-else>
              <!-- Customer Links -->
              <template v-if="isCustomer">
                <button @click="router.push('/customer'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Dashboard
                </button>
                <button @click="router.push('/orders'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Orders
                </button>
              </template>
              
              <!-- Farmer Links -->
              <template v-if="isFarmer">
                <button @click="router.push('/farmer'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Dashboard
                </button>
                <button @click="router.push('/farmer/farms'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Farms
                </button>
                <button @click="router.push('/farmer/listings'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Listings
                </button>
                <button @click="router.push('/farmer/orders'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Orders
                </button>
                <button @click="router.push('/farmer/payouts'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Payouts
                </button>
              </template>
              
              <!-- Rider Links -->
              <template v-if="isRider">
                <button @click="router.push('/rider'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Dashboard
                </button>
                <button @click="router.push('/rider/deliveries'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Deliveries
                </button>
              </template>
              
              <!-- Admin Links -->
              <template v-if="isAdmin">
                <button @click="router.push('/admin'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Dashboard
                </button>
                <button @click="router.push('/admin/users'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Users
                </button>
                <button @click="router.push('/admin/orders'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Orders
                </button>
                <button @click="router.push('/admin/settings'); showMobileMenu = false" 
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Settings
                </button>
              </template>
              
              <!-- Common Links -->
              <button @click="router.push('/profile'); showMobileMenu = false" 
                      class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                Profile
              </button>
              <div class="border-t border-gray-200 my-1"></div>
              <button @click="handleLogout" 
                      class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                Logout
              </button>
            </template>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Overlay (Moved outside nav to start below it) -->
    <div v-show="showMobileMenu" 
         @click="showMobileMenu = false"
         class="fixed top-16 inset-x-0 bottom-0 bg-black bg-opacity-25 z-40 md:hidden"></div>
    
    <!-- Main Content -->
    <RouterView />
  </div>
</template>
