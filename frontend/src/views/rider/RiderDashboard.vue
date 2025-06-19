<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Rider Dashboard</h1>
        <p class="mt-2 text-gray-600">Welcome back, {{ riderName }}! Manage your deliveries and track earnings</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <TruckIcon class="h-6 w-6 text-blue-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Active Deliveries</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.activeDeliveries }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <CheckCircleIcon class="h-6 w-6 text-green-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Completed Today</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.completedToday }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <CurrencyDollarIcon class="h-6 w-6 text-green-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Today's Earnings</dt>
                  <dd class="text-lg font-medium text-gray-900">KES {{ formatCurrency(stats.todayEarnings) }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <StarIcon class="h-6 w-6 text-yellow-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Rating</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.averageRating.toFixed(1) }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Earnings Section -->
      <div class="bg-white shadow rounded-lg mb-8">
        <div class="p-6 border-b border-gray-200">
          <h2 class="text-lg font-medium text-gray-900">Earnings Overview</h2>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Total Available Balance -->
            <div class="bg-green-50 rounded-lg p-6">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Available for Withdrawal</h3>
              <p class="text-3xl font-bold text-green-600">KES {{ formatCurrency(stats.availableBalance) }}</p>
              <button 
                @click="showRequestPayout = true"
                :disabled="!stats.availableBalance"
                class="mt-4 w-full inline-flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Request Withdrawal
              </button>
            </div>

            <!-- Pending Balance -->
            <div class="bg-yellow-50 rounded-lg p-6">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Pending Clearance</h3>
              <p class="text-3xl font-bold text-yellow-600">KES {{ formatCurrency(stats.pendingBalance) }}</p>
              <p class="mt-4 text-sm text-gray-600">Will be available in 24-48 hours</p>
            </div>

            <!-- Total Earnings -->
            <div class="bg-blue-50 rounded-lg p-6">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Total Earnings</h3>
              <p class="text-3xl font-bold text-blue-600">KES {{ formatCurrency(stats.totalEarnings) }}</p>
              <router-link 
                to="/rider/earnings"
                class="mt-4 inline-block text-sm text-blue-600 hover:text-blue-500"
              >
                View detailed report →
              </router-link>
            </div>
          </div>

          <!-- Recent Transactions -->
          <div class="mt-8">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Transactions</h3>
            <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div v-if="recentTransactions.length === 0" class="p-6 text-center text-gray-500">
                <p>No recent transactions</p>
              </div>
              <div v-else class="divide-y divide-gray-200">
                <div v-for="transaction in recentTransactions" :key="transaction.id" class="p-4 hover:bg-gray-50">
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
      <div class="mb-8">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <router-link
            to="/rider/deliveries"
            class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow"
          >
            <div class="flex items-center">
              <TruckIcon class="h-8 w-8 text-blue-600" />
              <div class="ml-4">
                <p class="text-lg font-medium text-gray-900">View Deliveries</p>
                <p class="text-sm text-gray-500">Manage active deliveries</p>
              </div>
            </div>
          </router-link>

          <div class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer">
            <div class="flex items-center">
              <MapPinIcon class="h-8 w-8 text-green-600" />
              <div class="ml-4">
                <p class="text-lg font-medium text-gray-900">Update Location</p>
                <p class="text-sm text-gray-500">Share your current location</p>
              </div>
            </div>
          </div>

          <div class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer">
            <div class="flex items-center">
              <ClockIcon class="h-8 w-8 text-purple-600" />
              <div class="ml-4">
                <p class="text-lg font-medium text-gray-900">Work Schedule</p>
                <p class="text-sm text-gray-500">Manage availability</p>
              </div>
            </div>
          </div>

          <div class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer">
            <div class="flex items-center">
              <ChartBarIcon class="h-8 w-8 text-orange-600" />
              <div class="ml-4">
                <p class="text-lg font-medium text-gray-900">Earnings Report</p>
                <p class="text-sm text-gray-500">View detailed earnings</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Deliveries -->
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Recent Deliveries</h3>
          <p class="mt-1 text-sm text-gray-500">Your latest delivery activities</p>
        </div>

        <div v-if="recentDeliveries.length === 0" class="text-center py-8">
          <TruckIcon class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-4 text-sm font-medium text-gray-900">No deliveries yet</h3>
          <p class="mt-2 text-sm text-gray-500">Check back when you have active deliveries assigned.</p>
        </div>

        <ul v-else class="divide-y divide-gray-200">
          <li v-for="delivery in recentDeliveries" :key="delivery.delivery_id" class="px-4 py-4 sm:px-6 hover:bg-gray-50">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <TruckIcon class="h-4 w-4 text-blue-600" />
                  </div>
                </div>
                <div class="ml-4">
                  <div class="text-sm font-medium text-gray-900">
                    Order #{{ delivery.order?.order_number }}
                  </div>
                  <div class="text-sm text-gray-500">
                    {{ delivery.delivery_address }}
                  </div>
                  <div class="text-xs text-gray-400">
                    {{ formatDate(delivery.created_at) }}
                  </div>
                </div>
              </div>
              <div class="flex items-center space-x-3">
                <span :class="getStatusClass(delivery.delivery_status)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ formatStatus(delivery.delivery_status) }}
                </span>
                <div class="text-sm font-medium text-gray-900">
                  KES {{ formatCurrency(delivery.delivery_fee) }}
                </div>
              </div>
            </div>
          </li>
        </ul>

        <div class="px-4 py-3 border-t border-gray-200">
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
                      <p class="text-sm text-gray-500 mb-4">
                        Available balance: KES {{ formatCurrency(stats.availableBalance) }}
                      </p>
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
                            :max="stats.availableBalance"
                            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                            placeholder="Enter amount"
                          />
                        </div>
                        <p v-if="payoutError" class="mt-2 text-sm text-red-600">{{ payoutError }}</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button
                    type="button"
                    class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 sm:col-start-2"
                    :disabled="!isValidPayoutAmount"
                    @click="requestPayout"
                  >
                    Request Payout
                  </button>
                  <button
                    type="button"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                    @click="showRequestPayout = false"
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
import { ref, onMounted, computed } from 'vue'
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
  totalEarnings: 0
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

const isValidPayoutAmount = computed(() => {
  const amount = Number(payoutAmount.value)
  return amount > 0 && amount <= stats.value.availableBalance
})

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
      d.delivery_status === 'assigned' || d.delivery_status === 'picked_up'
    ).length

    const today = new Date()
    const todayDeliveries = deliveries.filter(d => {
      const deliveryDate = new Date(d.created_at)
      return deliveryDate.toDateString() === today.toDateString()
    })

    const completedToday = todayDeliveries.filter(d => d.delivery_status === 'delivered').length
    const todayEarnings = todayDeliveries
      .filter(d => d.delivery_status === 'delivered')
      .reduce((sum, d) => sum + parseFloat(d.delivery_fee || 0), 0)

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
      totalEarnings: earningsResponse.total_earnings || 0
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
    'pending': 'Pending',
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
    'pending': 'bg-yellow-100 text-yellow-800',
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

  try {
    await financeAPI.createPayout({
      amount: Number(payoutAmount.value)
    })
    toast.success('Payout request submitted successfully')
    showRequestPayout.value = false
    payoutAmount.value = ''
    payoutError.value = ''
    await loadDashboardData()
  } catch (error) {
    toast.error('Failed to submit payout request')
    console.error('Error requesting payout:', error)
  }
}

onMounted(() => {
  loadDashboardData()
})
</script> 