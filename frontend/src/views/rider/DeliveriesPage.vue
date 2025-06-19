<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 py-12">
      <!-- Header -->
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-2xl font-bold text-gray-900">My Deliveries</h1>
        <div class="flex items-center space-x-4">
          <select 
            v-model="statusFilter"
            @change="loadDeliveries"
            class="form-input"
          >
            <option value="">All Statuses</option>
            <option value="pending_pickup">Pending Pickup</option>
            <option value="on_the_way">On The Way</option>
            <option value="delivered">Delivered</option>
            <option value="failed">Failed</option>
          </select>
          <button 
            @click="loadDeliveries"
            class="btn-secondary"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-2 bg-yellow-100 rounded-lg">
              <div class="h-6 w-6 text-yellow-600">⏳</div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Pending Pickup</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats.pending_pickup }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-2 bg-blue-100 rounded-lg">
              <div class="h-6 w-6 text-blue-600">🚗</div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">On The Way</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats.on_the_way }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 rounded-lg">
              <div class="h-6 w-6 text-green-600">✅</div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Delivered</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats.delivered }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-2 bg-red-100 rounded-lg">
              <div class="h-6 w-6 text-red-600">❌</div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Failed</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats.failed }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
        <p class="mt-4 text-gray-500">Loading deliveries...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="deliveries.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
        <div class="h-12 w-12 text-gray-400 mx-auto mb-4">📦</div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Deliveries Found</h3>
        <p class="text-gray-500">You don't have any deliveries matching the current filter.</p>
      </div>

      <!-- Deliveries List -->
      <div v-else class="space-y-6">
        <div 
          v-for="delivery in deliveries" 
          :key="delivery.delivery_id"
          class="bg-white rounded-lg shadow overflow-hidden"
        >
          <div class="p-6">
            <!-- Delivery Header -->
            <div class="flex justify-between items-start mb-4">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">
                  Order #{{ delivery.order_number }}
                </h3>
                <p class="text-sm text-gray-500">
                  Customer: {{ delivery.customer_name }} • 
                  Created: {{ formatDate(delivery.created_at) }}
                </p>
              </div>
              <div class="text-right">
                <span 
                  :class="getStatusBadgeClass(delivery.delivery_status)"
                  class="px-3 py-1 rounded-full text-sm font-medium"
                >
                  {{ getStatusLabel(delivery.delivery_status) }}
                </span>
              </div>
            </div>

            <!-- Delivery Details -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <!-- Pickup Information -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="font-medium text-gray-900 mb-3">📍 Delivery Address</h4>
                <div class="space-y-2 text-sm">
                  <p class="text-gray-900 font-medium">{{ delivery.delivery_location?.location_name }}</p>
                  <p class="text-gray-600">{{ delivery.delivery_location?.sub_location }}</p>
                  <p class="text-gray-600" v-if="delivery.delivery_location?.landmark">
                    Landmark: {{ delivery.delivery_location.landmark }}
                  </p>
                </div>
              </div>

              <!-- Timing Information -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="font-medium text-gray-900 mb-3">⏰ Timing</h4>
                <div class="space-y-2 text-sm">
                  <div v-if="delivery.pickup_time">
                    <p class="text-gray-600">Picked up at:</p>
                    <p class="text-gray-900 font-medium">{{ formatDateTime(delivery.pickup_time) }}</p>
                  </div>
                  <div v-if="delivery.delivery_time">
                    <p class="text-gray-600">Delivered at:</p>
                    <p class="text-gray-900 font-medium">{{ formatDateTime(delivery.delivery_time) }}</p>
                  </div>
                  <div v-if="!delivery.pickup_time && !delivery.delivery_time">
                    <p class="text-gray-600">Awaiting pickup</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Vehicle Information -->
            <div v-if="delivery.vehicle_details" class="bg-blue-50 rounded-lg p-4 mb-6">
              <h4 class="font-medium text-gray-900 mb-2">🚗 Vehicle</h4>
              <p class="text-sm text-gray-700">
                {{ delivery.vehicle_details.vehicle_type }} - {{ delivery.vehicle_details.registration_number }}
                <span v-if="delivery.vehicle_details.capacity_kg">
                  (Capacity: {{ delivery.vehicle_details.capacity_kg }}kg)
                </span>
              </p>
            </div>

            <!-- Delivery Notes -->
            <div v-if="delivery.delivery_notes" class="bg-yellow-50 rounded-lg p-4 mb-6">
              <h4 class="font-medium text-gray-900 mb-2">📝 Notes</h4>
              <p class="text-sm text-gray-700">{{ delivery.delivery_notes }}</p>
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-between items-center">
              <div class="flex space-x-3">
                <!-- Start Delivery -->
                <button
                  v-if="canUpdateToStatus(delivery.delivery_status, 'on_the_way')"
                  @click="updateDeliveryStatus(delivery.delivery_id, 'on_the_way')"
                  :disabled="updatingStatus === delivery.delivery_id"
                  class="btn-primary"
                >
                  🚗 Start Delivery
                </button>
                
                <!-- Mark as Delivered -->
                <button
                  v-if="canUpdateToStatus(delivery.delivery_status, 'delivered')"
                  @click="markAsDelivered(delivery)"
                  :disabled="updatingStatus === delivery.delivery_id"
                  class="btn-success"
                >
                  ✅ Mark Delivered
                </button>
                
                <!-- Mark as Failed -->
                <button
                  v-if="['pending_pickup', 'on_the_way'].includes(delivery.delivery_status)"
                  @click="markAsFailed(delivery)"
                  :disabled="updatingStatus === delivery.delivery_id"
                  class="btn-danger"
                >
                  ❌ Mark Failed
                </button>
                
                <!-- Contact Customer -->
                <a 
                  :href="`tel:${delivery.customer_phone || ''}`"
                  class="btn-secondary inline-flex items-center"
                >
                  📞 Call Customer
                </a>
              </div>
              
              <div class="text-sm text-gray-500">
                Last updated: {{ formatDateTime(delivery.updated_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMoreDeliveries && !loading" class="text-center mt-8">
        <button 
          @click="loadMoreDeliveries"
          class="btn-secondary"
        >
          Load More Deliveries
        </button>
      </div>
    </div>

    <!-- Delivery Notes Modal -->
    <div v-if="showNotesModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3 text-center">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Add Delivery Notes</h3>
          <textarea
            v-model="deliveryNotes"
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Add any notes about the delivery..."
          ></textarea>
          <div class="flex justify-center space-x-3 mt-4">
            <button
              @click="confirmStatusUpdate"
              :disabled="updatingStatus"
              class="btn-primary"
            >
              Confirm
            </button>
            <button
              @click="cancelStatusUpdate"
              class="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { deliveryAPI } from '@/services/api'

export default {
  name: 'DeliveriesPage',
  setup() {
    const loading = ref(true)
    const deliveries = ref([])
    const statusFilter = ref('')
    const currentPage = ref(1)
    const hasMoreDeliveries = ref(false)
    const updatingStatus = ref(null)
    
    // Modal state
    const showNotesModal = ref(false)
    const deliveryNotes = ref('')
    const pendingStatusUpdate = ref(null)

    // Computed statistics
    const stats = computed(() => {
      const counts = {
        pending_pickup: 0,
        on_the_way: 0,
        delivered: 0,
        failed: 0
      }
      
      deliveries.value.forEach(delivery => {
        if (counts.hasOwnProperty(delivery.delivery_status)) {
          counts[delivery.delivery_status]++
        }
      })
      
      return counts
    })

    // Methods
    const loadDeliveries = async (reset = true) => {
      if (reset) {
        currentPage.value = 1
        deliveries.value = []
      }
      
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          page_size: 10
        }
        
        if (statusFilter.value) {
          params.delivery_status = statusFilter.value
        }
        
        const response = await deliveryAPI.getMyDeliveries(params)
        
        if (reset) {
          deliveries.value = response.results || response
        } else {
          deliveries.value.push(...(response.results || response))
        }
        
        hasMoreDeliveries.value = response.next ? true : false
        
      } catch (error) {
        console.error('Failed to load deliveries:', error)
      } finally {
        loading.value = false
      }
    }

    const loadMoreDeliveries = () => {
      currentPage.value++
      loadDeliveries(false)
    }

    const updateDeliveryStatus = async (deliveryId, newStatus, notes = '') => {
      updatingStatus.value = deliveryId
      try {
        await deliveryAPI.updateDeliveryStatus(deliveryId, {
          delivery_status: newStatus,
          delivery_notes: notes
        })
        
        // Update local state
        const delivery = deliveries.value.find(d => d.delivery_id === deliveryId)
        if (delivery) {
          delivery.delivery_status = newStatus
          if (notes) delivery.delivery_notes = notes
          delivery.updated_at = new Date().toISOString()
          
          // Set timing fields
          if (newStatus === 'on_the_way' && !delivery.pickup_time) {
            delivery.pickup_time = new Date().toISOString()
          } else if (newStatus === 'delivered') {
            delivery.delivery_time = new Date().toISOString()
          }
        }
        
        console.log(`Delivery ${deliveryId} status updated to ${newStatus}`)
        
      } catch (error) {
        console.error('Failed to update delivery status:', error)
        alert('Failed to update status. Please try again.')
      } finally {
        updatingStatus.value = null
      }
    }

    const markAsDelivered = (delivery) => {
      showNotesModal.value = true
      deliveryNotes.value = delivery.delivery_notes || ''
      pendingStatusUpdate.value = {
        id: delivery.delivery_id,
        status: 'delivered'
      }
    }

    const markAsFailed = (delivery) => {
      showNotesModal.value = true
      deliveryNotes.value = delivery.delivery_notes || ''
      pendingStatusUpdate.value = {
        id: delivery.delivery_id,
        status: 'failed'
      }
    }

    const confirmStatusUpdate = async () => {
      if (pendingStatusUpdate.value) {
        await updateDeliveryStatus(
          pendingStatusUpdate.value.id,
          pendingStatusUpdate.value.status,
          deliveryNotes.value
        )
      }
      cancelStatusUpdate()
    }

    const cancelStatusUpdate = () => {
      showNotesModal.value = false
      deliveryNotes.value = ''
      pendingStatusUpdate.value = null
    }

    const canUpdateToStatus = (currentStatus, targetStatus) => {
      const validTransitions = {
        'pending_pickup': ['on_the_way', 'failed'],
        'on_the_way': ['delivered', 'failed'],
        'delivered': [],
        'failed': []
      }
      
      return validTransitions[currentStatus]?.includes(targetStatus) || false
    }

    const getStatusLabel = (status) => {
      const labels = {
        'pending_pickup': 'Pending Pickup',
        'on_the_way': 'On The Way',
        'delivered': 'Delivered',
        'failed': 'Failed'
      }
      return labels[status] || status
    }

    const getStatusBadgeClass = (status) => {
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

    // Lifecycle
    onMounted(() => {
      loadDeliveries()
    })

    return {
      loading,
      deliveries,
      statusFilter,
      hasMoreDeliveries,
      updatingStatus,
      showNotesModal,
      deliveryNotes,
      stats,
      loadDeliveries,
      loadMoreDeliveries,
      updateDeliveryStatus,
      markAsDelivered,
      markAsFailed,
      confirmStatusUpdate,
      cancelStatusUpdate,
      canUpdateToStatus,
      getStatusLabel,
      getStatusBadgeClass,
      formatDate,
      formatDateTime
    }
  }
}
</script>

<style scoped>
/* Styles will be added here if needed */
</style>
