<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
        <div class="flex flex-col space-y-3 sm:space-y-0 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex-1 min-w-0">
            <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold leading-7 text-gray-900">
              Farmer Support Center
            </h1>
            <p class="mt-1 text-sm text-gray-500">
              Get help with your business operations and earnings
            </p>
          </div>
          <div class="w-full sm:w-auto sm:ml-4">
            <button @click="openCreateTicketModal" class="btn-primary w-full sm:w-auto inline-flex justify-center items-center">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              New Support Request
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8">
      <!-- Business Stats -->
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <div class="ml-2 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">
                    Payment Issues
                  </dt>
                  <dd class="text-sm sm:text-lg font-medium text-gray-900">
                    {{ stats.paymentIssues }}
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div class="ml-2 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">
                    Success Rate
                  </dt>
                  <dd class="text-sm sm:text-lg font-medium text-gray-900">
                    {{ stats.successRate }}
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
                My Support Requests
              </h3>
              <button @click="viewAllTickets" class="text-sm font-medium text-green-600 hover:text-green-500">
                View all
              </button>
            </div>
            
            <div v-if="loadingTickets" class="flex justify-center py-4">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
            </div>
            
            <div v-else-if="!tickets.length" class="text-center py-6">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
              </svg>
              <p class="text-sm text-gray-500 mb-2">No support requests yet</p>
              <button @click="openCreateTicketModal" class="text-sm font-medium text-green-600 hover:text-green-500">
                Get business support
              </button>
            </div>
            
            <div v-else class="space-y-3">
              <TicketCard 
                v-for="ticket in tickets.slice(0, 3)" 
                :key="ticket.ticket_id"
                :ticket="ticket"
                @click="viewTicketDetails"
              />
            </div>
          </div>
        </div>

        <!-- Farmer Resources & FAQ -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-3 py-4 sm:px-6 sm:py-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-base sm:text-lg leading-6 font-medium text-gray-900">
                Farmer Resources
              </h3>
              <button @click="viewAllFAQs" class="text-sm font-medium text-green-600 hover:text-green-500">
                View all
              </button>
            </div>
            
            <div v-if="loadingFAQs" class="flex justify-center py-4">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
            </div>
            
            <div v-else-if="!faqs.length" class="text-center py-6">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-gray-500">No resources available</p>
            </div>
            
            <div v-else class="space-y-3">
              <div 
                v-for="faq in faqs.slice(0, 5)" 
                :key="faq.faq_id"
                @click="viewFAQ(faq)"
                class="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
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

      <!-- Business Help Categories -->
      <div class="mt-8 bg-green-50 rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Business Support Categories</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="text-center">
            <div class="bg-green-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900">Order Management</h4>
            <p class="text-xs text-gray-600 mt-1">Order fulfillment, modifications, and tracking</p>
          </div>
          <div class="text-center">
            <div class="bg-blue-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900">Payment & Payouts</h4>
            <p class="text-xs text-gray-600 mt-1">Earnings, payout schedules, and payment issues</p>
          </div>
          <div class="text-center">
            <div class="bg-purple-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900">Product Listings</h4>
            <p class="text-xs text-gray-600 mt-1">Creating, editing, and optimizing your listings</p>
          </div>
          <div class="text-center">
            <div class="bg-yellow-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900">Business Growth</h4>
            <p class="text-xs text-gray-600 mt-1">Tips and strategies to increase sales</p>
          </div>
          <div class="text-center">
            <div class="bg-red-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900">Quality Issues</h4>
            <p class="text-xs text-gray-600 mt-1">Product quality concerns and resolutions</p>
          </div>
          <div class="text-center">
            <div class="bg-gray-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900">Technical Support</h4>
            <p class="text-xs text-gray-600 mt-1">App issues and technical difficulties</p>
          </div>
        </div>
      </div>

      <!-- Business Performance Tips -->
      <div class="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Performance Tips</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="text-sm font-semibold text-gray-900 mb-2">Increase Your Sales</h4>
            <ul class="text-xs text-gray-600 space-y-1">
              <li>• Upload high-quality product photos</li>
              <li>• Keep your listings updated with accurate inventory</li>
              <li>• Respond quickly to customer inquiries</li>
              <li>• Offer competitive prices in your area</li>
            </ul>
          </div>
          <div>
            <h4 class="text-sm font-semibold text-gray-900 mb-2">Improve Customer Satisfaction</h4>
            <ul class="text-xs text-gray-600 space-y-1">
              <li>• Ensure products are fresh and properly packaged</li>
              <li>• Fulfill orders promptly and accurately</li>
              <li>• Communicate any delays or issues immediately</li>
              <li>• Maintain good relationships with delivery riders</li>
            </ul>
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
    <div v-if="showFAQModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">{{ selectedFAQ?.question }}</h3>
          <button @click="closeFAQModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="p-6">
          <div class="prose prose-sm max-w-none text-gray-700" v-html="selectedFAQ?.answer"></div>
          <div class="mt-6 pt-6 border-t border-gray-200">
            <p class="text-sm text-gray-600 mb-3">Was this helpful?</p>
            <div class="flex space-x-3">
              <button class="btn-secondary text-sm">Yes</button>
              <button class="btn-secondary text-sm">No</button>
              <button @click="openCreateTicketModal" class="btn-primary text-sm">Need more help?</button>
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
  paymentIssues: 0,
  avgResponse: '1.5h',
  successRate: '94%'
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
    stats.paymentIssues = tickets.value.filter(t => t.category === 'payment_problem').length
  } catch (error) {
    console.error('Failed to load tickets:', error)
  } finally {
    loadingTickets.value = false
  }
}

const loadFAQs = async () => {
  loadingFAQs.value = true
  try {
    const response = await communicationAPI.getFAQs({ target_role: 'farmer' })
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
  console.log('View all tickets')
}

const viewAllFAQs = () => {
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