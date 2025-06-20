import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated, hasRole } from '@/stores/auth'

// Lazy load components for better performance
const HomePage = () => import('@/views/HomePage.vue')
const LoginPage = () => import('@/views/auth/LoginPage.vue')
const RegisterPage = () => import('@/views/auth/RegisterPage.vue')
const ProfilePage = () => import('@/views/ProfilePage.vue')

// Common pages
const NotificationsPage = () => import('@/views/common/NotificationsPage.vue')

// Customer pages
const CustomerDashboard = () => import('@/views/customer/CustomerDashboard.vue')
const ProductsPage = () => import('@/views/customer/ProductsPage.vue')
const ProductDetail = () => import('@/views/customer/ProductDetail.vue')
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

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
    meta: { requiresGuest: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfilePage,
    meta: { requiresAuth: true }
  },

  // Common routes (accessible by all authenticated users)
  {
    path: '/notifications',
    name: 'notifications',
    component: NotificationsPage,
    meta: { requiresAuth: true }
  },

  // Customer routes
  {
    path: '/customer',
    name: 'customer-dashboard',
    component: CustomerDashboard,
    meta: { requiresAuth: true, roles: ['customer'] }
  },
  {
    path: '/products',
    name: 'products',
    component: ProductsPage
  },
  {
    path: '/products/:id',
    name: 'product-detail',
    component: ProductDetail
  },
  {
    path: '/cart',
    name: 'cart',
    component: CartPage
    // Removed meta: { requiresAuth: true, roles: ['customer'] } to allow guest access
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: CheckoutPage,
    meta: { requiresAuth: true, roles: ['customer'] }
  },
  {
    path: '/orders',
    name: 'orders',
    component: OrdersPage,
    meta: { requiresAuth: true, roles: ['customer'] }
  },
  {
    path: '/orders/:id',
    name: 'order-detail',
    component: OrderDetail,
    meta: { requiresAuth: true, roles: ['customer'] }
  },
  {
    path: '/reviews',
    name: 'reviews',
    component: ReviewsPage,
    meta: { requiresAuth: true, roles: ['customer'] }
  },

  // Farmer routes
  {
    path: '/farmer',
    name: 'farmer-dashboard',
    component: FarmerDashboard,
    meta: { requiresAuth: true, roles: ['farmer'] }
  },
  {
    path: '/farmer/farms',
    name: 'farms',
    component: FarmsPage,
    meta: { requiresAuth: true, roles: ['farmer'] }
  },
  {
    path: '/farmer/farms/:id',
    name: 'farm-detail',
    component: FarmDetail,
    meta: { requiresAuth: true, roles: ['farmer'] }
  },
  {
    path: '/farmer/listings',
    name: 'product-listings',
    component: ProductListingsPage,
    meta: { requiresAuth: true, roles: ['farmer'] }
  },
  {
    path: '/farmer/listings/create',
    name: 'product-listing-create',
    component: ProductListingCreatePage,
    meta: { requiresAuth: true, roles: ['farmer'] }
  },
  {
    path: '/farmer/orders',
    name: 'farmer-orders',
    component: FarmerOrdersPage,
    meta: { requiresAuth: true, roles: ['farmer'] }
  },
  {
    path: '/farmer/insights',
    name: 'market-insights',
    component: MarketInsightsPage,
    meta: { requiresAuth: true, roles: ['farmer'] }
  },
  {
    path: '/farmer/payouts',
    name: 'farmer-payouts',
    component: PayoutsPage,
    meta: { requiresAuth: true, roles: ['farmer'] }
  },

  // Rider routes
  {
    path: '/rider',
    name: 'rider-dashboard',
    component: RiderDashboard,
    meta: { requiresAuth: true, roles: ['rider'] }
  },
  {
    path: '/rider/deliveries',
    name: 'deliveries',
    component: DeliveriesPage,
    meta: { requiresAuth: true, roles: ['rider'] }
  },
  {
    path: '/rider/deliveries/:id',
    name: 'delivery-detail',
    component: DeliveryDetail,
    meta: { requiresAuth: true, roles: ['rider'] }
  },
  {
    path: '/rider/payouts',
    name: 'rider-payouts',
    component: PayoutsPage,
    meta: { requiresAuth: true, roles: ['rider'] }
  },

  // Admin routes
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/users',
    name: 'users-management',
    component: UsersManagement,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/orders',
    name: 'orders-management',
    component: OrdersManagement,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/deliveries',
    name: 'deliveries-management',
    component: DeliveriesManagement,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/reviews',
    name: 'reviews-management',
    component: ReviewsManagement,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/payouts',
    name: 'payouts-management',
    component: PayoutsManagement,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/settings',
    name: 'system-settings',
    component: SystemSettings,
    meta: { requiresAuth: true, roles: ['admin'] }
  },

  // Catch all route
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    redirect: '/'
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

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const { requiresAuth, requiresGuest, roles } = to.meta

  // Check if route requires authentication
  if (requiresAuth && !isAuthenticated.value) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // Check if route requires guest (not authenticated)
  if (requiresGuest && isAuthenticated.value) {
    next({ name: 'home' })
    return
  }

  // Check role-based access
  if (roles && roles.length > 0) {
    const userHasRole = roles.some(role => hasRole(role))
    if (!userHasRole) {
      // Redirect to appropriate dashboard based on user role
      const { user } = await import('@/stores/auth')
      const userRole = user.value?.user_role
      
      if (userRole) {
        next({ name: `${userRole}-dashboard` })
      } else {
        next({ name: 'home' })
      }
      return
    }
  }

  next()
})

export default router
