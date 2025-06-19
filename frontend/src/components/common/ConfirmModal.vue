<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3 text-center">
        <!-- Icon -->
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
          <ExclamationTriangleIcon class="h-6 w-6 text-red-600" />
        </div>
        
        <!-- Title -->
        <h3 class="text-lg leading-6 font-medium text-gray-900 mt-4">
          {{ title }}
        </h3>
        
        <!-- Message -->
        <div class="mt-2 px-7 py-3">
          <p class="text-sm text-gray-500">
            {{ message }}
          </p>
        </div>
        
        <!-- Buttons -->
        <div class="flex justify-center space-x-3 px-4 py-3">
          <button
            @click="$emit('cancel')"
            class="px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Cancel
          </button>
          <button
            @click="$emit('confirm')"
            class="px-4 py-2 bg-red-600 text-white border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineEmits } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  title: {
    type: String,
    default: 'Confirm Action'
  },
  message: {
    type: String,
    default: 'Are you sure you want to perform this action?'
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  }
})

defineEmits(['confirm', 'cancel'])
</script> 