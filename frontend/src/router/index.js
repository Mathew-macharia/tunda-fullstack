import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated, hasRole, isCustomer, isFarmer, isRider, isAdmin, user, logout, isInitialized, initializeAuth } from '@/stores/auth'

// Lazy load components for better performance
const HomePage = () => import('@/views/HomePage.vue')
const LoginPage = () => import('@/views/auth/LoginPage.vue')
const RegisterPage = () => import('@/views/auth/RegisterPage.vue')
const ProfilePage = () => import('@/views/ProfilePage.vue')

// Common pages
const NotificationsPage = () => import('@/views/common/NotificationsPage.vue')

// Support pages
const CustomerSupportPage = () => import('@/views/customer/SupportPage.vue')
const FarmerSupportPage = () => import('@/views/farmer/SupportPage.vue')
const RiderSupportPage = () => import('@/views/rider/SupportPage.vue')

// Customer pages
const CustomerDashboard = () => import('@/views/customer/CustomerDashboard.vue')
const ProductsPage = () => import('@/views/customer/ProductsPage.vue')
const ProductDetail = () => import('@/views/customer/ProductDetail.vue')
const FarmerDetailPage = () => import('@/views/customer/FarmerDetailPage.vue')
const CartPage = () => import('@/views/customer/CartPage.vue')
const CheckoutPage = () => import('@/views/customer/CheckoutPage.vue')
const OrdersPage = () => import('@/views/customer/OrdersPage.vue')
const OrderDetail = () => import('@/views/customer/OrderDetail.vue')
const ReviewsPage = () => import('@/views/customer/ReviewsPage.vue')

// Farmer pages
const FarmerDashboard = () => import('@/views/farmer/FarmerDashboard.vue')
const FarmsPage = () => import('@/views/farmer/FarmsPage.vue')
const FarmDetail = () => import('@/views/farmer/FarmDetail.vue')
const ProductListingsPage = () => import('@/views/farmer/ProductListingsPage.vue')
const ProductListingCreatePage = () => import('@/views/farmer/ProductListingCreatePage.vue')
const FarmerOrdersPage = () => import('@/views/farmer/FarmerOrdersPage.vue')
const MarketInsightsPage = () => import('@/views/farmer/MarketInsightsPage.vue')
const PayoutsPage = () => import('@/views/farmer/PayoutsPage.vue')

// Rider pages
const RiderDashboard = () => import('@/views/rider/RiderDashboard.vue')
const DeliveriesPage = () => import('@/views/rider/DeliveriesPage.vue')
const DeliveryDetail = () => import('@/views/rider/DeliveryDetail.vue')

