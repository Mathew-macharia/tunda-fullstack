import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { productsAPI, farmsAPI } from '@/services/api'

export function useHomePageData() {
  const router = useRouter()

  // State
  const categories = ref([])
  const farmers = ref([])
  const freshPicks = ref([])
  const searchQuery = ref('') // Keeping search query here for now, can be moved if search becomes global
  
  // Loading states
  const loadingCategories = ref(false)
  const loadingFarmers = ref(false)
  const loadingFreshPicks = ref(false)

  // Image mapping for categories with SVG icons
  const categoryImages = {
    'dairy': 'dairy.svg',
    'fruits' : 'fruits.svg',
    'grains': 'grains.svg',
    'herbs and spices': 'herbs.svg',
    'honey and natural': 'honey.svg',
    'legumes': 'legumes.svg',
    'meat and poultry': 'meat.svg', // Assuming 'Meat and poultry' maps to 'meat.svg'
    'nuts and seeds': 'nuts.svg',
    'processed foods': 'processed_foods.svg',
    'vegetables': 'vegetables.svg',
    'default': 'default.svg' // Fallback default SVG icon
  }

  // Methods
  const getCategoryImage = (categoryName) => {
    const normalizedCategoryName = categoryName.toLowerCase().replace(/ & /g, ' and ');
    const imagePath = categoryImages[normalizedCategoryName] || categoryImages.default;
    return `/images/category_icon/${imagePath}`;
  }

  let searchTimeout = null; // Declare searchTimeout here
  const debouncedSearch = () => {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
      if (searchQuery.value.trim()) {
        router.push(`/products?search=${encodeURIComponent(searchQuery.value)}`)
      }
    }, 500)
  }

  const loadCategories = async () => {
    loadingCategories.value = true
    try {
      const response = await productsAPI.getCategories()
      categories.value = response.results || response
    } catch (error) {
      console.error('Failed to load categories:', error)
    } finally {
      loadingCategories.value = false
    }
  }
  
  const loadFarmers = async () => {
    loadingFarmers.value = true
    try {
      // Fetch all farmers, then slice to limit for homepage display
      const response = await farmsAPI.getFarms() // Corrected API call to farmsAPI.getFarms()
      // console.log('API Response for farmers (useHomePageData):', response); // Debugging line
      const farmerData = response.results || response;
      farmers.value = Array.isArray(farmerData) ? farmerData.slice(0, 6) : [];
      // console.log('Farmers after assignment (useHomePageData):', farmers.value); // Debugging line
    } catch (error) {
      console.error('Failed to load farmers:', error)
    } finally {
      loadingFarmers.value = false
    }
  }

  const getFarmerDisplayImage = (farmer) => {
    if (farmer.profile_photo_url) {
      return farmer.profile_photo_url;
    }
    // Fallback to a generic image if no profile photo
    // Using a relevant image from existing assets
    return '/images/categories/vegetables.webp'; 
  }
  
  const loadFreshPicks = async () => {
    loadingFreshPicks.value = true
    try {
      const response = await productsAPI.getListings({
        page_size: 10,
        listing_status: 'available',
        ordering: '-created_at'
      })
      
      if (response.results) {
        freshPicks.value = response.results
      } else if (Array.isArray(response)) {
        freshPicks.value = response.slice(0, 10)
      }
    } catch (error) {
      console.error('Failed to load fresh picks:', error)
    } finally {
      loadingFreshPicks.value = false
    }
  }

  const getStatusDisplay = (status) => {
    const statusMap = {
      'available': 'Available',
      'pre_order': 'Pre-order',
      'sold_out': 'Sold Out',
      'inactive': 'Inactive'
    }
    return statusMap[status] || status
  }
  
  const filterByCategory = (categoryId) => {
    router.push(`/products?category=${categoryId}`)
  }
  
  const filterByFarmer = (farmerId) => {
    // console.log('Navigating to farmer detail for ID:', farmerId); // Debugging line
    router.push(`/farmers/${farmerId}`)
  }
  
  const getInitials = (name) => {
    if (!name) return '?'
    const parts = name.trim().split(' ')
    if (parts.length === 1) {
      return parts[0].charAt(0).toUpperCase()
    }
    return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
  }
  
  const viewProduct = (listing) => {
    router.push(`/products/${listing.listing_id}`)
  }

  // New function to navigate to the farmer marketplace page
  const viewAllFarmers = () => {
    router.push('/farmers-marketplace');
  }

  // Lifecycle
  onMounted(() => {
    loadCategories()
    loadFarmers()
    loadFreshPicks()
  })

  return {
    categories,
    farmers,
    freshPicks,
    searchQuery,
    loadingCategories,
    loadingFarmers,
    loadingFreshPicks,
    getCategoryImage,
    debouncedSearch,
    getStatusDisplay,
    filterByCategory,
    filterByFarmer,
    getInitials,
    viewProduct,
    viewAllFarmers, // Expose new function
    loadCategories, // Expose for potential external refresh
    loadFarmers,
    loadFreshPicks,
    getFarmerDisplayImage // Expose new function
  }
}
