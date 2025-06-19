<template>
  <div class="min-h-screen bg-gray-50 pb-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Mobile Header -->
      <div class="pt-6 pb-4 sm:pt-8">
        <div class="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
          <div class="min-w-0 flex-1">
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Users Management</h1>
            <p class="mt-1 text-sm sm:text-base text-gray-600">Manage all users in the system</p>
          </div>
          <div class="flex flex-col space-y-2 sm:flex-row sm:space-y-0 sm:space-x-3">
            <button
              @click="exportUsers"
              class="inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <DocumentArrowDownIcon class="-ml-1 mr-2 h-4 w-4" />
              Export
            </button>
            <button
              @click="openCreateModal"
              class="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <UserPlusIcon class="-ml-1 mr-2 h-4 w-4" />
              Add User
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile Stats Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <UsersIcon class="h-5 w-5 sm:h-6 sm:w-6 text-gray-400" />
              </div>
              <div class="ml-3 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Total Users</dt>
                  <dd class="text-base sm:text-lg font-medium text-gray-900">{{ userStats.total }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <UserGroupIcon class="h-5 w-5 sm:h-6 sm:w-6 text-green-400" />
              </div>
              <div class="ml-3 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Farmers</dt>
                  <dd class="text-base sm:text-lg font-medium text-gray-900">{{ userStats.farmers }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <ShoppingCartIcon class="h-5 w-5 sm:h-6 sm:w-6 text-blue-400" />
              </div>
              <div class="ml-3 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Customers</dt>
                  <dd class="text-base sm:text-lg font-medium text-gray-900">{{ userStats.customers }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-3 sm:p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <TruckIcon class="h-5 w-5 sm:h-6 sm:w-6 text-purple-400" />
              </div>
              <div class="ml-3 sm:ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-xs sm:text-sm font-medium text-gray-500 truncate">Riders</dt>
                  <dd class="text-base sm:text-lg font-medium text-gray-900">{{ userStats.riders }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Mobile Filters -->
      <div class="bg-white shadow rounded-lg p-4 sm:p-6 mb-4 sm:mb-6">
        <div class="space-y-4 sm:space-y-0 sm:grid sm:grid-cols-2 lg:grid-cols-4 sm:gap-4">
          <div class="sm:col-span-2 lg:col-span-1">
            <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              v-model="filters.search"
              type="text"
              placeholder="Search users..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              @input="debouncedFilter"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Role</label>
            <select
              v-model="filters.role"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">All Roles</option>
              <option value="farmer">Farmer</option>
              <option value="customer">Customer</option>
              <option value="rider">Rider</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              v-model="filters.status"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Date Joined</label>
            <select
              v-model="filters.dateRange"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="year">This Year</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 sm:h-12 sm:w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
        <div class="flex">
          <ExclamationTriangleIcon class="h-5 w-5 text-red-400 flex-shrink-0" />
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium text-red-800">Error loading users</h3>
            <p class="mt-1 text-sm text-red-700">{{ error }}</p>
            <button 
              @click="loadUsers"
              class="mt-2 text-sm text-red-600 hover:text-red-500 underline focus:outline-none"
            >
              Try again
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile Users List -->
      <div v-else class="space-y-4 sm:space-y-0">
        <!-- Mobile Card View -->
        <div class="block sm:hidden space-y-3">
          <div
            v-for="user in users"
            :key="user.user_id"
            class="bg-white shadow rounded-lg p-4 border border-gray-200"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-center flex-1 min-w-0">
                <div class="flex-shrink-0 h-10 w-10">
                  <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                    <UserIcon class="h-5 w-5 text-gray-600" />
                  </div>
                </div>
                <div class="ml-3 flex-1 min-w-0">
                  <div class="text-sm font-medium text-gray-900 truncate">
                    {{ user.first_name }} {{ user.last_name }}
                  </div>
                  <div class="text-xs text-gray-500 truncate">
                    {{ user.email || user.phone_number }}
                  </div>
                  <div class="flex items-center space-x-2 mt-1">
                    <span :class="getRoleClass(user.user_role)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                      {{ formatRole(user.user_role) }}
                    </span>
                    <span :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                      {{ user.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="flex items-center space-x-1 ml-2">
                <button
                  @click="viewUser(user)"
                  class="p-2 text-indigo-600 hover:text-indigo-900 hover:bg-indigo-50 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <EyeIcon class="h-4 w-4" />
                </button>
                <button
                  @click="editUser(user)"
                  class="p-2 text-green-600 hover:text-green-900 hover:bg-green-50 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <PencilIcon class="h-4 w-4" />
                </button>
                <button
                  @click="toggleUserStatus(user)"
                  class="p-2 text-yellow-600 hover:text-yellow-900 hover:bg-yellow-50 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
                >
                  <component :is="user.is_active ? PowerIcon : PlayIcon" class="h-4 w-4" />
                </button>
                <button
                  @click="deleteUser(user)"
                  class="p-2 text-red-600 hover:text-red-900 hover:bg-red-50 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                  <TrashIcon class="h-4 w-4" />
                </button>
              </div>
            </div>
            <div class="mt-3 pt-3 border-t border-gray-100">
              <div class="flex justify-between text-xs text-gray-500">
                <span>Joined: {{ formatDate(user.date_joined) }}</span>
                <span>Last login: {{ user.last_login ? formatDate(user.last_login) : 'Never' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Desktop Table View -->
        <div class="hidden sm:block bg-white shadow overflow-hidden rounded-md">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Joined
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Login
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="user in users" :key="user.user_id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-10 w-10">
                        <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                          <UserIcon class="h-6 w-6 text-gray-600" />
                        </div>
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">
                          {{ user.first_name }} {{ user.last_name }}
                        </div>
                        <div class="text-sm text-gray-500">
                          {{ user.email || user.phone_number }}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="getRoleClass(user.user_role)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                      {{ formatRole(user.user_role) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                      {{ user.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDate(user.date_joined) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ user.last_login ? formatDate(user.last_login) : 'Never' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex justify-end space-x-2">
                      <button
                        @click="viewUser(user)"
                        class="text-indigo-600 hover:text-indigo-900 p-1 rounded hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      >
                        <EyeIcon class="h-4 w-4" />
                      </button>
                      <button
                        @click="editUser(user)"
                        class="text-green-600 hover:text-green-900 p-1 rounded hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        <PencilIcon class="h-4 w-4" />
                      </button>
                      <button
                        @click="toggleUserStatus(user)"
                        class="text-yellow-600 hover:text-yellow-900 p-1 rounded hover:bg-yellow-50 focus:outline-none focus:ring-2 focus:ring-yellow-500"
                      >
                        <component :is="user.is_active ? PowerIcon : PlayIcon" class="h-4 w-4" />
                      </button>
                      <button
                        @click="deleteUser(user)"
                        class="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500"
                      >
                        <TrashIcon class="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Mobile Pagination -->
      <div v-if="totalPages > 1" class="mt-6">
        <!-- Mobile Pagination -->
        <div class="flex items-center justify-between sm:hidden">
          <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1"
            :class="currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Previous
          </button>
          <span class="text-sm text-gray-700">
            Page {{ currentPage }} of {{ totalPages }}
          </span>
          <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            :class="currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Next
          </button>
        </div>

        <!-- Desktop Pagination -->
        <div class="hidden sm:flex sm:items-center sm:justify-between bg-white px-4 py-3 border-t border-gray-200 sm:px-6 rounded-b-md">
          <div>
            <p class="text-sm text-gray-700">
              Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalUsers) }} of {{ totalUsers }} results
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="changePage(page)"
                :class="currentPage === page 
                  ? 'bg-indigo-50 border-indigo-500 text-indigo-600 z-10' 
                  : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'"
                class="relative inline-flex items-center px-4 py-2 border text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                {{ page }}
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <UserModal
      v-if="showUserModal"
      :user="selectedUser"
      @close="closeUserModal"
      @save="handleSaveUser"
    />

    <UserDetailsModal
      v-if="showDetailsModal"
      :user="selectedUser"
      @close="showDetailsModal = false"
      @edit="editUser"
    />

    <ConfirmModal
      v-if="showDeleteModal"
      title="Delete User"
      message="Are you sure you want to delete this user? This action cannot be undone."
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { usersAPI } from '@/services/api'
import {
  UserPlusIcon,
  UsersIcon,
  UserGroupIcon,
  ShoppingCartIcon,
  TruckIcon,
  DocumentArrowDownIcon,
  ExclamationTriangleIcon,
  UserIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  PowerIcon,
  PlayIcon
} from '@heroicons/vue/24/outline'
import UserModal from '@/components/admin/UserModal.vue'
import UserDetailsModal from '@/components/admin/UserDetailsModal.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

// State
const loading = ref(true)
const error = ref(null)
const users = ref([])
const selectedUser = ref(null)
const showUserModal = ref(false)
const showDetailsModal = ref(false)
const showDeleteModal = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const totalUsers = ref(0)
const pageSize = 20

// User Statistics
const userStats = ref({
  total: 0,
  farmers: 0,
  customers: 0,
  riders: 0
})

// Filters
const filters = ref({
  search: '',
  role: '',
  status: '',
  dateRange: ''
})

// Computed
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// Methods
const loadUsers = async () => {
  loading.value = true
  error.value = null
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize,
      ordering: '-date_joined'
    }
    
    // Apply filters
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.role) params.user_role = filters.value.role
    if (filters.value.status) params.is_active = filters.value.status === 'active'
    
    const response = await usersAPI.getUsers(params)
    
    if (response.results) {
      users.value = response.results
      totalPages.value = Math.ceil(response.count / pageSize)
      totalUsers.value = response.count
    } else {
      users.value = Array.isArray(response) ? response : []
    }
    
    await loadUserStats()
    
  } catch (err) {
    console.error('Error loading users:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load users'
  } finally {
    loading.value = false
  }
}

const loadUserStats = async () => {
  try {
    const response = await usersAPI.getUserStats()
    userStats.value = response
  } catch (err) {
    console.error('Error loading user stats:', err)
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
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

const openCreateModal = () => {
  selectedUser.value = null
  showUserModal.value = true
}

const viewUser = (user) => {
  selectedUser.value = user
  showDetailsModal.value = true
}

const editUser = (user) => {
  selectedUser.value = user
  showUserModal.value = true
  showDetailsModal.value = false
}

const closeUserModal = () => {
  showUserModal.value = false
  selectedUser.value = null
}

const handleSaveUser = async (userData) => {
  try {
    if (selectedUser.value) {
      await usersAPI.updateUser(selectedUser.value.user_id, userData)
    } else {
      await usersAPI.createUser(userData)
    }
    
    closeUserModal()
    await loadUsers()
  } catch (err) {
    console.error('Error saving user:', err)
    throw err
  }
}

const toggleUserStatus = async (user) => {
  try {
    await usersAPI.updateUser(user.user_id, { is_active: !user.is_active })
    await loadUsers()
  } catch (err) {
    console.error('Error updating user status:', err)
    error.value = 'Failed to update user status'
  }
}

const deleteUser = (user) => {
  selectedUser.value = user
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  try {
    await usersAPI.deleteUser(selectedUser.value.user_id)
    showDeleteModal.value = false
    selectedUser.value = null
    await loadUsers()
  } catch (err) {
    console.error('Error deleting user:', err)
    error.value = 'Failed to delete user'
  }
}

const exportUsers = async () => {
  try {
    const response = await usersAPI.exportUsers(filters.value)
    // Handle CSV download
    const blob = new Blob([response], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `users_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Error exporting users:', err)
    error.value = 'Failed to export users'
  }
}

const applyFilters = () => {
  currentPage.value = 1
  loadUsers()
}

// Debounced search
let searchTimeout
const debouncedFilter = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(applyFilters, 500)
}

const changePage = (page) => {
  currentPage.value = page
  loadUsers()
}

onMounted(() => {
  loadUsers()
})
</script>