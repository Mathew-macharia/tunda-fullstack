<template>
  <div class="min-h-screen bg-gray-50 py-4 sm:py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="sm:flex sm:items-center sm:justify-between mb-6 sm:mb-8">
        <div class="min-w-0 flex-1">
          <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">My Farms</h1>
          <p class="mt-1 sm:mt-2 text-sm sm:text-base text-gray-600">Manage your farm profiles and information</p>
        </div>
        <div class="mt-4 sm:mt-0 sm:ml-4">
          <button
            @click="openCreateModal"
            class="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
          >
            <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
            Add New Farm
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
        <div class="flex">
          <ExclamationTriangleIcon class="h-5 w-5 text-red-400 flex-shrink-0" />
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error loading farms</h3>
            <p class="mt-1 text-sm text-red-700">{{ error }}</p>
            <button 
              @click="loadFarms"
              class="mt-2 text-sm text-red-600 hover:text-red-500 underline"
            >
              Try again
            </button>
          </div>
        </div>
      </div>

      <!-- Farms Grid -->
      <div v-else-if="farms.length > 0" class="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="farm in farms"
          :key="farm.farm_id"
          class="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow duration-200"
        >
          <div class="p-4 sm:p-6">
            <!-- Farm Header -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center min-w-0 flex-1">
                <div class="flex-shrink-0">
                  <HomeIcon class="h-6 w-6 sm:h-8 sm:w-8 text-green-600" />
                </div>
                <div class="ml-3 min-w-0 flex-1">
                  <h3 class="text-base sm:text-lg font-medium text-gray-900 truncate">{{ farm.farm_name }}</h3>
                  <p class="text-xs sm:text-sm text-gray-500">Farm ID: #{{ farm.farm_id }}</p>
                </div>
              </div>
              <div class="flex items-center space-x-2 ml-2">
                <span v-if="farm.is_certified_organic" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <CheckBadgeIcon class="w-3 h-3 mr-1" />
                  <span class="hidden xs:inline">Organic</span>
                  <span class="xs:hidden">Org</span>
                </span>
                <button
                  @click="editFarm(farm)"
                  class="text-gray-400 hover:text-gray-600 p-1"
                  title="Edit Farm"
                >
                  <PencilIcon class="h-4 w-4 sm:h-5 sm:w-5" />
                </button>
              </div>
            </div>

            <!-- Farm Details -->
            <div class="space-y-2 sm:space-y-3">
              <div class="flex items-center text-xs sm:text-sm text-gray-600">
                <MapPinIcon class="h-4 w-4 mr-2 text-gray-400 flex-shrink-0" />
                <span class="truncate">{{ farm.location_name }}</span>
              </div>
              
              <div class="flex items-center text-xs sm:text-sm text-gray-600">
                <HomeIcon class="h-4 w-4 mr-2 text-gray-400 flex-shrink-0" />
                <span>{{ farm.total_acreage }} acres</span>
              </div>

              <div v-if="farm.soil_type" class="flex items-center text-xs sm:text-sm text-gray-600">
                <GlobeAltIcon class="h-4 w-4 mr-2 text-gray-400 flex-shrink-0" />
                <span class="truncate">{{ formatSoilType(farm.soil_type) }} soil</span>
              </div>

              <div v-if="farm.water_source" class="flex items-center text-xs sm:text-sm text-gray-600">
                <BeakerIcon class="h-4 w-4 mr-2 text-gray-400 flex-shrink-0" />
                <span class="truncate">{{ formatWaterSource(farm.water_source) }}</span>
              </div>

              <div v-if="farm.weather_zone" class="flex items-center text-xs sm:text-sm text-gray-600">
                <CloudIcon class="h-4 w-4 mr-2 text-gray-400 flex-shrink-0" />
                <span>Weather Zone {{ farm.weather_zone }}</span>
              </div>
            </div>

            <!-- Farm Stats -->
            <div class="mt-4 sm:mt-6 grid grid-cols-2 gap-3 sm:gap-4">
              <div class="text-center bg-gray-50 rounded-lg p-2 sm:p-3">
                <p class="text-base sm:text-lg font-semibold text-gray-900">{{ farm.active_listings || 0 }}</p>
                <p class="text-xs text-gray-500">Active Listings</p>
              </div>
              <div class="text-center bg-gray-50 rounded-lg p-2 sm:p-3">
                <p class="text-base sm:text-lg font-semibold text-gray-900">{{ farm.total_orders || 0 }}</p>
                <p class="text-xs text-gray-500">Total Orders</p>
              </div>
            </div>

            <!-- Actions - Removed duplicate Edit button -->
            <div class="mt-4 sm:mt-6">
              <button
                @click="viewFarmDetails(farm)"
                class="w-full bg-green-600 border border-transparent rounded-md px-3 py-2 text-sm font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 transition-colors"
              >
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <HomeIcon class="mx-auto h-16 w-16 sm:h-24 sm:w-24 text-gray-400" />
        <h3 class="mt-4 sm:mt-6 text-lg font-medium text-gray-900">No farms registered</h3>
        <p class="mt-2 text-sm sm:text-base text-gray-500 px-4">Get started by creating your first farm profile.</p>
        <div class="mt-4 sm:mt-6">
          <button
            @click="openCreateModal"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
          >
            <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
            Create Your First Farm
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Farm Modal -->
    <FarmModal 
      v-if="showModal"
      :farm="selectedFarm"
      @close="closeModal"
      @save="handleSaveFarm"
    />

    <!-- Farm Details Modal -->
    <FarmDetailsModal
      v-if="showDetailsModal"
      :farm="selectedFarm"
      @close="showDetailsModal = false"
      @edit="editFarm"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { farmsAPI } from '@/services/api'
