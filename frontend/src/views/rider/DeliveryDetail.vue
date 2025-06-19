<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <button
              @click="$router.go(-1)"
              class="flex items-center text-indigo-600 hover:text-indigo-700 mb-4"
            >
              <ArrowLeftIcon class="h-5 w-5 mr-2" />
              Back to Deliveries
            </button>
            <h1 class="text-3xl font-bold text-gray-900">
              Delivery #{{ delivery?.delivery_id }}
            </h1>
            <p class="mt-2 text-gray-600">
              Order #{{ delivery?.order?.order_number }}
            </p>
          </div>
          <div class="flex space-x-3">
            <button
              v-if="delivery?.delivery_status === 'assigned'"
              @click="acceptDelivery"
              class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Accept Delivery
            </button>
            <button
              v-if="delivery?.delivery_status === 'picked_up'"
              @click="markDelivered"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Mark as Delivered
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
        <div class="flex">
          <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error loading delivery</h3>
            <p class="mt-1 text-sm text-red-700">{{ error }}</p>
            <button 
              @click="loadDelivery"
              class="mt-2 text-sm text-red-600 hover:text-red-500 underline"
            >
              Try again
            </button>
          </div>
        </div>
      </div>

      <!-- Delivery Content -->
      <div v-else-if="delivery" class="space-y-6">
        <!-- Status Card -->
        <div class="bg-white shadow rounded-lg p-6">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-medium text-gray-900">Delivery Status</h2>
              <p class="mt-1 text-sm text-gray-500">Current status of this delivery</p>
            </div>
            <span :class="getStatusClass(delivery.delivery_status)" class="px-3 py-1 text-sm font-medium rounded-full">
              {{ formatStatus(delivery.delivery_status) }}
            </span>
          </div>

          <!-- Status Timeline -->
          <div class="mt-6">
            <div class="flow-root">
              <ul class="-mb-8">
                <li v-for="(step, stepIdx) in statusSteps" :key="step.id" class="relative pb-8">
                  <div v-if="stepIdx !== statusSteps.length - 1" class="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"></div>
                  <div class="relative flex space-x-3">
                    <div>
                      <span :class="step.completed ? 'bg-green-500' : step.current ? 'bg-blue-500' : 'bg-gray-300'" class="h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white">
                        <component :is="step.icon" class="h-4 w-4 text-white" />
                      </span>
                    </div>
                    <div class="min-w-0 flex-1 pt-1.5">
                      <p :class="step.completed || step.current ? 'text-gray-900' : 'text-gray-500'" class="text-sm font-medium">
                        {{ step.name }}
                      </p>
                      <p class="text-sm text-gray-500">{{ step.description }}</p>
                      <p v-if="step.time" class="text-xs text-gray-400 mt-1">
                        {{ formatDate(step.time) }}
                      </p>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Customer Information -->
        <div class="bg-white shadow rounded-lg p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Customer Information</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-500">Name</label>
              <p class="mt-1 text-sm text-gray-900">
                {{ delivery.order?.customer?.first_name }} {{ delivery.order?.customer?.last_name }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Phone Number</label>
              <p class="mt-1 text-sm text-gray-900">
                <a :href="`tel:${delivery.order?.customer?.phone_number}`" class="text-indigo-600 hover:text-indigo-700">
                  {{ delivery.order?.customer?.phone_number }}
                </a>
              </p>
            </div>
          </div>
        </div>

        <!-- Delivery Address -->
        <div class="bg-white shadow rounded-lg p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Delivery Address</h2>
          <div class="flex items-start space-x-3">
            <MapPinIcon class="h-5 w-5 text-gray-400 mt-1" />
            <div class="flex-1">
              <p class="text-sm text-gray-900">{{ delivery.delivery_address }}</p>
              <div class="mt-4">
                <button
                  @click="openMaps"
                  class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  Open in Maps
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Items -->
        <div class="bg-white shadow rounded-lg p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Order Items</h2>
          <div class="space-y-4">
            <div v-for="item in delivery.order?.items" :key="item.order_item_id" class="flex items-center justify-between border-b border-gray-200 pb-4">
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">{{ item.product_name }}</p>
                <p class="text-sm text-gray-500">From {{ item.farm_name }}</p>
                <p class="text-sm text-gray-500">Quality: {{ formatQuality(item.quality_grade) }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-medium text-gray-900">
                  {{ item.quantity }} {{ item.product_unit }}
                </p>
                <p class="text-sm text-gray-500">
                  KES {{ formatCurrency(item.unit_price) }} each
                </p>
              </div>
            </div>
          </div>
          
          <!-- Order Total -->
          <div class="mt-4 border-t border-gray-200 pt-4">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Subtotal</span>
              <span class="text-gray-900">KES {{ formatCurrency(delivery.order?.subtotal) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Delivery Fee</span>
              <span class="text-gray-900">KES {{ formatCurrency(delivery.delivery_fee) }}</span>
            </div>
            <div class="flex justify-between text-sm font-medium">
              <span class="text-gray-900">Total</span>
              <span class="text-gray-900">KES {{ formatCurrency(delivery.order?.total_amount) }}</span>
            </div>
          </div>
        </div>

        <!-- Delivery Notes -->
        <div v-if="delivery.delivery_notes" class="bg-white shadow rounded-lg p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Delivery Notes</h2>
          <p class="text-sm text-gray-700">{{ delivery.delivery_notes }}</p>
        </div>

        <!-- Actions -->
        <div class="bg-white shadow rounded-lg p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Actions</h2>
          <div class="space-y-3">
            <button
              v-if="delivery.delivery_status === 'assigned'"
              @click="acceptDelivery"
              class="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Accept This Delivery
            </button>
            
            <button
              v-if="delivery.delivery_status === 'picked_up'"
              @click="updateLocation"
              class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Update Location
            </button>
            
            <button
              v-if="delivery.delivery_status === 'picked_up'"
              @click="markDelivered"
              class="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Mark as Delivered
            </button>
            
            <button
              v-if="['assigned', 'picked_up'].includes(delivery.delivery_status)"
              @click="reportProblem"
              class="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Report Problem
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Update Location Modal -->
    <LocationUpdateModal
      v-if="showLocationModal"
      :delivery="delivery"
      @close="showLocationModal = false"
      @save="handleLocationUpdate"
    />

    <!-- Problem Report Modal -->
    <ProblemReportModal
      v-if="showProblemModal"
      :delivery="delivery"
      @close="showProblemModal = false"
      @save="handleProblemReport"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { riderAPI } from '@/services/api'
import {
  ArrowLeftIcon,
  ExclamationTriangleIcon,
  MapPinIcon,
  ClockIcon,
  TruckIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'
import LocationUpdateModal from '@/components/rider/LocationUpdateModal.vue'
import ProblemReportModal from '@/components/rider/ProblemReportModal.vue'

const route = useRoute()

// State
const loading = ref(true)
const error = ref(null)
const delivery = ref(null)
const showLocationModal = ref(false)
const showProblemModal = ref(false)

// Computed
const statusSteps = computed(() => {
  if (!delivery.value) return []
  
  const currentStatus = delivery.value.delivery_status
  const steps = [
    { 
      id: 'assigned', 
      name: 'Assigned', 
      description: 'Delivery assigned to rider',
      icon: ClockIcon,
      completed: ['picked_up', 'in_transit', 'delivered'].includes(currentStatus),
      current: currentStatus === 'assigned',
      time: delivery.value.created_at
    },
    { 
      id: 'picked_up', 
      name: 'Picked Up', 
      description: 'Order picked up from farmer',
      icon: TruckIcon,
      completed: ['in_transit', 'delivered'].includes(currentStatus),
      current: currentStatus === 'picked_up',
      time: currentStatus === 'picked_up' ? delivery.value.updated_at : null
    },
    { 
      id: 'in_transit', 
      name: 'In Transit', 
      description: 'On the way to customer',
      icon: TruckIcon,
      completed: currentStatus === 'delivered',
      current: currentStatus === 'in_transit',
      time: currentStatus === 'in_transit' ? delivery.value.updated_at : null
    },
    { 
      id: 'delivered', 
      name: 'Delivered', 
      description: 'Delivered to customer',
      icon: CheckCircleIcon,
      completed: currentStatus === 'delivered',
      current: false,
      time: currentStatus === 'delivered' ? delivery.value.updated_at : null
    }
  ]
  
  return steps
})

// Methods
const loadDelivery = async () => {
  loading.value = true
  error.value = null
  
  try {
    const deliveryId = route.params.id
    const response = await riderAPI.getDeliveryById(deliveryId)
    delivery.value = response
  } catch (err) {
    console.error('Error loading delivery:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load delivery'
  } finally {
    loading.value = false
  }
}

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

const formatStatus = (status) => {
  const statusMap = {
    'assigned': 'Assigned',
    'picked_up': 'Picked Up',
    'in_transit': 'In Transit',
    'delivered': 'Delivered',
    'failed': 'Failed'
  }
  return statusMap[status] || status
}

const formatQuality = (quality) => {
  const qualityMap = {
    'premium': 'Premium',
    'standard': 'Standard',
    'economy': 'Economy'
  }
  return qualityMap[quality] || quality
}

const getStatusClass = (status) => {
  const statusClasses = {
    'assigned': 'bg-blue-100 text-blue-800',
    'picked_up': 'bg-indigo-100 text-indigo-800',
    'in_transit': 'bg-purple-100 text-purple-800',
    'delivered': 'bg-green-100 text-green-800',
    'failed': 'bg-red-100 text-red-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const acceptDelivery = async () => {
  try {
    await riderAPI.acceptDelivery(delivery.value.delivery_id)
    await loadDelivery()
  } catch (err) {
    console.error('Error accepting delivery:', err)
    error.value = 'Failed to accept delivery'
  }
}

const markDelivered = async () => {
  try {
    await riderAPI.completeDelivery(delivery.value.delivery_id)
    await loadDelivery()
  } catch (err) {
    console.error('Error marking delivery as delivered:', err)
    error.value = 'Failed to mark delivery as delivered'
  }
}

const updateLocation = () => {
  showLocationModal.value = true
}

const reportProblem = () => {
  showProblemModal.value = true
}

const handleLocationUpdate = async (locationData) => {
  try {
    await riderAPI.updateLocation(delivery.value.delivery_id, locationData)
    showLocationModal.value = false
    await loadDelivery()
  } catch (err) {
    console.error('Error updating location:', err)
    error.value = 'Failed to update location'
  }
}

const handleProblemReport = async (problemData) => {
  try {
    // Update delivery status to failed with notes
    await riderAPI.updateDeliveryStatus(delivery.value.delivery_id, {
      delivery_status: 'failed',
      delivery_notes: problemData.notes
    })
    showProblemModal.value = false
    await loadDelivery()
  } catch (err) {
    console.error('Error reporting problem:', err)
    error.value = 'Failed to report problem'
  }
}

const openMaps = () => {
  const address = encodeURIComponent(delivery.value.delivery_address)
  const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${address}`
  window.open(mapsUrl, '_blank')
}

onMounted(() => {
  loadDelivery()
})
</script> 