<template>
  <div class="mt-16 md:mt-0 pt-0 pb-0 sm:py-12 lg:py-24 bg-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <p class="text-2xl text-gray-900 font-semibold tracking-wide uppercase font-dancing-script">Our</p>
      <h2 class="mt-2 text-4xl font-extrabold text-green-600 tracking-tight sm:text-4xl">
        Category
      </h2>
      
      <!-- Loading State -->
      <div v-if="loadingCategories" class="mt-10 grid grid-cols-2 gap-8 md:grid-cols-3 lg:grid-cols-6">
        <div v-for="n in 6" :key="n" class="bg-white rounded-2xl p-6 shadow-sm animate-pulse">
          <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-gray-200 mx-auto mb-4"></div>
          <div class="h-4 bg-gray-200 rounded"></div>
        </div>
      </div>
      
      <!-- Categories Scrollable List -->
      <div v-else class="relative mt-10">
        <div ref="categoryListRef" class="flex space-x-4 overflow-x-auto pb-2 -mb-2 scrollbar-hide scroll-fade">
          <div
            v-for="category in visibleCategories"
            :key="category.category_id"
            @click="filterByCategory(category.category_id)"
            class="flex-shrink-0 w-32 sm:w-40 bg-white rounded-2xl p-4 sm:p-6 shadow-sm transition-all duration-300 cursor-pointer text-center"
          >
            <img 
              :src="getCategoryImage(category.category_name)"
              :alt="category.category_name"
              class="w-24 h-24 mx-auto mb-3 sm:mb-4"
            />
            <h3 class="text-sm sm:text-base font-semibold text-gray-900 line-clamp-2">
              {{ category.category_name }}
            </h3>
            <p class="mt-1 text-sm text-gray-500 line-clamp-2">
              {{ category.description }}
            </p>
          </div>
        </div>
      </div>
      <div class="mt-8">
        <router-link 
          to="/products" 
          class="text-green-600 hover:text-green-700 text-sm font-medium flex items-center justify-center space-x-1"
        >
          <span>View All Categories</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useHomePageData } from '@/composables/useHomePageData'

const router = useRouter()
const { categories, loadingCategories, getCategoryImage, filterByCategory } = useHomePageData()

const categoryListRef = ref(null)
let scrollInterval = null
const scrollSpeed = 1 // Adjust scroll speed as needed
const isOverflowing = ref(false)

const visibleCategories = computed(() => {
  if (isOverflowing.value) {
    return [...categories.value, ...categories.value]
  }
  return categories.value
})

const startScrolling = () => {
  if (!categoryListRef.value || !isOverflowing.value) return

  const scrollContainer = categoryListRef.value
  // Calculate the width of a single set of categories
  // This assumes all category items have roughly the same width and margin
  const firstCategoryItem = scrollContainer.querySelector('.flex-shrink-0')
  if (!firstCategoryItem) return

  const itemWidth = firstCategoryItem.offsetWidth + parseInt(getComputedStyle(firstCategoryItem).marginRight || '0')
  const totalItemsWidth = categories.value.length * itemWidth;
  
  // The point to jump back is when scrollLeft reaches the end of the first set of original categories
  const jumpBackPoint = totalItemsWidth;

  scrollInterval = setInterval(() => {
    if (scrollContainer.scrollLeft >= jumpBackPoint) {
      // If scrolled past the first set, instantly jump back to the start of the first set
      scrollContainer.scrollLeft -= jumpBackPoint
    }
    scrollContainer.scrollLeft += scrollSpeed
  }, 20) // Adjust interval for smoother/faster scrolling
}

const checkOverflowAndStartScrolling = async () => {
  if (scrollInterval) {
    clearInterval(scrollInterval)
    scrollInterval = null
  }

  await nextTick() // Ensure DOM is updated before measuring

  if (categoryListRef.value) {
    const scrollContainer = categoryListRef.value
    isOverflowing.value = scrollContainer.scrollWidth > scrollContainer.clientWidth

    if (isOverflowing.value) {
      startScrolling()
    } else {
      // If not overflowing, ensure scroll position is reset and no scrolling happens
      scrollContainer.scrollLeft = 0
    }
  }
}

onMounted(() => {
  checkOverflowAndStartScrolling()
})

onUnmounted(() => {
  if (scrollInterval) {
    clearInterval(scrollInterval)
  }
})

watch(categories, () => {
  checkOverflowAndStartScrolling()
}, { deep: true }) // Watch for changes in the categories array itself
</script>

<style scoped>
/* Add custom font if needed, or define in global CSS */
.font-dancing-script {
  font-family: 'Dancing Script', cursive;
}

/* Hide scrollbar for Chrome, Safari and Opera */
.scrollbar-hide::-webkit-scrollbar {
    display: none;
}

/* Hide scrollbar for IE, Edge and Firefox */
.scrollbar-hide {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
}
</style>
