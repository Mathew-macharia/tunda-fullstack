import { ref } from 'vue'
import { isAuthenticated, isCustomer, addGuestCartItem } from '@/stores/auth'
import { cartAPI } from '@/services/api'

export function useCartActions() {
  const addingToCart = ref(null)
  const showNotification = ref(false)
  const notificationMessage = ref('')

  const addToCart = async (listing) => {
    addingToCart.value = listing.listing_id
    
    try {
      if (isAuthenticated.value && isCustomer.value) {
        await cartAPI.addToCart(listing.listing_id, listing.min_order_quantity || 1)
        console.log(`${listing.product_name} added to authenticated cart!`)
      } else {
        // Add to guest cart if not authenticated or not a customer
        addGuestCartItem(listing, listing.min_order_quantity || 1) // Pass the full listing object
        console.log(`${listing.product_name} added to guest cart!`)
      }
      
      window.dispatchEvent(new CustomEvent('cartUpdated'))
      
      notificationMessage.value = `${listing.product_name} added to cart!`
      showNotification.value = true
      setTimeout(() => {
        showNotification.value = false
      }, 3000) // Hide after 3 seconds
      
    } catch (error) {
      console.error('Failed to add to cart:', error)
      notificationMessage.value = 'Failed to add item to cart. Please try again.'
      showNotification.value = true
      setTimeout(() => {
        showNotification.value = false
      }, 3000) // Hide after 3 seconds
    } finally {
      addingToCart.value = null
    }
  }

  return {
    addingToCart,
    showNotification,
    notificationMessage,
    addToCart
  }
}
