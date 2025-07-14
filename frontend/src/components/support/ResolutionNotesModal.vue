<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-lg w-full">
      <div class="p-6">
        <h3 class="text-lg font-medium text-gray-900">Resolution Notes</h3>
        <div class="mt-4">
          <textarea
            v-model="resolutionNotes"
            rows="4"
            class="form-input w-full"
            placeholder="Enter resolution notes..."
          ></textarea>
        </div>
      </div>
      <div class="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
        <button @click="closeModal" type="button" class="btn-secondary">
          Cancel
        </button>
        <button @click="submitNotes" type="button" class="btn-primary">
          Submit
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
  }
})

const emit = defineEmits(['close', 'submit'])

const resolutionNotes = ref('')

const closeModal = () => {
  resolutionNotes.value = ''
  emit('close')
}

const submitNotes = () => {
  emit('submit', resolutionNotes.value)
  closeModal()
}
</script>
