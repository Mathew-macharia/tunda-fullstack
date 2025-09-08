import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || 'http://localhost:8000'

// Helper function to convert relative media URLs to absolute URLs
const getAbsoluteMediaUrl = (relativeUrl) => {
  if (!relativeUrl) return null
  if (relativeUrl.startsWith('http')) return relativeUrl
  if (relativeUrl.startsWith('/media')) return `${BACKEND_BASE_URL}${relativeUrl}`
  return relativeUrl
}

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Helper function to get token from localStorage
const getAccessToken = () => {
  return localStorage.getItem('access_token')
}

const getRefreshToken = () => {
  return localStorage.getItem('refresh_token')
}

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken()
    if (token) {
      config.headers.Authorization = `JWT ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const refreshToken = getRefreshToken()
      if (refreshToken) {
        try {
          const response = await api.post('/users/jwt/refresh/', { refresh: refreshToken })
          const newAccessToken = response.data.access
          
          // Update token in localStorage
          localStorage.setItem('access_token', newAccessToken)
          
          // Retry the original request with new token
          originalRequest.headers.Authorization = `JWT ${newAccessToken}`
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh failed, logout user
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

// Add response interceptor to handle media URLs
api.interceptors.response.use(response => {
  // If response is array or object, process all media URLs
  const processMediaUrls = (data) => {
    if (Array.isArray(data)) {
      return data.map(item => processMediaUrls(item))
    } else if (data && typeof data === 'object') {
      const processed = { ...data }
      
      // Convert photo URLs in the photos array
      if (Array.isArray(processed.photos)) {
        processed.photos = processed.photos.map(photo => getAbsoluteMediaUrl(photo))
      }
      
      // Also handle single image_url if present
      if (processed.image_url) {
        processed.image_url = getAbsoluteMediaUrl(processed.image_url)
      }
      
      // Recursively process nested objects and arrays
      for (const key in processed) {
        if (processed[key] && typeof processed[key] === 'object') {
          processed[key] = processMediaUrls(processed[key])
        }
      }
      
      return processed
    }
    return data
  }

  if (response.data) {
    response.data = processMediaUrls(response.data)
  }
  return response
})

// Auth API
export const authAPI = {
  async login(credentials) {
    const response = await api.post('/users/jwt/create/', credentials)
    return response.data
  },

  async register(userData) {
    const response = await api.post('/users/register/', userData)
    return response.data
  },

  async refreshToken(refreshToken) {
    const response = await api.post('/users/jwt/refresh/', { refresh: refreshToken })
    return response.data
  },

  async getCurrentUser() {
    const response = await api.get('/users/users/me/')
    return response.data
  },

  async updateProfile(userData) {
    const response = await api.patch('/users/profile/', userData)
    return response.data
  },

  async changePassword(passwordData) {
    const response = await api.post('/users/change-password/', passwordData)
    return response.data
  },

  async mergeGuestCart(items) {
    // This endpoint will need to be implemented on the backend
    const response = await api.post('/carts/merge_guest_cart/', { items })
    return response.data
  }
}

// Products API
export const productsAPI = {
  async getCategories(params = {}) {
    const response = await api.get('/products/categories/', { params });
    return response.data;
  },

  async createCategory(categoryData) {
    const response = await api.post('/products/categories/', categoryData);
    return response.data;
  },

  async updateCategory(id, categoryData) {
    const response = await api.patch(`/products/categories/${id}/`, categoryData);
    return response.data;
  },

  async deleteCategory(id) {
    const response = await api.delete(`/products/categories/${id}/`);
    return response.data;
  },

  async getProducts(params = {}) {
    const response = await api.get('/products/items/', { params })
    return response.data
  },

  async getProductById(id) {
    const response = await api.get(`/products/items/${id}/`)
    return response.data
  },

  async createProduct(productData) {
    const response = await api.post('/products/items/', productData)
    return response.data
  },

  async getListings(params = {}) {
    const response = await api.get('/products/listings/', { params })
    return response.data
  },

  async getListingById(id) {
    const response = await api.get(`/products/listings/${id}/`)
    return response.data
  },

  async createListing(listingData) {
    const response = await api.post('/products/listings/', listingData)
    return response.data
  },

  async updateListing(id, listingData) {
    const response = await api.patch(`/products/listings/${id}/`, listingData)
    return response.data
  },

  async deleteListing(id) {
    const response = await api.delete(`/products/listings/${id}/`)
    return response.data
  },

  async getMyListings(params = {}) {
    const response = await api.get('/products/listings/my_listings/', { params })
    return response.data
  },

  async getListingsByFarm(farmId) {
    const response = await api.get('/products/listings/by_farm/', { params: { farm_id: farmId } })
    return response.data
  },

  async markListingSoldOut(id) {
    const response = await api.post(`/products/listings/${id}/mark_sold_out/`)
    return response.data
  },

  async markListingAvailable(id) {
    const response = await api.post(`/products/listings/${id}/mark_available/`)
    return response.data
  },

  async markListingInactive(id) {
    const response = await api.post(`/products/listings/${id}/mark_inactive/`)
    return response.data
  },

  async markListingPreOrder(id) {
    const response = await api.post(`/products/listings/${id}/mark_pre_order/`)
    return response.data
  },

  async uploadPhoto(formData) {
    const response = await api.post('/products/listings/upload_photo/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }
}

// Cart API
export const cartAPI = {
  async getCart() {
    const response = await api.get('/carts/my_cart/')
    return response.data
  },

  async addToCart(listingId, quantity) {
    const response = await api.post('/carts/add_item/', {
      listing_id: listingId,
      quantity: parseFloat(quantity).toFixed(2) // Format to 2 decimal places
    })
    return response.data
  },

  async updateCartItem(itemId, quantity) {
    const response = await api.post('/carts/update_quantity/', {
      cart_item_id: itemId,
      quantity: parseFloat(quantity).toFixed(2) // Format to 2 decimal places
    })
    return response.data
  },

  async removeFromCart(itemId) {
    const response = await api.post('/carts/remove_item/', {
      cart_item_id: itemId
    })
    return response.data
  },

  async clearCart() {
    const response = await api.post('/carts/clear_cart/')
    return response.data
  },

  async estimateDeliveryFee(deliveryAddress) {
    const response = await api.post('/carts/estimate_delivery_fee/', {
      delivery_address: deliveryAddress
    })
    return response.data
  },

  async getAddressAutocomplete(query) {
    const response = await api.get(`/carts/address_autocomplete/?q=${encodeURIComponent(query)}`)
    return response.data
  }
}

// Orders API
export const ordersAPI = {
  async getOrders(params = {}) {
    const response = await api.get('/orders/orders/', { params })
    return response.data
  },

  async getOrderById(id) {
    const response = await api.get(`/orders/orders/${id}/`)
    return response.data
  },

  async createOrder(orderData) {
    const response = await api.post('/orders/orders/', orderData)
    return response.data
  },

  async updateOrderStatus(id, status) {
    const response = await api.patch(`/orders/orders/${id}/`, {
      order_status: status
    })
    return response.data
  },

  async cancelOrder(id) {
    const response = await api.patch(`/orders/orders/${id}/`, {
      order_status: 'cancelled'
    })
    return response.data
  }
}

// Farmer Orders API
export const farmerOrdersAPI = {
  async getOrderItems(params = {}) {
    const response = await api.get('/orders/farmer-order-items/', { params })
    return response.data
  },

  async getOrderItemById(id) {
    const response = await api.get(`/orders/farmer-order-items/${id}/`)
    return response.data
  },

  async updateOrderItemStatus(id, status) {
    const response = await api.patch(`/orders/farmer-order-items/${id}/`, {
      item_status: status
    })
    return response.data
  },

  async getPendingItems() {
    const response = await api.get('/orders/farmer-order-items/pending/')
    return response.data
  },

  async getHarvestedItems() {
    const response = await api.get('/orders/farmer-order-items/harvested/')
    return response.data
  },

  async getPackedItems() {
    const response = await api.get('/orders/farmer-order-items/packed/')
    return response.data
  }
}

// Farms API
export const farmsAPI = {
  async getFarms(params = {}) {
    const response = await api.get('/farms/', { params })
    return response.data
  },

  async getFarmById(id) {
    const response = await api.get(`/farms/${id}/`)
    return response.data
  },

  async createFarm(farmData) {
    const response = await api.post('/farms/', farmData)
    return response.data
  },

  async updateFarm(id, farmData) {
    const response = await api.patch(`/farms/${id}/`, farmData)
    return response.data
  },

  async deleteFarm(id) {
    const response = await api.delete(`/farms/${id}/`)
    return response.data
  },

  async getOrganicFarms() {
    const response = await api.get('/farms/', { params: { is_certified_organic: true } })
    return response.data
  },

  async getFarmsByWeatherZone(zone) {
    const response = await api.get('/farms/by_weather_zone/', { params: { zone } })
    return response.data
  }
}

// Locations API
export const locationsAPI = {
  async getLocations(params = {}) {
    const response = await api.get('/locations/', { params })
    return response.data
  },

  async getCounties() {
    const response = await api.get('/locations/counties/')
    return response.data
  },

  async getSubCounties(countyId) {
    const response = await api.get(`/locations/counties/${countyId}/sub_counties/`)
    return response.data
  },

  async createLocation(locationData) {
    const response = await api.post('/locations/', locationData)
    return response.data
  },

  async updateLocation(id, locationData) {
    const response = await api.patch(`/locations/${id}/`, locationData)
    return response.data
  },

  async deleteLocation(id) {
    const response = await api.delete(`/locations/${id}/`)
    return response.data
  }
}

// Payments API
export const paymentsAPI = {
  async getPaymentMethods() {
    const response = await api.get('/payments/methods/')
    return response.data
  },

  async createPaymentMethod(paymentData) {
    const response = await api.post('/payments/methods/', paymentData)
    return response.data
  },

  async processPayment(paymentData) {
    const response = await api.post('/payments/', paymentData)
    return response.data
  },

  async getPaymentStatus(paymentId) {
    const response = await api.get(`/payments/${paymentId}/`)
    return response.data
  },

  async initiateSTKPush(paymentData) {
    const response = await api.post('/payments/stk-push/', paymentData)
    return response.data
  },

  // M-Pesa specific payment methods
  async initiateMpesaPayment(paymentData) {
    const response = await api.post('/payments/transactions/initiate_mpesa_payment/', paymentData)
    return response.data
  },

  async checkMpesaStatus(transactionId) {
    const response = await api.get(`/payments/transactions/${transactionId}/check_mpesa_status/`)
    return response.data
  },

  async getPaymentTransaction(transactionId) {
    const response = await api.get(`/payments/transactions/${transactionId}/`)
    return response.data
  },

  // Payment Session API methods
  async createPaymentSession(sessionData) {
    const response = await api.post('/payments/sessions/', sessionData)
    return response.data
  },

  async getPaymentSession(sessionId) {
    const response = await api.get(`/payments/sessions/${sessionId}/`)
    return response.data
  },

  async initiateSessionPayment(sessionId, paymentData) {
    const response = await api.post(`/payments/sessions/${sessionId}/initiate_payment/`, paymentData)
    return response.data
  },

  async getSessionStatus(sessionId) {
    const response = await api.get(`/payments/sessions/${sessionId}/status/`)
    return response.data
  },

  async extendSession(sessionId, extensionData = {}) {
    const response = await api.post(`/payments/sessions/${sessionId}/extend_session/`, extensionData)
    return response.data
  }
}

// Delivery API
export const deliveryAPI = {
  async getDeliveries(params = {}) {
    const response = await api.get('/delivery/deliveries/', { params })
    return response.data
  },

  async getMyDeliveries(params = {}) {
    const response = await api.get('/delivery/deliveries/my_deliveries/', { params })
    return response.data
  },

  async getDeliveryById(id) {
    const response = await api.get(`/delivery/deliveries/${id}/`)
    return response.data
  },

  async updateDeliveryStatus(id, statusData) {
    const response = await api.patch(`/delivery/deliveries/${id}/`, statusData)
    return response.data
  },

  async assignRider(deliveryId, riderId) {
    const response = await api.post(`/delivery/deliveries/${deliveryId}/assign_rider/`, { rider_id: riderId })
    return response.data
  },

  async getAvailableRiders() {
    const response = await api.get('/delivery/deliveries/available_riders/')
    return response.data
  }
}

// Rider API  
export const riderAPI = {
  async getRiderDeliveries(params = {}) {
    const response = await api.get('/delivery/deliveries/my_deliveries/', { params })
    return response.data
  },

  async acceptDelivery(deliveryId) {
    const response = await api.post(`/delivery/deliveries/${deliveryId}/accept/`)
    return response.data
  },

  async updateLocation(deliveryId, locationData) {
    const response = await api.post(`/delivery/deliveries/${deliveryId}/update_location/`, locationData)
    return response.data
  },

  async completeDelivery(deliveryId) {
    const response = await api.post(`/delivery/deliveries/${deliveryId}/complete/`)
    return response.data
  }
}

// Admin Users API
export const usersAPI = {
  async getUsers(params = {}) {
    const response = await api.get('/users/admin/', { params })
    return response.data
  },

  async getUserById(id) {
    const response = await api.get(`/users/admin/${id}/`)
    return response.data
  },

  async createUser(userData) {
    const response = await api.post('/users/admin/', userData)
    return response.data
  },

  async updateUser(id, userData) {
    const response = await api.patch(`/users/admin/${id}/`, userData)
    return response.data
  },

  async deleteUser(id) {
    const response = await api.delete(`/users/admin/${id}/`)
    return response.data
  },

  async getUserStats() {
    const response = await api.get('/users/admin/stats/')
    return response.data
  },

  async exportUsers(filters = {}) {
    const response = await api.get('/users/admin/export/', { 
      params: filters,
      responseType: 'blob'
    })
    return response.data
  },

  async toggleUserStatus(id) {
    const response = await api.patch(`/users/admin/${id}/toggle_status/`)
    return response.data
  },

  async resetUserPassword(id, newPassword) {
    const response = await api.post(`/users/admin/${id}/reset_password/`, {
      new_password: newPassword
    })
    return response.data
  }
}

// Admin Orders API
export const adminOrdersAPI = {
  async getOrders(params = {}) {
    const response = await api.get('/orders/admin-orders/', { params })
    return response.data
  },

  async getOrderById(id) {
    const response = await api.get(`/orders/admin-orders/${id}/`)
    return response.data
  },

  async getOrderStats() {
    const response = await api.get('/orders/admin-orders/stats/')
    return response.data
  },

  async exportOrders(filters = {}) {
    const response = await api.get('/orders/admin-orders/export/', { 
      params: filters,
      responseType: 'blob'
    })
    return response.data
  },

  async updateOrderStatus(id, status) {
    const response = await api.patch(`/orders/admin-orders/${id}/update_status/`, {
      order_status: status
    })
    return response.data
  },

  async updatePaymentStatus(id, status) {
    const response = await api.patch(`/orders/admin-orders/${id}/update_payment_status/`, {
      payment_status: status
    })
    return response.data
  }
}

// Feedback/Reviews API
export const reviewsAPI = {
  async getReviews(params = {}) {
    const response = await api.get('/feedback/reviews/', { params })
    return response.data
  },

  async createReview(reviewData) {
    const response = await api.post('/feedback/reviews/', reviewData)
    return response.data
  },

  async updateReview(id, reviewData) {
    const response = await api.patch(`/feedback/reviews/${id}/`, reviewData)
    return response.data
  },

  async deleteReview(id) {
    const response = await api.delete(`/feedback/reviews/${id}/`)
    return response.data
  },

  async getMyReviews() {
    const response = await api.get('/feedback/reviews/my_reviews/')
    return response.data
  },

  async getProductReviews(productId) {
    const response = await api.get('/feedback/reviews/product_reviews/', { 
      params: { product_id: productId } 
    })
    return response.data
  },

  async getFarmerReviews(farmerId) {
    const response = await api.get('/feedback/reviews/farmer_reviews/', { 
      params: { farmer_id: farmerId } 
    })
    return response.data
  },

  async getRiderReviews(riderId) {
    const response = await api.get('/feedback/reviews/rider_reviews/', { 
      params: { rider_id: riderId } 
    })
    return response.data
  },

  async moderateReview(id, moderationData) {
    const response = await api.patch(`/feedback/reviews/${id}/moderate/`, moderationData)
    return response.data
  }
}

// Communication API
export const communicationAPI = {
  // Notifications
  async getNotifications(params = {}) {
    const response = await api.get('/communication/notifications/', { params })
    return response.data
  },

  async markNotificationRead(id) {
    const response = await api.post(`/communication/notifications/${id}/mark_read/`)
    return response.data
  },

  async markAllNotificationsRead() {
    const response = await api.post('/communication/notifications/mark_all_read/')
    return response.data
  },
  // Note: createNotification and bulkCreateNotifications are backend-only operations
  // as notifications are created by the NotificationService on the backend.
  // Frontend will only fetch and manage read status.

  // Messages
  async getMessages(params = {}) {
    const response = await api.get('/communication/messages/', { params })
    return response.data
  },

  async sendMessage(messageData) {
    const response = await api.post('/communication/messages/', messageData)
    return response.data
  },

  async getConversation(userId) {
    const response = await api.get('/communication/messages/conversation/', { 
      params: { user_id: userId } 
    })
    return response.data
  },

  async markMessageRead(id) {
    const response = await api.post(`/communication/messages/${id}/mark_read/`)
    return response.data
  },

  // Support Tickets
  async getSupportTickets(params = {}) {
    const response = await api.get('/communication/support-tickets/', { params })
    return response.data
  },

  async createSupportTicket(ticketData) {
    const response = await api.post('/communication/support-tickets/', ticketData)
    return response.data
  },

  async updateSupportTicket(id, ticketData) {
    const response = await api.patch(`/communication/support-tickets/${id}/`, ticketData)
    return response.data
  },

  async getUnassignedTickets() {
    const response = await api.get('/communication/support-tickets/unassigned/')
    return response.data
  },

  async getMyTickets() {
    const response = await api.get('/communication/support-tickets/assigned_to_me/')
    return response.data
  },

  async assignTicket(id, adminId) {
    const response = await api.post(`/communication/support-tickets/${id}/assign/`, {
      admin_id: adminId
    })
    return response.data
  },

  async resolveTicket(id, resolutionData) {
    const response = await api.post(`/communication/support-tickets/${id}/resolve/`, resolutionData)
    return response.data
  }
}

// Data Insights API
export const dataInsightsAPI = {
  // Market Prices
  async getMarketPrices(params = {}) {
    const response = await api.get('/data_insights/market-prices/', { params })
    return response.data
  },

  async createMarketPrice(priceData) {
    const response = await api.post('/data_insights/market-prices/', priceData)
    return response.data
  },

  async updateMarketPrice(id, priceData) {
    const response = await api.patch(`/data_insights/market-prices/${id}/`, priceData)
    return response.data
  },

  async deleteMarketPrice(id) {
    const response = await api.delete(`/data_insights/market-prices/${id}/`)
    return response.data
  },

  async getProductPrices(productId, days = 30) {
    const response = await api.get('/data_insights/market-prices/product_trends/', {
      params: { product_id: productId, days }
    })
    return response.data
  },

  async getLocationPrices(locationId, days = 30) {
    const response = await api.get('/data_insights/market-prices/location_trends/', {
      params: { location_id: locationId, days }
    })
    return response.data
  },

  async getLatestPrices() {
    const response = await api.get('/data_insights/market-prices/latest/')
    return response.data
  },

  // Weather Alerts
  async getWeatherAlerts(params = {}) {
    const response = await api.get('/data_insights/weather-alerts/', { params })
    return response.data
  },

  async createWeatherAlert(alertData) {
    const response = await api.post('/data_insights/weather-alerts/', alertData)
    return response.data
  },

  async updateWeatherAlert(id, alertData) {
    const response = await api.patch(`/data_insights/weather-alerts/${id}/`, alertData)
    return response.data
  },

  async deleteWeatherAlert(id) {
    const response = await api.delete(`/data_insights/weather-alerts/${id}/`)
    return response.data
  },

  async getActiveAlerts() {
    const response = await api.get('/data_insights/weather-alerts/active/')
    return response.data
  },

  async getUrgentAlerts() {
    const response = await api.get('/data_insights/weather-alerts/urgent/')
    return response.data
  }
}

// Finance API
export const financeAPI = {
  async getFarmerEarnings() {
    const response = await api.get('/finance/farmer-earnings/')
    return response.data
  },

  async getRiderEarnings() {
    const response = await api.get('/finance/rider-earnings/')
    return response.data
  },

  async getRiderTransactions(params = {}) {
    const response = await api.get('/finance/rider-transactions/', { params })
    return response.data
  },

  async createPayout(payoutData) {
    const response = await api.post('/finance/payouts/', payoutData)
    return response.data
  },

  async getPayouts(params = {}) {
    const response = await api.get('/finance/payouts/', { params })
    return response.data
  },

  async getPayoutById(id) {
    const response = await api.get(`/finance/payouts/${id}/`)
    return response.data
  },

  async getPayoutStats() {
    const response = await api.get('/finance/payouts/stats/')
    return response.data
  },

  async processPayout(payoutId, data) {
    const response = await api.post(`/finance/payouts/${payoutId}/process/`, data)
    return response.data
  },

  async failPayout(payoutId, notes) {
    const response = await api.post(`/finance/payouts/${payoutId}/fail/`, { notes })
    return response.data
  }
}

// System Settings API
export const settingsAPI = {
  async getSettings() {
    const response = await api.get('/core/settings/')
    return response.data
  },
  async updateSettings(settingsData) {
    const response = await api.post('/core/settings/update_bulk/', settingsData)
    return response.data
  }
}

// Admin API for dashboard and admin-specific operations
export const adminAPI = {
  async getUsers(params = {}) {
    const response = await api.get('/users/admin/', { params })
    return response.data
  },

  async getUserStats() {
    const response = await api.get('/users/admin/stats/')
    return response.data
  },

  async getOrders(params = {}) {
    const response = await api.get('/orders/admin-orders/', { params })
    return response.data
  },

  async getOrderStats() {
    const response = await api.get('/orders/admin-orders/stats/')
    return response.data
  },

  async updateOrderStatus(id, status) {
    const response = await api.patch(`/orders/admin-orders/${id}/status/`, { status })
    return response.data
  },

  async updatePaymentStatus(id, status) {
    const response = await api.patch(`/orders/admin-orders/${id}/payment/`, { status })
    return response.data
  },

  async getDashboardStats() {
    const [userStats, orderStats, financeStats] = await Promise.all([
      api.get('/users/admin/stats/').catch(() => ({ data: {} })),
      api.get('/orders/admin-orders/stats/').catch(() => ({ data: {} })),
      api.get('/finance/payouts/stats/').catch(() => ({ data: {} }))
    ])
    
    // Map the API responses to what the frontend expects
    const users = userStats.data || {}
    const orders = orderStats.data || {};
    const finance = financeStats.data || {};
    
    return {
      total_users: users.total || 0,
      customers_count: users.customers || 0,
      farmers_count: users.farmers || 0,
      riders_count: users.riders || 0,
      admins_count: users.admins || 0,
      
      total_orders: orders.orders.total || 0,
      orders_pending_payment: orders.payments.pending || 0,
      orders_confirmed: orders.orders.confirmed || 0,
      orders_processing: orders.orders.processing || 0,
      orders_out_for_delivery: orders.orders.out_for_delivery || 0,
      orders_delivered: orders.orders.delivered || 0,
      orders_cancelled: orders.orders.cancelled || 0,
      
      // Gross Revenue (Total Sales)
      total_gross_revenue: orders.gross_revenue.total || 0,
      monthly_gross_revenue: orders.gross_revenue.monthly || 0,

      // Platform Revenue (Net Revenue from Fees)
      total_platform_revenue: orders.platform_revenue.total || 0,
      monthly_platform_revenue: orders.platform_revenue.monthly || 0,
      total_platform_fees: orders.platform_revenue.total_platform_fees || 0,
      total_vat_on_platform_fees: orders.platform_revenue.total_vat_on_platform_fees || 0,
      total_transaction_fees: orders.platform_revenue.total_transaction_fees || 0,
      monthly_platform_fees: orders.platform_revenue.monthly_platform_fees || 0,
      monthly_vat_on_platform_fees: orders.platform_revenue.monthly_vat_on_platform_fees || 0,
      monthly_transaction_fees: orders.platform_revenue.monthly_transaction_fees || 0,
      
      // Delivery Fees Collected (Pass-through)
      total_delivery_fees_collected: orders.delivery_fees.total_collected || 0,
      monthly_delivery_fees_collected: orders.delivery_fees.monthly_collected || 0,
      
      total_deliveries: orders.orders.delivered || 0,
      active_deliveries: orders.orders.out_for_delivery || 0,

      total_payouts: finance.total_processed || 0,
      pending_payouts: finance.total_pending || 0,
      
      pending_orders: orders.orders.pending || 0,
      active_users: users.active || 0
    };
  },

  async getRecentOrders(limit = 5) {
    const response = await api.get('/orders/admin-orders/', { 
      params: { page_size: limit, ordering: '-created_at' } 
    })
    return response.data
  },

  async getRecentUsers(limit = 5) {
    const response = await api.get('/users/admin/', { 
      params: { page_size: limit, ordering: '-date_joined' } 
    })
    return response.data
  }
}
