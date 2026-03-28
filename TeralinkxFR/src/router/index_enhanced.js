// src/router/index.js - Enhanced Router with Comprehensive Protection
import { createRouter, createWebHashHistory } from 'vue-router'
import { authGuard, routeGuards } from './guards'
import { useAuthStore } from '@/stores/auth_resilient'

// Import views
import Dashboard from '@/views/Dashboard.vue'
import SignIn from '@/views/Signin.vue'
import ImConnected from '@/views/Connected.vue'
import Loader from '@/views/Loader.vue'
import LocalIP from '@/views/Ip.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: SignIn,
    meta: { 
      requiresAuth: false,
      guestOnly: true,
      title: 'Sign In - TeralinkX'
    },
    beforeEnter: routeGuards.guestOnly
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: { 
      requiresAuth: true,
      requiresActiveAccount: true,
      title: 'Dashboard - TeralinkX'
    },
    beforeEnter: routeGuards.requiresActiveAccount
  },
  {
    path: '/connected',
    name: 'connected',
    component: ImConnected,
    meta: { 
      requiresAuth: true,
      requiresActiveAccount: true,
      title: 'Connected - TeralinkX'
    },
    beforeEnter: routeGuards.requiresActiveAccount
  },
  {
    path: '/loader',
    name: 'loader',
    component: Loader,
    meta: { 
      requiresAuth: false,
      title: 'Loading - TeralinkX'
    }
  },
  {
    path: '/ip',
    name: 'Myip',
    component: LocalIP,
    meta: { 
      requiresAuth: false,
      title: 'My IP - TeralinkX'
    }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/Profile.vue'),
    meta: { 
      requiresAuth: true,
      requiresActiveAccount: true,
      title: 'Profile - TeralinkX'
    },
    beforeEnter: routeGuards.requiresActiveAccount
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/Settings.vue'),
    meta: { 
      requiresAuth: true,
      requiresActiveAccount: true,
      title: 'Settings - TeralinkX'
    },
    beforeEnter: routeGuards.requiresActiveAccount
  },
  {
    path: '/user-guide',
    name: 'user-guide',
    component: () => import('@/views/UserGuide.vue'),
    meta: { 
      requiresAuth: true,
      title: 'User Guide - TeralinkX'
    },
    beforeEnter: routeGuards.requiresAuth
  },
  {
    path: '/faq',
    name: 'faq',
    component: () => import('@/views/FAQ.vue'),
    meta: { 
      requiresAuth: true,
      title: 'FAQ - TeralinkX'
    },
    beforeEnter: routeGuards.requiresAuth
  },
  {
    path: '/service-policy',
    name: 'service-policy',
    component: () => import('@/views/ServicePolicy.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Service Policy - TeralinkX'
    },
    beforeEnter: routeGuards.requiresAuth
  },
  {
    path: '/rewards',
    name: 'rewards',
    component: () => import('@/views/Rewards.vue'),
    meta: { 
      requiresAuth: true,
      requiresActiveAccount: true,
      title: 'Rewards - TeralinkX'
    },
    beforeEnter: routeGuards.requiresActiveAccount
  },
  {
    path: '/usevoucher',
    name: 'usevoucher',
    component: () => import('@/views/Login.vue'),
    meta: { 
      requiresAuth: true,
      requiresActiveAccount: true,
      title: 'Use Voucher - TeralinkX'
    },
    beforeEnter: routeGuards.requiresActiveAccount
  },
  // Admin routes (if needed)
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/Admin.vue'),
    meta: { 
      requiresAuth: true,
      requiresAdmin: true,
      title: 'Admin Panel - TeralinkX'
    },
    beforeEnter: routeGuards.requiresAdmin
  },
  // Error routes
  {
    path: '/unauthorized',
    name: 'unauthorized',
    component: () => import('@/views/Unauthorized.vue'),
    meta: { 
      requiresAuth: false,
      title: 'Unauthorized - TeralinkX'
    }
  },
  {
    path: '/maintenance',
    name: 'maintenance',
    component: () => import('@/views/Maintenance.vue'),
    meta: { 
      requiresAuth: false,
      title: 'Maintenance - TeralinkX'
    }
  },
  // Catch-all route
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
    meta: { 
      requiresAuth: false,
      title: 'Page Not Found - TeralinkX'
    }
  }
]

