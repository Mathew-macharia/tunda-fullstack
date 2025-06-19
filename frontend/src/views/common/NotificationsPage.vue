<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Notifications</h1>
        <p class="mt-2 text-gray-600">Stay updated with important alerts and messages</p>
      </div>
      <div class="flex space-x-3">
        <button @click="markAllAsRead" 
                :disabled="unreadCount === 0"
                class="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50">
          Mark All Read
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <dt class="text-sm font-medium text-gray-500 truncate">Total Notifications</dt>
        <dd class="text-2xl font-bold text-gray-900">{{ totalCount }}</dd>
      </div>
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <dt class="text-sm font-medium text-gray-500 truncate">Unread</dt>
        <dd class="text-2xl font-bold text-red-600">{{ unreadCount }}</dd>
      </div>
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <dt class="text-sm font-medium text-gray-500 truncate">Read</dt>
        <dd class="text-2xl font-bold text-green-600">{{ readCount }}</dd>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select v-model="filters.notification_type" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
            <option value="">All Types</option>
            <option value="order">Order Updates</option>
            <option value="delivery">Delivery Updates</option>
            <option value="payment">Payment Alerts</option>
            <option value="system">System Alerts</option>
            <option value="promotion">Promotions</option>
            <option value="weather">Weather Alerts</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select v-model="filters.is_read" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
            <option value="">All Status</option>
            <option value="false">Unread</option>
            <option value="true">Read</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
          <select v-model="filters.priority" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
            <option value="">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        <div class="flex items-end space-x-2">
          <button @click="loadNotifications" 
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

    <!-- Notifications List -->
    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      <p class="mt-2 text-gray-600">Loading notifications...</p>
    </div>

    <div v-else-if="notifications.length === 0" class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5-5-5h5zm0 0V9a6 6 0 10-12 0v8"></path>
      </svg>
      <h3 class="mt-4 text-lg font-medium text-gray-900">No notifications</h3>
      <p class="mt-2 text-gray-600">You're all caught up! No notifications match your current filters.</p>
    </div>

    <div v-else class="space-y-4">
      <div v-for="notification in notifications" :key="notification.notification_id"
           @click="markAsRead(notification)"
           :class="!notification.is_read ? 'border-l-4 border-l-blue-500 bg-blue-50' : 'border-l-4 border-l-gray-200'"
           class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 cursor-pointer hover:shadow-md transition-shadow">
        
        <div class="flex items-start justify-between">
          <div class="flex items-start space-x-4 flex-1">
            <!-- Notification Icon -->
            <div :class="getNotificationIconClass(notification.notification_type)" 
                 class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path v-if="notification.notification_type === 'order'" d="M3 1a1 1 0 000 2h1.22l.305 1.222a.997.997 0 00.01.042l1.358 5.43-.893.892C3.74 11.846 4.632 14 6.414 14H15a1 1 0 000-2H6.414l1-1H14a1 1 0 00.894-.553l3-6A1 1 0 0017 3H6.28l-.31-1.243A1 1 0 005 1H3zM16 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM6.5 18a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"/>
                <path v-else-if="notification.notification_type === 'delivery'" d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"/>
                <path v-else-if="notification.notification_type === 'payment'" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 6a2 2 0 114 0 2 2 0 01-4 0zm8-1a1 1 0 100 2h2a1 1 0 100-2h-2z"/>
                <path v-else-if="notification.notification_type === 'weather'" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"/>
                <path v-else d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"/>
              </svg>
            </div>

            <!-- Notification Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-2 mb-1">
                <h4 class="text-sm font-medium text-gray-900">{{ notification.title }}</h4>
                <span :class="getPriorityClass(notification.priority)" 
                      class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ notification.priority || 'Medium' }}
                </span>
                <span :class="getTypeClass(notification.notification_type)" 
                      class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ getTypeLabel(notification.notification_type) }}
                </span>
              </div>
              <p class="text-sm text-gray-600 mb-2">{{ notification.message }}</p>
              
              <!-- Action Data (e.g., order link, delivery tracking) -->
              <div v-if="notification.action_data" class="mt-3">
                <button v-if="notification.action_data.action_url" 
                        @click.stop="handleAction(notification)"
                        class="text-sm font-medium text-blue-600 hover:text-blue-700">
                  {{ notification.action_data.action_text || 'View Details' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Timestamp and Read Status -->
          <div class="flex flex-col items-end space-y-2 ml-4">
            <span class="text-xs text-gray-500">{{ formatDate(notification.created_at) }}</span>
            <div v-if="!notification.is_read" class="w-2 h-2 bg-blue-500 rounded-full"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="pagination.total > pagination.pageSize" class="mt-8 flex justify-center">
      <nav class="flex items-center space-x-2">
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
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { communicationAPI } from '@/services/api'

const router = useRouter()
const loading = ref(false)
const notifications = ref([])

const filters = ref({
  notification_type: '',
  is_read: '',
  priority: ''
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const totalCount = computed(() => notifications.value.length)
const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)
const readCount = computed(() => notifications.value.filter(n => n.is_read).length)

onMounted(() => {
  loadNotifications()
})

const loadNotifications = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      page_size: pagination.value.pageSize
    }
    
    Object.keys(filters.value).forEach(key => {
      if (filters.value[key]) params[key] = filters.value[key]
    })

    const response = await communicationAPI.getNotifications(params)
    
    if (response.results) {
      notifications.value = response.results
      pagination.value.total = response.count || 0
      pagination.value.page = page
    } else {
      notifications.value = Array.isArray(response) ? response : []
    }
  } catch (error) {
    console.error('Failed to load notifications:', error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    notification_type: '',
    is_read: '',
    priority: ''
  }
  loadNotifications(1)
}

const goToPage = (page) => {
  loadNotifications(page)
}

const markAsRead = async (notification) => {
  if (notification.is_read) return
  
  try {
    await communicationAPI.markNotificationRead(notification.notification_id)
    notification.is_read = true
  } catch (error) {
    console.error('Failed to mark notification as read:', error)
  }
}

const markAllAsRead = async () => {
  try {
    await communicationAPI.markAllNotificationsRead()
    notifications.value.forEach(n => n.is_read = true)
  } catch (error) {
    console.error('Failed to mark all notifications as read:', error)
  }
}

const handleAction = (notification) => {
  if (notification.action_data?.action_url) {
    // Handle different types of actions
    const url = notification.action_data.action_url
    
    if (url.startsWith('/')) {
      // Internal route
      router.push(url)
    } else if (url.startsWith('http')) {
      // External link
      window.open(url, '_blank')
    }
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) {
    return 'Yesterday'
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  } else {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
}

const getNotificationIconClass = (type) => {
  const classes = {
    order: 'bg-blue-100 text-blue-600',
    delivery: 'bg-green-100 text-green-600',
    payment: 'bg-yellow-100 text-yellow-600',
    system: 'bg-red-100 text-red-600',
    promotion: 'bg-purple-100 text-purple-600',
    weather: 'bg-orange-100 text-orange-600'
  }
  return classes[type] || 'bg-gray-100 text-gray-600'
}

const getPriorityClass = (priority) => {
  const classes = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800'
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

const getTypeClass = (type) => {
  const classes = {
    order: 'bg-blue-100 text-blue-800',
    delivery: 'bg-green-100 text-green-800',
    payment: 'bg-yellow-100 text-yellow-800',
    system: 'bg-red-100 text-red-800',
    promotion: 'bg-purple-100 text-purple-800',
    weather: 'bg-orange-100 text-orange-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const getTypeLabel = (type) => {
  const labels = {
    order: 'Order',
    delivery: 'Delivery',
    payment: 'Payment',
    system: 'System',
    promotion: 'Promotion',
    weather: 'Weather'
  }
  return labels[type] || 'Notification'
}
</script> 