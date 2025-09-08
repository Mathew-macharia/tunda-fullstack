import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { communicationAPI } from '@/services/api'
import { user } from '@/stores/auth' // Assuming user store is available for current user ID

export const useNotificationStore = defineStore('notifications', () => {
  const notifications = ref([])
  const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)
  const loading = ref(false)
  const error = ref(null)

  async function fetchNotifications() {
    if (!user.value) {
      notifications.value = []
      return
    }

    loading.value = true
    error.value = null
    try {
      const response = await communicationAPI.getNotifications({ user_id: user.value.user_id })
      notifications.value = response.results || response // Adjust based on actual API response structure
    } catch (err) {
      console.error('Failed to fetch notifications:', err)
      error.value = 'Failed to load notifications.'
    } finally {
      loading.value = false
    }
  }

  async function markNotificationRead(notificationId) {
    try {
      await communicationAPI.markNotificationRead(notificationId)
      const index = notifications.value.findIndex(n => n.notification_id === notificationId)
      if (index !== -1) {
        notifications.value[index].is_read = true
      }
    } catch (err) {
      console.error(`Failed to mark notification ${notificationId} as read:`, err)
      error.value = 'Failed to mark notification as read.'
    }
  }

  async function markAllNotificationsRead() {
    try {
      await communicationAPI.markAllNotificationsRead()
      notifications.value.forEach(n => {
        n.is_read = true
      })
    } catch (err) {
      console.error('Failed to mark all notifications as read:', err)
      error.value = 'Failed to mark all notifications as read.'
    }
  }

  // Optionally, add a method to clear notifications from the store (e.g., on logout)
  function clearNotifications() {
    notifications.value = []
  }

  return {
    notifications,
    unreadCount,
    loading,
    error,
    fetchNotifications,
    markNotificationRead,
    markAllNotificationsRead,
    clearNotifications
  }
})
