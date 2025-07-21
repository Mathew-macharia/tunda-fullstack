<template>
  <transition
    enter-active-class="transition ease-out duration-300"
    enter-from-class="transform opacity-0 translate-y-full sm:translate-y-0 sm:translate-x-full"
    enter-to-class="transform opacity-100 translate-y-0 sm:translate-x-0"
    leave-active-class="transition ease-in duration-200"
    leave-from-class="transform opacity-100 translate-y-0 sm:translate-x-0"
    leave-to-class="transform opacity-0 translate-y-full sm:translate-y-0 sm:translate-x-full"
  >
    <div
      v-if="visible"
      :class="toastClasses"
      class="fixed bottom-4 right-4 sm:top-4 sm:right-4 text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center space-x-3"
    >
      <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path v-if="type === 'success'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        <path v-if="type === 'error'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        <path v-if="type === 'info'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <p class="font-medium">{{ message }}</p>
      <button @click="hide" class="ml-auto -mr-1 p-1 rounded-full hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white">
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  message: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    default: 'success', // success, error, info
  },
  duration: {
    type: Number,
    default: 3000,
  },
});

const visible = ref(false);

const toastClasses = computed(() => {
  switch (props.type) {
    case 'error':
      return 'bg-red-600';
    case 'info':
      return 'bg-blue-600';
    default:
      return 'bg-green-600';
  }
});

const show = () => {
  visible.value = true;
  setTimeout(() => {
    hide();
  }, props.duration);
};

const hide = () => {
  visible.value = false;
};

watch(() => props.message, (newMessage) => {
  if (newMessage) {
    show();
  }
});

defineExpose({ show, hide });
</script>
