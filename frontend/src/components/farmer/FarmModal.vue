<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">
          {{ farm ? 'Edit Farm' : 'Create New Farm' }}
        </h3>
      </div>

      <form @submit.prevent="handleSubmit" class="px-6 py-4 space-y-4">
        <!-- Farm Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Farm Name <span class="text-red-500">*</span>
          </label>
          <input
            v-model="formData.farm_name"
            type="text"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Enter farm name"
          />
        </div>

        <!-- Location -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- County -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              County <span class="text-red-500">*</span>
            </label>
            <select
              v-model="selectedCounty"
              @change="loadSubCounties"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">Select County</option>
              <option v-for="county in counties" :key="county.county_id" :value="county.county_id">
                {{ county.county_name }}
              </option>
            </select>
          </div>

          <!-- Sub-County -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
              Sub-County <span class="text-red-500">*</span>
          </label>
          <select
            v-model="formData.location_id"
            required
              :disabled="!selectedCounty || loadingSubCounties"
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
          >
              <option value="">
                {{ loadingSubCounties ? 'Loading sub-counties...' : 'Select Sub-County' }}
              </option>
              <option v-for="subCounty in subCounties" :key="subCounty.sub_county_id" :value="subCounty.sub_county_id">
                {{ subCounty.sub_county_name }}
            </option>
          </select>
          </div>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            v-model="formData.farm_description"
            rows="3"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Describe your farm..."
          ></textarea>
        </div>

        <!-- Total Acreage -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Total Acreage (acres)
          </label>
          <input
            v-model.number="formData.total_acreage"
            type="number"
            step="0.01"
            min="0"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="0.00"
          />
        </div>

        <!-- Cultivated Area -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Cultivated Area (acres)
          </label>
          <input
            v-model.number="formData.cultivated_area"
            type="number"
            step="0.01"
            min="0"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="0.00"
          />
        </div>

        <!-- Soil Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Soil Type
          </label>
          <select
            v-model="formData.soil_type"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select soil type</option>
            <option value="clay">Clay</option>
            <option value="sandy">Sandy</option>
            <option value="loamy">Loamy</option>
            <option value="silt">Silt</option>
            <option value="peaty">Peaty</option>
            <option value="chalky">Chalky</option>
          </select>
        </div>

        <!-- Water Source -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Water Source
          </label>
          <select
            v-model="formData.water_source"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select water source</option>
            <option value="borehole">Borehole</option>
            <option value="river">River</option>
            <option value="rain">Rain Water</option>
            <option value="well">Well</option>
            <option value="municipal">Municipal Supply</option>
            <option value="dam">Dam</option>
          </select>
        </div>

        <!-- Weather Zone -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Weather Zone
          </label>
          <select
            v-model="formData.weather_zone"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select weather zone</option>
            <option value="highland">Highland</option>
            <option value="midland">Midland</option>
            <option value="lowland">Lowland</option>
          </select>
        </div>

        <!-- Organic Certification -->
        <div class="flex items-center">
          <input
            v-model="formData.is_certified_organic"
            type="checkbox"
            class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
          />
          <label class="ml-2 block text-sm text-gray-900">
            Organic Certified Farm
          </label>
        </div>

        <!-- Farm Photos -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Farm Photos
          </label>
          <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
            <div class="space-y-1 text-center">
              <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              <div class="flex text-sm text-gray-600">
                <label for="farm-photos" class="relative cursor-pointer bg-white rounded-md font-medium text-green-600 hover:text-green-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-green-500">
                  <span>Upload farm photos</span>
                  <input
                    id="farm-photos"
                    ref="farmPhotosInput"
                    type="file"
                    class="sr-only"
                    multiple
                    accept="image/*"
                    @change="handlePhotoUpload"
                  />
                </label>
                <p class="pl-1">or drag and drop</p>
              </div>
              <p class="text-xs text-gray-500">PNG, JPG, GIF up to 10MB each</p>
            </div>
          </div>
          
          <!-- Preview uploaded photos -->
          <div v-if="uploadedPhotos.length > 0" class="mt-4 grid grid-cols-3 gap-4">
            <div v-for="(photo, index) in uploadedPhotos" :key="index" class="relative">
              <img :src="photo.preview" :alt="`Farm photo ${index + 1}`" class="h-24 w-full object-cover rounded-lg" />
              <button
                @click="removePhoto(index)"
                type="button"
                class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
              >
                ×
              </button>
            </div>
          </div>
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
            :disabled="saving"
            class="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
          >
            {{ saving ? 'Saving...' : (farm ? 'Update Farm' : 'Create Farm') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const props = defineProps({
  farm: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const saving = ref(false)
const selectedCounty = ref('')
const loadingSubCounties = ref(false)
const counties = ref([])
const subCounties = ref([])
const uploadedPhotos = ref([])
const farmPhotosInput = ref(null)

const formData = reactive({
  farm_name: '',
  location_id: '',
  farm_description: '',
  total_acreage: null,
  cultivated_area: null,
  soil_type: '',
  water_source: '',
  weather_zone: '',
  is_certified_organic: false
})

const loadCounties = async () => {
  try {
    const { locationsAPI } = await import('@/services/api')
    const response = await locationsAPI.getCounties()
    counties.value = response.results || response
  } catch (error) {
    console.error('Error loading counties:', error)
  }
}

const loadSubCounties = async () => {
  // Clear the current subcounty selection when county changes
  formData.location_id = ''
  
  if (!selectedCounty.value) {
    subCounties.value = []
    loadingSubCounties.value = false
    return
  }
  
  loadingSubCounties.value = true
  
  try {
    const { locationsAPI } = await import('@/services/api')
    const response = await locationsAPI.getSubCounties(selectedCounty.value)
    subCounties.value = response.results || response
  } catch (error) {
    console.error('Error loading sub-counties:', error)
    subCounties.value = []
  } finally {
    loadingSubCounties.value = false
  }
}

const handlePhotoUpload = (event) => {
  const files = Array.from(event.target.files)
  
  files.forEach(file => {
    // Check file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      alert(`File ${file.name} is too large. Maximum size is 10MB.`)
      return
    }
    
    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      uploadedPhotos.value.push({
        file: file,
        preview: e.target.result,
        name: file.name
      })
    }
    reader.readAsDataURL(file)
  })
  
  // Clear the input
  if (farmPhotosInput.value) {
    farmPhotosInput.value.value = ''
  }
}

const removePhoto = (index) => {
  uploadedPhotos.value.splice(index, 1)
}

const handleSubmit = async () => {
  saving.value = true
  try {
    // Add photos to form data
    const submissionData = { 
      ...formData,
      farm_photos: uploadedPhotos.value.map(photo => photo.preview) // For now, send base64 previews
    }
    await emit('save', submissionData)
  } catch (error) {
    console.error('Error saving farm:', error)
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  // Load counties
  await loadCounties()
  
  // If editing an existing farm, populate the form
  if (props.farm) {
    Object.assign(formData, {
      farm_name: props.farm.farm_name || '',
      location_id: props.farm.sub_county?.sub_county_id || props.farm.location_id || '',
      farm_description: props.farm.farm_description || props.farm.description || '',
      total_acreage: props.farm.total_acreage || props.farm.total_area || null,
      cultivated_area: props.farm.cultivated_area || null,
      soil_type: props.farm.soil_type || '',
      water_source: props.farm.water_source || '',
      weather_zone: props.farm.weather_zone || '',
      is_certified_organic: props.farm.is_certified_organic || props.farm.is_organic_certified || false
    })
    
    // Load existing photos
    if (props.farm.farm_photos && Array.isArray(props.farm.farm_photos)) {
      uploadedPhotos.value = props.farm.farm_photos.map((photo, index) => ({
        preview: photo,
        name: `existing-photo-${index + 1}`,
        isExisting: true
      }))
    }
    
    // If there's a sub_county, find and set the county
    if (props.farm.sub_county) {
      // Find the county from the sub_county
      const county = counties.value.find(c => 
        c.county_id === props.farm.sub_county.county.county_id
      )
      if (county) {
        selectedCounty.value = county.county_id
        await loadSubCounties()
      }
    }
  }
})
</script> 