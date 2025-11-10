<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-3xl sm:text-4xl font-extrabold text-gray-900 text-center mb-8">
        Our Farmers
      </h1>

      <!-- Loading State -->
      <div v-if="loadingFarmers" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 sm:gap-6">
        <div v-for="n in 10" :key="n" class="bg-white rounded-2xl p-4 sm:p-6 shadow-sm animate-pulse">
          <div class="w-24 h-24 rounded-2xl bg-gray-200 mx-auto mb-3 sm:mb-4"></div>
          <div class="h-4 bg-gray-200 rounded mb-2"></div>
          <div class="h-3 bg-gray-200 rounded w-2/3 mx-auto"></div>
        </div>
      </div>

      <!-- Farmers Grid -->
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 sm:gap-6">
        <FarmerCard
          v-for="farmer in allFarmers"
          :key="farmer.farmer_id"
          :farmer="farmer"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { productsAPI, farmsAPI } from '@/services/api';
import { useHomePageData } from '@/composables/useHomePageData'; // Import the composable
import FarmerCard from '@/components/FarmerCard.vue'; // Import FarmerCard

const router = useRouter();
const allFarmers = ref([]);
const loadingFarmers = ref(false);

// Destructure functions from the composable
const { getInitials, getFarmerDisplayImage } = useHomePageData();

const loadAllFarmers = async () => {
  loadingFarmers.value = true;
  try {
    const response = await farmsAPI.getFarms(); // Fetch all farmers
    allFarmers.value = response.results || response;
  } catch (error) {
    console.error('Failed to load all farmers:', error);
  } finally {
    loadingFarmers.value = false;
  }
};

const viewFarmerDetail = (farmerId) => {
  router.push(`/farmers/${farmerId}`);
};

onMounted(() => {
  loadAllFarmers();
});
</script>

<style scoped>
.line-clamp-1 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  line-clamp: 1;
}

.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}
</style>
