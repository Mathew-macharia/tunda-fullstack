<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center space-x-4 mb-4">
          <button
            @click="$router.go(-1)"
            class="p-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeftIcon class="h-5 w-5" />
          </button>
          <h1 class="text-3xl font-bold text-gray-900">Create Product Listing</h1>
        </div>
        <p class="text-gray-600">Add a new product to your marketplace</p>
      </div>

      <!-- Form -->
      <div class="bg-white shadow rounded-lg">
        <form @submit.prevent="submitListing" class="space-y-8 p-6">
          <!-- Basic Information -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Farm *</label>
                <select
                  v-model="form.farm"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Select a farm</option>
                  <option v-for="farm in farms" :key="farm.farm_id" :value="farm.farm_id">
                    {{ farm.farm_name }}
                  </option>
                </select>
                <p v-if="!farms.length" class="mt-1 text-sm text-gray-500">
                  <router-link to="/farmer/farms" class="text-green-600 hover:text-green-500">
                    Create a farm first
                  </router-link>
                </p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Product *</label>
                <div class="flex space-x-2">
                  <v-select
                    v-model="form.product"
                    :options="products"
                    :get-option-label="product => `${product.product_name} (${product.unit_of_measure})`"
                    :reduce="product => product.product_id"
                    placeholder="Select a product"
                    class="flex-1"
                    :clearable="false"
                    required
                  ></v-select>
                  <button
                    type="button"
                    @click="showCreateProductModal = true"
                    class="px-3 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    <PlusIcon class="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Pricing & Quantity -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Pricing & Quantity</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Price per unit (KES) *</label>
                <input
                  v-model.number="form.current_price"
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="0.00"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Quantity Available *</label>
                <input
                  v-model.number="form.quantity_available"
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="0.00"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Minimum Order Quantity</label>
                <input
                  v-model.number="form.min_order_quantity"
                  type="number"
                  step="0.01"
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="1.00"
                />
              </div>
            </div>
          </div>

          <!-- Product Details -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Product Details</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Quality Grade</label>
                <select
                  v-model="form.quality_grade"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="premium">Premium</option>
                  <option value="standard">Standard</option>
                  <option value="economy">Economy</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Listing Status</label>
                <select
                  v-model="form.listing_status"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="available">Available Now</option>
                  <option value="pre_order">Pre-Order</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Harvest Dates -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Harvest Information</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Harvest Date</label>
                <input
                  v-model="form.harvest_date"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
                <p class="mt-1 text-sm text-gray-500">When was this product harvested?</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Expected Harvest Date</label>
                <input
                  v-model="form.expected_harvest_date"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
                <p class="mt-1 text-sm text-gray-500">For pre-orders, when will this be ready?</p>
              </div>
            </div>
          </div>

          <!-- Certifications -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Certifications</h3>
            <div class="flex items-center">
              <input
                v-model="form.is_organic_certified"
                type="checkbox"
                id="organic_certified"
                class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              />
              <label for="organic_certified" class="ml-2 block text-sm text-gray-900">
                This product is organically certified
              </label>
            </div>
          </div>

          <!-- Photos -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Product Photos</h3>
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
            <label class="block text-sm font-medium text-gray-700 mb-2">Additional Notes</label>
            <textarea
              v-model="form.notes"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Any additional information about this product..."
            ></textarea>
          </div>

          <!-- Form Actions -->
          <div class="flex justify-end space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              @click="$router.go(-1)"
              class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading || !farms.length"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            >
              {{ loading ? 'Creating...' : 'Create Listing' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create Product Modal -->
    <CreateProductModal
      v-if="showCreateProductModal"
      @close="showCreateProductModal = false"
      @created="handleProductCreated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { productsAPI, farmsAPI } from '@/services/api'
import {
  ArrowLeftIcon,
  PlusIcon,
  PhotoIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import CreateProductModal from '@/components/farmer/CreateProductModal.vue'
import vSelect from 'vue-select'
import 'vue-select/dist/vue-select.css'

const router = useRouter()

// State
const loading = ref(false)
const farms = ref([])
const products = ref([])
const showCreateProductModal = ref(false)
const photoFiles = ref([])
const photoPreviewUrls = ref([])
const isDragging = ref(false) // New state for drag-and-drop visual feedback
const fileInput = ref(null) // Reference to the hidden file input

// Form data
const form = ref({
  farm: '',
  product: '',
  current_price: null,
  quantity_available: null,
  min_order_quantity: 1.0,
  quality_grade: 'standard',
  listing_status: 'available',
  harvest_date: '',
  expected_harvest_date: '',
  is_organic_certified: false,
  notes: ''
})

// Methods
const triggerFileInput = () => {
  fileInput.value.click()
}

const loadFarms = async () => {
  try {
    const response = await farmsAPI.getFarms()
    farms.value = Array.isArray(response) ? response : response.results || []
  } catch (err) {
    console.error('Error loading farms:', err)
  }
}

const loadProducts = async () => {
  try {
    const response = await productsAPI.getProducts()
    products.value = Array.isArray(response) ? response : response.results || []
  } catch (err) {
    console.error('Error loading products:', err)
  }
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  processFiles(files)
}

const handleDrop = (event) => {
  event.preventDefault()
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
  photoFiles.value.splice(index, 1)
  photoPreviewUrls.value.splice(index, 1)
}

const uploadPhotos = async () => {
  const uploadedUrls = []
  
  for (const file of photoFiles.value) {
    const formData = new FormData()
    formData.append('photo', file)
    
    try {
      const response = await productsAPI.uploadPhoto(formData)
      uploadedUrls.push(response.url)
    } catch (err) {
      console.error('Error uploading photo:', err)
      // You might want to show an error message to the user here
    }
  }
  
  return uploadedUrls
}

const submitListing = async () => {
  loading.value = true
  
  try {
    // Upload photos first
    const photoUrls = await uploadPhotos()
    
    // Prepare form data
    const listingData = {
      farm: form.value.farm,
      product: form.value.product,
      current_price: form.value.current_price,
      quantity_available: form.value.quantity_available,
      min_order_quantity: form.value.min_order_quantity,
      quality_grade: form.value.quality_grade,
      listing_status: form.value.listing_status,
      is_organic_certified: form.value.is_organic_certified,
      notes: form.value.notes,
      photos: photoUrls
    }
    
    // Add dates if provided
    if (form.value.harvest_date) {
      listingData.harvest_date = form.value.harvest_date
    }
    if (form.value.expected_harvest_date) {
      listingData.expected_harvest_date = form.value.expected_harvest_date
    }
    
    await productsAPI.createListing(listingData)
    
    // Success - redirect to listings page
    router.push('/farmer/listings')
    
  } catch (err) {
    console.error('Error creating listing:', err)
    // Handle error (show toast, etc.)
  } finally {
    loading.value = false
  }
}

const handleProductCreated = (product) => {
  products.value.push(product)
  form.value.product = product.product_id
  showCreateProductModal.value = false
}

onMounted(async () => {
  await Promise.all([
    loadFarms(),
    loadProducts()
  ])
})
</script>
