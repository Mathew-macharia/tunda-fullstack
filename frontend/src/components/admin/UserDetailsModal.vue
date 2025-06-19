<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-medium text-gray-900">User Details</h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <!-- User Info -->
        <div class="space-y-4">
          <div class="text-center">
            <div class="h-20 w-20 rounded-full bg-gray-300 flex items-center justify-center mx-auto mb-4">
              <UserIcon class="h-12 w-12 text-gray-600" />
            </div>
            <h4 class="text-xl font-medium text-gray-900">
              {{ user.first_name }} {{ user.last_name }}
            </h4>
            <span :class="getRoleClass(user.user_role)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full mt-2">
              {{ formatRole(user.user_role) }}
            </span>
          </div>

          <div class="border-t border-gray-200 pt-4">
            <dl class="space-y-3">
              <div>
                <dt class="text-sm font-medium text-gray-500">Phone Number</dt>
                <dd class="text-sm text-gray-900">{{ user.phone_number }}</dd>
              </div>
              
              <div v-if="user.email">
                <dt class="text-sm font-medium text-gray-500">Email</dt>
                <dd class="text-sm text-gray-900">{{ user.email }}</dd>
              </div>
              
              <div>
                <dt class="text-sm font-medium text-gray-500">Status</dt>
                <dd class="text-sm">
                  <span :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </dd>
              </div>
              
              <div>
                <dt class="text-sm font-medium text-gray-500">Date Joined</dt>
                <dd class="text-sm text-gray-900">{{ formatDate(user.date_joined) }}</dd>
              </div>
              
              <div>
                <dt class="text-sm font-medium text-gray-500">Last Login</dt>
                <dd class="text-sm text-gray-900">
                  {{ user.last_login ? formatDate(user.last_login) : 'Never' }}
                </dd>
              </div>
            </dl>
          </div>

          <!-- Actions -->
          <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              @click="$emit('close')"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Close
            </button>
            <button
              @click="$emit('edit', user)"
              class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700"
            >
              Edit User
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineEmits } from 'vue'
import { XMarkIcon, UserIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
})

defineEmits(['close', 'edit'])

// Methods
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatRole = (role) => {
  const roleMap = {
    'farmer': 'Farmer',
    'customer': 'Customer',
    'rider': 'Rider',
    'admin': 'Admin'
  }
  return roleMap[role] || role
}

const getRoleClass = (role) => {
  const roleClasses = {
    'farmer': 'bg-green-100 text-green-800',
    'customer': 'bg-blue-100 text-blue-800',
    'rider': 'bg-purple-100 text-purple-800',
    'admin': 'bg-red-100 text-red-800'
  }
  return roleClasses[role] || 'bg-gray-100 text-gray-800'
}
</script> 