// Admin pages
const AdminDashboard = () => import('@/views/admin/AdminDashboard.vue')
const UsersManagement = () => import('@/views/admin/UsersManagement.vue')
const OrdersManagement = () => import('@/views/admin/OrdersManagement.vue')
const DeliveriesManagement = () => import('@/views/admin/DeliveriesManagement.vue')
const SystemSettings = () => import('@/views/admin/SystemSettings.vue')
const ReviewsManagement = () => import('@/views/admin/ReviewsManagement.vue')
const PayoutsManagement = () => import('@/views/admin/PayoutsManagement.vue')
const SupportManagement = () => import('@/views/admin/SupportManagement.vue')
const ProductCategoriesManagement = () => import('@/views/admin/ProductCategoriesManagement.vue')

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: { 
      title: 'Tunda - Eat fresh, live healthy!', 
      description: 'Your one-stop shop for fresh, locally sourced produce. Connecting farmers directly to consumers for quality and convenience.' 
    },
    beforeEnter: (to, from, next) => {
      // Redirect non-customer users to their respective dashboards
      if (isAuthenticated.value) {
        if (isFarmer.value) {
          next('/farmer')
        } else if (isRider.value) {
          next('/rider')
        } else if (isAdmin.value) {
          next('/admin')
        } else {
          next() // Allow customers and guests to access homepage
        }
      } else {
        next() // Allow unauthenticated users to access homepage
      }
    }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { 
      requiresGuest: true,
      title: 'Login to Tunda App',
      description: 'Log in to your Tunda App account to manage orders, products, and more.'
    }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
    meta: { 
      requiresGuest: true,
      title: 'Register for Tunda App',
      description: 'Create a new account on Tunda App to start buying or selling fresh produce.'
    }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfilePage,
    meta: { 
      requiresAuth: true,
      title: 'User Profile - Tunda App',
      description: 'Manage your Tunda App profile, update personal information, and view account details.'
    }
  },

  // Common pages
  {
    path: '/notifications',
    name: 'notifications',
    component: NotificationsPage,
    meta: { 
      requiresAuth: true,
      title: 'Notifications - Tunda App',
      description: 'View your latest notifications and alerts from Tunda App.'
    }
  },

  // Support pages
  {
    path: '/support',
    name: 'customer-support',
    component: CustomerSupportPage,
    meta: { 
      requiresAuth: true, 
      roles: ['customer'],
      title: 'Customer Support - Tunda App',
      description: 'Get help and support for your Tunda App customer account.'
    }
  },

  // Customer routes
  {
    path: '/customer',
    name: 'customer-dashboard',
    component: CustomerDashboard,
    meta: { 
      requiresAuth: true, 
      roles: ['customer'],
      title: 'Customer Dashboard - Tunda App',
      description: 'Access your personalized customer dashboard on Tunda App.'
    }
  },
  {
    path: '/products',
    name: 'products',
    component: ProductsPage,
    meta: {
      title: 'Products - Tunda App',
      description: 'Browse a wide range of fresh produce available on Tunda App.'
    },
    beforeEnter: (to, from, next) => {
      // Block access for non-customer authenticated users
      if (isAuthenticated.value && (!isCustomer.value || isFarmer.value || isRider.value || isAdmin.value)) {
        console.log('Redirecting from products - Role:', { 
          isCustomer: isCustomer.value, 
          isFarmer: isFarmer.value, 
          isRider: isRider.value, 
          isAdmin: isAdmin.value 
        })
        if (isFarmer.value) {
          return next('/farmer')
        } else if (isRider.value) {
          return next('/rider')
        } else if (isAdmin.value) {
          return next('/admin')
        }
        return next('/')
      }
      next()
    }
  },
  {
    path: '/products/:id',
    name: 'product-detail',
    component: ProductDetail,
    meta: {
      title: 'Product Details - Tunda App',
      description: 'View detailed information about a specific product on Tunda App.'
    },
    beforeEnter: (to, from, next) => {
      // Block access for non-customer authenticated users
      if (isAuthenticated.value && (!isCustomer.value || isFarmer.value || isRider.value || isAdmin.value)) {
        if (isFarmer.value) {
          return next('/farmer')
        } else if (isRider.value) {
          return next('/rider')
        } else if (isAdmin.value) {
          return next('/admin')
        }
        return next('/')
      }
      next()
    }
  },
  {
    path: '/farmers/:id',
    name: 'farmer-detail',
    component: FarmerDetailPage,
    meta: {
      title: 'Farmer Profile - Tunda App',
      description: 'View farmer profile and products on Tunda App.'
    },
    beforeEnter: (to, from, next) => {
      // Block access for non-customer authenticated users
      if (isAuthenticated.value && (!isCustomer.value || isFarmer.value || isRider.value || isAdmin.value)) {
        if (isFarmer.value) {
          return next('/farmer')
        } else if (isRider.value) {
          return next('/rider')
        } else if (isAdmin.value) {
          return next('/admin')
        }
        return next('/')
      }
      next()
    }
  },
  {
    path: '/cart',
    name: 'cart',
    component: CartPage,
    meta: {
      title: 'Shopping Cart - Tunda App',
      description: 'Review items in your Tunda App shopping cart before checkout.'
    }
    // Removed meta: { requiresAuth: true, roles: ['customer'] } to allow guest access
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: CheckoutPage,
    meta: { 
      requiresAuth: true, 
      roles: ['customer'],
      title: 'Checkout - Tunda App',
      description: 'Complete your purchase on Tunda App with secure checkout.'
    }
  },
  {
    path: '/orders',
    name: 'orders',
    component: OrdersPage,
    meta: { 
      requiresAuth: true, 
      roles: ['customer'],
      title: 'My Orders - Tunda App',
      description: 'View your past and current orders on Tunda App.'
    }
  },
  {
    path: '/orders/:id',
    name: 'order-detail',
    component: OrderDetail,
    meta: { 
      requiresAuth: true, 
      roles: ['customer'],
      title: 'Order Details - Tunda App',
      description: 'View detailed information about a specific order on Tunda App.'
    }
  },
  {
    path: '/reviews',
    name: 'reviews',
    component: ReviewsPage,
    meta: { 
      requiresAuth: true, 
      roles: ['customer'],
      title: 'My Reviews - Tunda App',
      description: 'Manage and view your product reviews on Tunda App.'
    }
  },

  // Farmer routes
  {
    path: '/farmer',
    name: 'farmer-dashboard',
    component: FarmerDashboard,
    meta: { 
      requiresAuth: true, 
      roles: ['farmer'],
      title: 'Farmer Dashboard - Tunda App',
      description: 'Access your personalized farmer dashboard on Tunda App.'
    }
  },
  {
    path: '/farmer/farms',
    name: 'farms',
    component: FarmsPage,
    meta: { 
      requiresAuth: true, 
      roles: ['farmer'],
      title: 'My Farms - Tunda App',
      description: 'Manage your farm details and locations on Tunda App.'
    }
  },
  {
    path: '/farmer/farms/:id',
    name: 'farm-detail',
    component: FarmDetail,
    meta: { 
      requiresAuth: true, 
      roles: ['farmer'],
      title: 'Farm Details - Tunda App',
      description: 'View detailed information about a specific farm on Tunda App.'
    }
  },
  {
    path: '/farmer/listings',
    name: 'product-listings',
    component: ProductListingsPage,
    meta: { 
      requiresAuth: true, 
      roles: ['farmer'],
      title: 'Product Listings - Tunda App',
      description: 'Manage your product listings and inventory on Tunda App.'
    }
  },
  {
    path: '/farmer/listings/create',
    name: 'product-listing-create',
    component: ProductListingCreatePage,
    meta: { 
      requiresAuth: true, 
      roles: ['farmer'],
      title: 'Create Product Listing - Tunda App',
      description: 'Create a new product listing to sell your produce on Tunda App.'
    }
  },
  {
    path: '/farmer/orders',
    name: 'farmer-orders',
    component: FarmerOrdersPage,
    meta: { 
      requiresAuth: true, 
      roles: ['farmer'],
      title: 'Farmer Orders - Tunda App',
      description: 'View and manage orders for your farm on Tunda App.'
    }
  },
  {
    path: '/farmer/insights',
    name: 'market-insights',
    component: MarketInsightsPage,
    meta: { 
      requiresAuth: true, 
      roles: ['farmer'],
      title: 'Market Insights - Tunda App',
      description: 'Access market trends and insights to optimize your farming on Tunda App.'
    }
  },
  {
    path: '/farmer/payouts',
    name: 'farmer-payouts',
    component: PayoutsPage,
    meta: { 
      requiresAuth: true, 
      roles: ['farmer'],
      title: 'Farmer Payouts - Tunda App',
      description: 'Manage your payout requests and history on Tunda App.'
    }
  },
  {
    path: '/farmer/support',
    name: 'farmer-support',
    component: FarmerSupportPage,
    meta: { 
      requiresAuth: true, 
      roles: ['farmer'],
      title: 'Farmer Support - Tunda App',
      description: 'Get help and support for your Tunda App farmer account.'
    }
  },

  // Rider routes
  {
    path: '/rider',
    name: 'rider-dashboard',
    component: RiderDashboard,
    meta: { 
      requiresAuth: true, 
      roles: ['rider'],
      title: 'Rider Dashboard - Tunda App',
      description: 'Access your personalized rider dashboard on Tunda App.'
    }
  },
  {
    path: '/rider/deliveries',
    name: 'deliveries',
    component: DeliveriesPage,
    meta: { 
      requiresAuth: true, 
      roles: ['rider'],
      title: 'My Deliveries - Tunda App',
      description: 'View and manage your assigned deliveries on Tunda App.'
    }
  },
  {
    path: '/rider/deliveries/:id',
    name: 'delivery-detail',
    component: DeliveryDetail,
    meta: { 
      requiresAuth: true, 
      roles: ['rider'],
      title: 'Delivery Details - Tunda App',
      description: 'View detailed information about a specific delivery on Tunda App.'
    }
  },
  {
    path: '/rider/payouts',
    name: 'rider-payouts',
    component: PayoutsPage,
    meta: { 
      requiresAuth: true, 
      roles: ['rider'],
      title: 'Rider Payouts - Tunda App',
      description: 'Manage your payout requests and history as a rider on Tunda App.'
    }
  },
  {
    path: '/rider/support',
    name: 'rider-support',
    component: RiderSupportPage,
    meta: { 
      requiresAuth: true, 
      roles: ['rider'],
      title: 'Rider Support - Tunda App',
      description: 'Get help and support for your Tunda App rider account.'
    }
  },

  // Admin routes
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: AdminDashboard,
    meta: { 
      requiresAuth: true, 
      roles: ['admin'],
      title: 'Admin Dashboard - Tunda App',
      description: 'Access the administrative dashboard for Tunda App management.'
    }
  },
  {
    path: '/admin/users',
    name: 'users-management',
    component: UsersManagement,
    meta: { 
      requiresAuth: true, 
      roles: ['admin'],
      title: 'User Management - Tunda App',
      description: 'Manage user accounts and roles within the Tunda App system.'
    }
  },
  {
    path: '/admin/orders',
    name: 'orders-management',
    component: OrdersManagement,
    meta: { 
      requiresAuth: true, 
      roles: ['admin'],
      title: 'Order Management - Tunda App',
      description: 'Manage all customer and farmer orders on Tunda App.'
    }
  },
  {
    path: '/admin/deliveries',
    name: 'deliveries-management',
    component: DeliveriesManagement,
    meta: { 
      requiresAuth: true, 
      roles: ['admin'],
      title: 'Delivery Management - Tunda App',
      description: 'Oversee and manage all deliveries within the Tunda App system.'
    }
  },
  {
    path: '/admin/reviews',
    name: 'reviews-management',
    component: ReviewsManagement,
    meta: { 
      requiresAuth: true, 
      roles: ['admin'],
      title: 'Review Management - Tunda App',
      description: 'Manage product and service reviews on Tunda App.'
    }
  },
  {
    path: '/admin/payouts',
    name: 'payouts-management',
    component: PayoutsManagement,
    meta: { 
      requiresAuth: true, 
      roles: ['admin'],
      title: 'Payout Management - Tunda App',
      description: 'Manage farmer and rider payout requests on Tunda App.'
    }
  },
  {
    path: '/admin/categories',
    name: 'categories-management',
    component: ProductCategoriesManagement,
    meta: {
      requiresAuth: true,
      roles: ['admin'],
      title: 'Category Management - Tunda App',
      description: 'Manage product categories on Tunda App.'
    }
  },
  {
    path: '/admin/support',
    name: 'support-management',
    component: SupportManagement,
    meta: { 
      requiresAuth: true, 
      roles: ['admin'],
      title: 'Support Ticket Management - Tunda App',
      description: 'Manage customer, farmer, and rider support tickets on Tunda App.'
    }
  },
  {
    path: '/admin/settings',
    name: 'system-settings',
    component: SystemSettings,
    meta: { 
      requiresAuth: true, 
      roles: ['admin'],
      title: 'System Settings - Tunda App',
      description: 'Configure global system settings for the Tunda App.'
    }
  },

  // Catch all route
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    redirect: '/',
    meta: {
      title: 'Page Not Found - Tunda App',
      description: 'The page you are looking for does not exist on Tunda App.'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Global navigation guard
router.beforeEach(async (to, from, next) => {
  // Wait for auth to be initialized
  await initializeAuth()

  // If authenticated but no role is detected, something is wrong
  if (isAuthenticated.value && (!user.value || !user.value.user_role)) {
    console.error('User authenticated but no role detected - forcing logout')
    logout()
    return next('/login')
  }

  // Handle auth required routes
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return next('/login')
  }

  // Handle guest-only routes
  if (to.meta.requiresGuest && isAuthenticated.value) {
    return next('/')
  }

  // Block product routes for non-customers
  if (isAuthenticated.value && !isCustomer.value && to.path.startsWith('/products')) {    
    // Determine redirect based on role
    const role = user.value?.user_role
    switch(role) {
      case 'farmer':
        return next('/farmer')
      case 'rider':
        return next('/rider')
      case 'admin':
        return next('/admin')
      default:
        console.error('Unknown role detected:', role)
        return next('/')
    }
  }

  // Update meta tags
  document.title = to.meta.title || 'Tunda App';
  let metaDescriptionTag = document.querySelector('meta[name="description"]');
  if (!metaDescriptionTag) {
    metaDescriptionTag = document.createElement('meta');
    metaDescriptionTag.setAttribute('name', 'description');
    document.head.appendChild(metaDescriptionTag);
  }
  metaDescriptionTag.setAttribute('content', to.meta.description || 'Tunda: Eat fresh, live healthy!');

  next()
})

export default router