import {
  PlusIcon,
  HomeIcon,
  MapPinIcon,
  PencilIcon,
  ExclamationTriangleIcon,
  CheckBadgeIcon,
  GlobeAltIcon,
  BeakerIcon,
  CloudIcon
} from '@heroicons/vue/24/outline'
import FarmModal from '@/components/farmer/FarmModal.vue'
import FarmDetailsModal from '@/components/farmer/FarmDetailsModal.vue'

// State
const loading = ref(true)
const error = ref(null)
const farms = ref([])
const showModal = ref(false)
const showDetailsModal = ref(false)
const selectedFarm = ref(null)

// Methods
const loadFarms = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await farmsAPI.getFarms()
    farms.value = Array.isArray(response) ? response : response.results || []
  } catch (err) {
    console.error('Error loading farms:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load farms'
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  selectedFarm.value = null
  showModal.value = true
}

const editFarm = (farm) => {
  selectedFarm.value = farm
  showModal.value = true
  showDetailsModal.value = false
}

const viewFarmDetails = (farm) => {
  selectedFarm.value = farm
  showDetailsModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedFarm.value = null
}

const handleSaveFarm = async (farmData) => {
  try {
    if (selectedFarm.value) {
      // Update existing farm
      await farmsAPI.updateFarm(selectedFarm.value.farm_id, farmData)
    } else {
      // Create new farm
      await farmsAPI.createFarm(farmData)
    }
    
    closeModal()
    await loadFarms()
  } catch (err) {
    console.error('Error saving farm:', err)
    throw err
  }
}

const formatSoilType = (soilType) => {
  const soilTypes = {
    'clay': 'Clay',
    'sandy': 'Sandy',
    'loamy': 'Loamy',
    'silt': 'Silt',
    'peaty': 'Peaty',
    'chalky': 'Chalky'
  }
  return soilTypes[soilType] || soilType
}

const formatWaterSource = (waterSource) => {
  const waterSources = {
    'borehole': 'Borehole',
    'river': 'River',
    'rain': 'Rain Water',
    'well': 'Well',
    'municipal': 'Municipal Supply',
    'dam': 'Dam'
  }
  return waterSources[waterSource] || waterSource
}

onMounted(async () => {
  await loadFarms()
})
</script>