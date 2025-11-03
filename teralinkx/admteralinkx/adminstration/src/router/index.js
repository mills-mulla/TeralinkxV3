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
  // Add other routes...
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