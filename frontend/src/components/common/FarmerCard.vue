<template>
  <div 
    class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-all duration-300 cursor-pointer border border-gray-100"
    @click="handleClick"
  >
    <!-- Farmer Photo Section -->
    <div class="relative h-40 bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center">
      <img 
        v-if="farmer.profile_photo_url" 
        :src="farmer.profile_photo_url" 
        :alt="farmer.farmer_name"
        class="h-32 w-32 rounded-full object-cover border-4 border-white shadow-lg"
      />
      <div 
        v-else 
        class="h-32 w-32 rounded-full bg-green-600 flex items-center justify-center border-4 border-white shadow-lg"
      >
        <span class="text-3xl font-bold text-white">{{ getInitials(farmer.farmer_name) }}</span>
      </div>
      
      <!-- Organic Badge -->
      <div 
        v-if="showOrganicBadge && farmer.organic_products > 0" 
        class="absolute top-2 right-2 bg-green-600 text-white text-xs px-2 py-1 rounded-full flex items-center space-x-1"
      >
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <span>Organic</span>
      </div>
    </div>

    <!-- Farmer Info Section -->
    <div class="p-4">
      <!-- Farmer Name -->
      <h3 class="text-lg font-bold text-gray-900 mb-1 truncate">{{ farmer.farmer_name }}</h3>
      
      <!-- Location -->
      <div v-if="farmer.primary_location" class="flex items-center text-sm text-gray-600 mb-2">
        <svg class="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span class="truncate">{{ farmer.primary_location }}</span>
      </div>

      <!-- Rating -->
      <div class="flex items-center mb-3">
        <div class="flex items-center">
          <svg 
            v-for="star in 5" 
            :key="star"
            class="w-4 h-4"
            :class="star <= Math.round(farmer.average_rating) ? 'text-yellow-400' : 'text-gray-300'"
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        </div>
        <span class="ml-2 text-sm text-gray-600">
          {{ farmer.average_rating > 0 ? farmer.average_rating.toFixed(1) : 'New' }}
          <span v-if="farmer.review_count > 0" class="text-gray-400">({{ farmer.review_count }})</span>
        </span>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 gap-2 pt-3 border-t border-gray-100">
        <div class="text-center">
          <div class="text-lg font-bold text-green-600">{{ farmer.active_listings_count || farmer.total_products || 0 }}</div>
          <div class="text-xs text-gray-500">Products</div>
        </div>
        <div v-if="farmer.farms_count !== undefined" class="text-center">
          <div class="text-lg font-bold text-green-600">{{ farmer.farms_count || 0 }}</div>
          <div class="text-xs text-gray-500">Farms</div>
        </div>
        <div v-else-if="farmer.match_score !== undefined" class="text-center">
          <div class="text-lg font-bold text-blue-600">{{ farmer.match_score }}</div>
          <div class="text-xs text-gray-500">Match</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FarmerCard',
  props: {
    farmer: {
      type: Object,
      required: true
    },
    showOrganicBadge: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    getInitials(name) {
      if (!name) return '?'
      const parts = name.trim().split(' ')
      if (parts.length === 1) {
        return parts[0].charAt(0).toUpperCase()
      }
      return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
    },
    handleClick() {
      this.$emit('farmer-click', this.farmer.farmer_id)
    }
  }
}
</script>

<style scoped>
/* Any additional custom styles can go here */
</style>

