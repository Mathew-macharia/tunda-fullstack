<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Payouts & Earnings</h1>
        <p class="mt-2 text-gray-600">Track your earnings and payout history</p>
      </div>
    </div>

    <!-- Earnings Overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <dt class="text-sm font-medium text-gray-500 truncate">Total Earnings</dt>
        <dd class="text-2xl font-bold text-green-600">KES {{ formatCurrency(stats.totalEarnings) }}</dd>
        <p class="text-xs text-gray-500 mt-1">All time</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <dt class="text-sm font-medium text-gray-500 truncate">Pending Payouts</dt>
        <dd class="text-2xl font-bold text-yellow-600">KES {{ formatCurrency(stats.pendingAmount) }}</dd>
        <p class="text-xs text-gray-500 mt-1">{{ stats.pendingCount }} payout(s)</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <dt class="text-sm font-medium text-gray-500 truncate">Processed Payouts</dt>
        <dd class="text-2xl font-bold text-blue-600">KES {{ formatCurrency(stats.processedAmount) }}</dd>
        <p class="text-xs text-gray-500 mt-1">{{ stats.processedCount }} payout(s)</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <dt class="text-sm font-medium text-gray-500 truncate">This Month</dt>
        <dd class="text-2xl font-bold text-gray-900">KES {{ formatCurrency(stats.thisMonthEarnings) }}</dd>
        <p class="text-xs text-gray-500 mt-1">Current month earnings</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select v-model="filters.status" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="processed">Processed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
          <select v-model="filters.dateRange" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
            <option value="">All Time</option>
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 3 months</option>
            <option value="365">Last year</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Min Amount</label>
          <input v-model="filters.minAmount" type="number" placeholder="0.00"
                 class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
        </div>
        <div class="flex items-end space-x-2">
          <button @click="loadPayouts" 
                  class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
            Apply Filters
          </button>
          <button @click="resetFilters" 
                  class="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors">
            Reset
          </button>
        </div>
      </div>
    </div>

    <!-- Payouts List -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-medium text-gray-900">Payout History</h2>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        <p class="mt-2 text-gray-600">Loading payouts...</p>
      </div>

      <div v-else-if="payouts.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">No payouts found</h3>
        <p class="mt-2 text-gray-600">Your payout history will appear here once you have completed orders.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Payout ID
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Order Reference
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Transaction Ref
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="payout in payouts" :key="payout.payout_id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  #{{ payout.payout_id.slice(-8).toUpperCase() }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  KES {{ formatCurrency(payout.amount) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(payout.status)" 
                      class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                  {{ getStatusLabel(payout.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div v-if="payout.order" class="text-sm text-gray-900">
                  Order #{{ payout.order.order_number || payout.order.order_id }}
                </div>
                <div v-else class="text-sm text-gray-500">-</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatDate(payout.payout_date) }}</div>
                <div v-if="payout.processed_date" class="text-xs text-gray-500">
                  Processed: {{ formatDate(payout.processed_date) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div v-if="payout.transaction_reference" class="text-sm text-gray-900">
                  {{ payout.transaction_reference }}
                </div>
                <div v-else class="text-sm text-gray-500">-</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button @click="viewPayoutDetails(payout)" 
                        class="text-blue-600 hover:text-blue-700 mr-3">
                  View
                </button>
                <button v-if="payout.status === 'failed'" 
                        @click="retryPayout(payout)"
                        class="text-green-600 hover:text-green-700">
                  Retry
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.total > pagination.pageSize" class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <p class="text-sm text-gray-700">
              Showing {{ ((pagination.page - 1) * pagination.pageSize) + 1 }} to {{ Math.min(pagination.page * pagination.pageSize, pagination.total) }} of {{ pagination.total }} results
            </p>
          </div>
          <div class="flex items-center space-x-2">
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

    <!-- Payout Details Modal -->
    <div v-if="selectedPayout" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Payout Details</h3>
          <button @click="selectedPayout = null" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="p-6 space-y-6">
          <!-- Payout Info -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Payout ID</label>
              <p class="mt-1 text-sm text-gray-900">#{{ selectedPayout.payout_id.slice(-8).toUpperCase() }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Status</label>
              <span :class="getStatusClass(selectedPayout.status)" 
                    class="mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                {{ getStatusLabel(selectedPayout.status) }}
              </span>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Amount</label>
              <p class="mt-1 text-lg font-semibold text-gray-900">KES {{ formatCurrency(selectedPayout.amount) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Created Date</label>
              <p class="mt-1 text-sm text-gray-900">{{ formatDate(selectedPayout.payout_date) }}</p>
            </div>
          </div>

          <!-- Order Details -->
          <div v-if="selectedPayout.order" class="border-t border-gray-200 pt-6">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Related Order</h4>
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-medium text-gray-500">Order Number</label>
                  <p class="mt-1 text-sm text-gray-900">#{{ selectedPayout.order.order_number || selectedPayout.order.order_id }}</p>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-500">Customer</label>
                  <p class="mt-1 text-sm text-gray-900">{{ selectedPayout.order.customer_name || 'N/A' }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Transaction Details -->
          <div v-if="selectedPayout.transaction_reference || selectedPayout.processed_date" 
               class="border-t border-gray-200 pt-6">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Transaction Details</h4>
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="space-y-3">
                <div v-if="selectedPayout.transaction_reference">
                  <label class="block text-xs font-medium text-gray-500">Transaction Reference</label>
                  <p class="mt-1 text-sm text-gray-900 font-mono">{{ selectedPayout.transaction_reference }}</p>
                </div>
                <div v-if="selectedPayout.processed_date">
                  <label class="block text-xs font-medium text-gray-500">Processed Date</label>
                  <p class="mt-1 text-sm text-gray-900">{{ formatDateTime(selectedPayout.processed_date) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Notes -->
          <div v-if="selectedPayout.notes" class="border-t border-gray-200 pt-6">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Notes</h4>
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-sm text-gray-700">{{ selectedPayout.notes }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { financeAPI } from '@/services/api'

const loading = ref(false)
const payouts = ref([])
const selectedPayout = ref(null)

const stats = ref({
  totalEarnings: 0,
  pendingAmount: 0,
  pendingCount: 0,
  processedAmount: 0,
  processedCount: 0,
  thisMonthEarnings: 0
})

const filters = ref({
  status: '',
  dateRange: '',
  minAmount: ''
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
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
      totalEarnings: response.amount_processed || 0,
      pendingAmount: response.amount_pending || 0,
      pendingCount: response.total_pending || 0,
      processedAmount: response.amount_processed || 0,
      processedCount: response.total_processed || 0,
      thisMonthEarnings: response.this_month_amount || 0
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    dateRange: '',
    minAmount: ''
  }
  loadPayouts(1)
}

const goToPage = (page) => {
  loadPayouts(page)
}

const viewPayoutDetails = (payout) => {
  selectedPayout.value = payout
}

const retryPayout = async (payout) => {
  // This would typically involve contacting support or resubmitting payout request
  alert('Please contact support to retry this payout.')
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

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
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