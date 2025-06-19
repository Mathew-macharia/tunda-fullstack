<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Farm Details</h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>
      </div>

      <div v-if="farm" class="px-6 py-4">
        <!-- Farm Header -->
        <div class="mb-6">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ farm.farm_name }}</h2>
          <div class="flex items-center text-sm text-gray-600">
            <MapPinIcon class="h-4 w-4 mr-1" />
            <span>{{ farm.location?.county }}, {{ farm.location?.sub_county }}</span>
          </div>
        </div>

        <!-- Farm Description -->
        <div v-if="farm.description" class="mb-6">
          <h4 class="text-sm font-medium text-gray-900 mb-2">Description</h4>
          <p class="text-sm text-gray-600">{{ farm.description }}</p>
        </div>

        <!-- Farm Details Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <!-- Area Information -->
          <div class="space-y-4">
            <h4 class="text-sm font-medium text-gray-900">Area Information</h4>
            
            <div v-if="farm.total_area" class="flex justify-between">
              <span class="text-sm text-gray-600">Total Area:</span>
              <span class="text-sm font-medium text-gray-900">{{ farm.total_area }} acres</span>
            </div>
            
            <div v-if="farm.cultivated_area" class="flex justify-between">
              <span class="text-sm text-gray-600">Cultivated Area:</span>
              <span class="text-sm font-medium text-gray-900">{{ farm.cultivated_area }} acres</span>
            </div>
            
            <div v-if="farm.total_area && farm.cultivated_area" class="flex justify-between">
              <span class="text-sm text-gray-600">Utilization:</span>
              <span class="text-sm font-medium text-gray-900">
                {{ Math.round((farm.cultivated_area / farm.total_area) * 100) }}%
              </span>
            </div>
          </div>

          <!-- Farm Characteristics -->
          <div class="space-y-4">
            <h4 class="text-sm font-medium text-gray-900">Farm Characteristics</h4>
            
            <div v-if="farm.soil_type" class="flex justify-between">
              <span class="text-sm text-gray-600">Soil Type:</span>
              <span class="text-sm font-medium text-gray-900">{{ formatSoilType(farm.soil_type) }}</span>
            </div>
            
            <div v-if="farm.water_source" class="flex justify-between">
              <span class="text-sm text-gray-600">Water Source:</span>
              <span class="text-sm font-medium text-gray-900">{{ formatWaterSource(farm.water_source) }}</span>
            </div>
            
            <div v-if="farm.weather_zone" class="flex justify-between">
              <span class="text-sm text-gray-600">Weather Zone:</span>
              <span class="text-sm font-medium text-gray-900">{{ farm.weather_zone }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">Organic Certified:</span>
              <span class="text-sm font-medium">
                <span v-if="farm.is_organic_certified" class="text-green-600">
                  <CheckBadgeIcon class="h-4 w-4 inline mr-1" />
                  Yes
                </span>
                <span v-else class="text-gray-900">No</span>
              </span>
            </div>
          </div>
        </div>

        <!-- Farm Statistics -->
        <div class="border-t border-gray-200 pt-6 mb-6">
          <h4 class="text-sm font-medium text-gray-900 mb-4">Statistics</h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center">
              <p class="text-2xl font-semibold text-gray-900">{{ farm.active_listings || 0 }}</p>
              <p class="text-xs text-gray-500">Active Listings</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-semibold text-gray-900">{{ farm.total_orders || 0 }}</p>
              <p class="text-xs text-gray-500">Total Orders</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-semibold text-gray-900">{{ farm.total_revenue || 0 }}</p>
              <p class="text-xs text-gray-500">Total Revenue</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-semibold text-gray-900">{{ farm.avg_rating || 0 }}</p>
              <p class="text-xs text-gray-500">Avg Rating</p>
            </div>
          </div>
        </div>

        <!-- Registration Details -->
        <div class="border-t border-gray-200 pt-6">
          <h4 class="text-sm font-medium text-gray-900 mb-4">Registration Details</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Farm ID:</span>
              <span class="font-medium text-gray-900">{{ farm.farm_id }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Registered:</span>
              <span class="font-medium text-gray-900">{{ formatDate(farm.created_at) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Last Updated:</span>
              <span class="font-medium text-gray-900">{{ formatDate(farm.updated_at) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Status:</span>
              <span class="font-medium" :class="farm.is_active ? 'text-green-600' : 'text-red-600'">
                {{ farm.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
        <button
          @click="$emit('close')"
          class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          Close
        </button>
        <button
          @click="$emit('edit', farm)"
          class="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          Edit Farm
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { XMarkIcon, MapPinIcon, CheckBadgeIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  farm: {
    type: Object,
    required: true
  }
})

defineEmits(['close', 'edit'])

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

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script> 