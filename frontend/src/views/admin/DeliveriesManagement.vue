<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 sm:mb-8 space-y-4 sm:space-y-0">
        <div class="text-center sm:text-left">
          <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Deliveries Management</h1>
          <p class="mt-1 sm:mt-2 text-sm sm:text-base text-gray-600">Monitor and manage all delivery operations</p>
        </div>
        <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
          <button @click="exportDeliveries" 
                  class="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors text-sm">
            Export Data
          </button>
          <button @click="refreshData" 
                  :disabled="loading"
                  class="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 text-sm">
            Refresh
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-6">
          <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Total Deliveries</dt>
          <dd class="text-lg sm:text-2xl font-bold text-gray-900 mt-1">{{ stats.total || 0 }}</dd>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-6">
          <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Pending Pickup</dt>
          <dd class="text-lg sm:text-2xl font-bold text-yellow-600 mt-1">{{ stats.pending_pickup || 0 }}</dd>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-6">
          <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">On The Way</dt>
          <dd class="text-lg sm:text-2xl font-bold text-blue-600 mt-1">{{ stats.on_the_way || 0 }}</dd>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-6">
          <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Delivered</dt>
          <dd class="text-lg sm:text-2xl font-bold text-green-600 mt-1">{{ stats.delivered || 0 }}</dd>
        </div>
      </div>

      <!-- Filters and Search -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6 mb-6">
        <div class="space-y-4 sm:space-y-0 sm:grid sm:grid-cols-5 sm:gap-4">
          <div class="sm:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select v-model="filters.delivery_status" 
                    class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm">
              <option value="">All Status</option>
              <option value="pending_pickup">Pending Pickup</option>
              <option value="on_the_way">On The Way</option>
              <option value="delivered">Delivered</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div class="sm:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input v-model="filters.search" type="text" 
                   placeholder="Order number, customer..."
                   class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm">
          </div>
          <div class="flex flex-col sm:flex-row sm:items-end space-y-2 sm:space-y-0 sm:space-x-2">
            <button @click="loadDeliveries" 
                    class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors text-sm font-medium">
              Apply Filters
            </button>
            <button @click="resetFilters" 
                    class="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors text-sm font-medium">
              Reset
            </button>
          </div>
        </div>
      </div>

      <!-- Deliveries Table/Cards -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          <p class="mt-2 text-gray-600 text-sm">Loading deliveries...</p>
        </div>

        <div v-else-if="deliveries.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m13 0h-2M6 13h2"></path>
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900">No deliveries found</h3>
          <p class="mt-2 text-gray-600">No deliveries match your current filters.</p>
        </div>

        <!-- Mobile Card View -->
        <div v-else class="block sm:hidden">
          <div v-for="delivery in deliveries" :key="delivery.delivery_id" 
               class="border-b border-gray-200 p-4 hover:bg-gray-50">
            <div class="flex justify-between items-start mb-2">
              <div>
                <div class="text-sm font-medium text-gray-900">Delivery #{{ delivery.delivery_id }}</div>
                <div class="text-xs text-gray-500">{{ delivery.order_number }}</div>
              </div>
              <span :class="getDeliveryStatusClass(delivery.delivery_status)"
                    class="px-2 py-1 rounded-full text-xs font-medium">
                {{ getDeliveryStatusLabel(delivery.delivery_status) }}
              </span>
            </div>
            
            <div class="space-y-1 mb-3">
              <div class="text-sm text-gray-900">{{ delivery.customer_name }}</div>
              <div class="text-xs text-gray-500">{{ delivery.delivery_location?.location_name }}</div>
              <div class="text-xs text-gray-500">
                Rider: {{ delivery.rider_name || 'Unassigned' }}
              </div>
              <div class="text-xs text-gray-500">{{ formatDate(delivery.created_at) }}</div>
            </div>
            
            <div class="flex space-x-3">
              <button @click="viewDeliveryDetails(delivery)" 
                      class="text-blue-600 hover:text-blue-700 font-medium text-sm">
                View Details
              </button>
              <button v-if="!delivery.rider_name" 
                      @click="openAssignRiderModal(delivery)" 
                      class="text-green-600 hover:text-green-700 font-medium text-sm">
                Assign Rider
              </button>
            </div>
          </div>
        </div>

        <!-- Desktop Table View -->
        <div class="hidden sm:block overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Delivery ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Order
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Customer
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rider
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="delivery in deliveries" :key="delivery.delivery_id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">#{{ delivery.delivery_id }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ delivery.order_number }}</div>
                  <div class="text-xs text-gray-500">{{ formatDate(delivery.created_at) }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ delivery.customer_name }}</div>
                  <div class="text-xs text-gray-500">{{ delivery.delivery_location?.location_name }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div v-if="delivery.rider_name" class="text-sm text-gray-900">{{ delivery.rider_name }}</div>
                  <div v-else class="text-sm text-gray-500 italic">Unassigned</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getDeliveryStatusClass(delivery.delivery_status)"
                        class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ getDeliveryStatusLabel(delivery.delivery_status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div class="flex space-x-2">
                    <button @click="viewDeliveryDetails(delivery)" 
                            class="text-blue-600 hover:text-blue-700 font-medium">
                      View
                    </button>
                    <button v-if="!delivery.rider_name" 
                            @click="openAssignRiderModal(delivery)" 
                            class="text-green-600 hover:text-green-700 font-medium">
                      Assign
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Delivery Details Modal -->
      <div v-if="showDetailsModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 p-4">
        <div class="relative top-4 sm:top-20 mx-auto border w-full max-w-4xl shadow-lg rounded-md bg-white">
          <div class="p-4 sm:p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg sm:text-xl font-medium text-gray-900">
                Delivery Details #{{ selectedDelivery?.delivery_id }}
              </h3>
              <button @click="closeDetailsModal" class="text-gray-400 hover:text-gray-600">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <div v-if="selectedDelivery" class="space-y-4 sm:space-y-6">
              <!-- Order Information -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="font-medium text-gray-900 mb-3 flex items-center">
                  <span class="w-4 h-4 bg-blue-500 rounded mr-2"></span>
                  Order Information
                </h4>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span class="text-gray-600">Order Number:</span>
                    <span class="ml-2 font-medium">{{ selectedDelivery.order_number }}</span>
                  </div>
                  <div>
                    <span class="text-gray-600">Customer:</span>
                    <span class="ml-2 font-medium">{{ selectedDelivery.customer_name }}</span>
                  </div>
                </div>
              </div>

              <!-- Delivery Address -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="font-medium text-gray-900 mb-3 flex items-center">
                  <span class="w-4 h-4 bg-red-500 rounded mr-2"></span>
                  Delivery Address
                </h4>
                <div class="space-y-2 text-sm">
                  <p class="text-gray-900 font-medium">{{ selectedDelivery.delivery_location?.location_name }}</p>
                  <p class="text-gray-600">{{ selectedDelivery.delivery_location?.sub_location }}</p>
                </div>
              </div>

              <!-- Rider Information -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="font-medium text-gray-900 mb-3 flex items-center">
                  <span class="w-4 h-4 bg-green-500 rounded mr-2"></span>
                  Rider Information
                </h4>
                <div v-if="selectedDelivery.rider_name" class="space-y-2 text-sm">
                  <div>
                    <span class="text-gray-600">Rider:</span>
                    <span class="ml-2 font-medium">{{ selectedDelivery.rider_name }}</span>
                  </div>
                </div>
                <div v-else class="text-gray-500 italic">No rider assigned</div>
              </div>

              <!-- Timeline -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="font-medium text-gray-900 mb-3 flex items-center">
                  <span class="w-4 h-4 bg-purple-500 rounded mr-2"></span>
                  Delivery Timeline
                </h4>
                <div class="space-y-2 text-sm">
                  <div class="flex flex-col sm:flex-row sm:justify-between">
                    <span class="text-gray-600">Created:</span>
                    <span class="font-medium">{{ formatDateTime(selectedDelivery.created_at) }}</span>
                  </div>
                  <div v-if="selectedDelivery.pickup_time" class="flex flex-col sm:flex-row sm:justify-between">
                    <span class="text-gray-600">Picked up:</span>
                    <span class="font-medium">{{ formatDateTime(selectedDelivery.pickup_time) }}</span>
                  </div>
                  <div v-if="selectedDelivery.delivery_time" class="flex flex-col sm:flex-row sm:justify-between">
                    <span class="text-gray-600">Delivered:</span>
                    <span class="font-medium">{{ formatDateTime(selectedDelivery.delivery_time) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Assign Rider Modal -->
      <div v-if="showAssignRiderModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 p-4">
        <div class="relative top-4 sm:top-20 mx-auto border w-full max-w-md shadow-lg rounded-md bg-white">
          <div class="p-4 sm:p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-medium text-gray-900">Assign Rider</h3>
              <button @click="closeAssignRiderModal" class="text-gray-400 hover:text-gray-600">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <div v-if="deliveryToAssign">
              <p class="text-gray-600 mb-4 text-sm">
                Assign a rider to delivery #{{ deliveryToAssign.delivery_id }} 
                (Order #{{ deliveryToAssign.order_number }})
              </p>
              
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">Select Rider</label>
                <select v-model="selectedRiderId" 
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                  <option value="">-- Select a rider --</option>
                  <option v-for="rider in availableRiders" 
                          :key="rider.user_id" 
                          :value="rider.user_id">
                    {{ rider.full_name }} 
                    ({{ rider.active_deliveries_count }} active)
                    {{ rider.has_vehicle ? ' - Vehicle Available' : ' - No Vehicle' }}
                  </option>
                </select>
              </div>
              
              <div class="flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-3">
                <button @click="closeAssignRiderModal" 
                        class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 text-sm font-medium">
                  Cancel
                </button>
                <button @click="assignRider" 
                        :disabled="!selectedRiderId || assigning"
                        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium">
                  {{ assigning ? 'Assigning...' : 'Assign Rider' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Toast Notification -->
    <transition enter-active-class="transition ease-out duration-300"
                enter-from-class="transform opacity-0 translate-y-full"
                enter-to-class="transform opacity-100 translate-y-0"
                leave-active-class="transition ease-in duration-300"
                leave-from-class="transform opacity-100 translate-y-0"
                leave-to-class="transform opacity-0 translate-y-full">
      <div v-if="showToast" 
           :class="{ 'bg-green-500': toastType === 'success', 'bg-red-500': toastType === 'error', 'bg-blue-500': toastType === 'info' }"
           class="fixed bottom-4 right-4 text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center space-x-3">
        <svg v-if="toastType === 'success'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <svg v-else-if="toastType === 'error'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <svg v-else-if="toastType === 'info'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <p class="font-medium">{{ toastMessage }}</p>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { deliveryAPI } from '@/services/api'

export default {
  name: 'DeliveriesManagement',
  setup() {
    const loading = ref(true)
    const deliveries = ref([])
    const stats = ref({})
    const showDetailsModal = ref(false)
    const selectedDelivery = ref(null)
    
    // Assign rider modal state
    const showAssignRiderModal = ref(false)
    const deliveryToAssign = ref(null)
    const selectedRiderId = ref('')
    const availableRiders = ref([])
    const assigning = ref(false)

    // Toast notification state
    const showToast = ref(false)
    const toastMessage = ref('')
    const toastType = ref('success') // 'success' or 'error'
    
    const filters = ref({
      delivery_status: '',
      search: ''
    })

    const loadDeliveries = async () => {
      loading.value = true
      try {
        const params = { ...filters.value }
        
        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (params[key] === '') delete params[key]
        })
        
        const response = await deliveryAPI.getDeliveries(params)
        console.log('Deliveries API response:', response)
        
        // Handle different response structures
        if (Array.isArray(response)) {
          deliveries.value = response
        } else if (response.results) {
          deliveries.value = response.results
        } else if (response.data) {
          deliveries.value = response.data
        } else {
          deliveries.value = []
        }
        
        console.log('Parsed deliveries:', deliveries.value)
        
        // Calculate stats
        calculateStats()
        
      } catch (error) {
        console.error('Failed to load deliveries:', error)
        deliveries.value = []
      } finally {
        loading.value = false
      }
    }

    const calculateStats = () => {
      const total = deliveries.value.length
      const pending_pickup = deliveries.value.filter(d => d.delivery_status === 'pending_pickup').length
      const on_the_way = deliveries.value.filter(d => d.delivery_status === 'on_the_way').length
      const delivered = deliveries.value.filter(d => d.delivery_status === 'delivered').length
      
      stats.value = { total, pending_pickup, on_the_way, delivered }
    }

    const resetFilters = () => {
      filters.value = {
        delivery_status: '',
        search: ''
      }
      loadDeliveries()
    }

    const refreshData = () => {
      loadDeliveries()
    }

    const viewDeliveryDetails = (delivery) => {
      selectedDelivery.value = delivery
      showDetailsModal.value = true
    }

    const closeDetailsModal = () => {
      showDetailsModal.value = false
      selectedDelivery.value = null
    }

    const exportDeliveries = () => {
      alert('Export feature coming soon!')
    }

    const openAssignRiderModal = async (delivery) => {
      deliveryToAssign.value = delivery
      showAssignRiderModal.value = true
      await loadAvailableRiders()
    }

    const closeAssignRiderModal = () => {
      showAssignRiderModal.value = false
      deliveryToAssign.value = null
      selectedRiderId.value = ''
      availableRiders.value = []
    }

    const loadAvailableRiders = async () => {
      try {
        const riders = await deliveryAPI.getAvailableRiders()
        availableRiders.value = riders
      } catch (error) {
        console.error('Failed to load available riders:', error)
        alert('Failed to load available riders')
      }
    }

    const assignRider = async () => {
      if (!selectedRiderId.value || !deliveryToAssign.value) return
      
      assigning.value = true
      try {
        const response = await deliveryAPI.assignRider(deliveryToAssign.value.delivery_id, selectedRiderId.value)
        
        // Update the delivery in the local list
        const deliveryIndex = deliveries.value.findIndex(d => d.delivery_id === deliveryToAssign.value.delivery_id)
        if (deliveryIndex !== -1) {
          deliveries.value[deliveryIndex] = response.delivery
        }
        
        // Show success message
        showToast.value = true
        toastMessage.value = response.detail || 'Rider assigned successfully!'
        toastType.value = 'success'
        setTimeout(() => { showToast.value = false }, 3000) // Hide after 3 seconds
        
        closeAssignRiderModal()
        
      } catch (error) {
        console.error('Failed to assign rider:', error)
        showToast.value = true
        toastMessage.value = error.response?.data?.detail || 'Failed to assign rider'
        toastType.value = 'error'
        setTimeout(() => { showToast.value = false }, 3000) // Hide after 3 seconds
      } finally {
        assigning.value = false
      }
    }

    const getDeliveryStatusLabel = (status) => {
      const labels = {
        'pending_pickup': 'Pending Pickup',
        'on_the_way': 'On The Way',
        'delivered': 'Delivered',
        'failed': 'Failed'
      }
      return labels[status] || status
    }

    const getDeliveryStatusClass = (status) => {
      const classes = {
        'pending_pickup': 'bg-yellow-100 text-yellow-800',
        'on_the_way': 'bg-blue-100 text-blue-800',
        'delivered': 'bg-green-100 text-green-800',
        'failed': 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      loadDeliveries()
    })

    return {
      loading,
      deliveries,
      stats,
      filters,
      showDetailsModal,
      selectedDelivery,
      showAssignRiderModal,
      deliveryToAssign,
      selectedRiderId,
      availableRiders,
      assigning,
      loadDeliveries,
      resetFilters,
      refreshData,
      viewDeliveryDetails,
      closeDetailsModal,
      openAssignRiderModal,
      closeAssignRiderModal,
      assignRider,
      exportDeliveries,
      getDeliveryStatusLabel,
      getDeliveryStatusClass,
      formatDate,
      formatDateTime,
      showToast,
      toastMessage,
      toastType
    }
  }
}
</script>
