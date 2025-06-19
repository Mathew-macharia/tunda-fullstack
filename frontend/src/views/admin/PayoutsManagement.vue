<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 sm:mb-8 space-y-4 sm:space-y-0">
        <div>
          <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Payouts Management</h1>
          <p class="mt-1 sm:mt-2 text-sm sm:text-base text-gray-600">Process and manage farmer and rider payouts</p>
        </div>
        <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
          <button @click="exportPayouts" 
                  class="w-full sm:w-auto bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors text-sm">
            Export Data
          </button>
          <button @click="showCreateModal = true" 
                  class="w-full sm:w-auto bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors text-sm">
            Create Payout
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-6">
          <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Total Payouts</dt>
          <dd class="text-lg sm:text-2xl font-bold text-gray-900">{{ stats.total }}</dd>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-6">
          <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Pending</dt>
          <dd class="text-lg sm:text-2xl font-bold text-yellow-600">{{ formatCurrency(stats.pendingAmount) }}</dd>
          <p class="text-xs text-gray-500 mt-1">{{ stats.pending }} payouts</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-6">
          <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Processed</dt>
          <dd class="text-lg sm:text-2xl font-bold text-green-600">{{ formatCurrency(stats.processedAmount) }}</dd>
          <p class="text-xs text-gray-500 mt-1">{{ stats.processed }} payouts</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-6">
          <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Failed</dt>
          <dd class="text-lg sm:text-2xl font-bold text-red-600">{{ formatCurrency(stats.failedAmount) }}</dd>
          <p class="text-xs text-gray-500 mt-1">{{ stats.failed }} payouts</p>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6 mb-6">
        <!-- Mobile Filter Toggle -->
        <div class="sm:hidden mb-4">
          <button @click="showMobileFilters = !showMobileFilters" 
                  class="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-sm font-medium text-gray-700">Filters</span>
            <svg class="w-5 h-5 transform transition-transform" 
                 :class="showMobileFilters ? 'rotate-180' : ''"
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </button>
        </div>

        <!-- Filter Content -->
        <div :class="showMobileFilters || !isMobile ? 'block' : 'hidden'" class="space-y-4 sm:space-y-0">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select v-model="filters.status" 
                      class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm">
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="processed">Processed</option>
                <option value="failed">Failed</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">User Type</label>
              <select v-model="filters.user_role" 
                      class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm">
                <option value="">All Users</option>
                <option value="farmer">Farmers</option>
                <option value="rider">Riders</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
              <select v-model="filters.dateRange" 
                      class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm">
                <option value="">All Time</option>
                <option value="7">Last 7 days</option>
                <option value="30">Last 30 days</option>
                <option value="90">Last 3 months</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <input v-model="filters.search" type="text" 
                     placeholder="Search by user..."
                     class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm">
            </div>
            <div class="flex flex-col sm:flex-row sm:items-end space-y-2 sm:space-y-0 sm:space-x-2">
              <button @click="loadPayouts" 
                      class="w-full sm:w-auto bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors text-sm">
                Apply
              </button>
              <button @click="resetFilters" 
                      class="w-full sm:w-auto bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors text-sm">
                Reset
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Bulk Actions -->
      <div v-if="selectedPayouts.length > 0" class="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
          <div class="flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-2 sm:space-y-0">
            <span class="text-sm font-medium text-blue-900">
              {{ selectedPayouts.length }} payout(s) selected
            </span>
            <button @click="clearSelection" 
                    class="text-blue-600 hover:text-blue-700 text-sm font-medium text-left">
              Clear Selection
            </button>
          </div>
          <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
            <button @click="bulkProcessPayouts" 
                    :disabled="!canBulkProcess"
                    class="bg-green-600 text-white px-3 py-2 rounded-md text-sm hover:bg-green-700 disabled:opacity-50">
              Process Selected
            </button>
            <button @click="bulkFailPayouts" 
                    :disabled="!canBulkFail"
                    class="bg-red-600 text-white px-3 py-2 rounded-md text-sm hover:bg-red-700 disabled:opacity-50">
              Mark as Failed
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile Cards / Desktop Table -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          <p class="mt-2 text-gray-600 text-sm">Loading payouts...</p>
        </div>

        <div v-else-if="payouts.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900">No payouts found</h3>
          <p class="mt-2 text-gray-600 text-sm">No payouts match your current filters.</p>
        </div>

        <!-- Mobile Cards View -->
        <div v-else class="sm:hidden">
          <div class="p-4 border-b border-gray-200">
            <label class="flex items-center space-x-2">
              <input type="checkbox" 
                     :checked="isAllSelected" 
                     @change="toggleSelectAll"
                     class="rounded border-gray-300 text-green-600 focus:ring-green-500">
              <span class="text-sm font-medium text-gray-700">Select All</span>
            </label>
          </div>
          <div class="divide-y divide-gray-200">
            <div v-for="payout in payouts" :key="payout.payout_id" 
                 :class="selectedPayouts.includes(payout.payout_id) ? 'bg-blue-50' : ''"
                 class="p-4">
              <div class="flex items-start space-x-3">
                <input type="checkbox" 
                       :value="payout.payout_id"
                       v-model="selectedPayouts"
                       class="mt-1 rounded border-gray-300 text-green-600 focus:ring-green-500">
                
                <div class="flex-1 min-w-0">
                  <!-- User Info -->
                  <div class="flex items-center space-x-3 mb-3">
                    <div class="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <span class="text-white font-medium text-sm">
                        {{ payout.user_username?.charAt(0)?.toUpperCase() || 'U' }}
                      </span>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 truncate">{{ payout.user_username }}</p>
                      <p class="text-xs text-gray-500 capitalize">{{ payout.user_role }}</p>
                    </div>
                  </div>

                  <!-- Payout Details -->
                  <div class="grid grid-cols-2 gap-3 mb-3">
                    <div>
                      <p class="text-xs text-gray-500">Amount</p>
                      <p class="text-sm font-medium text-gray-900">KES {{ formatCurrency(payout.amount) }}</p>
                    </div>
                    <div>
                      <p class="text-xs text-gray-500">Status</p>
                      <span :class="getStatusClass(payout.status)" 
                            class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                        {{ getStatusLabel(payout.status) }}
                      </span>
                    </div>
                    <div>
                      <p class="text-xs text-gray-500">Order</p>
                      <p class="text-sm text-gray-900">
                        {{ payout.order ? '#' + (payout.order.order_number || payout.order.order_id) : '-' }}
                      </p>
                    </div>
                    <div>
                      <p class="text-xs text-gray-500">Date</p>
                      <p class="text-sm text-gray-900">{{ formatDate(payout.payout_date) }}</p>
                    </div>
                  </div>

                  <!-- Actions -->
                  <div class="flex flex-wrap gap-2">
                    <button @click="viewPayout(payout)" 
                            class="text-blue-600 hover:text-blue-700 text-sm font-medium">
                      View
                    </button>
                    <button v-if="payout.status === 'pending'" 
                            @click="processPayout(payout)"
                            class="text-green-600 hover:text-green-700 text-sm font-medium">
                      Process
                    </button>
                    <button v-if="payout.status === 'pending'" 
                            @click="failPayout(payout)"
                            class="text-red-600 hover:text-red-700 text-sm font-medium">
                      Fail
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Desktop Table View -->
        <div class="hidden sm:block overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="w-4 px-6 py-3">
                  <input type="checkbox" 
                         :checked="isAllSelected" 
                         @change="toggleSelectAll"
                         class="rounded border-gray-300 text-green-600 focus:ring-green-500">
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Order
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="payout in payouts" :key="payout.payout_id" 
                  :class="selectedPayouts.includes(payout.payout_id) ? 'bg-blue-50' : 'hover:bg-gray-50'">
                <td class="px-6 py-4">
                  <input type="checkbox" 
                         :value="payout.payout_id"
                         v-model="selectedPayouts"
                         class="rounded border-gray-300 text-green-600 focus:ring-green-500">
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <span class="text-white font-medium text-xs">
                        {{ payout.user_username?.charAt(0)?.toUpperCase() || 'U' }}
                      </span>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900">{{ payout.user_username }}</p>
                      <p class="text-xs text-gray-500 capitalize">{{ payout.user_role }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm font-medium text-gray-900">
                    KES {{ formatCurrency(payout.amount) }}
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span :class="getStatusClass(payout.status)" 
                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                    {{ getStatusLabel(payout.status) }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div v-if="payout.order" class="text-sm text-gray-900">
                    #{{ payout.order.order_number || payout.order.order_id }}
                  </div>
                  <div v-else class="text-sm text-gray-500">-</div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm text-gray-900">{{ formatDate(payout.payout_date) }}</div>
                  <div v-if="payout.processed_date" class="text-xs text-gray-500">
                    Processed: {{ formatDate(payout.processed_date) }}
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center space-x-2">
                    <button @click="viewPayout(payout)" 
                            class="text-blue-600 hover:text-blue-700 text-sm font-medium">
                      View
                    </button>
                    <button v-if="payout.status === 'pending'" 
                            @click="processPayout(payout)"
                            class="text-green-600 hover:text-green-700 text-sm font-medium">
                      Process
                    </button>
                    <button v-if="payout.status === 'pending'" 
                            @click="failPayout(payout)"
                            class="text-red-600 hover:text-red-700 text-sm font-medium">
                      Fail
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.total > pagination.pageSize" class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
            <div class="flex items-center">
              <p class="text-sm text-gray-700">
                Showing {{ ((pagination.page - 1) * pagination.pageSize) + 1 }} to {{ Math.min(pagination.page * pagination.pageSize, pagination.total) }} of {{ pagination.total }} results
              </p>
            </div>
            <div class="flex items-center justify-center sm:justify-end space-x-2">
              <button @click="goToPage(pagination.page - 1)"
                      :disabled="pagination.page === 1"
                      class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50">
                Previous
              </button>
              <span class="px-3 py-1 text-sm text-gray-700">
                Page {{ pagination.page }} of {{ Math.ceil(pagination.total / pagination.pageSize) }}
              </span>
              <button @click="goToPage(pagination.page + 1)"
                      :disabled="pagination.page >= Math.ceil(pagination.total / pagination.pageSize)"
                      class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50">
                Next
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Process Payout Modal -->
      <div v-if="showProcessModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-screen overflow-y-auto">
          <div class="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Process Payout</h3>
            <button @click="closeProcessModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <form @submit.prevent="confirmProcessPayout" class="p-4 sm:p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Transaction Reference</label>
              <input v-model="processForm.transactionReference" type="text" required
                     placeholder="Enter transaction reference"
                     class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm">
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
              <textarea v-model="processForm.notes" rows="3"
                        placeholder="Add any processing notes..."
                        class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm"></textarea>
            </div>

            <div class="flex flex-col sm:flex-row sm:justify-end space-y-2 sm:space-y-0 sm:space-x-3 pt-4">
              <button type="button" @click="closeProcessModal" 
                      class="w-full sm:w-auto px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                Cancel
              </button>
              <button type="submit" :disabled="!processForm.transactionReference || processing"
                      class="w-full sm:w-auto px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50">
                {{ processing ? 'Processing...' : 'Process Payout' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Fail Payout Modal -->
      <div v-if="showFailModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-screen overflow-y-auto">
          <div class="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Mark Payout as Failed</h3>
            <button @click="closeFailModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <form @submit.prevent="confirmFailPayout" class="p-4 sm:p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Reason for Failure</label>
              <textarea v-model="failForm.notes" rows="4" required
                        placeholder="Explain why this payout failed..."
                        class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm"></textarea>
            </div>

            <div class="flex flex-col sm:flex-row sm:justify-end space-y-2 sm:space-y-0 sm:space-x-3 pt-4">
              <button type="button" @click="closeFailModal" 
                      class="w-full sm:w-auto px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                Cancel
              </button>
              <button type="submit" :disabled="!failForm.notes || processing"
                      class="w-full sm:w-auto px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 disabled:opacity-50">
                {{ processing ? 'Processing...' : 'Mark as Failed' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { financeAPI } from '@/services/api'

const loading = ref(false)
const processing = ref(false)
const payouts = ref([])
const selectedPayouts = ref([])
const selectedPayout = ref(null)

const showProcessModal = ref(false)
const showFailModal = ref(false)
const showCreateModal = ref(false)
const showMobileFilters = ref(false)

const stats = ref({
  total: 0,
  pending: 0,
  processed: 0,
  failed: 0,
  pendingAmount: 0,
  processedAmount: 0,
  failedAmount: 0
})

const filters = ref({
  status: '',
  user_role: '',
  dateRange: '',
  search: ''
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const processForm = ref({
  transactionReference: '',
  notes: ''
})

const failForm = ref({
  notes: ''
})

const isMobile = computed(() => {
  return window.innerWidth < 640
})

const isAllSelected = computed(() => {
  return payouts.value.length > 0 && selectedPayouts.value.length === payouts.value.length
})

const canBulkProcess = computed(() => {
  return selectedPayouts.value.some(id => {
    const payout = payouts.value.find(p => p.payout_id === id)
    return payout?.status === 'pending'
  })
})

const canBulkFail = computed(() => {
  return selectedPayouts.value.some(id => {
    const payout = payouts.value.find(p => p.payout_id === id)
    return payout?.status === 'pending'
  })
})

onMounted(() => {
  loadPayouts()
  loadStats()
})

const loadPayouts = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      page_size: pagination.value.pageSize
    }
    
    Object.keys(filters.value).forEach(key => {
      if (filters.value[key]) params[key] = filters.value[key]
    })

    const response = await financeAPI.getPayouts(params)
    
    if (response.results) {
      payouts.value = response.results
      pagination.value.total = response.count || 0
      pagination.value.page = page
    } else {
      payouts.value = Array.isArray(response) ? response : []
    }
  } catch (error) {
    console.error('Failed to load payouts:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await financeAPI.getPayoutStats()
    stats.value = {
      total: (response.total_pending || 0) + (response.total_processed || 0) + (response.total_failed || 0),
      pending: response.total_pending || 0,
      processed: response.total_processed || 0,
      failed: response.total_failed || 0,
      pendingAmount: response.amount_pending || 0,
      processedAmount: response.amount_processed || 0,
      failedAmount: response.amount_failed || 0
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    user_role: '',
    dateRange: '',
    search: ''
  }
  loadPayouts(1)
}

const goToPage = (page) => {
  loadPayouts(page)
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedPayouts.value = []
  } else {
    selectedPayouts.value = payouts.value.map(payout => payout.payout_id)
  }
}

const clearSelection = () => {
  selectedPayouts.value = []
}

const viewPayout = (payout) => {
  selectedPayout.value = payout
  // You could open a detailed modal here
}

const processPayout = (payout) => {
  selectedPayout.value = payout
  showProcessModal.value = true
}

const failPayout = (payout) => {
  selectedPayout.value = payout
  showFailModal.value = true
}

const closeProcessModal = () => {
  showProcessModal.value = false
  selectedPayout.value = null
  processForm.value = { transactionReference: '', notes: '' }
}

const closeFailModal = () => {
  showFailModal.value = false
  selectedPayout.value = null
  failForm.value = { notes: '' }
}

const confirmProcessPayout = async () => {
  if (!selectedPayout.value || !processForm.value.transactionReference) return
  
  processing.value = true
  try {
    await financeAPI.processPayout(selectedPayout.value.payout_id, {
      transaction_reference: processForm.value.transactionReference,
      notes: processForm.value.notes
    })
    
    loadPayouts(pagination.value.page)
    loadStats()
    closeProcessModal()
  } catch (error) {
    console.error('Failed to process payout:', error)
  } finally {
    processing.value = false
  }
}

const confirmFailPayout = async () => {
  if (!selectedPayout.value || !failForm.value.notes) return
  
  processing.value = true
  try {
    await financeAPI.failPayout(selectedPayout.value.payout_id, failForm.value.notes)
    
    loadPayouts(pagination.value.page)
    loadStats()
    closeFailModal()
  } catch (error) {
    console.error('Failed to mark payout as failed:', error)
  } finally {
    processing.value = false
  }
}

const bulkProcessPayouts = async () => {
  const transactionRef = prompt('Enter transaction reference for bulk processing:')
  if (!transactionRef) return
  
  processing.value = true
  try {
    await Promise.all(
      selectedPayouts.value.map(payoutId => {
        const payout = payouts.value.find(p => p.payout_id === payoutId)
        if (payout?.status === 'pending') {
          return financeAPI.processPayout(payoutId, { transaction_reference: transactionRef })
        }
      })
    )
    
    selectedPayouts.value = []
    loadPayouts(pagination.value.page)
    loadStats()
  } catch (error) {
    console.error('Failed to bulk process payouts:', error)
  } finally {
    processing.value = false
  }
}

const bulkFailPayouts = async () => {
  const notes = prompt('Enter reason for bulk failure:')
  if (!notes) return
  
  processing.value = true
  try {
    await Promise.all(
      selectedPayouts.value.map(payoutId => {
        const payout = payouts.value.find(p => p.payout_id === payoutId)
        if (payout?.status === 'pending') {
          return financeAPI.failPayout(payoutId, notes)
        }
      })
    )
    
    selectedPayouts.value = []
    loadPayouts(pagination.value.page)
    loadStats()
  } catch (error) {
    console.error('Failed to bulk fail payouts:', error)
  } finally {
    processing.value = false
  }
}

const exportPayouts = async () => {
  try {
    // This would need to be implemented in the backend
    const params = { ...filters.value, format: 'csv' }
    // For now, just download current payouts as JSON
    const dataStr = JSON.stringify(payouts.value, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `payouts_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export payouts:', error)
  }
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toLocaleString('en-US', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getStatusClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    processed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getStatusLabel = (status) => {
  const labels = {
    pending: 'Pending',
    processed: 'Processed',
    failed: 'Failed'
  }
  return labels[status] || status
}
</script> 