<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-lg w-full">
      <div class="p-6">
        <h3 class="text-lg font-medium text-gray-900">Assign Ticket</h3>
        <div class="mt-4">
          <select v-model="selectedAdmin" class="form-input w-full">
            <option value="">Select an admin</option>
            <option v-for="admin in admins" :key="admin.user_id" :value="admin.user_id">
              {{ admin.first_name }} {{ admin.last_name }}
            </option>
          </select>
        </div>
      </div>
      <div class="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
        <button @click="closeModal" type="button" class="btn-secondary">
          Cancel
        </button>
        <button @click="submitAssignment" type="button" class="btn-primary">
          Assign
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  admins: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'submit'])

const selectedAdmin = ref('')

const closeModal = () => {
  selectedAdmin.value = ''
  emit('close')
}

const submitAssignment = () => {
  emit('submit', selectedAdmin.value)
  closeModal()
}
</script>
