<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Market Insights</h1>
        <p class="mt-2 text-gray-600">Stay informed with market prices, weather alerts, and agricultural insights</p>
      </div>
      <div class="flex space-x-3">
        <button @click="refreshData" 
                class="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors">
          Refresh Data
        </button>
      </div>
    </div>

    <!-- Weather Alerts -->
    <div v-if="activeAlerts.length > 0" class="mb-8">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Active Weather Alerts</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="alert in activeAlerts" :key="alert.alert_id"
             :class="getSeverityClass(alert.severity)"
             class="rounded-lg border p-4">
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-3">
              <div :class="getSeverityIconClass(alert.severity)" 
                   class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path v-if="alert.alert_type === 'rain'" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"/>
                  <path v-else-if="alert.alert_type === 'drought'" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
                  <path v-else d="M10 2L3 7v11a2 2 0 002 2h10a2 2 0 002-2V7l-7-5z"/>
                </svg>
              </div>
              <div>
                <h3 class="text-sm font-medium">{{ alert.title }}</h3>
                <p class="text-xs text-gray-600 mt-1">{{ alert.description }}</p>
                <div class="flex items-center space-x-2 mt-2">
                  <span class="text-xs bg-gray-100 text-gray-800 px-2 py-0.5 rounded-full">
                    {{ alert.alert_type }}
                  </span>
                  <span class="text-xs text-gray-500">
                    {{ formatDate(alert.start_date) }} - {{ formatDate(alert.end_date) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Market Prices Overview -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <div class="lg:col-span-2">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-medium text-gray-900">Market Prices</h2>
            <select v-model="selectedLocation" @change="loadMarketPrices"
                    class="text-sm rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
              <option value="">All Locations</option>
              <option v-for="location in locations" :key="location.location_id" :value="location.location_id">
                {{ location.location_name }}
              </option>
            </select>
          </div>
          
          <div v-if="loadingPrices" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
            <p class="mt-2 text-sm text-gray-600">Loading market prices...</p>
          </div>

          <div v-else-if="marketPrices.length === 0" class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
            <h3 class="mt-4 text-lg font-medium text-gray-900">No market data available</h3>
            <p class="mt-2 text-gray-600">Market price information will appear here when available.</p>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="min-w-full">
              <thead>
                <tr class="border-b border-gray-200">
                  <th class="text-left py-2 text-sm font-medium text-gray-900">Product</th>
                  <th class="text-left py-2 text-sm font-medium text-gray-900">Current Price</th>
                  <th class="text-left py-2 text-sm font-medium text-gray-900">Change</th>
                  <th class="text-left py-2 text-sm font-medium text-gray-900">Market</th>
                  <th class="text-left py-2 text-sm font-medium text-gray-900">Updated</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="price in marketPrices" :key="price.market_price_id" class="hover:bg-gray-50">
                  <td class="py-3">
                    <div class="flex items-center">
                      <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3">
                        <span class="text-green-600 text-xs font-medium">
                          {{ price.product_name?.charAt(0)?.toUpperCase() || 'P' }}
                        </span>
                      </div>
                      <div>
                        <p class="text-sm font-medium text-gray-900">{{ price.product_name }}</p>
                        <p class="text-xs text-gray-500">{{ price.unit || 'per kg' }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="py-3">
                    <span class="text-sm font-medium text-gray-900">
                      KES {{ formatCurrency(price.current_price) }}
                    </span>
                  </td>
                  <td class="py-3">
                    <span :class="getPriceChangeClass(price.price_change)" 
                          class="inline-flex items-center text-sm font-medium">
                      <svg v-if="price.price_change > 0" class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                      </svg>
                      <svg v-else-if="price.price_change < 0" class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M14.707 12.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                      </svg>
                      {{ Math.abs(price.price_change || 0).toFixed(1) }}%
                    </span>
                  </td>
                  <td class="py-3">
                    <span class="text-sm text-gray-600">{{ price.location_name || 'General' }}</span>
                  </td>
                  <td class="py-3">
                    <span class="text-sm text-gray-500">{{ formatDate(price.updated_at) }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="space-y-6">
        <!-- Market Summary -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Market Summary</h3>
          <div class="space-y-4">
            <div>
              <dt class="text-sm font-medium text-gray-500">Products Tracked</dt>
              <dd class="text-2xl font-bold text-gray-900">{{ marketStats.totalProducts }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Avg. Price Increase</dt>
              <dd class="text-2xl font-bold text-green-600">+{{ marketStats.avgIncrease }}%</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
              <dd class="text-sm text-gray-600">{{ formatDate(marketStats.lastUpdated) }}</dd>
            </div>
          </div>
        </div>

        <!-- Price Alerts -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Price Alerts</h3>
          <div v-if="priceAlerts.length === 0" class="text-center py-6">
            <svg class="mx-auto h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5-5-5h5zm0 0V9a6 6 0 10-12 0v8"></path>
            </svg>
            <p class="mt-2 text-sm text-gray-600">No price alerts</p>
          </div>
          <div v-else class="space-y-3">
            <div v-for="alert in priceAlerts" :key="alert.id" 
                 class="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <div class="w-6 h-6 bg-yellow-100 rounded-full flex items-center justify-center">
                <svg class="w-3 h-3 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                </svg>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900">{{ alert.message }}</p>
                <p class="text-xs text-gray-600">{{ formatDate(alert.created_at) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Price Trends Chart -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-medium text-gray-900">Price Trends</h2>
        <div class="flex space-x-2">
          <select v-model="selectedProduct" @change="loadPriceTrends"
                  class="text-sm rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
            <option value="">Select Product</option>
            <option v-for="product in availableProducts" :key="product.product_id" :value="product.product_id">
              {{ product.product_name }}
            </option>
          </select>
          <select v-model="trendPeriod" @change="loadPriceTrends"
                  class="text-sm rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 3 months</option>
          </select>
        </div>
      </div>
      
      <div v-if="loadingTrends" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
        <p class="mt-2 text-sm text-gray-600">Loading price trends...</p>
      </div>

      <div v-else-if="!selectedProduct" class="text-center py-8">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">Select a product</h3>
        <p class="mt-2 text-gray-600">Choose a product from the dropdown to view price trends.</p>
      </div>

      <div v-else-if="priceTrends.length === 0" class="text-center py-8">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">No trend data available</h3>
        <p class="mt-2 text-gray-600">Price trend data for this product will appear here when available.</p>
      </div>

      <!-- Simple trend visualization -->
      <div v-else class="space-y-4">
        <div class="grid grid-cols-7 gap-2">
          <div v-for="trend in priceTrends.slice(-7)" :key="trend.date" class="text-center">
            <div class="bg-gray-100 rounded-lg p-3">
              <div class="text-xs text-gray-500 mb-1">{{ formatShortDate(trend.date) }}</div>
              <div class="text-sm font-medium text-gray-900">KES {{ formatCurrency(trend.price) }}</div>
              <div :class="getPriceChangeClass(trend.change)" class="text-xs mt-1">
                {{ trend.change > 0 ? '+' : '' }}{{ trend.change?.toFixed(1) || '0.0' }}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { dataInsightsAPI, locationsAPI, productsAPI } from '@/services/api'

const loading = ref(false)
const loadingPrices = ref(false)
const loadingTrends = ref(false)

const activeAlerts = ref([])
const marketPrices = ref([])
const priceTrends = ref([])
const priceAlerts = ref([])
const locations = ref([])
const availableProducts = ref([])

const selectedLocation = ref('')
const selectedProduct = ref('')
const trendPeriod = ref('30')

const marketStats = computed(() => ({
  totalProducts: marketPrices.value.length,
  avgIncrease: marketPrices.value.length > 0 
    ? (marketPrices.value.reduce((sum, p) => sum + (p.price_change || 0), 0) / marketPrices.value.length).toFixed(1)
    : 0,
  lastUpdated: marketPrices.value.length > 0 
    ? Math.max(...marketPrices.value.map(p => new Date(p.updated_at).getTime()))
    : null
}))

onMounted(() => {
  loadInitialData()
})

const loadInitialData = async () => {
  await Promise.all([
    loadWeatherAlerts(),
    loadMarketPrices(),
    loadLocations(),
    loadProducts()
  ])
}

const loadWeatherAlerts = async () => {
  try {
    const response = await dataInsightsAPI.getActiveAlerts()
    activeAlerts.value = Array.isArray(response) ? response : (response.results || [])
  } catch (error) {
    console.error('Failed to load weather alerts:', error)
  }
}

const loadMarketPrices = async () => {
  loadingPrices.value = true
  try {
    const params = {}
    if (selectedLocation.value) params.location_id = selectedLocation.value

    const response = await dataInsightsAPI.getLatestPrices()
    marketPrices.value = Array.isArray(response) ? response : (response.results || [])
  } catch (error) {
    console.error('Failed to load market prices:', error)
  } finally {
    loadingPrices.value = false
  }
}

const loadLocations = async () => {
  try {
    const response = await locationsAPI.getLocations()
    locations.value = Array.isArray(response) ? response : (response.results || [])
  } catch (error) {
    console.error('Failed to load locations:', error)
  }
}

const loadProducts = async () => {
  try {
    const response = await productsAPI.getProducts()
    availableProducts.value = Array.isArray(response) ? response : (response.results || [])
  } catch (error) {
    console.error('Failed to load products:', error)
  }
}

const loadPriceTrends = async () => {
  if (!selectedProduct.value) return
  
  loadingTrends.value = true
  try {
    const response = await dataInsightsAPI.getProductPrices(selectedProduct.value, parseInt(trendPeriod.value))
    priceTrends.value = Array.isArray(response) ? response : (response.results || [])
  } catch (error) {
    console.error('Failed to load price trends:', error)
  } finally {
    loadingTrends.value = false
  }
}

const refreshData = () => {
  loadInitialData()
  if (selectedProduct.value) {
    loadPriceTrends()
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

const formatShortDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

const getSeverityClass = (severity) => {
  const classes = {
    high: 'bg-red-50 border-red-200',
    medium: 'bg-yellow-50 border-yellow-200',
    low: 'bg-blue-50 border-blue-200'
  }
  return classes[severity] || 'bg-gray-50 border-gray-200'
}

const getSeverityIconClass = (severity) => {
  const classes = {
    high: 'bg-red-100 text-red-600',
    medium: 'bg-yellow-100 text-yellow-600',
    low: 'bg-blue-100 text-blue-600'
  }
  return classes[severity] || 'bg-gray-100 text-gray-600'
}

const getPriceChangeClass = (change) => {
  if (change > 0) return 'text-green-600'
  if (change < 0) return 'text-red-600'
  return 'text-gray-600'
}
</script>