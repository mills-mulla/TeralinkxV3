import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Auth from '../views/Auth.vue'

const routes = [
  {
    path: '/',
    name: 'Auth',
    component: Auth,
     meta: { requiresAuth: false } 
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true } 
  },
  {
    path: '/clients',
    name: 'Clients',
    component: () => import('../views/Clients.vue'),
    meta: { requiresAuth: true } 
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/Users.vue'),
    meta: { requiresAuth: true } 
  },
  {
    path: '/devices',
    name: 'Devices',
    component: () => import('../views/Devices.vue'),
    meta: { requiresAuth: true } 
  },
  {
    path: '/sessions',
    name: 'Sessions',
    component: () => import('../views/Sessions.vue'),
    meta: { requiresAuth: true } 
  },
  {
    path: '/packages',
    name: 'Packages',
    component: () => import('../views/Packages.vue'),
    meta: { requiresAuth: true } 
  },
  {
    path: '/vouchers',
    name: 'Vouchers',
    component: () => import('../views/Vouchers.vue'),
    meta: { requiresAuth: true } 
  },
  {
    path: '/coupons',
    name: 'Coupons',
    component: () => import('../views/Coupons.vue'),
    meta: { requiresAuth: true } 
  },
  {
    path: '/promotions',
    name: 'Promotions',
    component: () => import('../views/Promotions.vue'),
    meta: { requiresAuth: true } 
  },
  {
    path: '/point-transactions',
    name: 'PointTransactions',
    component: () => import('../views/PointTransactions.vue'),
    meta: { requiresAuth: true } 
  },
  {
    path: '/locations',
    name: 'Locations',
    component: () => import('../views/Locations.vue'),
    meta: { requiresAuth: true } 
  },
  {
    path: '/transactions',
    name: 'Transactions',
    component: () => import('../views/Transactions.vue'),
    meta: { requiresAuth: true } 
  },
  {
    path: '/refunds',
    name: 'Refunds',
    component: () => import('../views/Refunds.vue'),
    meta: { requiresAuth: true } 
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const checkAuth = async () => {
  try {
    const response = await fetch('service.teralinkxwaves.uk/suapi/auth/check/', {
      credentials: 'include'
    })
    if (response.ok) {
      const data = await response.json()
      return data.authenticated
    }
    return false
  } catch (error) {
    console.error('Auth check failed:', error)
    return false
  }
}
export default router