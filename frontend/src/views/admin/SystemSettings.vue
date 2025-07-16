<template>
  <div class="min-h-screen bg-gray-50 py-4 sm:py-8">
    <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-6 sm:mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">System Settings</h1>
        <p class="mt-1 sm:mt-2 text-sm sm:text-base text-gray-600">Manage system configuration and preferences</p>
      </div>

      <!-- Settings Sections -->
      <div class="space-y-4 sm:space-y-6">
        <!-- General Settings -->
        <div class="bg-white shadow-sm rounded-lg border border-gray-200">
          <div class="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200">
            <h2 class="text-base sm:text-lg font-medium text-gray-900">General Settings</h2>
          </div>
          <div class="p-4 sm:p-6 space-y-4 sm:space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Platform Name</label>
                <input
                  v-model="settings.general.platform_name"
                  type="text"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Support Email</label>
                <input
                  v-model="settings.general.support_email"
                  type="email"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>

            <div class="space-y-1">
              <label class="block text-sm font-medium text-gray-700">Platform Description</label>
              <textarea
                v-model="settings.general.description"
                rows="3"
                class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              ></textarea>
            </div>

            <div class="flex items-center space-x-2">
              <input
                v-model="settings.general.maintenance_mode"
                type="checkbox"
                class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <label class="text-sm text-gray-700">Maintenance Mode</label>
            </div>
          </div>
        </div>

        <!-- Order Settings -->
        <div class="bg-white shadow-sm rounded-lg border border-gray-200">
          <div class="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200">
            <h2 class="text-base sm:text-lg font-medium text-gray-900">Order Settings</h2>
          </div>
          <div class="p-4 sm:p-6 space-y-4 sm:space-y-6">
            <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Minimum Order Amount (KES)</label>
                <input
                  v-model.number="settings.orders.minimum_order_amount"
                  type="number"
                  step="0.01"
                  min="0"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Order Timeout (hours)</label>
                <input
                  v-model.number="settings.orders.order_timeout_hours"
                  type="number"
                  min="1"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div class="space-y-1 sm:col-span-2 xl:col-span-1">
                <label class="block text-sm font-medium text-gray-700">Auto-cancel After (days)</label>
                <input
                  v-model.number="settings.orders.auto_cancel_days"
                  type="number"
                  min="1"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>

            <div class="space-y-3">
              <div class="flex items-center space-x-2">
                <input
                  v-model="settings.orders.allow_pre_orders"
                  type="checkbox"
                  class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <label class="text-sm text-gray-700">Allow Pre-orders</label>
              </div>
              <div class="flex items-center space-x-2">
                <input
                  v-model="settings.orders.require_phone_verification"
                  type="checkbox"
                  class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <label class="text-sm text-gray-700">Require Phone Verification</label>
              </div>
            </div>
          </div>
        </div>

        <!-- Delivery Settings -->
        <div class="bg-white shadow-sm rounded-lg border border-gray-200">
          <div class="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200">
            <h2 class="text-base sm:text-lg font-medium text-gray-900">Delivery Settings</h2>
          </div>
          <div class="p-4 sm:p-6 space-y-4 sm:space-y-6">
            <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Base Delivery Fee (KES)</label>
                <input
                  v-model.number="settings.delivery.base_delivery_fee"
                  type="number"
                  step="0.01"
                  min="0"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Free Delivery Threshold (KES)</label>
                <input
                  v-model.number="settings.delivery.free_delivery_threshold"
                  type="number"
                  step="0.01"
                  min="0"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div class="space-y-1 sm:col-span-2 xl:col-span-1">
                <label class="block text-sm font-medium text-gray-700">Max Delivery Distance (km)</label>
                <input
                  v-model.number="settings.delivery.max_delivery_distance"
                  type="number"
                  min="1"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Standard Delivery Time (hours)</label>
                <input
                  v-model.number="settings.delivery.standard_delivery_hours"
                  type="number"
                  min="1"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Express Delivery Time (hours)</label>
                <input
                  v-model.number="settings.delivery.express_delivery_hours"
                  type="number"
                  min="1"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Withholding Tax Rate (%)</label>
                <input
                  v-model.number="settings.payments.wht_rate"
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Withholding Tax Threshold (KES)</label>
                <input
                  v-model.number="settings.payments.wht_threshold"
                  type="number"
                  step="0.01"
                  min="0"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Payment Settings -->
        <div class="bg-white shadow-sm rounded-lg border border-gray-200">
          <div class="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200">
            <h2 class="text-base sm:text-lg font-medium text-gray-900">Payment Settings</h2>
          </div>
          <div class="p-4 sm:p-6 space-y-4 sm:space-y-6">
            <div class="space-y-3">
              <div class="flex items-center space-x-2">
                <input
                  v-model="settings.payments.enable_mpesa"
                  type="checkbox"
                  class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <label class="text-sm text-gray-700">Enable M-Pesa Payments</label>
              </div>
              <div class="flex items-center space-x-2">
                <input
                  v-model="settings.payments.enable_cash_on_delivery"
                  type="checkbox"
                  class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <label class="text-sm text-gray-700">Enable Cash on Delivery</label>
              </div>
              <div class="flex items-center space-x-2">
                <input
                  v-model="settings.payments.enable_bank_transfer"
                  type="checkbox"
                  class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <label class="text-sm text-gray-700">Enable Bank Transfer</label>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Payment Timeout (minutes)</label>
                <input
                  v-model.number="settings.payments.payment_timeout_minutes"
                  type="number"
                  min="5"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Transaction Fee (%)</label>
                <input
                  v-model.number="settings.payments.transaction_fee_percentage"
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>
            <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">M-Pesa Callback URL</label>
                <input
                  v-model="settings.payments.mpesa_callback_url"
                  type="text"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
          </div>
        </div>

        <!-- Notification Settings -->
        <div class="bg-white shadow-sm rounded-lg border border-gray-200">
          <div class="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200">
            <h2 class="text-base sm:text-lg font-medium text-gray-900">Notification Settings</h2>
          </div>
          <div class="p-4 sm:p-6 space-y-4 sm:space-y-6">
            <div class="space-y-3">
              <div class="flex items-center space-x-2">
                <input
                  v-model="settings.notifications.sms_enabled"
                  type="checkbox"
                  class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <label class="text-sm text-gray-700">Enable SMS Notifications</label>
              </div>
              <div class="flex items-center space-x-2">
                <input
                  v-model="settings.notifications.email_enabled"
                  type="checkbox"
                  class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <label class="text-sm text-gray-700">Enable Email Notifications</label>
              </div>
              <div class="flex items-center space-x-2">
                <input
                  v-model="settings.notifications.push_enabled"
                  type="checkbox"
                  class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <label class="text-sm text-gray-700">Enable Push Notifications</label>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">SMS Provider</label>
                <select
                  v-model="settings.notifications.sms_provider"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
                >
                  <option value="africa_talking">Africa's Talking</option>
                  <option value="twilio">Twilio</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Email Provider</label>
                <select
                  v-model="settings.notifications.email_provider"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
                >
                  <option value="sendgrid">SendGrid</option>
                  <option value="mailgun">Mailgun</option>
                  <option value="smtp">SMTP</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- Security Settings -->
        <div class="bg-white shadow-sm rounded-lg border border-gray-200">
          <div class="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200">
            <h2 class="text-base sm:text-lg font-medium text-gray-900">Security Settings</h2>
          </div>
          <div class="p-4 sm:p-6 space-y-4 sm:space-y-6">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Session Timeout (minutes)</label>
                <input
                  v-model.number="settings.security.session_timeout_minutes"
                  type="number"
                  min="15"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Max Login Attempts</label>
                <input
                  v-model.number="settings.security.max_login_attempts"
                  type="number"
                  min="3"
                  class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>

            <div class="space-y-3">
              <div class="flex items-center space-x-2">
                <input
                  v-model="settings.security.two_factor_required"
                  type="checkbox"
                  class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <label class="text-sm text-gray-700">Require Two-Factor Authentication</label>
              </div>
              <div class="flex items-center space-x-2">
                <input
                  v-model="settings.security.password_complexity"
                  type="checkbox"
                  class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <label class="text-sm text-gray-700">Enforce Password Complexity</label>
              </div>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
          <div class="flex">
            <ExclamationTriangleIcon class="h-5 w-5 text-red-400 flex-shrink-0" />
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Error saving settings</h3>
              <p class="mt-1 text-sm text-red-700">{{ error }}</p>
            </div>
          </div>
        </div>

        <!-- Success Message -->
        <div v-if="success" class="bg-green-50 border border-green-200 rounded-md p-4">
          <div class="flex">
            <CheckCircleIcon class="h-5 w-5 text-green-400 flex-shrink-0" />
            <div class="ml-3">
              <h3 class="text-sm font-medium text-green-800">Settings saved successfully</h3>
            </div>
          </div>
        </div>

        <!-- Save Button -->
        <div class="flex justify-end pt-4">
          <button
            @click="saveSettings"
            :disabled="loading"
            class="w-full sm:w-auto px-6 py-2.5 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? 'Saving...' : 'Save Settings' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'

