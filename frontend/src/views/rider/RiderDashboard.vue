<template>
  <div class="min-h-screen bg-gray-50 py-4 sm:py-8">
    <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-6 sm:mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Rider Dashboard</h1>
        <p class="mt-2 text-sm sm:text-base text-gray-600">Welcome back, {{ riderName }}! Manage your deliveries and track earnings</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-4 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <TruckIcon class="h-5 w-5 sm:h-6 sm:w-6 text-blue-400" />
              </div>
              <div class="ml-3 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Active Deliveries</dt>
                  <dd class="text-base sm:text-lg font-medium text-gray-900">{{ stats.activeDeliveries }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-4 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <CheckCircleIcon class="h-5 w-5 sm:h-6 sm:w-6 text-green-400" />
              </div>
              <div class="ml-3 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Completed Today</dt>
                  <dd class="text-base sm:text-lg font-medium text-gray-900">{{ stats.completedToday }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-4 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <CurrencyDollarIcon class="h-5 w-5 sm:h-6 sm:w-6 text-green-400" />
              </div>
              <div class="ml-3 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Today's Earnings</dt>
                  <dd class="text-base sm:text-lg font-medium text-gray-900">KES {{ formatCurrency(stats.todayEarnings) }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-4 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <StarIcon class="h-5 w-5 sm:h-6 sm:w-6 text-yellow-400" />
              </div>
              <div class="ml-3 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Rating</dt>
                  <dd class="text-base sm:text-lg font-medium text-gray-900">{{ stats.averageRating.toFixed(1) }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Earnings Section -->
      <div class="bg-white shadow rounded-lg mb-6 sm:mb-8">
        <div class="p-4 sm:p-6 border-b border-gray-200">
          <h2 class="text-lg sm:text-xl font-medium text-gray-900">Earnings Overview</h2>
        </div>
        <div class="p-4 sm:p-6">
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6">
            <!-- Total Available Balance -->
            <div class="bg-green-50 rounded-lg p-4 sm:p-6">
              <h3 class="text-xs sm:text-sm font-medium text-gray-700 mb-3 sm:mb-4">Available for Withdrawal</h3>
              <p class="text-2xl sm:text-3xl font-bold text-green-600">KES {{ formatCurrency(stats.availableBalance) }}</p>
              <button 
                @click="showRequestPayout = true"
                :disabled="!stats.availableBalance || hasPendingPayout"
                class="mt-3 sm:mt-4 w-full inline-flex justify-center items-center px-3 sm:px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {{ hasPendingPayout ? 'Pending Payout in Progress' : 'Request Withdrawal' }}
              </button>
              <p v-if="hasPendingPayout" class="mt-2 text-xs text-gray-600">
                Please wait for your pending payout to be processed before requesting another.
              </p>
            </div>

            <!-- Pending Balance -->
            <div v-if="stats.pendingBalance > 0" class="bg-yellow-50 rounded-lg p-4 sm:p-6">
              <h3 class="text-xs sm:text-sm font-medium text-gray-700 mb-3 sm:mb-4">Pending Clearance</h3>
              <p class="text-2xl sm:text-3xl font-bold text-yellow-600">KES {{ formatCurrency(stats.pendingBalance) }}</p>
              <p class="mt-3 sm:mt-4 text-xs sm:text-sm text-gray-600">Amounts KES {{ formatCurrency(stats.clearanceThresholdAmount) }} and above are subject to 24-48 hour clearance.</p>
            </div>

            <!-- Total Earnings -->
            <div class="bg-blue-50 rounded-lg p-4 sm:p-6">
              <h3 class="text-xs sm:text-sm font-medium text-gray-700 mb-3 sm:mb-4">Total Earnings</h3>
              <p class="text-2xl sm:text-3xl font-bold text-blue-600">KES {{ formatCurrency(stats.totalEarnings) }}</p>
              <router-link 
                to="/rider/earnings"
                class="mt-3 sm:mt-4 inline-block text-sm text-blue-600 hover:text-blue-500"
              >
                View detailed report →
              </router-link>
            </div>

            <!-- Withholding Tax -->
            <div v-if="stats.withholdingTax > 0" class="bg-red-50 rounded-lg p-4 sm:p-6">
              <h3 class="text-xs sm:text-sm font-medium text-gray-700 mb-3 sm:mb-4">Withholding Tax (WHT)</h3>
              <p class="text-2xl sm:text-3xl font-bold text-red-600">KES {{ formatCurrency(stats.withholdingTax) }}</p>
              <p class="mt-3 sm:mt-4 text-xs sm:text-sm text-gray-600">Deducted from your earnings</p>
            </div>
          </div>

          <!-- Recent Transactions -->
          <div class="mt-6 sm:mt-8">
            <h3 class="text-lg sm:text-xl font-medium text-gray-900 mb-3 sm:mb-4">Recent Transactions</h3>
            <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div v-if="recentTransactions.length === 0" class="p-4 sm:p-6 text-center text-gray-500">
                <p>No recent transactions</p>
              </div>
              <div v-else class="divide-y divide-gray-200">
                <div v-for="transaction in recentTransactions" :key="transaction.id" class="p-3 sm:p-4 hover:bg-gray-50">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="text-sm font-medium text-gray-900">{{ transaction.description }}</p>
                      <p class="text-xs text-gray-500">{{ formatDate(transaction.date) }}</p>
                    </div>
                    <div :class="transaction.type === 'credit' ? 'text-green-600' : 'text-red-600'" class="text-sm font-medium">
                      {{ transaction.type === 'credit' ? '+' : '-' }}KES {{ formatCurrency(transaction.amount) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="mb-6 sm:mb-8">
        <h2 class="text-lg sm:text-xl font-medium text-gray-900 mb-3 sm:mb-4">Quick Actions</h2>
        <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <router-link
            to="/rider/deliveries"
            class="bg-white p-4 sm:p-6 rounded-lg shadow hover:shadow-md transition-shadow"
          >
            <div class="flex items-center">
              <TruckIcon class="h-6 w-6 sm:h-8 sm:w-8 text-blue-600" />
              <div class="ml-3 sm:ml-4">
                <p class="text-base sm:text-lg font-medium text-gray-900">View Deliveries</p>
                <p class="text-xs sm:text-sm text-gray-500">Manage active deliveries</p>
              </div>
            </div>
          </router-link>

          <div class="bg-white p-4 sm:p-6 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer">
            <div class="flex items-center">
              <MapPinIcon class="h-6 w-6 sm:h-8 sm:w-8 text-green-600" />
              <div class="ml-3 sm:ml-4">
                <p class="text-base sm:text-lg font-medium text-gray-900">Update Location</p>
                <p class="text-xs sm:text-sm text-gray-500">Share your current location</p>
              </div>
            </div>
          </div>

          <div class="bg-white p-4 sm:p-6 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer">
            <div class="flex items-center">
              <ClockIcon class="h-6 w-6 sm:h-8 sm:w-8 text-purple-600" />
              <div class="ml-3 sm:ml-4">
                <p class="text-base sm:text-lg font-medium text-gray-900">Work Schedule</p>
                <p class="text-xs sm:text-sm text-gray-500">Manage availability</p>
              </div>
            </div>
          </div>

          <div class="bg-white p-4 sm:p-6 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer">
            <div class="flex items-center">
              <ChartBarIcon class="h-6 w-6 sm:h-8 sm:w-8 text-orange-600" />
              <div class="ml-3 sm:ml-4">
                <p class="text-base sm:text-lg font-medium text-gray-900">Earnings Report</p>
                <p class="text-xs sm:text-sm text-gray-500">View detailed earnings</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Deliveries -->
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <div class="px-4 sm:px-6 py-4 sm:py-5 border-b border-gray-200">
          <h3 class="text-lg sm:text-xl leading-6 font-medium text-gray-900">Recent Deliveries</h3>
          <p class="mt-1 text-xs sm:text-sm text-gray-500">Your latest delivery activities</p>
        </div>

        <div v-if="recentDeliveries.length === 0" class="text-center py-6 sm:py-8">
          <TruckIcon class="mx-auto h-10 w-10 sm:h-12 sm:w-12 text-gray-400" />
          <h3 class="mt-3 sm:mt-4 text-sm font-medium text-gray-900">No deliveries yet</h3>
          <p class="mt-1 sm:mt-2 text-xs sm:text-sm text-gray-500">Check back when you have active deliveries assigned.</p>
        </div>

        <ul v-else class="divide-y divide-gray-200">
          <li v-for="delivery in recentDeliveries" :key="delivery.delivery_id" class="px-4 sm:px-6 py-3 sm:py-4 hover:bg-gray-50">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <TruckIcon class="h-4 w-4 text-blue-600" />
                  </div>
                </div>
                <div class="ml-3 sm:ml-4">
                  <div class="text-sm font-medium text-gray-900">
                    Order #{{ delivery.order?.order_number }}
                  </div>
                  <div class="text-xs sm:text-sm text-gray-500">
                    {{ delivery.order?.delivery_location?.location_name }}
                  </div>
                  <div class="text-xs text-gray-400">
                    {{ formatDate(delivery.created_at) }}
                  </div>
                </div>
              </div>
              <div class="flex items-center justify-between sm:justify-end space-x-3">
                <span :class="getStatusClass(delivery.delivery_status)" class="px-2 sm:px-3 py-1 text-xs font-medium rounded-full">
                  {{ formatStatus(delivery.delivery_status) }}
                </span>
                <div class="text-sm font-medium text-gray-900">
                  KES {{ formatCurrency(delivery.order?.delivery_fee) }}
                </div>
              </div>
            </div>
          </li>
        </ul>

        <div class="px-4 sm:px-6 py-3 sm:py-4 border-t border-gray-200">
          <router-link
            to="/rider/deliveries"
            class="text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            View all deliveries →
          </router-link>
        </div>
      </div>
    </div>

    <!-- Request Payout Modal -->
    <TransitionRoot as="template" :show="showRequestPayout">
      <Dialog as="div" class="relative z-10" @close="showRequestPayout = false">
        <TransitionChild
          as="template"
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild
              as="template"
              enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div>
                  <div class="mt-3 text-center sm:mt-5">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                      Request Payout
                    </DialogTitle>
                    <div class="mt-2">
                      <div class="flex justify-between items-center mb-4">
                        <p class="text-sm text-gray-500">
                          Available balance: KES {{ formatCurrency(stats.availableBalance) }}
                        </p>
                        <p class="text-sm" :class="{'text-red-600 font-medium': Number(payoutAmount) < stats.minWithdrawalAmount, 'text-gray-500': Number(payoutAmount) >= stats.minWithdrawalAmount}">
                          Min: KES {{ formatCurrency(stats.minWithdrawalAmount) }}
                        </p>
                      </div>
                      <div class="mt-4">
                        <label for="amount" class="block text-sm font-medium text-gray-700 text-left">
                          Amount to withdraw
                        </label>
                        <div class="mt-1">
                          <input
                            type="number"
                            name="amount"
                            id="amount"
                            v-model="payoutAmount"
                            :min="stats.minWithdrawalAmount"
                            :max="stats.availableBalance"
                            :class="{
                              'border-red-300 focus:ring-red-500 focus:border-red-500': Number(payoutAmount) < stats.minWithdrawalAmount && payoutAmount,
                              'border-gray-300 focus:ring-blue-500 focus:border-blue-500': !payoutAmount || Number(payoutAmount) >= stats.minWithdrawalAmount
                            }"
                            class="block w-full rounded-md shadow-sm sm:text-sm"
                            placeholder="Enter amount"
                          />
                        </div>
                        <p v-if="payoutError && payoutError !== `Minimum withdrawal amount is KES ${formatCurrency(stats.minWithdrawalAmount)}`" class="mt-2 text-sm text-red-600">{{ payoutError }}</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button
                    type="button"
                    class="inline-flex w-full justify-center rounded-md px-3 py-2 text-sm font-semibold text-white shadow-sm sm:col-start-2 disabled:cursor-not-allowed transition-all duration-200"
                    :class="{
                      'bg-blue-600 hover:bg-blue-500': isValidPayoutAmount && Number(payoutAmount) >= stats.minWithdrawalAmount,
                      'bg-gray-300': !isValidPayoutAmount || Number(payoutAmount) < stats.minWithdrawalAmount
                    }"
                    :disabled="!isValidPayoutAmount || Number(payoutAmount) < stats.minWithdrawalAmount"
                    @click="requestPayout"
                  >
                    Request Payout
                  </button>
                  <button
                    type="button"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                    @click="() => {
                      showRequestPayout = false;
                      payoutAmount.value = '';
                      payoutError.value = '';
                    }"
                  >
                    Cancel
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { user } from '@/stores/auth'
import { riderAPI } from '@/services/api'
import { financeAPI } from '@/services/api'
import {
  TruckIcon,
  CheckCircleIcon,
  CurrencyDollarIcon,
  StarIcon,
  MapPinIcon,
  ClockIcon,
  ChartBarIcon
} from '@heroicons/vue/24/outline'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { useToast } from 'vue-toastification'

const toast = useToast()

// State
const stats = ref({
  activeDeliveries: 0,
  completedToday: 0,
  todayEarnings: 0,
  averageRating: 0,
  availableBalance: 0,
  pendingBalance: 0,
  totalEarnings: 0,
  withholdingTax: 0,
  minWithdrawalAmount: 0,
  clearanceThresholdAmount: 0
})

const recentDeliveries = ref([])
const recentTransactions = ref([])
const showRequestPayout = ref(false)
const payoutAmount = ref('')
const payoutError = ref('')

// Computed
const riderName = computed(() => {
  return user.value?.first_name || user.value?.phone_number || 'Rider'
})

// Update the isValidPayoutAmount computed property
const isValidPayoutAmount = computed(() => {
  const amount = Number(payoutAmount.value)
  return amount >= stats.value.minWithdrawalAmount && 
         amount <= stats.value.availableBalance && 
         amount > 0
})

// Add watcher for payoutAmount to show validation message
watch(payoutAmount, (newValue) => {
  const amount = Number(newValue)
  if (amount < stats.value.minWithdrawalAmount) {
    payoutError.value = `Minimum withdrawal amount is KES ${formatCurrency(stats.value.minWithdrawalAmount)}`
  } else if (amount > stats.value.availableBalance) {
    payoutError.value = 'Amount exceeds available balance'
  } else {
    payoutError.value = ''
  }
})

// Add computed property for pending payout
const hasPendingPayout = computed(() => stats.value.pendingBalance > 0)

// Methods
const loadDashboardData = async () => {
  try {
    // Load rider deliveries and basic stats
    const deliveriesResponse = await riderAPI.getRiderDeliveries({ 
      ordering: '-created_at',
      page_size: 5 
    })
    
    const deliveries = Array.isArray(deliveriesResponse) ? deliveriesResponse : deliveriesResponse.results || []
    recentDeliveries.value = deliveries

    // Calculate basic stats
    const activeDeliveries = deliveries.filter(d => 
      d.delivery_status === 'assigned' || d.delivery_status === 'picked_up' || d.delivery_status === 'in_transit'
    ).length

    const today = new Date()
    const todayDeliveries = deliveries.filter(d => {
      const deliveryDate = new Date(d.created_at)
      return deliveryDate.toDateString() === today.toDateString()
    })

    const completedToday = todayDeliveries.filter(d => d.delivery_status === 'delivered').length
    const todayEarnings = todayDeliveries
      .filter(d => d.delivery_status === 'delivered')
      .reduce((sum, d) => sum + parseFloat(d.order?.delivery_fee || 0), 0)

    // Load earnings data
    const earningsResponse = await financeAPI.getRiderEarnings()
    
    // Load recent transactions
    const transactionsResponse = await financeAPI.getRiderTransactions({ page_size: 5 })
    recentTransactions.value = transactionsResponse.results || []

    stats.value = {
      activeDeliveries,
      completedToday,
      todayEarnings,
      averageRating: 4.8, // Would come from rider rating system
      availableBalance: earningsResponse.available_balance || 0,
      pendingBalance: earningsResponse.pending_balance || 0,
      totalEarnings: earningsResponse.total_earnings || 0,
      withholdingTax: earningsResponse.withholding_tax || 0,
      minWithdrawalAmount: earningsResponse.min_withdrawal_amount || 0,
      clearanceThresholdAmount: earningsResponse.clearance_threshold_amount || 0
    }

  } catch (err) {
    console.error('Error loading dashboard data:', err)
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatStatus = (status) => {
  const statusMap = {
    'assigned': 'Assigned',
    'picked_up': 'Picked Up',
    'in_transit': 'In Transit',
    'delivered': 'Delivered',
    'failed': 'Failed'
  }
  return statusMap[status] || status
}

const getStatusClass = (status) => {
  const statusClasses = {
    'assigned': 'bg-blue-100 text-blue-800',
    'picked_up': 'bg-indigo-100 text-indigo-800',
    'in_transit': 'bg-purple-100 text-purple-800',
    'delivered': 'bg-green-100 text-green-800',
    'failed': 'bg-red-100 text-red-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

  const requestPayout = async () => {
    if (!isValidPayoutAmount.value) {
      payoutError.value = 'Please enter a valid amount'
      return
    }

    if (hasPendingPayout.value) {
      payoutError.value = 'You already have a pending payout request'
      return
    }

    try {
      await financeAPI.createPayout({
        amount: Number(payoutAmount.value),
        user: user.value.id
      })
      toast.success('Payout request submitted successfully')
      showRequestPayout.value = false
      payoutAmount.value = ''
      payoutError.value = ''
      await loadDashboardData()
    } catch (error) {
      if (error.response?.data?.detail) {
        payoutError.value = error.response.data.detail
        toast.error(error.response.data.detail)
      } else {
        payoutError.value = 'Failed to submit payout request'
        toast.error('Failed to submit payout request')
      }
      console.error('Error requesting payout:', error)
    }
  }

onMounted(() => {
  loadDashboardData()
})
</script>
