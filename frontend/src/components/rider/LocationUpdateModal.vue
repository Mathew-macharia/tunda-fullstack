<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Update Location</h3>
      </div>

      <form @submit.prevent="handleSubmit" class="px-6 py-4 space-y-4">
        <!-- Current Location Display -->
        <div v-if="currentLocation">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Current Location
          </label>
          <div class="bg-gray-50 rounded-md p-3 text-sm text-gray-600">
            <div>Latitude: {{ currentLocation.latitude }}</div>
            <div>Longitude: {{ currentLocation.longitude }}</div>
            <div v-if="currentLocation.address" class="mt-1">
              Address: {{ currentLocation.address }}
            </div>
          </div>
        </div>

        <!-- Manual Location Entry -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Latitude <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="formData.latitude"
              type="number"
              step="any"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="e.g., -1.286389"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Longitude <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="formData.longitude"
              type="number"
              step="any"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="e.g., 36.817223"
            />
          </div>
        </div>

        <!-- Address -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Address/Landmark
          </label>
          <input
            v-model="formData.address"
            type="text"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Enter address or landmark"
          />
        </div>

        <!-- GPS Button -->
        <div class="text-center">
          <button
            type="button"
            @click="getCurrentLocation"
            :disabled="gettingLocation"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
          >
            <MapPinIcon class="h-4 w-4 mr-2" />
            {{ gettingLocation ? 'Getting Location...' : 'Use Current GPS Location' }}
          </button>
        </div>

        <!-- Notes -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Update Notes
          </label>
          <textarea
            v-model="formData.notes"
            rows="3"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Any additional notes about your location or delivery status..."
          ></textarea>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="updating"
            class="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
          >
            {{ updating ? 'Updating...' : 'Update Location' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { MapPinIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  deliveryId: {
    type: [String, Number],
    required: true
  },
  currentLocation: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'updated'])

const updating = ref(false)
const gettingLocation = ref(false)

const formData = reactive({
  latitude: '',
  longitude: '',
  address: '',
  notes: ''
})

const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    alert('Geolocation is not supported by this browser.')
    return
  }

  gettingLocation.value = true
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      formData.latitude = position.coords.latitude
      formData.longitude = position.coords.longitude
      gettingLocation.value = false
    },
    (error) => {
      console.error('Error getting location:', error)
      alert('Unable to get your current location. Please enter manually.')
      gettingLocation.value = false
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 60000
    }
  )
}

const handleSubmit = async () => {
  if (!formData.latitude || !formData.longitude) {
    alert('Please provide latitude and longitude')
    return
  }

  updating.value = true
  try {
    const locationData = {
      latitude: formData.latitude,
      longitude: formData.longitude,
      address: formData.address || null,
      notes: formData.notes || null,
      timestamp: new Date().toISOString()
    }

    emit('updated', locationData)
    emit('close')
  } catch (error) {
    console.error('Error updating location:', error)
    alert('Failed to update location. Please try again.')
  } finally {
    updating.value = false
  }
}

onMounted(() => {
  if (props.currentLocation) {
    formData.latitude = props.currentLocation.latitude || ''
    formData.longitude = props.currentLocation.longitude || ''
    formData.address = props.currentLocation.address || ''
  }
})
</script>
