<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div class="py-4 sm:py-6">
          <div class="flex flex-col space-y-3 sm:space-y-0 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex-1 min-w-0">
              <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Support Management</h1>
              <p class="mt-1 text-sm text-gray-500">Manage support tickets and FAQs</p>
            </div>
            <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 w-full sm:w-auto">
              <button
                @click="showTicketModal = true"
                class="inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors w-full sm:w-auto"
              >
                <PlusIcon class="w-4 h-4 mr-2" />
                New Ticket
              </button>
              <button
                @click="showFAQModal = true"
                class="inline-flex items-center justify-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors w-full sm:w-auto"
              >
                <PlusIcon class="w-4 h-4 mr-2" />
                New FAQ
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Overview -->
    <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
        <div class="bg-white rounded-lg shadow p-3 sm:p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <ExclamationTriangleIcon class="w-6 w-6 sm:w-8 sm:h-8 text-red-500" />
            </div>
            <div class="ml-2 sm:ml-4">
              <p class="text-xs sm:text-sm font-medium text-gray-500">Open Tickets</p>
              <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ stats.openTickets }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-3 sm:p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <ClockIcon class="w-6 h-6 sm:w-8 sm:h-8 text-yellow-500" />
            </div>
            <div class="ml-2 sm:ml-4">
              <p class="text-xs sm:text-sm font-medium text-gray-500">In Progress</p>
              <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ stats.inProgressTickets }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-3 sm:p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <CheckCircleIcon class="w-6 h-6 sm:w-8 sm:h-8 text-green-500" />
            </div>
            <div class="ml-2 sm:ml-4">
              <p class="text-xs sm:text-sm font-medium text-gray-500">Resolved Today</p>
              <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ stats.resolvedToday }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-3 sm:p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <UserGroupIcon class="w-6 h-6 sm:w-8 sm:h-8 text-blue-500" />
            </div>
            <div class="ml-2 sm:ml-4">
              <p class="text-xs sm:text-sm font-medium text-gray-500">Unassigned</p>
              <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ stats.unassignedTickets }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="bg-white rounded-lg shadow">
        <div class="border-b border-gray-200">
          <nav class="flex overflow-x-auto px-3 sm:px-6" aria-label="Tabs">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              @click="activeTab = tab.key"
              :class="[
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                'whitespace-nowrap py-4 px-3 sm:px-1 border-b-2 font-medium text-sm flex items-center mr-6 sm:mr-8'
              ]"
            >
              <component :is="tab.icon" class="w-4 h-4 sm:w-5 sm:h-5 mr-1 sm:mr-2" />
              <span class="hidden sm:inline">{{ tab.name }}</span>
              <span class="sm:hidden">{{ tab.name.split(' ')[0] }}</span>
            </button>
          </nav>
        </div>

        <!-- Tickets Tab -->
        <div v-show="activeTab === 'tickets'" class="p-3 sm:p-6">
          <!-- Filters -->
          <div class="mb-6 space-y-4 sm:space-y-0 sm:flex sm:flex-wrap sm:gap-4">
            <div class="w-full sm:flex-1 sm:min-w-64">
              <input
                v-model="ticketFilters.search"
                type="text"
                placeholder="Search tickets..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div class="grid grid-cols-3 gap-2 sm:flex sm:gap-4">
              <select
                v-model="ticketFilters.status"
                class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                <option value="">All Status</option>
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="resolved">Resolved</option>
                <option value="closed">Closed</option>
              </select>
              <select
                v-model="ticketFilters.priority"
                class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                <option value="">All Priority</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
              <select
                v-model="ticketFilters.assignedTo"
                class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm col-span-3 sm:col-span-1"
              >
                <option value="">All Assignments</option>
                <option value="unassigned">Unassigned</option>
                <option v-for="admin in admins" :key="admin.user_id" :value="admin.user_id">
                  {{ admin.first_name }} {{ admin.last_name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Tickets List -->
          <div class="space-y-4">
            <TicketCard
              v-for="ticket in filteredTickets"
              :key="ticket.ticket_id"
              :ticket="ticket"
              :is-admin="true"
              @click="openTicketModal"
              @update="handleTicketUpdate"
              @assign="handleTicketAssign"
              @resolve="handleTicketResolve"
              @edit="openTicketModal"
            />
          </div>

          <!-- Pagination -->
          <div v-if="ticketPagination.totalPages > 1" class="mt-6 flex items-center justify-between">
            <div class="text-sm text-gray-700">
              Showing {{ (ticketPagination.currentPage - 1) * ticketPagination.perPage + 1 }} to 
              {{ Math.min(ticketPagination.currentPage * ticketPagination.perPage, ticketPagination.total) }} 
              of {{ ticketPagination.total }} tickets
            </div>
            <div class="flex space-x-2">
              <button
                @click="ticketPagination.currentPage--"
                :disabled="ticketPagination.currentPage === 1"
                class="px-3 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Previous
              </button>
              <button
                @click="ticketPagination.currentPage++"
                :disabled="ticketPagination.currentPage === ticketPagination.totalPages"
                class="px-3 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          </div>
        </div>

        <!-- FAQs Tab -->
        <div v-show="activeTab === 'faqs'" class="p-3 sm:p-6">
          <!-- FAQ Filters -->
          <div class="mb-6 space-y-4 sm:space-y-0 sm:flex sm:flex-wrap sm:gap-4">
            <div class="w-full sm:flex-1 sm:min-w-64">
              <input
                v-model="faqFilters.search"
                type="text"
                placeholder="Search FAQs..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <select
              v-model="faqFilters.targetRole"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Roles</option>
              <option value="customer">Customer</option>
              <option value="farmer">Farmer</option>
              <option value="rider">Rider</option>
              <option value="all">All Users</option>
            </select>
            <select
              v-model="faqFilters.isActive"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Status</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>

          <!-- FAQs List -->
          <div class="space-y-4">
            <div
              v-for="faq in filteredFAQs"
              :key="faq.faq_id"
              class="bg-white border border-gray-200 rounded-lg p-6"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    <h3 class="text-lg font-medium text-gray-900">{{ faq.question }}</h3>
                    <span :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      faq.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    ]">
                      {{ faq.is_active ? 'Active' : 'Inactive' }}
                    </span>
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {{ faq.target_role === 'all' ? 'All Users' : faq.target_role.charAt(0).toUpperCase() + faq.target_role.slice(1) }}
                    </span>
                  </div>
                  <p class="text-gray-600 mb-3">{{ faq.answer }}</p>
                  <div class="text-sm text-gray-500">
                    Order: {{ faq.order_index }} | Created: {{ formatDate(faq.created_at) }}
                  </div>
                </div>
                <div class="ml-4 flex space-x-2">
                  <button
                    @click="editFAQ(faq)"
                    class="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                  >
                    <PencilIcon class="w-5 h-5" />
                  </button>
                  <button
                    @click="deleteFAQ(faq)"
                    class="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <TrashIcon class="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Support Ticket Modal -->
    <SupportTicketModal
      v-if="showTicketModal"
      :key="selectedTicket ? selectedTicket.ticket_id : 'new-ticket'"
      :ticket="selectedTicket"
      :is-admin="true"
      @close="showTicketModal = false"
      @saved="handleTicketSaved"
    />

    <!-- FAQ Modal -->
    <FAQModal
      v-if="showFAQModal"
      :faq="selectedFAQ"
      @close="showFAQModal = false"
      @saved="handleFAQSaved"
    />

    <!-- Resolution Notes Modal -->
    <ResolutionNotesModal
      :is-open="showResolutionModal"
      @close="showResolutionModal = false"
      @submit="submitResolutionNotes"
    />

    <!-- Assign Ticket Modal -->
    <AssignTicketModal
      :is-open="showAssignModal"
      :admins="admins"
      @close="showAssignModal = false"
      @submit="submitAssignment"
    />
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import {
  PlusIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon,
  UserGroupIcon,
  TicketIcon,
  QuestionMarkCircleIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import { communicationAPI, usersAPI } from '@/services/api'
import TicketCard from '@/components/support/TicketCard.vue'
import SupportTicketModal from '@/components/support/SupportTicketModal.vue'
import FAQModal from '@/components/FAQModal.vue'
import ResolutionNotesModal from '@/components/support/ResolutionNotesModal.vue'
import AssignTicketModal from '@/components/support/AssignTicketModal.vue'

export default {
  name: 'SupportManagement',
  components: {
    TicketCard,
    SupportTicketModal,
    FAQModal,
    ResolutionNotesModal,
    AssignTicketModal,
    PlusIcon,
    ExclamationTriangleIcon,
    ClockIcon,
    CheckCircleIcon,
    UserGroupIcon,
    TicketIcon,
    QuestionMarkCircleIcon,
    PencilIcon,
    TrashIcon
  },
  setup() {
    const toast = useToast()
    const activeTab = ref('tickets')
    const showTicketModal = ref(false)
    const showFAQModal = ref(false)
    const showResolutionModal = ref(false)
    const resolvingTicket = ref(null)
    const showAssignModal = ref(false)
    const assigningTicket = ref(null)
    const selectedTicket = ref(null)
    const selectedFAQ = ref(null)

    const stats = reactive({
      openTickets: 0,
      inProgressTickets: 0,
      resolvedToday: 0,
      unassignedTickets: 0
    })

    const tickets = ref([])
    const faqs = ref([])
    const admins = ref([])

    const ticketFilters = reactive({
      search: '',
      status: '',
      priority: '',
      assignedTo: ''
    })

    const faqFilters = reactive({
      search: '',
      targetRole: '',
      isActive: ''
    })

    const ticketPagination = reactive({
      currentPage: 1,
      perPage: 10,
      total: 0,
      totalPages: 0
    })

    const tabs = [
      { key: 'tickets', name: 'Support Tickets', icon: TicketIcon },
      { key: 'faqs', name: 'FAQs', icon: QuestionMarkCircleIcon }
    ]

    const filteredTickets = computed(() => {
      let filtered = tickets.value

      if (ticketFilters.search) {
        const search = ticketFilters.search.toLowerCase()
        filtered = filtered.filter(ticket => 
          ticket.ticket_number.toLowerCase().includes(search) ||
          ticket.subject.toLowerCase().includes(search) ||
          ticket.description.toLowerCase().includes(search)
        )
      }

      if (ticketFilters.status) {
        filtered = filtered.filter(ticket => ticket.status === ticketFilters.status)
      }

      if (ticketFilters.priority) {
        filtered = filtered.filter(ticket => ticket.priority === ticketFilters.priority)
      }

      if (ticketFilters.assignedTo) {
        if (ticketFilters.assignedTo === 'unassigned') {
          filtered = filtered.filter(ticket => !ticket.assigned_to)
        } else {
          filtered = filtered.filter(ticket => ticket.assigned_to?.user_id === ticketFilters.assignedTo)
        }
      }

      return filtered
    })

    const filteredFAQs = computed(() => {
      let filtered = faqs.value

      if (faqFilters.search) {
        const search = faqFilters.search.toLowerCase()
        filtered = filtered.filter(faq => 
          faq.question.toLowerCase().includes(search) ||
          faq.answer.toLowerCase().includes(search)
        )
      }

      if (faqFilters.targetRole) {
        filtered = filtered.filter(faq => faq.target_role === faqFilters.targetRole)
      }

      if (faqFilters.isActive !== '') {
        const isActive = faqFilters.isActive === 'true'
        filtered = filtered.filter(faq => faq.is_active === isActive)
      }

      return filtered
    })

    const loadStats = async () => {
      try {
        const [openResponse, inProgressResponse, resolvedResponse, unassignedResponse] = await Promise.all([
          communicationAPI.getSupportTickets({ status: 'open' }),
          communicationAPI.getSupportTickets({ status: 'in_progress' }),
          communicationAPI.getSupportTickets({ status: 'resolved', created_at__date: new Date().toISOString().split('T')[0] }),
          communicationAPI.getUnassignedTickets()
        ])

        stats.openTickets = openResponse.results?.length || openResponse.length || 0
        stats.inProgressTickets = inProgressResponse.results?.length || inProgressResponse.length || 0
        stats.resolvedToday = resolvedResponse.results?.length || resolvedResponse.length || 0
        stats.unassignedTickets = unassignedResponse.results?.length || unassignedResponse.length || 0
      } catch (error) {
        console.error('Error loading stats:', error)
      }
    }

    const loadTickets = async () => {
      try {
        const response = await communicationAPI.getSupportTickets()
        tickets.value = response.results || response || []
      } catch (error) {
        console.error('Error loading tickets:', error)
      }
    }

    const loadFAQs = async () => {
      try {
        const response = await communicationAPI.getFAQs()
        faqs.value = response.results || response || []
      } catch (error) {
        console.error('Error loading FAQs:', error)
      }
    }

    const loadAdmins = async () => {
      try {
        const response = await usersAPI.getUsers({ user_role: 'admin' });
        admins.value = response.results || response || [];
      } catch (error) {
        console.error('Error loading admins:', error);
      }
    };

    const handleTicketUpdate = async (ticket) => {
      await loadTickets()
      await loadStats()
    }

    const handleTicketAssign = (ticket) => {
      assigningTicket.value = ticket
      showAssignModal.value = true
    }

    const submitAssignment = async (adminId) => {
      if (!adminId) {
        toast.error('Admin is required to assign a ticket.')
        return
      }
      try {
        await communicationAPI.assignTicket(assigningTicket.value.ticket_id, adminId)
        toast.success('Ticket assigned successfully!')
        await loadTickets()
        await loadStats()
      } catch (error) {
        console.error('Error assigning ticket:', error)
        toast.error('Failed to assign ticket. Check console for details.')
      } finally {
        assigningTicket.value = null
      }
    }

    const handleTicketResolve = (ticket) => {
      resolvingTicket.value = ticket
      showResolutionModal.value = true
    }

    const submitResolutionNotes = async (resolutionNotes) => {
      if (!resolutionNotes) {
        toast.error('Resolution notes are required to resolve a ticket.')
        return
      }
      try {
        await communicationAPI.resolveTicket(resolvingTicket.value.ticket_id, { resolution_notes: resolutionNotes })
        toast.success('Ticket resolved successfully!')
        await loadTickets()
        await loadStats()
      } catch (error) {
        console.error('Error resolving ticket:', error)
        toast.error('Failed to resolve ticket. Check console for details.')
      } finally {
        resolvingTicket.value = null
      }
    }

    const openTicketModal = (ticket) => {
      console.log('Attempting to open modal for ticket:', ticket);
      showTicketModal.value = true; // Set visibility first
      selectedTicket.value = ticket; // Then set the data
      console.log('showTicketModal after setting:', showTicketModal.value);
    }

    const handleTicketSaved = () => {
      showTicketModal.value = false
      selectedTicket.value = null
      loadTickets()
      loadStats()
    }

    const editFAQ = (faq) => {
      selectedFAQ.value = faq
      showFAQModal.value = true
    }

    const deleteFAQ = async (faq) => {
      if (confirm('Are you sure you want to delete this FAQ?')) {
        try {
          await communicationAPI.deleteFAQ(faq.faq_id)
          await loadFAQs()
        } catch (error) {
          console.error('Error deleting FAQ:', error)
        }
      }
    }

    const handleFAQSaved = () => {
      showFAQModal.value = false
      selectedFAQ.value = null
      loadFAQs()
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    onMounted(() => {
      loadStats()
      loadTickets()
      loadFAQs()
      loadAdmins()
    })

    return {
      activeTab,
      showTicketModal,
      showFAQModal,
      selectedTicket,
      selectedFAQ,
      stats,
      tickets,
      faqs,
      admins,
      ticketFilters,
      faqFilters,
      ticketPagination,
      tabs,
      filteredTickets,
      filteredFAQs,
      openTicketModal,
      handleTicketUpdate,
      handleTicketAssign,
      submitAssignment,
      handleTicketResolve,
      submitResolutionNotes,
      handleTicketSaved,
      editFAQ,
      deleteFAQ,
      handleFAQSaved,
      formatDate,
      showResolutionModal,
      resolvingTicket,
      showAssignModal,
      assigningTicket
    }
  }
}
</script>
