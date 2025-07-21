<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center">
    <div class="relative mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
      <div class="text-center">
        <h3 class="text-lg leading-6 font-medium text-gray-900">{{ isEditMode ? 'Edit' : 'Create' }} Category</h3>
        <div class="mt-2 px-7 py-3">
          <form @submit.prevent="submitForm">
            <div class="mb-4">
              <label for="category_name" class="block text-sm font-medium text-gray-700 text-left">Category Name</label>
              <input type="text" id="category_name" v-model="form.category_name" required class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            </div>
            <div class="mb-4">
              <label for="parent_category" class="block text-sm font-medium text-gray-700 text-left">Parent Category</label>
              <select id="parent_category" v-model="form.parent_category" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                <option :value="null">-- No Parent --</option>
                <option v-for="category in categories" :key="category.category_id" :value="category.category_id">
                  {{ category.category_name }}
                </option>
              </select>
            </div>
            <div class="mb-4">
              <label for="description" class="block text-sm font-medium text-gray-700 text-left">Description</label>
              <textarea id="description" v-model="form.description" rows="3" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"></textarea>
            </div>
            <div class="mb-4 flex items-center">
              <input type="checkbox" id="is_active" v-model="form.is_active" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
              <label for="is_active" class="ml-2 block text-sm text-gray-900">Active</label>
            </div>
            <div class="items-center px-4 py-3">
              <button type="button" @click="$emit('close')" class="px-4 py-2 bg-gray-500 text-white text-base font-medium rounded-md w-auto shadow-sm hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500">
                Cancel
              </button>
              <button type="submit" class="ml-3 px-4 py-2 bg-blue-600 text-white text-base font-medium rounded-md w-auto shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                {{ isEditMode ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import { productsAPI } from '@/services/api';

const props = defineProps({
  category: Object,
  isEditMode: Boolean,
});

const emit = defineEmits(['close', 'save']);

const form = reactive({
  category_name: '',
  parent_category: null,
  description: '',
  is_active: true,
});

const categories = ref([]);

onMounted(async () => {
  try {
    const response = await productsAPI.getCategories();
    categories.value = response.results || response;
  } catch (error) {
    console.error('Failed to load categories:', error);
  }
});

watch(() => props.category, (newVal) => {
  if (newVal && props.isEditMode) {
    form.category_name = newVal.category_name;
    form.parent_category = newVal.parent_category;
    form.description = newVal.description;
    form.is_active = newVal.is_active;
  } else {
    form.category_name = '';
    form.parent_category = null;
    form.description = '';
    form.is_active = true;
  }
}, { immediate: true });

const submitForm = () => {
  emit('save', { ...form });
};
</script>
