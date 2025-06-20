import { ref, computed } from 'vue'
import { authAPI, cartAPI } from '@/services/api' // Import cartAPI
import { jwtDecode } from 'jwt-decode'

// Global authentication state
const user = ref(null)
const isAuthenticated = ref(false)
const isLoading = ref(false)

// Guest cart state
const GUEST_CART_STORAGE_KEY = 'guest_cart_items'
const guestCartItems = ref([])

// Helper to save guest cart to localStorage
const saveGuestCart = () => {
  localStorage.setItem(GUEST_CART_STORAGE_KEY, JSON.stringify(guestCartItems.value))
}

// Helper to load guest cart from localStorage
const loadGuestCart = () => {
  try {
    const storedCart = localStorage.getItem(GUEST_CART_STORAGE_KEY)
    guestCartItems.value = storedCart ? JSON.parse(storedCart) : []
  } catch (e) {
    console.error("Failed to parse guest cart from localStorage", e)
    guestCartItems.value = []
  }
}

// Initialize auth state from localStorage
const initializeAuth = () => {
  const token = localStorage.getItem('access_token')
  if (token) {
    try {
      const decodedToken = jwtDecode(token)
      const currentTime = Date.now() / 1000
      
      if (decodedToken.exp > currentTime) {
        isAuthenticated.value = true
        // Fetch user data
        authAPI.getCurrentUser().then(userData => {
          user.value = userData
          // Merge guest cart if user is customer
          if (userData.user_role === 'customer' && guestCartItems.value.length > 0) {
            mergeGuestCartToUserCart()
          }
        }).catch(() => {
          logout()
        })
      } else {
        logout()
      }
    } catch (error) {
      logout()
    }
  }
  loadGuestCart() // Always load guest cart on initialization
}

// Computed properties for role-based access
const isCustomer = computed(() => user.value?.user_role === 'customer')
const isFarmer = computed(() => user.value?.user_role === 'farmer')
const isRider = computed(() => user.value?.user_role === 'rider')
const isAdmin = computed(() => user.value?.user_role === 'admin')

// Auth methods
const login = async (phoneNumber, password) => {
  isLoading.value = true
  try {
    const response = await authAPI.login({ phone_number: phoneNumber, password: password })
    
    // Store tokens
    localStorage.setItem('access_token', response.access)
    localStorage.setItem('refresh_token', response.refresh)
    
    // Get user data
    const userData = await authAPI.getCurrentUser()
    user.value = userData
    isAuthenticated.value = true

    // Merge guest cart if user is customer
    if (userData.user_role === 'customer' && guestCartItems.value.length > 0) {
      await mergeGuestCartToUserCart()
    }
    
    return { success: true, user: userData }
  } catch (error) {
    console.error('Login error:', error)
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Login failed' 
    }
  } finally {
    isLoading.value = false
  }
}

const register = async (userData) => {
  isLoading.value = true
  try {
    const response = await authAPI.register(userData)
    
    // Auto-login after successful registration
    const loginResult = await login(userData.phone_number, userData.password)
    if (loginResult.success) {
      // Merge guest cart if user is customer
      if (loginResult.user.user_role === 'customer' && guestCartItems.value.length > 0) {
        await mergeGuestCartToUserCart()
      }
      return { success: true, user: loginResult.user, message: 'Registration successful!' }
    }
    
    // If auto-login fails, still consider registration successful
    return { success: true, data: response, message: 'Registration successful! Please login.' }
  } catch (error) {
    console.error('Registration error:', error)
    return { 
      success: false, 
      error: error.response?.data || 'Registration failed' 
    }
  } finally {
    isLoading.value = false
  }
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  user.value = null
  isAuthenticated.value = false
  // Do NOT clear guest cart on logout, it might be used by another guest session
}

