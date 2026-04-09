import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/views/Dashboard.vue';
import SignIn from '@/views/Signin.vue';
import ImConnected from '@/views/Connected.vue';
import Loader from '@/views/Loader.vue';
import LocalIP from '@/views/Ip.vue';
import { useAuthStore } from '@/stores/auth';

const routes = [
  {
    path: '/',
    name: 'home',
    component: SignIn
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/connected',
    name: 'connected',
    component: ImConnected,
    meta: { requiresAuth: true }
  },
  {
    path: '/loader',
    name: 'loader',
    component: Loader
  },
  {
    path: '/ip',
    name: 'Myip',
    component: LocalIP
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user-guide',
    name: 'user-guide',
    component: () => import('@/views/UserGuide.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/faq',
    name: 'faq',
    component: () => import('@/views/FAQ.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/service-policy',
    name: 'service-policy',
    component: () => import('@/views/ServicePolicy.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/rewards',
    name: 'rewards',
    component: () => import('@/views/Rewards.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/usevoucher',
    name: 'usevoucher',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Route guard for seamless authentication
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth) {
    // Wait for auth initialization if needed
    if (authStore.loading) {
      // Wait for seamless re-auth to complete
      const maxWait = 5000 // 5 seconds max
      const startTime = Date.now()
      
      while (authStore.loading && (Date.now() - startTime) < maxWait) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
    }
    
    // Check if user has valid authentication after potential seamless re-auth
    if (!authStore.isAuthenticated) {
      // Redirect to signin with reason and intended destination
      const reason = 'Authentication required'
      const redirect = to.fullPath
      next(`/?reason=${encodeURIComponent(reason)}&redirect=${encodeURIComponent(redirect)}`)
      return
    }
  }
  
  next()
})

export default router;