<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-medium text-gray-900">
            Edit Product Listing
          </h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Basic Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Farm</label>
              <select
                v-model="formData.farm"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">Select Farm</option>
                <option v-for="farm in farms" :key="farm.farm_id" :value="farm.farm_id">
                  {{ farm.farm_name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Product</label>
              <select
                v-model="formData.product"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">Select Product</option>
                <option v-for="product in filteredProducts" :key="product.product_id" :value="product.product_id">
                  {{ product.product_name }} ({{ product.category_name }})
                </option>
              </select>
            </div>
          </div>

          <!-- Pricing and Quantity -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Price per Unit (KES)</label>
              <input
                v-model.number="formData.current_price"
                type="number"
                step="0.01"
                min="0"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Available Quantity</label>
              <input
                v-model.number="formData.quantity_available"
                type="number"
                min="0"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Quality Grade</label>
              <select
                v-model="formData.quality_grade"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">Select Quality</option>
                <option value="premium">Premium</option>
                <option value="standard">Standard</option>
                <option value="economy">Economy</option>
              </select>
            </div>
          </div>

          <!-- Dates -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Harvest Date</label>
              <input
                v-model="formData.harvest_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Expected Harvest Date</label>
              <input
                v-model="formData.expected_harvest_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>

          <!-- Status and Certifications -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Listing Status</label>
              <select
                v-model="formData.listing_status"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="available">Available</option>
                <option value="pre_order">Pre-Order</option>
                <option value="sold_out">Sold Out</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>

            <div class="flex items-center justify-center">
              <div class="flex items-center">
                <input
                  v-model="formData.is_organic_certified"
                  type="checkbox"
                  class="h-4 w-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                />
                <label class="ml-2 block text-sm text-gray-700">Organic Certified</label>
              </div>
            </div>
          </div>

          <!-- Product Photos -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Product Photos</label>
            <div
              @drop="handleDrop"
              @dragover.prevent="isDragging = true"
              @dragenter.prevent="isDragging = true"
              @dragleave="isDragging = false"
              @click="triggerFileInput"
              :class="[
                'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors duration-200',
                isDragging ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-gray-400'
              ]"
            >
              <input
                ref="fileInput"
                type="file"
                multiple
                accept="image/*"
                @change="handleFileSelect"
                class="sr-only"
              />
              
              <div v-if="photoPreviewUrls.length === 0" class="flex flex-col items-center">
                <PhotoIcon class="mx-auto h-12 w-12 text-gray-400" />
                <div class="mt-4">
                  <p class="mt-2 block text-sm font-medium text-gray-900">
                    Drag and drop photos here, or
                    <span class="text-green-600 hover:text-green-500">browse to upload</span>
                  </p>
                  <p class="mt-2 text-xs text-gray-500">PNG, JPG, GIF up to 10MB each</p>
                </div>
              </div>
              <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div
                  v-for="(url, index) in photoPreviewUrls"
                  :key="index"
                  class="relative group"
                >
                  <img
                    :src="url"
                    :alt="`Product photo ${index + 1}`"
                    class="w-full h-24 object-cover rounded-lg"
                  />
                  <button
                    type="button"
                    @click.stop="removePhoto(index)"
                    class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <XMarkIcon class="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Notes (Optional)</label>
            <textarea
              v-model="formData.notes"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-500"
              placeholder="Additional information about this listing..."
            ></textarea>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-3">
            <p class="text-sm text-red-700">{{ error }}</p>
          </div>

          <!-- Buttons -->
          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {{ loading ? 'Saving...' : 'Update Listing' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, defineEmits } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { productsAPI } from '@/services/api'

const props = defineProps({
  listing: {
    type: Object,
    required: true
  },
  farms: {
    type: Array,
    default: () => []
  },
  categories: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'save'])

// State
const loading = ref(false)
const error = ref(null)
const products = ref([])
const photoFiles = ref([])
const photoPreviewUrls = ref([])
const isDragging = ref(false)
const fileInput = ref(null)

const formData = ref({
  farm: '',
  product: '',
  current_price: 0,
  quantity_available: 0,
  quality_grade: '',
  harvest_date: '',
  expected_harvest_date: '',
  listing_status: 'available',
  is_organic_certified: false,
  notes: '',
  photos: []
})

// Computed
const filteredProducts = computed(() => {
  return products.value
})

// Methods
const triggerFileInput = () => {
  fileInput.value.click()
}

const loadProducts = async () => {
  try {
    const response = await productsAPI.getProducts()
    products.value = Array.isArray(response) ? response : response.results || []
  } catch (err) {
    console.error('Error loading products:', err)
  }
}

const initializeForm = () => {
  if (props.listing) {
    formData.value = {
      farm: props.listing.farm_id || '',
      product: props.listing.product_id || '',
      current_price: props.listing.current_price || 0,
      quantity_available: props.listing.quantity_available || 0,
      quality_grade: props.listing.quality_grade || '',
      harvest_date: props.listing.harvest_date || '',
      expected_harvest_date: props.listing.expected_harvest_date || '',
      listing_status: props.listing.listing_status || 'available',
      is_organic_certified: props.listing.is_organic_certified || false,
      notes: props.listing.notes || '',
      photos: props.listing.photos || []
    }
    // Populate photoPreviewUrls with existing photos
    photoPreviewUrls.value = [...(props.listing.photos || [])]
    photoFiles.value = [] // Clear photoFiles as these are existing URLs, not new files
  }
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  processFiles(files)
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files)
  processFiles(files)
}

const processFiles = (files) => {
  files.forEach(file => {
    if (file.type.startsWith('image/')) {
      photoFiles.value.push(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        photoPreviewUrls.value.push(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  })
}

const removePhoto = (index) => {
  // If removing an existing photo (from URL), remove it from formData.photos
  if (index < (formData.value.photos?.length || 0)) {
    formData.value.photos.splice(index, 1)
  } else {
    // If removing a newly added photo (from file), adjust index for photoFiles
    const fileIndex = index - (formData.value.photos?.length || 0)
    if (fileIndex >= 0 && fileIndex < photoFiles.value.length) {
      photoFiles.value.splice(fileIndex, 1)
    }
  }
  photoPreviewUrls.value.splice(index, 1)
}

const uploadPhotos = async () => {
  const uploadedUrls = []
  for (const file of photoFiles.value) {
    const formDataForUpload = new FormData()
    formDataForUpload.append('photo', file)
    try {
      const response = await productsAPI.uploadPhoto(formDataForUpload)
      uploadedUrls.push(response.url)
    } catch (err) {
      console.error('Error uploading photo:', err)
      // Handle error for individual photo upload
    }
  }
  return uploadedUrls
}

const handleSubmit = async () => {
  error.value = null
  loading.value = true
  
  try {
    // Upload new photos
    const newPhotoUrls = await uploadPhotos()
    
    // Combine existing photos (that weren't removed) with newly uploaded photos
    const finalPhotos = [...(formData.value.photos || []), ...newPhotoUrls]

    const listingData = {
      farm: formData.value.farm,
      product: formData.value.product,
      current_price: formData.value.current_price,
      quantity_available: formData.value.quantity_available,
      quality_grade: formData.value.quality_grade,
      listing_status: formData.value.listing_status,
      is_organic_certified: formData.value.is_organic_certified,
      notes: formData.value.notes,
      photos: finalPhotos // Send the combined list of photos
    }
    
    // Only include dates if they have values
    if (formData.value.harvest_date) {
      listingData.harvest_date = formData.value.harvest_date
    }
    if (formData.value.expected_harvest_date) {
      listingData.expected_harvest_date = formData.value.expected_harvest_date
    }
    
    await emit('save', listingData)
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Failed to update listing'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadProducts()
  initializeForm()
})
</script>
