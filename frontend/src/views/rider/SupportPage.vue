<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
        <div class="flex flex-col space-y-3 sm:space-y-0 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex-1 min-w-0">
            <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold leading-7 text-gray-900">
              Rider Support Center
            </h1>
            <p class="mt-1 text-sm text-gray-500">
              Get help with deliveries, safety, and earnings
            </p>
          </div>
          <div class="w-full sm:w-auto sm:ml-4 flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
            <button @click="openEmergencyContact" class="btn-secondary text-sm w-full sm:w-auto inline-flex justify-center items-center">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              Emergency
            </button>
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
      <!-- Emergency Alert -->
      <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium text-red-800">Emergency Assistance</h3>
            <p class="mt-1 text-sm text-red-700">
              In case of emergency during delivery, call <strong>0800-VEGAS-1</strong> (toll-free) or use the Emergency button above.
            </p>
          </div>
        </div>
      </div>

      <!-- Delivery Stats -->
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div class="ml-2 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">
                    Delivery Issues
                  </dt>
                  <dd class="text-sm sm:text-lg font-medium text-gray-900">
                    {{ stats.deliveryIssues }}
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div class="ml-2 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">
                    Safety Score
                  </dt>
                  <dd class="text-sm sm:text-lg font-medium text-gray-900">
                    {{ stats.safetyScore }}
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
                Get delivery support
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

        <!-- Rider Resources & FAQ -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-3 py-4 sm:px-6 sm:py-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-base sm:text-lg leading-6 font-medium text-gray-900">
                Rider Resources
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

      <!-- Delivery Support Categories -->
      <div class="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Delivery Support Categories</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="text-center">
            <div class="bg-blue-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900">Delivery Operations</h4>
            <p class="text-xs text-gray-600 mt-1">Route optimization, customer contact, and delivery issues</p>
          </div>
          <div class="text-center">
            <div class="bg-green-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900">Payment Issues</h4>
            <p class="text-xs text-gray-600 mt-1">Earnings, tips, fuel allowances, and payment delays</p>
          </div>
          <div class="text-center">
            <div class="bg-red-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900">Safety & Security</h4>
            <p class="text-xs text-gray-600 mt-1">Personal safety, emergency procedures, and incident reporting</p>
          </div>
          <div class="text-center">
            <div class="bg-purple-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900">App & Technical</h4>
            <p class="text-xs text-gray-600 mt-1">GPS issues, app crashes, and technical difficulties</p>
          </div>
          <div class="text-center">
            <div class="bg-yellow-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900">Customer Relations</h4>
            <p class="text-xs text-gray-600 mt-1">Difficult customers, complaints, and communication tips</p>
          </div>
          <div class="text-center">
            <div class="bg-gray-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-gray-900">General Support</h4>
            <p class="text-xs text-gray-600 mt-1">Schedule changes, account issues, and general questions</p>
          </div>
        </div>
      </div>

      <!-- Safety Guidelines -->
      <div class="mt-8 bg-yellow-50 rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Safety Guidelines</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="text-sm font-semibold text-gray-900 mb-2">Before Delivery</h4>
            <ul class="text-xs text-gray-600 space-y-1">
              <li>• Check your vehicle condition and fuel</li>
              <li>• Verify delivery address and contact information</li>
              <li>• Carry emergency contact numbers</li>
              <li>• Inform someone of your delivery route</li>
            </ul>
          </div>
          <div>
            <h4 class="text-sm font-semibold text-gray-900 mb-2">During Delivery</h4>
            <ul class="text-xs text-gray-600 space-y-1">
              <li>• Follow traffic rules and ride safely</li>
              <li>• Keep products secure and temperature-controlled</li>
              <li>• Call customers if you cannot find the address</li>
              <li>• Report any suspicious or unsafe situations immediately</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Emergency Contacts -->
      <div class="mt-8 bg-red-50 rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Emergency Contacts</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="bg-white rounded-lg p-4 text-center">
            <div class="text-red-600 font-semibold">Vegas Emergency</div>
            <div class="text-lg font-bold text-gray-900">0800-VEGAS-1</div>
            <div class="text-xs text-gray-500">24/7 Support</div>
          </div>
          <div class="bg-white rounded-lg p-4 text-center">
            <div class="text-red-600 font-semibold">Police Emergency</div>
            <div class="text-lg font-bold text-gray-900">999</div>
            <div class="text-xs text-gray-500">National Emergency</div>
          </div>
          <div class="bg-white rounded-lg p-4 text-center">
            <div class="text-red-600 font-semibold">Medical Emergency</div>
            <div class="text-lg font-bold text-gray-900">911</div>
            <div class="text-xs text-gray-500">Ambulance Service</div>
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

    <!-- Emergency Contact Modal -->
    <div v-if="showEmergencyModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 class="text-lg font-medium text-red-900">Emergency Contact</h3>
          <button @click="closeEmergencyModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="p-6">
          <div class="text-center mb-6">
            <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
              <svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">Need Emergency Help?</h3>
            <p class="text-sm text-gray-600 mb-4">
              If this is a life-threatening emergency, call 999 immediately.
              For Vegas-related emergencies, use our 24/7 hotline.
            </p>
          </div>
          <div class="space-y-3">
            <a href="tel:0800-VEGAS-1" class="w-full bg-red-600 text-white py-3 px-4 rounded-md text-center font-medium hover:bg-red-700 block">
              Call Vegas Emergency: 0800-VEGAS-1
            </a>
            <a href="tel:999" class="w-full bg-gray-600 text-white py-3 px-4 rounded-md text-center font-medium hover:bg-gray-700 block">
              Call 999 (Police/Fire/Medical)
            </a>
            <button @click="closeEmergencyModal" class="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-md text-center font-medium hover:bg-gray-200">
              Cancel
            </button>
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
const showEmergencyModal = ref(false)
const editingTicket = ref(null)
const selectedFAQ = ref(null)

const stats = reactive({
  openTickets: 0,
  deliveryIssues: 0,
  avgResponse: '45min',
  safetyScore: '4.8/5'
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
    stats.deliveryIssues = tickets.value.filter(t => t.category === 'delivery_issue').length
  } catch (error) {
    console.error('Failed to load tickets:', error)
  } finally {
    loadingTickets.value = false
  }
}

const loadFAQs = async () => {
  loadingFAQs.value = true
  try {
    const response = await communicationAPI.getFAQs({ target_role: 'rider' })
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

const openEmergencyContact = () => {
  showEmergencyModal.value = true
}

const closeEmergencyModal = () => {
  showEmergencyModal.value = false
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