<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
    <!-- Primary Focus: Net Payout & Available for Withdrawal -->
    <div class="mb-6 sm:mb-8">
      <h1 class="text-xl sm:text-2xl font-bold text-gray-900 mb-2">Your Earnings</h1>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="bg-white rounded-lg shadow-sm border-2 border-green-500 p-4 sm:p-6">
          <dt class="text-sm font-medium text-gray-500">Available for Withdrawal</dt>
          <dd class="text-2xl sm:text-3xl font-bold text-green-600 mt-1">KES {{ formatCurrency(stats.availableBalance) }}</dd>
          <div class="mt-4">
            <button @click="showPayoutModal = true" 
                    class="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
              Withdraw Funds
            </button>
          </div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
          <dt class="text-sm font-medium text-gray-500">Net Earnings This Period</dt>
          <dd class="text-2xl sm:text-3xl font-bold text-gray-900 mt-1">KES {{ formatCurrency(stats.netRevenue) }}</dd>
          <p class="text-sm text-gray-600 mt-2">Your earnings after all deductions</p>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Quick Overview</h2>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div>
          <dt class="text-sm font-medium text-gray-500">Completed Orders</dt>
          <dd class="text-xl font-bold text-gray-900 mt-1">{{ stats.completedOrders }}</dd>
        </div>
        <div>
          <dt class="text-sm font-medium text-gray-500">Gross Revenue</dt>
          <dd class="text-xl font-bold text-gray-900 mt-1">KES {{ formatCurrency(stats.grossRevenue) }}</dd>
        </div>
        <div>
          <dt class="text-sm font-medium text-gray-500">Total Fees</dt>
          <dd class="text-xl font-bold text-gray-900 mt-1">KES {{ formatCurrency(stats.totalFees) }}</dd>
        </div>
        <div v-if="stats.pendingBalance > 0">
          <dt class="text-sm font-medium text-gray-500">Pending Clearance</dt>
          <dd class="text-xl font-bold text-yellow-600 mt-1">KES {{ formatCurrency(stats.pendingBalance) }}</dd>
        </div>
      </div>
    </div>

    <!-- Transaction History -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div class="p-4 sm:p-6 border-b border-gray-200">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 class="text-lg font-medium text-gray-900">Transaction History</h2>
            <p class="text-sm text-gray-600 mt-1">Track all your earnings and payouts</p>
          </div>
          
          <!-- Compact Filter Button for Mobile -->
          <button class="sm:hidden w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 transition-colors flex items-center justify-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
            </svg>
            Filter Transactions
          </button>
        </div>

        <!-- Desktop Filters -->
        <div class="hidden sm:block mt-4">
          <div class="grid grid-cols-3 gap-4">
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
          </div>
        </div>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        <p class="mt-2 text-sm text-gray-600">Loading transactions...</p>
      </div>

      <div v-else-if="payouts.length === 0" class="text-center py-12">
        <div class="bg-gray-50 rounded-full p-4 mx-auto w-16 h-16 flex items-center justify-center">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
          </svg>
        </div>
        <h3 class="mt-4 text-base font-medium text-gray-900">No transactions yet</h3>
        <p class="mt-2 text-sm text-gray-600">Your transaction history will appear here once you have completed orders.</p>
      </div>

      <div v-else>
        <!-- Mobile Transaction List -->
        <div class="block sm:hidden">
          <div v-for="payout in payouts" :key="payout.payout_id" 
               class="border-b border-gray-200 p-4 hover:bg-gray-50 transition-colors">
            <div class="flex items-start justify-between mb-2">
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <span :class="[
                    getStatusClass(payout.status),
                    'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium'
                  ]">
                    {{ getStatusLabel(payout.status) }}
                  </span>
                  <span class="text-sm text-gray-500">
                    {{ formatDate(payout.payout_date) }}
                  </span>
                </div>
                <div class="mt-1 text-base font-medium text-gray-900">
                  KES {{ formatCurrency(payout.amount) }}
                </div>
                <div class="mt-1 text-sm text-gray-500">
                  #{{ payout.payout_id.slice(-8).toUpperCase() }}
                </div>
              </div>
              <button @click="viewPayoutDetails(payout)" 
                      class="text-gray-400 hover:text-gray-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Desktop Transaction Table -->
        <div class="hidden sm:block">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reference</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="payout in payouts" :key="payout.payout_id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ formatDate(payout.payout_date) }}</div>
                  <div v-if="payout.processed_date" class="text-xs text-gray-500">
                    Processed: {{ formatDate(payout.processed_date) }}
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
                    #{{ payout.order.order_number || payout.order.order_id }}
                  </div>
                  <div v-else class="text-sm text-gray-500">-</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-500">
                    {{ payout.transaction_reference || '-' }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button @click="viewPayoutDetails(payout)" 
                          class="text-green-600 hover:text-green-700">
                    View Details
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.total > pagination.pageSize" 
           class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div class="w-full sm:w-auto text-center sm:text-left">
            <p class="text-sm text-gray-700">
              Showing {{ ((pagination.page - 1) * pagination.pageSize) + 1 }} 
              to {{ Math.min(pagination.page * pagination.pageSize, pagination.total) }} 
              of {{ pagination.total }} results
            </p>
          </div>
          <div class="flex items-center justify-center sm:justify-end gap-2">
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

    <!-- Fee Breakdown Modal -->
    <div v-if="showFeeBreakdown" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div class="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Fee Breakdown</h3>
          <button @click="showFeeBreakdown = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="p-4 sm:p-6 space-y-4">
          <div>
            <dt class="text-sm font-medium text-gray-500">Platform Fee (10%)</dt>
            <dd class="mt-1 text-lg font-medium text-gray-900">KES {{ formatCurrency(stats.platformFee) }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">VAT on Platform Fee (16%)</dt>
            <dd class="mt-1 text-lg font-medium text-gray-900">KES {{ formatCurrency(stats.vat) }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Transaction Fee (1.5%)</dt>
            <dd class="mt-1 text-lg font-medium text-gray-900">KES {{ formatCurrency(stats.transactionFee) }}</dd>
          </div>
          <div class="pt-4 border-t border-gray-200">
            <dt class="text-sm font-medium text-gray-500">Total Deductions</dt>
            <dd class="mt-1 text-xl font-bold text-gray-900">KES {{ formatCurrency(stats.totalFees) }}</dd>
          </div>
        </div>
      </div>
    </div>

    <!-- Payout Details Modal -->
    <div v-if="selectedPayout" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Transaction Details</h3>
          <button @click="selectedPayout = null" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="p-4 sm:p-6 space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Transaction ID</label>
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
              <p class="mt-1 text-sm font-medium text-gray-900">KES {{ formatCurrency(selectedPayout.amount) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Date</label>
              <p class="mt-1 text-sm text-gray-900">{{ formatDate(selectedPayout.payout_date) }}</p>
            </div>
            <div v-if="selectedPayout.order">
              <label class="block text-sm font-medium text-gray-700">Order Reference</label>
              <p class="mt-1 text-sm text-gray-900">
                #{{ selectedPayout.order.order_number || selectedPayout.order.order_id }}
              </p>
            </div>
            <div v-if="selectedPayout.transaction_reference">
              <label class="block text-sm font-medium text-gray-700">Transaction Reference</label>
              <p class="mt-1 text-sm text-gray-900">{{ selectedPayout.transaction_reference }}</p>
            </div>
          </div>

          <div v-if="selectedPayout.status === 'failed'" class="mt-6">
            <button @click="retryPayout(selectedPayout)"
                    class="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
              Retry Transaction
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Payout Request Modal -->
    <PayoutRequestModal
      :show="showPayoutModal"
      :available-balance="stats.availableBalance"
      @close="showPayoutModal = false"
      @payout-requested="loadPayouts"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { financeAPI } from '@/services/api'
import PayoutRequestModal from '@/components/farmer/PayoutRequestModal.vue'

const loading = ref(false)
const payouts = ref([])
const selectedPayout = ref(null)
const showFeeBreakdown = ref(false)
const showPayoutModal = ref(false)

const stats = ref({
  grossRevenue: 0,
  platformFee: 0,
  vat: 0,
  transactionFee: 0,
  totalFees: 0,
  netRevenue: 0,
  pendingBalance: 0,
  availableBalance: 0,
  completedOrders: 0,
  pendingOrders: 0,
  minWithdrawalAmount: 0,
  clearanceThresholdAmount: 0,
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
    const response = await financeAPI.getFarmerEarnings()
    stats.value = {
      grossRevenue: response.gross_revenue || 0,
      platformFee: response.fees.platform_fee || 0,
      vat: response.fees.vat || 0,
      transactionFee: response.fees.transaction_fee || 0,
      totalFees: response.fees.total_fees || 0,
      netRevenue: response.net_revenue || 0,
      pendingBalance: response.pending_balance || 0,
      availableBalance: response.available_balance || 0,
      completedOrders: response.completed_orders || 0,
      pendingOrders: response.pending_orders || 0,
      minWithdrawalAmount: response.min_withdrawal_amount || 0,
      clearanceThresholdAmount: response.clearance_threshold_amount || 0,
    }
  } catch (error) {
    console.error('Failed to load farmer earnings stats:', error)
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
