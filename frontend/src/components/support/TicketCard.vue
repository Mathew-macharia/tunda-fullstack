<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-all duration-200 cursor-pointer touch-manipulation active:scale-95"
       @click="$emit('click', ticket)">
    <div class="flex items-start justify-between">
      <div class="flex-1 min-w-0">
        <!-- Ticket Header -->
        <div class="flex items-center space-x-2 mb-2">
          <span class="text-sm font-medium text-gray-900">
            #{{ ticket.ticket_number }}
          </span>
          <span :class="getPriorityClass(ticket.priority)" 
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
            {{ formatPriority(ticket.priority) }}
          </span>
          <span :class="getStatusClass(ticket.status)" 
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
            {{ formatStatus(ticket.status) }}
          </span>
        </div>

        <!-- Subject -->
        <h3 class="text-sm font-medium text-gray-900 mb-1 line-clamp-1">
          {{ ticket.subject }}
        </h3>

        <!-- Category and Description -->
        <div class="mb-3">
          <p class="text-xs text-gray-500 mb-1">
            {{ formatCategory(ticket.category) }}
          </p>
          <p class="text-sm text-gray-600 line-clamp-2">
            {{ ticket.description }}
          </p>
        </div>

        <!-- Order Reference -->
        <div v-if="ticket.order" class="mb-2">
          <p class="text-xs text-blue-600">
            Related to Order #{{ ticket.order?.order_number || ticket.order }}
          </p>
        </div>

        <!-- Meta Information -->
        <div class="flex items-center justify-between text-xs text-gray-500">
          <span>{{ formatDate(ticket.created_at) }}</span>
          <span v-if="ticket.assigned_to">
            Assigned to {{ ticket.assigned_to_username || 'Admin' }}
          </span>
        </div>
      </div>

      <!-- Action Button -->
      <div class="ml-4 flex-shrink-0">
        <button
          @click.stop="$emit('action', ticket)"
          class="text-gray-400 hover:text-gray-600"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Quick Actions (for admin) -->
    <div v-if="showAdminActions" class="mt-3 pt-3 border-t border-gray-100 flex flex-wrap gap-2">
      <button
        @click.stop="$emit('assign', ticket)"
        class="text-xs bg-blue-50 text-blue-700 px-3 py-2 rounded hover:bg-blue-100 active:bg-blue-200 touch-manipulation transition-colors"
      >
        Assign
      </button>
      <button
        @click.stop="$emit('resolve', ticket)"
        class="text-xs bg-green-50 text-green-700 px-3 py-2 rounded hover:bg-green-100 active:bg-green-200 touch-manipulation transition-colors"
      >
        Resolve
      </button>
      <button
        @click.stop="$emit('edit', ticket)"
        class="text-xs bg-gray-50 text-gray-700 px-3 py-2 rounded hover:bg-gray-100 active:bg-gray-200 touch-manipulation transition-colors"
      >
        Edit
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { user } from '@/stores/auth'

const props = defineProps({
  ticket: {
    type: Object,
    required: true
  }
})

defineEmits(['click', 'action', 'assign', 'resolve', 'edit'])

const showAdminActions = computed(() => {
  return user.value?.user_role === 'admin'
})

const formatPriority = (priority) => {
  const priorities = {
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    urgent: 'Urgent'
  }
  return priorities[priority] || priority
}

const formatStatus = (status) => {
  const statuses = {
    open: 'Open',
    in_progress: 'In Progress',
    resolved: 'Resolved',
    closed: 'Closed'
  }
  return statuses[status] || status
}

const formatCategory = (category) => {
  const categories = {
    order_issue: 'Order Issues',
    payment_problem: 'Payment Problems',
    delivery_issue: 'Delivery Issues',
    product_quality: 'Product Quality',
    technical_support: 'Technical Support',
    other: 'Other'
  }
  return categories[category] || category
}

const getPriorityClass = (priority) => {
  const classes = {
    low: 'bg-gray-100 text-gray-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    urgent: 'bg-red-100 text-red-800'
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

const getStatusClass = (status) => {
  const classes = {
    open: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    resolved: 'bg-green-100 text-green-800',
    closed: 'bg-gray-100 text-gray-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const now = new Date()
  const date = new Date(dateString)
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return 'Today'
  if (diffDays === 2) return 'Yesterday'
  if (diffDays <= 7) return `${diffDays} days ago`
  
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  line-clamp: 1;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-clamp: 2;
  overflow: hidden;
}
</style> 