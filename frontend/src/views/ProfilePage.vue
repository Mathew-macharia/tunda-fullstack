<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <h1 class="text-2xl font-bold text-gray-900">Profile Settings</h1>
        <p class="mt-1 text-sm text-gray-500">
          Manage your account information and preferences
        </p>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="space-y-8">
        <!-- Profile Information -->
        <div class="card">
          <div class="card-header">
            <h2 class="text-lg font-medium text-gray-900">Profile Information</h2>
            <p class="mt-1 text-sm text-gray-500">
              Update your personal information and contact details
            </p>
          </div>
          
          <div class="card-body">
            <form @submit.prevent="updateProfile">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <label for="first-name" class="form-label">First Name</label>
                  <input
                    id="first-name"
                    type="text"
                    v-model="profileForm.firstName"
                    class="form-input"
                    :class="{ 'border-red-300': errors.firstName }"
                    required
                  />
                  <p v-if="errors.firstName" class="mt-1 text-sm text-red-600">
                    {{ errors.firstName }}
                  </p>
                </div>
                
                <div>
                  <label for="last-name" class="form-label">Last Name</label>
                  <input
                    id="last-name"
                    type="text"
                    v-model="profileForm.lastName"
                    class="form-input"
                    :class="{ 'border-red-300': errors.lastName }"
                    required
                  />
                  <p v-if="errors.lastName" class="mt-1 text-sm text-red-600">
                    {{ errors.lastName }}
                  </p>
                </div>
                
                <div>
                  <label for="phone-number" class="form-label">Phone Number</label>
                  <input
                    id="phone-number"
                    type="tel"
                    v-model="profileForm.phoneNumber"
                    class="form-input bg-gray-50"
                    disabled
                  />
                  <p class="mt-1 text-sm text-gray-500">
                    Phone number cannot be changed
                  </p>
                </div>
                
                <div>
                  <label for="email" class="form-label">Email Address</label>
                  <input
                    id="email"
                    type="email"
                    v-model="profileForm.email"
                    class="form-input"
                    :class="{ 'border-red-300': errors.email }"
                  />
                  <p v-if="errors.email" class="mt-1 text-sm text-red-600">
                    {{ errors.email }}
                  </p>
                </div>
                
                <div>
                  <label for="language" class="form-label">Preferred Language</label>
                  <select
                    id="language"
                    v-model="profileForm.preferredLanguage"
                    class="form-input"
                  >
                    <option value="en">English</option>
                    <option value="sw">Swahili</option>
                    <option value="kikuyu">Kikuyu</option>
                  </select>
                </div>
                
                <div>
                  <label class="form-label">User Role</label>
                  <div class="mt-1 p-3 bg-gray-50 rounded-md">
                    <span class="text-sm font-medium text-gray-900 capitalize">
                      {{ user?.user_role }}
                    </span>
                    <p class="text-sm text-gray-500">
                      Your account type
                    </p>
                  </div>
                </div>
              </div>
              
              <div v-if="errors.general" class="mt-4 alert-error">
                {{ errors.general }}
              </div>
              
              <div v-if="successMessage" class="mt-4 alert-success">
                {{ successMessage }}
              </div>
              
              <div class="mt-6">
                <button
                  type="submit"
                  :disabled="updatingProfile"
                  class="btn-primary"
                >
                  <span v-if="updatingProfile">Updating...</span>
                  <span v-else>Update Profile</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Notification Preferences -->
        <div class="card">
          <div class="card-header">
            <h2 class="text-lg font-medium text-gray-900">Notification Preferences</h2>
            <p class="mt-1 text-sm text-gray-500">
              Choose how you want to receive notifications
            </p>
          </div>
          
          <div class="card-body">
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">SMS Notifications</h3>
                  <p class="text-sm text-gray-500">Receive notifications via SMS</p>
                </div>
                <button
                  @click="toggleNotification('smsNotifications')"
                  :class="profileForm.smsNotifications ? 'bg-green-600' : 'bg-gray-200'"
                  class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                >
                  <span
                    :class="profileForm.smsNotifications ? 'translate-x-5' : 'translate-x-0'"
                    class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                  ></span>
                </button>
              </div>
              
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">Email Notifications</h3>
                  <p class="text-sm text-gray-500">Receive notifications via email</p>
                </div>
                <button
                  @click="toggleNotification('emailNotifications')"
                  :class="profileForm.emailNotifications ? 'bg-green-600' : 'bg-gray-200'"
                  class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                >
                  <span
                    :class="profileForm.emailNotifications ? 'translate-x-5' : 'translate-x-0'"
                    class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                  ></span>
                </button>
              </div>
              
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">Order Updates</h3>
                  <p class="text-sm text-gray-500">Get notified about order status changes</p>
                </div>
                <button
                  @click="toggleNotification('orderUpdates')"
                  :class="profileForm.orderUpdates ? 'bg-green-600' : 'bg-gray-200'"
                  class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                >
                  <span
                    :class="profileForm.orderUpdates ? 'translate-x-5' : 'translate-x-0'"
                    class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                  ></span>
                </button>
              </div>
              
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">Marketing Messages</h3>
                  <p class="text-sm text-gray-500">Receive promotional offers and updates</p>
                </div>
                <button
                  @click="toggleNotification('marketingNotifications')"
                  :class="profileForm.marketingNotifications ? 'bg-green-600' : 'bg-gray-200'"
                  class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                >
                  <span
                    :class="profileForm.marketingNotifications ? 'translate-x-5' : 'translate-x-0'"
                    class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                  ></span>
                </button>
              </div>
              
              <!-- Farmer-specific notifications -->
              <div v-if="user?.user_role === 'farmer'" class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">Weather Alerts</h3>
                  <p class="text-sm text-gray-500">Get weather-related farming alerts</p>
                </div>
                <button
                  @click="toggleNotification('weatherAlerts')"
                  :class="profileForm.weatherAlerts ? 'bg-green-600' : 'bg-gray-200'"
                  class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                >
                  <span
                    :class="profileForm.weatherAlerts ? 'translate-x-5' : 'translate-x-0'"
                    class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                  ></span>
                </button>
              </div>
              
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">Price Alerts</h3>
                  <p class="text-sm text-gray-500">Get notified about price changes</p>
                </div>
                <button
                  @click="toggleNotification('priceAlerts')"
                  :class="profileForm.priceAlerts ? 'bg-green-600' : 'bg-gray-200'"
                  class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                >
                  <span
                    :class="profileForm.priceAlerts ? 'translate-x-5' : 'translate-x-0'"
                    class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                  ></span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Change Password -->
        <div class="card">
          <div class="card-header">
            <h2 class="text-lg font-medium text-gray-900">Change Password</h2>
            <p class="mt-1 text-sm text-gray-500">
              Update your password to keep your account secure
            </p>
          </div>
          
          <div class="card-body">
            <form @submit.prevent="changePassword">
              <div class="space-y-4">
                <div>
                  <label for="old-password" class="form-label">Current Password</label>
                  <input
                    id="old-password"
                    type="password"
                    v-model="passwordForm.oldPassword"
                    class="form-input"
                    :class="{ 'border-red-300': passwordErrors.oldPassword }"
                    required
                  />
                  <p v-if="passwordErrors.oldPassword" class="mt-1 text-sm text-red-600">
                    {{ passwordErrors.oldPassword }}
                  </p>
                </div>
                
                <div>
                  <label for="new-password" class="form-label">New Password</label>
                  <input
                    id="new-password"
                    type="password"
                    v-model="passwordForm.newPassword"
                    class="form-input"
                    :class="{ 'border-red-300': passwordErrors.newPassword }"
                    required
                  />
                  <p v-if="passwordErrors.newPassword" class="mt-1 text-sm text-red-600">
                    {{ passwordErrors.newPassword }}
                  </p>
                </div>
                
                <div>
                  <label for="confirm-password" class="form-label">Confirm New Password</label>
                  <input
                    id="confirm-password"
                    type="password"
                    v-model="passwordForm.confirmPassword"
                    class="form-input"
                    :class="{ 'border-red-300': passwordErrors.confirmPassword }"
                    required
                  />
                  <p v-if="passwordErrors.confirmPassword" class="mt-1 text-sm text-red-600">
                    {{ passwordErrors.confirmPassword }}
                  </p>
                </div>
              </div>
              
              <div v-if="passwordErrors.general" class="mt-4 alert-error">
                {{ passwordErrors.general }}
              </div>
              
              <div v-if="passwordSuccessMessage" class="mt-4 alert-success">
                {{ passwordSuccessMessage }}
              </div>
              
              <div class="mt-6">
                <button
                  type="submit"
                  :disabled="changingPassword"
                  class="btn-primary"
                >
                  <span v-if="changingPassword">Changing Password...</span>
                  <span v-else>Change Password</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { user, updateProfile, changePassword as changeUserPassword } from '@/stores/auth'