// State
const loading = ref(false)
const error = ref(null)
const success = ref(false)

const settings = ref({
  general: {
    platform_name: 'Vegas Agricultural Marketplace',
    support_email: 'support@vegas.co.ke',
    description: 'Connecting farmers directly with customers for fresh, quality produce',
    maintenance_mode: false
  },
  orders: {
    minimum_order_amount: 100,
    order_timeout_hours: 24,
    auto_cancel_days: 7,
    allow_pre_orders: true,
    require_phone_verification: true
  },
  delivery: {
    base_delivery_fee: 50,
    free_delivery_threshold: 500,
    max_delivery_distance: 50,
    standard_delivery_hours: 24,
    express_delivery_hours: 6
  },
  payments: {
    enable_mpesa: true,
    enable_cash_on_delivery: true,
    enable_bank_transfer: true,
    payment_timeout_minutes: 15,
    transaction_fee_percentage: 1.5, // Updated to 1.5%
    wht_rate: 3.0, // New setting for WHT rate (3%)
    wht_threshold: 24000.00, // New setting for WHT threshold (KES 24,000)
    mpesa_callback_url: ''
  },
  notifications: {
    sms_enabled: true,
    email_enabled: true,
    push_enabled: true,
    sms_provider: 'africa_talking',
    email_provider: 'sendgrid'
  },
  security: {
    session_timeout_minutes: 120,
    max_login_attempts: 5,
    two_factor_required: false,
    password_complexity: true
  }
})

