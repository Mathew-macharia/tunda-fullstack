<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto h-28 w-28 flex items-center justify-center">
          <img 
            src="@/assets/illustrations/login.svg" 
            alt="Login Illustration" 
            class="h-28 w-28 object-contain"
            @error="handleImageError"
          />
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold">
          <span class="text-primary">Welcome Back to </span>
          <span class="text-orange-400">Tunda!</span>
        </h2>
        <p class="mt-2 text-center text-sm text-primary">
          Sign in to access fresh produce  🥕
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="space-y-4">
          <div>
            <label for="phone-number" class="form-label">Phone Number</label>
            <input
              id="phone-number"
              name="phone-number"
              type="tel"
              autocomplete="tel"
              required
              v-model="form.phoneNumber"
              class="form-input"
              :class="{ 'border-red-300 focus:border-red-500 focus:ring-red-500': errors.phoneNumber }"
              placeholder="e.g., +254700000000"
            />
            <p v-if="errors.phoneNumber" class="mt-1 text-sm text-red-600">
              {{ errors.phoneNumber }}
            </p>
          </div>
          
          <div>
            <label for="password" class="form-label">Password</label>
            <div class="relative">
              <input
                id="password"
                name="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                required
                v-model="form.password"
                class="form-input pr-10"
                :class="{ 'border-red-300 focus:border-red-500 focus:ring-red-500': errors.password }"
                placeholder="Enter your password"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              >
                <svg v-if="showPassword" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L8.464 8.464M9.878 9.878L7.036 7.036m10.608 10.608l1.414 1.414M14.146 14.146L12 12m2.146 2.146L16.5 16.5M12 12L9 9"></path>
                </svg>
                <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                </svg>
              </button>
            </div>
            <p v-if="errors.password" class="mt-1 text-sm text-red-600">
              {{ errors.password }}
            </p>
          </div>
        </div>

        <div v-if="errors.general" class="rounded-lg bg-orange-50 border border-orange-200 p-4">
          <div class="flex items-start space-x-3">
            <svg class="h-5 w-5 text-orange-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
            </svg>
            <div class="flex-1">
              <h3 class="text-sm font-medium text-orange-800">Oops! We couldn't log you in</h3>
              <p class="mt-2 text-sm text-orange-700">Please double-check your phone number and password, or create a new account if you're new here.</p>
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-darkGreen focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            </span>
            {{ isLoading ? 'Signing in...' : 'Sign in' }}
          </button>
        </div>

        <div class="text-center">
          <span class="text-sm text-gray-600">
            Don't have an account?
            <router-link to="/register" class="font-medium text-primary hover:text-green-600">
              Sign up
            </router-link>
          </span>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { login, isLoading } from '@/stores/auth'

export default {
  name: 'LoginPage',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const showPassword = ref(false)
    
    const form = reactive({
      phoneNumber: '',
      password: ''
    })
    
    const errors = reactive({
      phoneNumber: '',
      password: '',
      general: ''
    })
    
    const validateForm = () => {
      // Clear previous errors
      Object.keys(errors).forEach(key => {
        errors[key] = ''
      })
      
      let isValid = true
      
      // Validate phone number
      if (!form.phoneNumber) {
        errors.phoneNumber = 'Phone number is required'
        isValid = false
      } else if (!/^\+?[1-9]\d{1,14}$/.test(form.phoneNumber.replace(/\s/g, ''))) {
        errors.phoneNumber = 'Please enter a valid phone number'
        isValid = false
      }
      
      // Validate password
      if (!form.password) {
        errors.password = 'Password is required'
        isValid = false
      } else if (form.password.length < 6) {
        errors.password = 'Password must be at least 6 characters'
        isValid = false
      }
      
      return isValid
    }
    
    const handleImageError = (event) => {
      // Fallback to the green circle with "T" if image fails to load
      const fallbackDiv = document.createElement('div')
      fallbackDiv.className = 'h-16 w-16 bg-green-600 rounded-full flex items-center justify-center'
      fallbackDiv.innerHTML = '<span class="text-white font-bold text-2xl">T</span>'
      event.target.parentNode.replaceChild(fallbackDiv, event.target)
    }
    
    const handleLogin = async () => {
      if (!validateForm()) return
      
      const result = await login(form.phoneNumber, form.password)
      
      if (result.success) {
        // Redirect based on user role or to intended page
        const redirectTo = route.query.redirect || getDashboardRoute(result.user.user_role)
        await router.push(redirectTo)
      } else {
        errors.general = result.error
      }
    }
    
    const getDashboardRoute = (role) => {
      const dashboardRoutes = {
        customer: '/customer',
        farmer: '/farmer',
        rider: '/rider',
        admin: '/admin'
      }
      return dashboardRoutes[role] || '/'
    }
    
    return {
      form,
      errors,
      showPassword,
      isLoading,
      handleLogin,
      handleImageError
    }
  }
}
</script>