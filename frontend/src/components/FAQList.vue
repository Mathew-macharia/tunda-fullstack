<template>
  <div class="space-y-4">
    <!-- Search -->
    <div v-if="showSearch" class="relative">
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
      </div>
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search FAQs..."
        class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredFAQs.length === 0" class="text-center py-8">
      <QuestionMarkCircleIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">No FAQs found</h3>
      <p class="mt-1 text-sm text-gray-500">
        {{ searchQuery ? 'Try adjusting your search terms' : 'No frequently asked questions are available yet' }}
      </p>
    </div>

    <!-- FAQ List -->
    <div v-else class="space-y-3">
      <div
        v-for="faq in filteredFAQs"
        :key="faq.faq_id"
        class="bg-white border border-gray-200 rounded-lg overflow-hidden"
      >
        <button
          @click="toggleFAQ(faq.faq_id)"
          class="w-full px-6 py-4 text-left hover:bg-gray-50 focus:outline-none focus:bg-gray-50 transition-colors"
        >
          <div class="flex items-center justify-between">
            <h3 class="text-base font-medium text-gray-900 pr-4">
              {{ faq.question }}
            </h3>
            <ChevronDownIcon
              :class="[
                'h-5 w-5 text-gray-500 transition-transform duration-200 flex-shrink-0',
                expandedFAQs.has(faq.faq_id) ? 'rotate-180' : ''
              ]"
            />
          </div>
        </button>
        
        <div
          v-show="expandedFAQs.has(faq.faq_id)"
          class="px-6 pb-4 border-t border-gray-100"
        >
          <div class="pt-4 text-gray-700 leading-relaxed whitespace-pre-wrap">
            {{ faq.answer }}
          </div>
        </div>
      </div>
    </div>

    <!-- Load More Button -->
    <div v-if="showLoadMore && hasMore" class="text-center pt-6">
      <button
        @click="loadMore"
        :disabled="loadingMore"
        class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="loadingMore" class="flex items-center">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading...
        </span>
        <span v-else>Load More FAQs</span>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import {
  MagnifyingGlassIcon,
  QuestionMarkCircleIcon,
  ChevronDownIcon
} from '@heroicons/vue/24/outline'
import { communicationAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'FAQList',
  components: {
    MagnifyingGlassIcon,
    QuestionMarkCircleIcon,
    ChevronDownIcon
  },
  props: {
    targetRole: {
      type: String,
      default: null
    },
    showSearch: {
      type: Boolean,
      default: true
    },
    showLoadMore: {
      type: Boolean,
      default: false
    },
    maxItems: {
      type: Number,
      default: null
    }
  },
  setup(props) {
    const authStore = useAuthStore()
    
    const loading = ref(false)
    const loadingMore = ref(false)
    const searchQuery = ref('')
    const faqs = ref([])
    const expandedFAQs = ref(new Set())
    const currentPage = ref(1)
    const hasMore = ref(false)

    const filteredFAQs = computed(() => {
      let filtered = faqs.value

      // Filter by search query
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(faq =>
          faq.question.toLowerCase().includes(query) ||
          faq.answer.toLowerCase().includes(query)
        )
      }

      // Limit items if maxItems is specified
      if (props.maxItems) {
        filtered = filtered.slice(0, props.maxItems)
      }

      return filtered
    })

    const toggleFAQ = (faqId) => {
      const expanded = new Set(expandedFAQs.value)
      if (expanded.has(faqId)) {
        expanded.delete(faqId)
      } else {
        expanded.add(faqId)
      }
      expandedFAQs.value = expanded
    }

    const loadFAQs = async (page = 1, append = false) => {
      if (page === 1) {
        loading.value = true
      } else {
        loadingMore.value = true
      }

      try {
        const params = {
          page,
          is_active: true
        }

        // Filter by target role if specified, otherwise use user's role
        const targetRole = props.targetRole || authStore.user?.user_role
        if (targetRole && targetRole !== 'admin') {
          params.target_role = targetRole
        }

        const response = await communicationAPI.getFAQs(params)
        const data = response

        if (append) {
          faqs.value = [...faqs.value, ...(data.results || data || [])]
        } else {
          faqs.value = data.results || data || []
        }

        // Check if there are more pages
        hasMore.value = !!(data.next || (data.results && data.results.length === 20))
        currentPage.value = page

      } catch (error) {
        console.error('Error loading FAQs:', error)
      } finally {
        loading.value = false
        loadingMore.value = false
      }
    }

    const loadMore = () => {
      if (!loadingMore.value && hasMore.value) {
        loadFAQs(currentPage.value + 1, true)
      }
    }

    // Watch for search query changes
    watch(searchQuery, () => {
      // Reset expanded state when searching
      expandedFAQs.value = new Set()
    })

    onMounted(() => {
      loadFAQs()
    })

    return {
      loading,
      loadingMore,
      searchQuery,
      filteredFAQs,
      expandedFAQs,
      hasMore,
      toggleFAQ,
      loadMore
    }
  }
}
</script> 