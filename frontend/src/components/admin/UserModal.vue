<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-medium text-gray-900">
            {{ user ? 'Edit User' : 'Create New User' }}
          </h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
              <input
                v-model="formData.first_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
              <input
                v-model="formData.last_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
            <input
              v-model="formData.phone_number"
              type="tel"
              required
              :disabled="!!user"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email (Optional)</label>
            <input
              v-model="formData.email"
              type="email"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <select
              v-model="formData.user_role"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select Role</option>
              <option value="customer">Customer</option>
              <option value="farmer">Farmer</option>
              <option value="rider">Rider</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div v-if="!user">
            <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              v-model="formData.password"
              type="password"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div v-if="!user">
            <label class="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
            <input
              v-model="formData.re_password"
              type="password"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div class="flex items-center">
            <input
              v-model="formData.is_active"
              type="checkbox"
              class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            />
            <label class="ml-2 block text-sm text-gray-700">Active User</label>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-3">
            <p class="text-sm text-red-700">{{ error }}</p>
          </div>

          <!-- Buttons -->
          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {{ loading ? 'Saving...' : (user ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineEmits } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  user: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

// State
const loading = ref(false)
const error = ref(null)

const formData = ref({
  first_name: '',
  last_name: '',
  phone_number: '',
  email: '',
  user_role: '',
  password: '',
  re_password: '',
  is_active: true
})

// Methods
const initializeForm = () => {
  if (props.user) {
    formData.value = {
      first_name: props.user.first_name || '',
      last_name: props.user.last_name || '',
      phone_number: props.user.phone_number || '',
      email: props.user.email || '',
      user_role: props.user.user_role || '',
      is_active: props.user.is_active !== false,
      password: '',
      re_password: ''
    }
  }
}

const handleSubmit = async () => {
  error.value = null
  
  // Validation
  if (!props.user && formData.value.password !== formData.value.re_password) {
    error.value = "Passwords don't match"
    return
  }
  
  if (!props.user && formData.value.password.length < 6) {
    error.value = "Password must be at least 6 characters"
    return
  }
  
  loading.value = true
  
  try {
    const userData = { ...formData.value }
    
    // Remove password fields for updates if they're empty
    if (props.user && !userData.password) {
      delete userData.password
      delete userData.re_password
    }
    
    await emit('save', userData)
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Failed to save user'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  initializeForm()
})
</script> 