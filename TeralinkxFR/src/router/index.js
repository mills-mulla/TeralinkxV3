import { createRouter, createWebHashHistory } from 'vue-router'; // Changed to createWebHashHistory
import Dashboard from '@/views/Dashboard.vue';
import SignIn from '@/views/Signin.vue';
import ImConnected from '@/views/Connected.vue';
import Loader from '@/components/Loader.vue';
import LocalIP from '@/views/Ip.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: SignIn
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard
  },
  {
    path: '/connected',
    name: 'connected',
    component: ImConnected
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
    component: () => import('@/views/Profile.vue') // Lazy-loaded
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/Settings.vue') // Lazy-loaded
  },
  {
    path: '/usevoucher',
    name: 'usevoucher',
    component: () => import('@/views/Login.vue') // Lazy-loaded

  }
];

const router = createRouter({
  history: createWebHashHistory(), // Using hash mode now
  routes
});

export default router;