const router = createRouter({
  history: createWebHashHistory(), // Using hash mode for MikroTik compatibility
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Scroll to top on route change, or restore saved position
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Global navigation guards with enhanced resilience
router.beforeEach(async (to, from, next) => {
  console.log(`🧭 Navigating from ${from.path} to ${to.path}`)
  
  try {
    // Set page title
    if (to.meta.title) {
      document.title = to.meta.title
    }

    // Handle maintenance mode
    if (await isMaintenanceMode() && to.name !== 'maintenance') {
      console.log('🚧 Maintenance mode active')
      return next('/maintenance')
    }

    // Skip auth checks for routes that don't require authentication
    if (!to.meta.requiresAuth) {
      console.log('✅ Route does not require authentication')
      return next()
    }

    // Initialize auth store if needed
    const authStore = useAuthStore()
    if (!authStore.token && !authStore.loading) {
      console.log('🔄 Initializing auth store for protected route...')
      await authStore.initialize()
    }

    // The specific route guards will handle the detailed auth checks
    // This global guard just ensures basic initialization
    next()
    
  } catch (error) {
    console.error('💥 Global navigation guard error:', error)
    
    // Handle critical errors
    if (error.message.includes('Network')) {
      return next('/maintenance')
    }
    
    // Fallback to home page
    next('/')
  }
})

// After navigation guard for cleanup and analytics
router.afterEach((to, from, failure) => {
  if (failure) {
    console.error('💥 Navigation failed:', failure)
    return
  }

  console.log(`✅ Navigation completed: ${to.path}`)
  
  // Clear any auth cache if navigating away from protected routes
  if (!to.meta.requiresAuth && from.meta.requiresAuth) {
    authGuard.clearCache()
  }

  // Track page views (if analytics is enabled)
  if (typeof gtag !== 'undefined') {
    gtag('config', 'GA_MEASUREMENT_ID', {
      page_path: to.path,
      page_title: to.meta.title || to.name
    })
  }

  // Update last activity timestamp for session tracking
  const authStore = useAuthStore()
  if (authStore.isAuthenticated) {
    localStorage.setItem('last_activity', Date.now())
  }
})

// Navigation error handler
router.onError((error) => {
  console.error('💥 Router error:', error)
  
  // Handle chunk loading errors (common in SPA)
  if (error.message.includes('Loading chunk')) {
    console.log('🔄 Chunk loading error, reloading page...')
    window.location.reload()
    return
  }
  
  // Handle other navigation errors
  router.push('/')
})

/**
 * Check if application is in maintenance mode
 */
async function isMaintenanceMode() {
  try {
    // Check local storage flag
    const maintenanceFlag = localStorage.getItem('maintenance_mode')
    if (maintenanceFlag === 'true') return true

    // Check backend status (optional)
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/status/`, {
      method: 'GET',
      timeout: 3000
    })
    
    if (response.ok) {
      const data = await response.json()
      return data.maintenance_mode === true
    }
    
    return false
  } catch (error) {
    // If we can't check, assume not in maintenance mode
    return false
  }
}

/**
 * Programmatic navigation helpers
 */
export const navigationHelpers = {
  /**
   * Navigate to dashboard with auth check
   */
  async goToDashboard() {
    const authStore = useAuthStore()
    
    if (!authStore.isAuthenticated) {
      await authStore.initialize()
    }
    
    if (authStore.isAuthenticated) {
      router.push('/dashboard')
    } else {
      router.push('/')
    }
  },

  /**
   * Navigate to login with context
   */
  goToLogin(reason = null, redirect = null) {
    const query = {}
    if (reason) query.reason = reason
    if (redirect) query.redirect = redirect
    
    router.push({ path: '/', query })
  },

  /**
   * Navigate back with fallback
   */
  goBack(fallback = '/dashboard') {
    if (window.history.length > 1) {
      router.go(-1)
    } else {
      router.push(fallback)
    }
  },

  /**
   * Force logout and redirect
   */
  async forceLogout(reason = 'Session expired') {
    const authStore = useAuthStore()
    await authStore.logout()
    
    this.goToLogin(reason)
  }
}

export default router