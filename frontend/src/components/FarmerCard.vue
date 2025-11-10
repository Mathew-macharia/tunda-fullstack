<template>
  <div
    class="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
    @click="viewFarmer"
  >
    <!-- Farmer Avatar/Photo -->
    <div class="relative overflow-hidden rounded-t-2xl">
      <img
        v-if="farmer.profile_photo_url"
        :src="farmer.profile_photo_url"
        :alt="farmer.farmer_name"
        class="w-full h-40 sm:h-48 object-cover"
      />
      <div v-else class="w-full h-40 sm:h-48 bg-gray-200 flex items-center justify-center">
        <span class="text-gray-500 text-4xl font-bold">{{ getInitials(farmer.farmer_name) }}</span>
      </div>
      
      <!-- Verified Badge -->
      <div v-if="farmer.average_rating >= 4.5" class="absolute top-3 right-3">
        <span class="bg-green-600 text-white px-2.5 py-1 rounded-full text-xs font-medium shadow-sm flex items-center">
          <svg class="w-3 h-3 mr-1 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
          Verified
        </span>
      </div>
    </div>
    
    <!-- Farmer Info -->
    <div class="p-4">
      <h3 class="text-sm font-semibold text-gray-900 line-clamp-1 mb-2">
        {{ farmer.farmer_name }}
      </h3>
      
      <!-- Rating -->
      <div v-if="farmer.review_count > 0" class="flex items-center text-xs text-gray-600 mb-3">
        <svg class="h-3 w-3 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.538 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.783.57-1.838-.197-1.538-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.929 8.72c-.783-.57-.38-1.81.588-1.81h3.462a1 1 0 00.95-.69l1.07-3.292z"></path>
        </svg>
        <span class="font-medium mr-1">{{ farmer.average_rating ? farmer.average_rating.toFixed(1) : '0.0' }}</span>
        <span class="text-gray-400">•</span>
        <span class="ml-1">{{ farmer.review_count }} reviews</span>
      </div>
      
      <!-- Farmer Metrics -->
      <div class="space-y-2 text-xs text-gray-600">
        <div class="flex items-center justify-between">
          <span class="font-medium text-gray-900">Products:</span>
          <span>{{ farmer.product_count }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="font-medium text-gray-900">Active Listings:</span>
          <span>{{ farmer.active_listings_count }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="font-medium text-gray-900">Farms:</span>
          <span>{{ farmer.number_of_farms }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="font-medium text-gray-900">Orders Completed:</span>
          <span>{{ farmer.total_orders_completed }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const props = defineProps({
  farmer: {
    type: Object,
    required: true,
  },
});

const router = useRouter();

const getInitials = (name) => {
  if (!name) return '?';
  const parts = name.trim().split(' ');
  if (parts.length === 1) {
    return parts[0].charAt(0).toUpperCase();
  }
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
};

const viewFarmer = () => {
  router.push(`/farmers/${props.farmer.farmer_id}`);
};
</script>

<style scoped>
.line-clamp-1 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  line-clamp: 1;
}
</style>