// Methods
import { settingsAPI } from '@/services/api'

const loadSettings = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await settingsAPI.getSettings()
    settings.value = {
      general: {
        platform_name: response.platform_name || 'Vegas Agricultural Marketplace',
        support_email: response.support_email || 'support@vegas.co.ke',
        description: response.description || 'Connecting farmers directly with customers for fresh, quality produce',
        maintenance_mode: response.maintenance_mode || false
      },
      orders: {
        minimum_order_amount: response.minimum_order_amount || 100,
        order_timeout_hours: response.order_timeout_hours || 24,
        auto_cancel_days: response.auto_cancel_days || 7,
        allow_pre_orders: response.allow_pre_orders || true,
        require_phone_verification: response.require_phone_verification || true
      },
      delivery: {
        base_delivery_fee: response.base_delivery_fee || 50,
        free_delivery_threshold: response.free_delivery_threshold || 500,
        max_delivery_distance: response.max_delivery_distance_km || 50,
        standard_delivery_hours: response.standard_delivery_hours || 24,
        express_delivery_hours: response.express_delivery_hours || 6
      },
      payments: {
        enable_mpesa: response.supported_payment_methods?.includes('Mpesa') || false,
        enable_cash_on_delivery: response.supported_payment_methods?.includes('CashOnDelivery') || false,
        enable_bank_transfer: response.supported_payment_methods?.includes('BankTransfer') || false,
        payment_timeout_minutes: response.payment_timeout_minutes || 15,
        transaction_fee_percentage: (response.transaction_fee_rate * 100) || 0, // Convert decimal to percentage
        wht_rate: (response.wht_rate * 100) || 0, // Convert decimal to percentage
        wht_threshold: response.wht_threshold || 0,
        mpesa_callback_url: response.mpesa_callback_url || ''
      },
      notifications: {
        sms_enabled: response.sms_notifications_enabled || false,
        email_enabled: response.email_notifications_enabled || false,
        push_enabled: response.push_notifications_enabled || false, // Assuming a push_notifications_enabled setting
        sms_provider: response.sms_provider || 'africa_talking', // Assuming an sms_provider setting
        email_provider: response.email_provider || 'sendgrid' // Assuming an email_provider setting
      },
      security: {
        session_timeout_minutes: response.session_timeout_minutes || 120, // Assuming a session_timeout_minutes setting
        max_login_attempts: response.max_login_attempts || 5, // Assuming a max_login_attempts setting
        two_factor_required: response.two_factor_required || false, // Assuming a two_factor_required setting
        password_complexity: response.password_complexity || true // Assuming a password_complexity setting
      }
    }
    console.log('Settings loaded:', settings.value)
  } catch (err) {
    console.error('Error loading settings:', err)
    error.value = 'Failed to load settings'
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  loading.value = true
  error.value = null
  success.value = false
  
  try {
    const payload = {
      platform_name: settings.value.general.platform_name,
      support_email: settings.value.general.support_email,
      description: settings.value.general.description,
      maintenance_mode: settings.value.general.maintenance_mode,
      minimum_order_amount: settings.value.orders.minimum_order_amount,
      order_timeout_hours: settings.value.orders.order_timeout_hours,
      auto_cancel_days: settings.value.orders.auto_cancel_days,
      allow_pre_orders: settings.value.orders.allow_pre_orders,
      require_phone_verification: settings.value.orders.require_phone_verification,
      base_delivery_fee: settings.value.delivery.base_delivery_fee,
      free_delivery_threshold: settings.value.delivery.free_delivery_threshold,
      max_delivery_distance_km: settings.value.delivery.max_delivery_distance,
      standard_delivery_hours: settings.value.delivery.standard_delivery_hours,
      express_delivery_hours: settings.value.delivery.express_delivery_hours,
      supported_payment_methods: [],
      payment_timeout_minutes: settings.value.payments.payment_timeout_minutes,
      transaction_fee_rate: settings.value.payments.transaction_fee_percentage / 100, // Convert percentage to decimal
      wht_rate: settings.value.payments.wht_rate / 100, // Convert percentage to decimal
      wht_threshold: settings.value.payments.wht_threshold,
      mpesa_callback_url: settings.value.payments.mpesa_callback_url,
      sms_notifications_enabled: settings.value.notifications.sms_enabled,
      email_notifications_enabled: settings.value.notifications.email_enabled,
      push_notifications_enabled: settings.value.notifications.push_enabled,
      sms_provider: settings.value.notifications.sms_provider,
      email_provider: settings.value.notifications.email_provider,
      session_timeout_minutes: settings.value.security.session_timeout_minutes,
      max_login_attempts: settings.value.security.max_login_attempts,
      two_factor_required: settings.value.security.two_factor_required,
      password_complexity: settings.value.security.password_complexity,
    }

    if (settings.value.payments.enable_mpesa) payload.supported_payment_methods.push('Mpesa')
    if (settings.value.payments.enable_cash_on_delivery) payload.supported_payment_methods.push('CashOnDelivery')
    if (settings.value.payments.enable_bank_transfer) payload.supported_payment_methods.push('BankTransfer')

    await settingsAPI.updateSettings(payload)
    
    success.value = true
    setTimeout(() => {
      success.value = false
    }, 3000)
    
    console.log('Settings saved:', settings.value)
  } catch (err) {
    console.error('Error saving settings:', err)
    error.value = 'Failed to save settings'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>