const updateProfile = async (profileData) => {
  isLoading.value = true
  try {
    const updatedUser = await authAPI.updateProfile(profileData)
    user.value = { ...user.value, ...updatedUser }
    return { success: true, user: user.value }
  } catch (error) {
    console.error('Profile update error:', error)
    return { 
      success: false, 
      error: error.response?.data || 'Profile update failed' 
    }
  } finally {
    isLoading.value = false
  }
}

const changePassword = async (passwordData) => {
  isLoading.value = true
  try {
    await authAPI.changePassword(passwordData)
    return { success: true }
  } catch (error) {
    console.error('Password change error:', error)
    return { 
      success: false, 
      error: error.response?.data || 'Password change failed' 
    }
  } finally {
    isLoading.value = false
  }
}

// Guest Cart Methods
const addGuestCartItem = (listing, quantity) => {
  const existingItemIndex = guestCartItems.value.findIndex(item => item.listing_id === listing.listing_id)
  
  const itemDetails = {
    listing_id: listing.listing_id,
    product_name: listing.product_name,
    farm_name: listing.farm_name,
    photos: listing.photos,
    current_price: listing.current_price,
    product_unit: listing.product_unit_display, // Use the new direct field
    min_order_quantity: listing.min_order_quantity,
    quantity_available: listing.quantity_available,
    // Add any other details needed for display on the cart page
  }

  if (existingItemIndex > -1) {
    guestCartItems.value[existingItemIndex].quantity = parseFloat(guestCartItems.value[existingItemIndex].quantity) + parseFloat(quantity)
  } else {
    guestCartItems.value.push({ ...itemDetails, quantity: parseFloat(quantity) })
  }
  saveGuestCart()
}

const updateGuestCartItem = (listingId, newQuantity) => {
  const item = guestCartItems.value.find(item => item.listing_id === listingId)
  if (item) {
    item.quantity = parseFloat(newQuantity)
    saveGuestCart()
  }
}

const removeGuestCartItem = (listingId) => {
  guestCartItems.value = guestCartItems.value.filter(item => item.listing_id !== listingId)
  saveGuestCart()
}

const clearGuestCart = () => {
  guestCartItems.value = []
  saveGuestCart()
}

const mergeGuestCartToUserCart = async () => {
  if (guestCartItems.value.length > 0) {
    try {
      await authAPI.mergeGuestCart(guestCartItems.value)
      clearGuestCart() // Clear local guest cart after merging
      window.dispatchEvent(new CustomEvent('cartUpdated')) // Notify UI
      console.log('Guest cart merged successfully!')
    } catch (error) {
      console.error('Failed to merge guest cart:', error)
      // Optionally, notify user that some items might not have been merged
    }
  }
}

// Check if user has required role
const hasRole = (role) => {
  return user.value?.user_role === role
}

// Check if user has any of the required roles
const hasAnyRole = (roles) => {
  return roles.includes(user.value?.user_role)
}

// Get user's full name
const getUserName = computed(() => {
  if (!user.value) return ''
  return `${user.value.first_name} ${user.value.last_name}`.trim()
})

// Get user's role display name
const getUserRoleDisplay = computed(() => {
  const roleMap = {
    customer: 'Customer',
    farmer: 'Farmer',
    rider: 'Rider',
    admin: 'Administrator'
  }
  return roleMap[user.value?.user_role] || 'User'
})

// Initialize auth on module load
initializeAuth()

export {
  // State
  user,
  isAuthenticated,
  isLoading,
  guestCartItems, // Export guest cart state
  
  // Computed
  isCustomer,
  isFarmer,
  isRider,
  isAdmin,
  getUserName,
  getUserRoleDisplay,
  
  // Methods
  login,
  register,
  logout,
  updateProfile,
  changePassword,
  hasRole,
  hasAnyRole,
  initializeAuth,
  // Export guest cart methods
  addGuestCartItem,
  updateGuestCartItem,
  removeGuestCartItem,
  clearGuestCart,
  mergeGuestCartToUserCart
}
