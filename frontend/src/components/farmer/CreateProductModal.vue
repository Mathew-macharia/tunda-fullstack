<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Create New Product</h3>
      </div>

      <form @submit.prevent="handleSubmit" class="px-6 py-4 space-y-4">
        <!-- Product Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Product Name <span class="text-red-500">*</span>
          </label>
          <input
            v-model="formData.product_name"
            type="text"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Enter product name"
          />
        </div>

        <!-- Category -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Category <span class="text-red-500">*</span>
          </label>
          <select
            v-model="formData.category"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select a category</option>
            <option v-for="category in categories" :key="category.category_id" :value="category.category_id">
              {{ category.category_name }}
            </option>
          </select>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            v-model="formData.description"
            rows="3"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Describe the product..."
          ></textarea>
        </div>

        <!-- Unit of Measurement -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Unit of Measurement <span class="text-red-500">*</span>
          </label>
          <select
            v-model="formData.unit_of_measure"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select unit</option>
            <option value="kg">Kilogram (kg)</option>
            <option value="piece">Piece</option>
            <option value="bunch">Bunch</option>
            <option value="bag">Bag</option>
            <option value="litre">Litre</option>
          </select>
        </div>

        <!-- Seasonal -->
        <div class="flex items-center">
          <input
            v-model="formData.is_seasonal"
            type="checkbox"
            class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
          />
          <label class="ml-2 block text-sm text-gray-900">
            Seasonal Product
          </label>
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
            {{ saving ? 'Creating...' : 'Create Product' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { productsAPI } from '@/services/api'

const emit = defineEmits(['close', 'created'])

const saving = ref(false)
const categories = ref([])

const formData = reactive({
  product_name: '',
  category: '', // Changed from category_id to category
  description: '',
  unit_of_measure: '',
  is_seasonal: false
})

const loadCategories = async () => {
  try {
    const response = await productsAPI.getCategories()
    categories.value = Array.isArray(response) ? response : response.results || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const handleSubmit = async () => {
  saving.value = true
  try {
    const response = await productsAPI.createProduct(formData)
    emit('created', response)
    emit('close')
  } catch (error) {
    console.error('Error creating product:', error)
    alert('Failed to create product. Please try again.')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadCategories()
})
</script>
