<template>
  <div class="p-6 bg-gray-100 min-h-screen">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-800">Product Category Management</h1>
      <button @click="openCreateModal" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-300">
        Add New Category
      </button>
    </div>

    <!-- Categories List -->
    <div class="bg-white shadow-lg rounded-lg p-6">
      <div v-if="loading" class="text-center py-10">
        <p class="text-gray-500">Loading categories...</p>
      </div>
      <div v-else-if="error" class="text-center py-10">
        <p class="text-red-500">{{ error }}</p>
      </div>
      <div v-else>
        <ul class="space-y-4">
          <li v-for="category in categories" :key="category.category_id" class="p-4 border rounded-lg hover:bg-gray-50 transition duration-200">
            <div class="flex justify-between items-center">
              <div>
                <p class="font-semibold text-lg text-gray-800">{{ category.category_name }}</p>
                <p class="text-sm text-gray-600">{{ category.description }}</p>
                <p class="text-xs text-gray-400 mt-1">Parent: {{ category.parent_category_name || 'None' }}</p>
              </div>
              <div class="flex items-center space-x-3">
                <span :class="category.is_active ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'" class="px-3 py-1 rounded-full text-sm font-medium">
                  {{ category.is_active ? 'Active' : 'Inactive' }}
                </span>
                <button @click="openEditModal(category)" class="text-blue-500 hover:text-blue-700 transition duration-200">
                  Edit
                </button>
                <button @click="openConfirmDeleteModal(category)" class="text-red-500 hover:text-red-700 transition duration-200">
                  Delete
                </button>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- Category Modal -->
    <ProductCategoryModal
      v-if="isModalOpen"
      :is-edit-mode="isEditMode"
      :category="selectedCategory"
      @close="closeModal"
      @save="handleSave"
    />

    <!-- Confirm Delete Modal -->
    <ConfirmModal
      :is-open="isConfirmDeleteModalOpen"
      title="Delete Category"
      :message="`Are you sure you want to delete the category '${categoryToDelete?.category_name}'? This action cannot be undone.`"
      @close="closeConfirmDeleteModal"
      @confirm="deleteCategory"
    />

    <!-- Toast Notification -->
    <ToastNotification
      ref="toast"
      :message="toastMessage"
      :type="toastType"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { productsAPI } from '@/services/api';
import ProductCategoryModal from '@/components/admin/ProductCategoryModal.vue';
import ConfirmModal from '@/components/common/ConfirmModal.vue';
import ToastNotification from '@/components/common/ToastNotification.vue';

const categories = ref([]);
const loading = ref(false);
const error = ref(null);
const isModalOpen = ref(false);
const isEditMode = ref(false);
const selectedCategory = ref(null);
const isConfirmDeleteModalOpen = ref(false);
const categoryToDelete = ref(null);
const toast = ref(null);
const toastMessage = ref('');
const toastType = ref('success');

const fetchCategories = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await productsAPI.getCategories();
    categories.value = response.results || response;
  } catch (err) {
    error.value = 'Failed to load categories. Please try again.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchCategories);

const openCreateModal = () => {
  isEditMode.value = false;
  selectedCategory.value = null;
  isModalOpen.value = true;
};

const openEditModal = (category) => {
  isEditMode.value = true;
  selectedCategory.value = { ...category };
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  selectedCategory.value = null;
};

const handleSave = async (formData) => {
  try {
    if (isEditMode.value) {
      await productsAPI.updateCategory(selectedCategory.value.category_id, formData);
      showToast('Category updated successfully.', 'success');
    } else {
      await productsAPI.createCategory(formData);
      showToast('Category created successfully.', 'success');
    }
    fetchCategories();
    closeModal();
  } catch (err) {
    console.error('Failed to save category:', err);
    showToast('Failed to save category. Please try again.', 'error');
  }
};

const openConfirmDeleteModal = (category) => {
  categoryToDelete.value = category;
  isConfirmDeleteModalOpen.value = true;
};

const closeConfirmDeleteModal = () => {
  isConfirmDeleteModalOpen.value = false;
  categoryToDelete.value = null;
};

const deleteCategory = async () => {
  if (!categoryToDelete.value) return;
  try {
    await productsAPI.deleteCategory(categoryToDelete.value.category_id);
    fetchCategories();
    showToast('Category deleted successfully.', 'success');
  } catch (err) {
    console.error('Failed to delete category:', err);
    showToast('Failed to delete category. It might be in use.', 'error');
  } finally {
    closeConfirmDeleteModal();
  }
};

const showToast = (message, type = 'success') => {
  toastMessage.value = message;
  toastType.value = type;
  toast.value.show();
};
</script>
