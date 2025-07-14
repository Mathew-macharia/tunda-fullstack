<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
        <div class="flex flex-col space-y-3 sm:space-y-0 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex-1 min-w-0">
            <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold leading-7 text-gray-900">
              Support Center
            </h1>
            <p class="mt-1 text-sm text-gray-500">
              Get help with your orders and account
            </p>
          </div>
          <div class="w-full sm:w-auto sm:ml-4">
            <button @click="openCreateTicketModal" class="btn-primary w-full sm:w-auto inline-flex justify-center items-center">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              New Ticket
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8">
      <!-- Quick Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 sm:h-6 sm:w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
                </svg>
              </div>
              <div class="ml-2 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">
                    Open Tickets
                  </dt>
                  <dd class="text-sm sm:text-lg font-medium text-gray-900">
                    {{ stats.openTickets }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 sm:h-6 sm:w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-2 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">
                    Resolved
                  </dt>
                  <dd class="text-sm sm:text-lg font-medium text-gray-900">
                    {{ stats.resolvedTickets }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 sm:h-6 sm:w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-2 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">
                    Avg Response
                  </dt>
                  <dd class="text-sm sm:text-lg font-medium text-gray-900">
                    {{ stats.avgResponse }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 sm:h-6 sm:w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m3 0v8a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2h10a2 2 0 012 2z" />
                </svg>
              </div>
              <div class="ml-2 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">
                    Last Contact
                  </dt>
                  <dd class="text-xs sm:text-lg font-medium text-gray-900">
                    {{ stats.lastContact }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-6 xl:space-y-0 xl:grid xl:grid-cols-2 xl:gap-8">
        <!-- My Support Tickets -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-3 py-4 sm:px-6 sm:py-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-base sm:text-lg leading-6 font-medium text-gray-900">
                My Support Tickets
              </h3>
              <button @click="viewAllTickets" class="text-sm font-medium text-green-600 hover:text-green-500 active:text-green-700">
                View all
              </button>
            </div>
            
            <div v-if="loadingTickets" class="flex justify-center py-8">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
            </div>
            
            <div v-else-if="!tickets.length" class="text-center py-8">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
              </svg>
              <p class="text-sm text-gray-500 mb-3">No support tickets yet</p>
              <button @click="openCreateTicketModal" class="text-sm font-medium text-green-600 hover:text-green-500 active:text-green-700">
                Create your first ticket
              </button>
            </div>
            
            <div v-else class="space-y-3">
              <TicketCard 
                v-for="ticket in tickets.slice(0, 3)" 
                :key="ticket.ticket_id"
                :ticket="ticket"
                @click="viewTicketDetails"
                class="cursor-pointer active:scale-95 transition-transform"
              />
            </div>
          </div>
        </div>

        <!-- Frequently Asked Questions -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-3 py-4 sm:px-6 sm:py-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-base sm:text-lg leading-6 font-medium text-gray-900">
                Frequently Asked Questions
              </h3>
              <button @click="viewAllFAQs" class="text-sm font-medium text-green-600 hover:text-green-500 active:text-green-700">
                View all
              </button>
            </div>
            
            <div v-if="loadingFAQs" class="flex justify-center py-8">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
            </div>
            
            <div v-else-if="!faqs.length" class="text-center py-8">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-gray-500">No FAQs available</p>
            </div>
            
            <div v-else class="space-y-3">
              <div 
                v-for="faq in faqs.slice(0, 5)" 
                :key="faq.faq_id"
                @click="viewFAQ(faq)"
                class="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 active:bg-gray-200 transition-colors touch-manipulation"
              >
                <h4 class="text-sm font-medium text-gray-900 mb-1">
                  {{ faq.question }}
                </h4>
                <p class="text-xs text-gray-600 line-clamp-2">
                  {{ faq.answer }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Help Section -->
      <div class="mt-6 sm:mt-8 bg-green-50 rounded-lg p-4 sm:p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Need Immediate Help?</h3>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="text-center p-3 bg-white rounded-lg hover:shadow-md transition-shadow cursor-pointer touch-manipulation active:scale-95">
            <div class="bg-green-100 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900 mb-1">Order Issues</h4>
            <p class="text-xs text-gray-600">Track, modify, or report problems with your orders</p>
          </div>
          <div class="text-center p-3 bg-white rounded-lg hover:shadow-md transition-shadow cursor-pointer touch-manipulation active:scale-95">
            <div class="bg-blue-100 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900 mb-1">Payment Help</h4>
            <p class="text-xs text-gray-600">Payment failures, refunds, and billing questions</p>
          </div>
          <div class="text-center p-3 bg-white rounded-lg hover:shadow-md transition-shadow cursor-pointer touch-manipulation active:scale-95 sm:col-span-1 col-span-1">
            <div class="bg-purple-100 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900 mb-1">General Support</h4>
            <p class="text-xs text-gray-600">Account questions and technical support</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Support Ticket Modal -->
    <SupportTicketModal
      :is-open="showCreateTicketModal"
      :editing-ticket="editingTicket"
      @close="closeCreateTicketModal"
      @success="handleTicketSuccess"
    />

    <!-- FAQ Modal -->
    <div v-if="showFAQModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-3 sm:p-4 z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900 pr-4 leading-tight">{{ selectedFAQ?.question }}</h3>
          <button @click="closeFAQModal" class="text-gray-400 hover:text-gray-600 p-1 touch-manipulation">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="p-4 sm:p-6">
          <div class="prose prose-sm max-w-none text-gray-700" v-html="selectedFAQ?.answer"></div>
          <div class="mt-6 pt-6 border-t border-gray-200">
            <p class="text-sm text-gray-600 mb-3">Was this helpful?</p>
            <div class="flex flex-wrap gap-3">
              <button class="btn-secondary text-sm touch-manipulation">Yes</button>
              <button class="btn-secondary text-sm touch-manipulation">No</button>
              <button @click="openCreateTicketModal" class="btn-primary text-sm touch-manipulation">Still need help?</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { communicationAPI } from '@/services/api'
import SupportTicketModal from '@/components/support/SupportTicketModal.vue'
import TicketCard from '@/components/support/TicketCard.vue'

const router = useRouter()

const loadingTickets = ref(false)
const loadingFAQs = ref(false)
const tickets = ref([])
const faqs = ref([])
const showCreateTicketModal = ref(false)
const showFAQModal = ref(false)
const editingTicket = ref(null)
const selectedFAQ = ref(null)

const stats = reactive({
  openTickets: 0,
  resolvedTickets: 0,
  avgResponse: '2.5h',
  lastContact: 'Never'
})

onMounted(() => {
  loadTickets()
  loadFAQs()
})

const loadTickets = async () => {
  loadingTickets.value = true
  try {
    const response = await communicationAPI.getSupportTickets({ page_size: 10 })
    tickets.value = response.results || response || []
    
    // Calculate stats
    stats.openTickets = tickets.value.filter(t => ['open', 'in_progress'].includes(t.status)).length
    stats.resolvedTickets = tickets.value.filter(t => t.status === 'resolved').length
    
    if (tickets.value.length > 0) {
      const latest = tickets.value[0]
      stats.lastContact = formatRelativeDate(latest.created_at)
    }
  } catch (error) {
    console.error('Failed to load tickets:', error)
  } finally {
    loadingTickets.value = false
  }
}

const loadFAQs = async () => {
  loadingFAQs.value = true
  try {
    const response = await communicationAPI.getFAQs({ target_role: 'customer' })
    faqs.value = response.results || response || []
  } catch (error) {
    console.error('Failed to load FAQs:', error)
  } finally {
    loadingFAQs.value = false
  }
}

const openCreateTicketModal = () => {
  editingTicket.value = null
  showCreateTicketModal.value = true
}

const closeCreateTicketModal = () => {
  showCreateTicketModal.value = false
  editingTicket.value = null
}

const handleTicketSuccess = () => {
  loadTickets() // Reload tickets
}

const viewTicketDetails = (ticket) => {
  editingTicket.value = ticket
  showCreateTicketModal.value = true
}

const viewAllTickets = () => {
  // TODO: Navigate to full tickets list
  console.log('View all tickets')
}

const viewAllFAQs = () => {
  // TODO: Navigate to full FAQ list
  console.log('View all FAQs')
}

const viewFAQ = (faq) => {
  selectedFAQ.value = faq
  showFAQModal.value = true
}

const closeFAQModal = () => {
  showFAQModal.value = false
  selectedFAQ.value = null
}

const formatRelativeDate = (dateString) => {
  if (!dateString) return 'Never'
  const now = new Date()
  const date = new Date(dateString)
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return 'Today'
  if (diffDays === 2) return 'Yesterday'
  if (diffDays <= 7) return `${diffDays} days ago`
  
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-clamp: 2;
  overflow: hidden;
}

.prose {
  max-width: none;
}

.prose p {
  margin-bottom: 0.5rem;
}

.prose h1, .prose h2, .prose h3, .prose h4 {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.prose ul, .prose ol {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  padding-left: 1.25rem;
}
</style> 