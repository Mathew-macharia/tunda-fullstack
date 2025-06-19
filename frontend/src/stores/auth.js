import { ref, computed } from 'vue'
import { authAPI } from '@/services/api'
import { jwtDecode } from 'jwt-decode'

// Global authentication state
const user = ref(null)
const isAuthenticated = ref(false)
const isLoading = ref(false)

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
  initializeAuth
} 