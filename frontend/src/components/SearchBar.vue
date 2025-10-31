<template>
  <div class="relative mt-36 md:mt-48 mb-0 z-40">
<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-primary rounded-lg shadow-lg p-2 sm:p-3 flex flex-col sm:flex-row items-center space-y-3 sm:space-y-0 sm:space-x-4">
        <!-- Category Dropdown -->
        <div class="relative w-full sm:w-auto">
            <select
              v-model="selectedCategory"
              @change="handleCategoryChange"
              class="block w-full sm:w-48 pl-4 pr-10 py-1 border border-primary rounded-md leading-5 bg-primary text-white placeholder-white focus:outline-none focus:ring-0 focus:border-transparent text-base font-semibold appearance-none"
            >
              <option value="" class="bg-primary text-white">All Categories</option>
              <option v-for="category in categories" :key="category.category_id" :value="category.category_id" class="bg-primary text-white">
                {{ category.category_name }}
              </option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-white">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </div>
          </div>

          <!-- Separator -->
          <div class="hidden sm:block text-white text-xl font-light">|</div>

          <!-- Search Input -->
          <div class="relative flex-grow w-full">
            <input
              type="text"
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              placeholder="Search here..."
              class="block w-full pl-4 pr-10 py-1 border border-primary rounded-md leading-5 bg-primary text-white placeholder-white focus:outline-none focus:ring-0 focus:border-transparent text-sm"
            />
            <button
              @click="handleSearch"
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-white hover:text-primary focus:outline-none"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
            </button>
          </div>

        <!-- Submit Button -->
        <button
          @click="handleSearch"
          class="w-full sm:w-auto bg-white text-primary px-6 py-2 rounded-md text-sm font-medium hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors duration-200"
        >
          Submit
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  initialSearchQuery: {
    type: String,
    default: ''
  },
  initialSelectedCategory: {
    type: [String, Number],
    default: ''
  }
})

const emit = defineEmits(['search'])

const router = useRouter()
const searchQuery = ref(props.initialSearchQuery)
const selectedCategory = ref(props.initialSelectedCategory)

watch(() => props.initialSearchQuery, (newValue) => {
  searchQuery.value = newValue
})

watch(() => props.initialSelectedCategory, (newValue) => {
  selectedCategory.value = newValue
})

const handleSearch = () => {
  emit('search', {
    query: searchQuery.value,
    category: selectedCategory.value
  })
  router.push({
    path: '/products',
    query: {
      search: searchQuery.value,
      category_id: selectedCategory.value
    }
  })
}

const handleCategoryChange = () => {
  handleSearch()
}
</script>

<style scoped>
/* Add any specific styles here if needed, though Tailwind should handle most */
</style>