export default {
  name: 'ProfilePage',
  setup() {
    const updatingProfile = ref(false)
    const changingPassword = ref(false)
    const successMessage = ref('')
    const passwordSuccessMessage = ref('')
    
    const profileForm = reactive({
      firstName: '',
      lastName: '',
      phoneNumber: '',
      email: '',
      preferredLanguage: 'sw',
      smsNotifications: true,
      emailNotifications: true,
      orderUpdates: true,
      marketingNotifications: false,
      weatherAlerts: true,
      priceAlerts: true
    })
    
    const passwordForm = reactive({
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const errors = reactive({
      firstName: '',
      lastName: '',
      email: '',
      general: ''
    })
    
    const passwordErrors = reactive({
      oldPassword: '',
      newPassword: '',
      confirmPassword: '',
      general: ''
    })
    
    // Initialize form with user data
    onMounted(() => {
      if (user.value) {
        profileForm.firstName = user.value.first_name || ''
        profileForm.lastName = user.value.last_name || ''
        profileForm.phoneNumber = user.value.phone_number || ''
        profileForm.email = user.value.email || ''
        profileForm.preferredLanguage = user.value.preferred_language || 'sw'
        profileForm.smsNotifications = user.value.sms_notifications ?? true
        profileForm.emailNotifications = user.value.email_notifications ?? true
        profileForm.orderUpdates = user.value.order_updates ?? true
        profileForm.marketingNotifications = user.value.marketing_notifications ?? false
        profileForm.weatherAlerts = user.value.weather_alerts ?? true
        profileForm.priceAlerts = user.value.price_alerts ?? true
      }
    })
    
    const validateProfileForm = () => {
      // Clear previous errors
      Object.keys(errors).forEach(key => {
        errors[key] = ''
      })
      
      let isValid = true
      
      if (!profileForm.firstName.trim()) {
        errors.firstName = 'First name is required'
        isValid = false
      }
      
      if (!profileForm.lastName.trim()) {
        errors.lastName = 'Last name is required'
        isValid = false
      }
      
      if (profileForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profileForm.email)) {
        errors.email = 'Please enter a valid email address'
        isValid = false
      }
      
      return isValid
    }
    
    const updateUserProfile = async () => {
      if (!validateProfileForm()) return
      
      updatingProfile.value = true
      successMessage.value = ''
      
      try {
        const updateData = {
          first_name: profileForm.firstName.trim(),
          last_name: profileForm.lastName.trim(),
          email: profileForm.email || null,
          preferred_language: profileForm.preferredLanguage,
          sms_notifications: profileForm.smsNotifications,
          email_notifications: profileForm.emailNotifications,
          order_updates: profileForm.orderUpdates,
          marketing_notifications: profileForm.marketingNotifications,
          weather_alerts: profileForm.weatherAlerts,
          price_alerts: profileForm.priceAlerts
        }
        
        const result = await updateProfile(updateData)
        
        if (result.success) {
          successMessage.value = 'Profile updated successfully!'
          setTimeout(() => {
            successMessage.value = ''
          }, 3000)
        } else {
          errors.general = result.error
        }
      } catch (error) {
        errors.general = 'Failed to update profile'
      } finally {
        updatingProfile.value = false
      }
    }
    
    const validatePasswordForm = () => {
      // Clear previous errors
      Object.keys(passwordErrors).forEach(key => {
        passwordErrors[key] = ''
      })
      
      let isValid = true
      
      if (!passwordForm.oldPassword) {
        passwordErrors.oldPassword = 'Current password is required'
        isValid = false
      }
      
      if (!passwordForm.newPassword) {
        passwordErrors.newPassword = 'New password is required'
        isValid = false
      } else if (passwordForm.newPassword.length < 8) {
        passwordErrors.newPassword = 'Password must be at least 8 characters long'
        isValid = false
      }
      
      if (passwordForm.newPassword !== passwordForm.confirmPassword) {
        passwordErrors.confirmPassword = 'Passwords do not match'
        isValid = false
      }
      
      return isValid
    }
    
    const changeUserPasswordHandler = async () => {
      if (!validatePasswordForm()) return
      
      changingPassword.value = true
      passwordSuccessMessage.value = ''
      
      try {
        const result = await changeUserPassword({
          old_password: passwordForm.oldPassword,
          new_password: passwordForm.newPassword
        })
        
        if (result.success) {
          passwordSuccessMessage.value = 'Password changed successfully!'
          // Clear form
          passwordForm.oldPassword = ''
          passwordForm.newPassword = ''
          passwordForm.confirmPassword = ''
          
          setTimeout(() => {
            passwordSuccessMessage.value = ''
          }, 3000)
        } else {
          passwordErrors.general = result.error
        }
      } catch (error) {
        passwordErrors.general = 'Failed to change password'
      } finally {
        changingPassword.value = false
      }
    }
    
    const toggleNotification = (field) => {
      profileForm[field] = !profileForm[field]
      // Auto-save notification preferences
      updateUserProfile()
    }
    
    return {
      user,
      profileForm,
      passwordForm,
      errors,
      passwordErrors,
      updatingProfile,
      changingPassword,
      successMessage,
      passwordSuccessMessage,
      
      // Methods
      updateProfile: updateUserProfile,
      changePassword: changeUserPasswordHandler,
      toggleNotification
    }
  }
}
</script> 