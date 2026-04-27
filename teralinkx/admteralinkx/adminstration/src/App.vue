<template>
  <div id="app" class="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
    <!-- Show main layout when authenticated -->
    <div v-if="authChecked">
      <div v-if="isAuthenticated" class="min-h-screen">
        <!-- Sidebar Component -->
        <Sidebar 
          @component-selected="setActiveComponent"
          @finance-tab-selected="setFinanceTab"
          @refresh-data="refreshData"
          :is-mobile-open="isMobileSidebarOpen"
          @close-mobile="closeMobileSidebar"
          @sidebar-toggle="handleSidebarToggle"
          :user="user"
          :stats="sidebarStats"
          :active-component="activeComponent"
        />

        <!-- Main Content Area -->
        <main class="transition-all duration-300 min-h-screen" :class="isSidebarCollapsed ? 'lg:ml-[72px]' : 'lg:ml-[232px]'">
          <!-- Header -->
          <header class="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-200 dark:border-slate-700/50 sticky top-0 z-40 transition-colors duration-300">
            <div class="px-4 py-2 flex justify-between items-center gap-3">
              <!-- Left: mobile menu + breadcrumb + search -->
              <div class="flex items-center gap-3 flex-1">
                <button @click="toggleMobileSidebar" class="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-100 dark:bg-slate-700/50 transition-all">
                  <svg v-if="!isMobileSidebarOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
                <!-- Breadcrumb -->
                <div class="hidden lg:flex items-center gap-1.5 text-xs">
                  <span class="text-slate-500 dark:text-slate-400">TeralinkX</span>
                  <span class="text-slate-600">/</span>
                  <span class="text-slate-700 dark:text-slate-200 font-medium">{{ activeComponent.replace(/([A-Z])/g, ' $1').trim() }}</span>
                </div>
                <!-- Search -->
                <div class="relative flex-1 max-w-xs">
                  <input v-model="globalSearch" @focus="showSearchResults = true" @blur="hideSearchResults" type="text" placeholder="Search..."
                    class="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/50 rounded-lg text-slate-700 dark:text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all" />
                  <svg class="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                  <div v-if="showSearchResults && globalSearch" class="absolute top-full mt-1.5 w-full bg-white dark:bg-slate-800 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 max-h-80 overflow-y-auto z-50">
                    <div v-if="searchResults.length === 0" class="p-3 text-center text-slate-500 dark:text-slate-400 text-xs">No results found</div>
                    <button v-for="result in searchResults" :key="result.id" @mousedown="navigateToResult(result)"
                      class="w-full px-3 py-2.5 text-left hover:bg-slate-100 dark:bg-slate-700/50 transition-colors border-b border-slate-200 dark:border-slate-700/50 last:border-0 flex items-center gap-2.5">
                      <span class="text-base">{{ result.icon }}</span>
                      <div><p class="text-xs font-medium text-slate-700 dark:text-slate-200">{{ result.title }}</p><p class="text-[10px] text-slate-500 dark:text-slate-400">{{ result.subtitle }}</p></div>
                    </button>
                  </div>
                </div>
              </div>
              <!-- Right: notifications + user -->
              <div class="flex items-center gap-2">
                <!-- Notifications -->
                <div class="relative">
                  <button @click="toggleNotifications" class="relative w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-700/50 hover:bg-slate-700 flex items-center justify-center text-slate-400 hover:text-white transition-all">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
                    <span v-if="unreadNotifications > 0" class="absolute -top-0.5 -right-0.5 w-4 h-4 bg-rose-500 text-white text-[9px] rounded-full flex items-center justify-center font-bold">{{ unreadNotifications > 9 ? '9+' : unreadNotifications }}</span>
                  </button>
                  <div v-if="showNotifications" class="absolute right-0 mt-2 w-80 bg-white dark:bg-slate-800 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 z-50">
                    <div class="px-4 py-3 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
                      <h3 class="text-xs font-semibold text-white">Notifications</h3>
                      <button @click="markAllAsRead" class="text-[10px] text-blue-400 hover:underline">Mark all read</button>
                    </div>
                    <div class="max-h-80 overflow-y-auto">
                      <div v-if="notifications.length === 0" class="p-4 text-center text-slate-500 dark:text-slate-400 text-xs">No notifications</div>
                      <button v-for="notif in notifications" :key="notif.id" @click="handleNotificationClick(notif)"
                        class="w-full px-4 py-3 text-left hover:bg-slate-100 dark:bg-slate-700/50 transition-colors border-b border-slate-200 dark:border-slate-700/50 last:border-0"
                        :class="{ 'bg-blue-500/10': !notif.read }">
                        <div class="flex items-start gap-3">
                          <svg class="w-4 h-4 text-blue-400 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 24 24"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/></svg>
                          <div class="flex-1 min-w-0">
                            <p class="text-xs font-medium text-slate-700 dark:text-slate-200 truncate">{{ notif.title }}</p>
                            <p class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{{ notif.message }}</p>
                            <p class="text-[10px] text-slate-600 mt-0.5">{{ notif.time }}</p>
                          </div>
                          <div v-if="!notif.read" class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1 shrink-0"></div>
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
                <!-- User menu -->
                <div class="relative">
                  <button @click="toggleUserMenu" class="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-100 dark:bg-slate-700/50 transition-all">
                    <div class="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white text-xs font-bold">{{ (user?.username || 'A').charAt(0).toUpperCase() }}</div>
                    <div class="hidden md:block text-left">
                      <p class="text-xs font-medium text-slate-700 dark:text-slate-200 leading-none">{{ user?.username }}</p>
                      <p class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{{ user?.is_superuser ? 'Superuser' : 'Admin' }}</p>
                    </div>
                    <svg class="w-3 h-3 text-slate-500 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                  </button>
                  <div v-if="showUserMenu" class="absolute right-0 mt-1.5 w-48 bg-white dark:bg-slate-800 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 z-50">
                    <div class="px-4 py-3 border-b border-slate-200 dark:border-slate-700">
                      <p class="text-xs font-semibold text-white">{{ user?.username }}</p>
                      <p class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{{ user?.email || 'admin@teralinkx.com' }}</p>
                    </div>
                    <div class="py-1">
                      <button class="w-full px-4 py-2 text-left text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:bg-slate-700/50 transition-colors flex items-center gap-2">
                        <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                        Profile
                      </button>
                      <button class="w-full px-4 py-2 text-left text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:bg-slate-700/50 transition-colors flex items-center gap-2">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                        Settings
                      </button>
                    </div>
                    <div class="border-t border-slate-200 dark:border-slate-700 py-1">
                      <button @click="handleLogout" class="w-full px-4 py-2 text-left text-xs text-rose-400 hover:bg-rose-500/10 transition-colors flex items-center gap-2">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                        Logout
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </header>

          <!-- Main Content -->
          <div class="p-6">
            <transition name="component-fade" mode="out-in">
              <component :is="activeComponent" :key="activeComponent" :active-tab="activeComponent === 'Finance' ? activeFinanceTab : undefined" />
            </transition>
          </div>
        </main>

        <!-- Real-Time Notifications -->
        <RealTimeNotifications />

        <!-- Toast Notification -->
        <div v-if="showToast" class="fixed top-4 right-4 bg-emerald-500 dark:bg-emerald-600 text-white px-5 py-3 rounded-lg shadow-lg z-50 animate-fade-in">
          <div class="flex items-center space-x-2">
            <div class="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></div>
            <span class="text-sm font-medium">{{ toastMessage }}</span>
          </div>
        </div>
      </div>

      <!-- Show Auth component when not authenticated -->
      <Auth v-else @login-success="handleLoginSuccess" />
    </div>

    <!-- Loading state while checking authentication -->
    <div v-else class="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900">
      <div class="text-center">
        <div class="w-12 h-12 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-slate-900 dark:text-white font-medium">Checking authentication...</p>
        <p class="text-slate-500 dark:text-slate-400 dark:text-slate-400 text-sm mt-2">Please wait</p>
      </div>
    </div>
  </div>
</template>

<script>
import { useTheme } from './composables/useTheme'
import Sidebar from './components/Sidebar.vue'
import RealTimeNotifications from './components/RealTimeNotifications.vue'
import Dashboard from './views/Dashboard.vue'
import Clients from './views/Clients.vue'
import Users from './views/Users.vue'
import Devices from './views/Devices.vue'
import Sessions from './views/Sessions.vue'
import Packages from './views/Packages.vue'
import Vouchers from './views/Vouchers.vue'
import Coupons from './views/Coupons.vue'
import Promotions from './views/Promotions.vue'
import PointTransactions from './views/PointTransactions.vue'
import Locations from './views/Locations.vue'
import Transactions from './views/Transactions.vue'
import Refunds from './views/Refunds.vue'
import Finance from './views/Finance.vue'
import Auth from './views/Auth.vue'
import CustomerIntelligence from './views/CustomerIntelligence.vue'

// Axios configuration for JWT
import axios from 'axios';

// Set base URL and default headers
axios.defaults.baseURL = 'https://srv.teralinkxwaves.uk';
axios.defaults.headers.common['Content-Type'] = 'application/json';

export default {
  name: 'App',
  setup() {
    const { initTheme } = useTheme()
    initTheme()
    return {}
  },
  components: {
    Sidebar,
    RealTimeNotifications,
    Dashboard,
    CustomerIntelligence,
    Clients,
    Users,
    Devices,
    Sessions,
    Packages,
    Vouchers,
    Coupons,
    Promotions,
    PointTransactions,
    Locations,
    Transactions,
    Refunds,
    Finance,
    Auth,
    CustomerIntelligence,
  },
  data() {
    return {
      activeComponent: 'Dashboard',
      activeFinanceTab: 'analytics',
      isMobileSidebarOpen: false,
      hideValues: false,
      isSidebarCollapsed: false,
      showToast: false,
      toastMessage: '',
      isAuthenticated: false,
      authChecked: false,
      user: null,
      refreshTokenInterval: null,
      axiosInterceptor: null,
      globalSearch: '',
      showSearchResults: false,
      showNotifications: false,
      showUserMenu: false,
      notifications: [
        { id: 1, icon: '🔔', title: 'New User Registration', message: '5 new users registered today', time: '5 min ago', read: false },
        { id: 2, icon: '💳', title: 'Payment Received', message: 'Payment of $150 received', time: '1 hour ago', read: false },
        { id: 3, icon: '⚠️', title: 'System Alert', message: 'High server load detected', time: '2 hours ago', read: true },
      ],
      sidebarStats: {
        activeUsers: 0,
        activeSessions: 0,
        activeDevices: 0,
        pendingRefunds: 0
      }
    }
  },
  computed: {
    unreadNotifications() {
      return this.notifications.filter(n => !n.read).length
    },
    searchResults() {
      if (!this.globalSearch) return []
      const query = this.globalSearch.toLowerCase()
      const results = []
      
      const pages = [
        { id: 'dashboard', icon: '📊', title: 'Dashboard', subtitle: 'Overview and analytics', component: 'Dashboard' },
        { id: 'clients', icon: '👥', title: 'Clients', subtitle: 'Manage client profiles', component: 'Clients' },
        { id: 'users', icon: '🔐', title: 'Users', subtitle: 'User management', component: 'Users' },
        { id: 'devices', icon: '📱', title: 'Devices', subtitle: 'Connected devices', component: 'Devices' },
        { id: 'sessions', icon: '🔌', title: 'Sessions', subtitle: 'Active sessions', component: 'Sessions' },
        { id: 'packages', icon: '📦', title: 'Packages', subtitle: 'Data packages', component: 'Packages' },
        { id: 'vouchers', icon: '🎫', title: 'Vouchers', subtitle: 'Voucher management', component: 'Vouchers' },
        { id: 'coupons', icon: '🎟️', title: 'Coupons', subtitle: 'Discount coupons', component: 'Coupons' },
        { id: 'promotions', icon: '🎁', title: 'Promotions', subtitle: 'Marketing promotions', component: 'Promotions' },
        { id: 'points', icon: '🏆', title: 'Points', subtitle: 'Reward points', component: 'PointTransactions' },
        { id: 'locations', icon: '📍', title: 'Locations', subtitle: 'Network locations', component: 'Locations' },
        { id: 'transactions', icon: '💳', title: 'Transactions', subtitle: 'Payment transactions', component: 'Transactions' },
        { id: 'refunds', icon: '🔄', title: 'Refunds', subtitle: 'Refund requests', component: 'Refunds' },
        { id: 'finance', icon: '📊', title: 'Finance', subtitle: 'Revenue, expenses & analytics', component: 'Finance' },
        { id: 'customer-intelligence', icon: '🧠', title: 'Customer Intelligence', subtitle: 'Churn, retention & revenue at risk', component: 'CustomerIntelligence' },
      ]
      
      pages.forEach(page => {
        if (page.title.toLowerCase().includes(query) || page.subtitle.toLowerCase().includes(query)) {
          results.push(page)
        }
      })
      
      return results.slice(0, 5)
    }
  },
  methods: {
    setActiveComponent(componentName) {
      this.activeComponent = componentName;
      sessionStorage.setItem('activeComponent', componentName)
      if (window.innerWidth < 1024) this.isMobileSidebarOpen = false;
      this.showNotifications = false
      this.showUserMenu = false
      this.showSearchResults = false
    },
    setFinanceTab(tabId) {
      this.activeFinanceTab = tabId
      this.activeComponent = 'Finance'
      sessionStorage.setItem('activeComponent', 'Finance')
    },
    
    getUserInitials() {
      if (!this.user?.username) return 'AD'
      const parts = this.user.username.split(' ')
      if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase()
      }
      return this.user.username.substring(0, 2).toUpperCase()
    },
    
    toggleNotifications() {
      this.showNotifications = !this.showNotifications
      this.showUserMenu = false
      this.showSearchResults = false
    },
    
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu
      this.showNotifications = false
      this.showSearchResults = false
    },
    
    hideSearchResults() {
      setTimeout(() => {
        this.showSearchResults = false
      }, 200)
    },
    
    navigateToResult(result) {
      this.setActiveComponent(result.component)
      this.globalSearch = ''
      this.showSearchResults = false
    },
    
    markAllAsRead() {
      this.notifications.forEach(n => n.read = true)
    },
    
    handleNotificationClick(notif) {
      notif.read = true
      this.showNotifications = false
    },
    
    async fetchSidebarStats() {
      try {
        const [usersRes, sessionsRes, devicesRes] = await Promise.all([
          axios.get('/suapi/users/stats/'),
          axios.get('/suapi/sessions/stats/'),
          axios.get('/suapi/devices/stats/')
        ])
        
        this.sidebarStats = {
          activeUsers: usersRes.data.active_users || 0,
          activeSessions: sessionsRes.data.active_sessions || 0,
          activeDevices: devicesRes.data.online_devices || 0,
          pendingRefunds: 0
        }
      } catch (error) {
        console.error('Error fetching sidebar stats:', error)
      }
    },
    
    refreshData() {
      // Refresh data for the current component
      if (this.$refs[this.activeComponent]?.refreshData) {
        this.$refs[this.activeComponent].refreshData();
      }
      
      // Show toast notification
      this.showToastMessage('Data refreshed successfully!');
    },
    
    showToastMessage(message) {
      this.toastMessage = message;
      this.showToast = true;
      
      setTimeout(() => {
        this.showToast = false;
      }, 3000);
    },

    toggleMobileSidebar() {
      this.isMobileSidebarOpen = !this.isMobileSidebarOpen;
      console.log('Mobile sidebar toggled:', this.isMobileSidebarOpen)
    },
    
    closeMobileSidebar() {
      this.isMobileSidebarOpen = false;
    },

    handleSidebarToggle(isCollapsed) {
      this.isSidebarCollapsed = isCollapsed;
    },

    // Set up axios interceptor for automatic token refresh
    setupAxiosInterceptor() {
      // Remove existing interceptor if any
      if (this.axiosInterceptor) {
        axios.interceptors.response.eject(this.axiosInterceptor);
      }

      this.axiosInterceptor = axios.interceptors.response.use(
        (response) => response,
        async (error) => {
          const originalRequest = error.config;
          
          if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            try {
              console.log('🔄 Token expired, attempting refresh...');
              await this.refreshAccessToken();
              
              // Retry the original request with new token
              const newToken = localStorage.getItem('access_token');
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return axios(originalRequest);
            } catch (refreshError) {
              console.error('❌ Token refresh failed:', refreshError);
              // Refresh failed, logout user
              this.handleLogout();
              return Promise.reject(refreshError);
            }
          }
          
          return Promise.reject(error);
        }
      );
    },

    // Set authorization header from stored token
    setAuthHeader() {
      const token = localStorage.getItem('access_token');
      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      } else {
        delete axios.defaults.headers.common['Authorization'];
      }
    },

    // Check if user has valid tokens
    async checkAuthStatus() {
      const accessToken = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!accessToken || !refreshToken) {
        console.log('❌ No JWT tokens found');
        this.isAuthenticated = false;
        this.user = null;
        this.authChecked = true;
        return;
      }

      // Set authorization header
      this.setAuthHeader();

      try {
        // Verify token by making a simple API call
        console.log('🔍 Verifying JWT token...');
        const response = await axios.get('/suapi/auth/verify/');
        
        if (response.data.authenticated) {
          console.log('✅ JWT token verified successfully');
          this.isAuthenticated = true;
          this.user = response.data.user;
          
          // Load additional user data from localStorage if available
          const storedUser = localStorage.getItem('user');
          if (storedUser) {
            this.user = { ...response.data.user, ...JSON.parse(storedUser) };
          }

          // Restore last active page from sessionStorage (reload persistence)
          const saved = sessionStorage.getItem('activeComponent')
          if (saved) this.activeComponent = saved
        } else {
          console.log('❌ JWT token verification failed');
          this.isAuthenticated = false;
          this.user = null;
        }
      } catch (error) {
        console.error('❌ Auth check failed:', error);
        
        // Try to refresh token if access token is expired
        if (error.response?.status === 401) {
          try {
            console.log('🔄 Access token expired, attempting refresh...');
            await this.refreshAccessToken();
            await this.checkAuthStatus(); // Retry auth check with new token
            return;
          } catch (refreshError) {
            console.error('❌ Token refresh failed:', refreshError);
          }
        }
        
        this.isAuthenticated = false;
        this.user = null;
      } finally {
        this.authChecked = true;
      }
    },

    // Refresh access token using refresh token
    async refreshAccessToken() {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      try {
        console.log('🔄 Refreshing access token...');
        const response = await axios.post('/suapi/token/refresh/', {
          refresh: refreshToken
        });
        
        const newAccessToken = response.data.access;
        localStorage.setItem('access_token', newAccessToken);
        this.setAuthHeader();
        
        console.log('✅ Access token refreshed successfully');
        return newAccessToken;
      } catch (error) {
        console.error('❌ Token refresh failed:', error);
        // Clear tokens if refresh fails
        this.clearTokens();
        throw error;
      }
    },

    // Handle successful login from Auth component
    handleLoginSuccess({ access, refresh, user }) {
      console.log('🎉 Login success received in App.vue');
      
      // Store tokens
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Set authorization header
      this.setAuthHeader();
      
      // Update state
      this.isAuthenticated = true;
      this.user = user;
      this.authChecked = true;
      
      // On fresh login always start at Dashboard
      sessionStorage.removeItem('activeComponent')
      this.activeComponent = 'Dashboard'
      
      // Show welcome message
      this.showToastMessage(`Welcome back, ${user.username}!`);
      
      console.log('✅ User authenticated and state updated');
    },

    // Clear all tokens and user data
    clearTokens() {
      console.log('🧹 Clearing all tokens and user data');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      localStorage.removeItem('lastLogin');
      localStorage.removeItem('rememberMe');
      sessionStorage.removeItem('activeComponent');
      delete axios.defaults.headers.common['Authorization'];
    },

    async handleLogout() {
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          // Call logout endpoint to blacklist refresh token
          await axios.post('/suapi/auth/logout/', {
            refresh_token: refreshToken
          });
        }
      } catch (error) {
        console.error('Logout API error:', error);
        // Continue with client-side logout even if API call fails
      } finally {
        // Clear all tokens and data
        this.clearTokens();
        
        // Reset auth state
        this.isAuthenticated = false;
        this.user = null;
        
        // Clear refresh interval
        if (this.refreshTokenInterval) {
          clearInterval(this.refreshTokenInterval);
        }
        
        // Show logout message
        this.showToastMessage('Logged out successfully');
        
        console.log('✅ User logged out successfully');
      }
    },

    // Setup periodic token refresh (every 45 minutes)
    setupTokenRefresh() {
      this.refreshTokenInterval = setInterval(async () => {
        if (this.isAuthenticated) {
          try {
            await this.refreshAccessToken();
            console.log('✅ Access token refreshed automatically');
          } catch (error) {
            console.error('❌ Automatic token refresh failed:', error);
            this.handleLogout();
          }
        }
      }, 45 * 60 * 1000); // 45 minutes
    },

    // Check token expiration and setup auto-refresh
    setupTokenExpirationCheck() {
      // Check token every minute
      setInterval(() => {
        if (this.isAuthenticated) {
          const token = localStorage.getItem('access_token');
          if (token) {
            try {
              const payload = JSON.parse(atob(token.split('.')[1]));
              const expiresAt = payload.exp * 1000;
              const now = Date.now();
              const timeUntilExpiry = expiresAt - now;
              
              // If token expires in less than 5 minutes, refresh it
              if (timeUntilExpiry < 5 * 60 * 1000 && timeUntilExpiry > 0) {
                console.log('🔄 Token expiring soon, refreshing...');
                this.refreshAccessToken().catch(error => {
                  console.error('Preemptive token refresh failed:', error);
                });
              }
            } catch (error) {
              console.error('Error checking token expiration:', error);
            }
          }
        }
      }, 60 * 1000); // Check every minute
    }
  },
  
  provide() {
    return {
      closeMobileSidebar: () => {
        this.isMobileSidebarOpen = false
      },
      openMobileSidebar: () => {
        this.isMobileSidebarOpen = true
      }
    }
  },
  
  async mounted() {
    console.log('🚀 App.vue mounted - Initializing JWT authentication...');
    
    // Set up axios interceptor first
    this.setupAxiosInterceptor();
    
    // Check authentication status when app loads
    await this.checkAuthStatus();
    
    // Set up automatic token refresh
    this.setupTokenRefresh();
    
    // Set up token expiration monitoring
    this.setupTokenExpirationCheck();
    
    // Fetch sidebar stats
    if (this.isAuthenticated) {
      this.fetchSidebarStats()
      // Refresh stats every 30 seconds
      setInterval(() => {
        if (this.isAuthenticated) {
          this.fetchSidebarStats()
        }
      }, 30000)
    }
    
    // Global keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      // Ctrl+K for search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        document.querySelector('input[placeholder*="Search"]')?.focus()
      }
      // Escape to close dropdowns
      if (e.key === 'Escape') {
        this.showNotifications = false
        this.showUserMenu = false
        this.showSearchResults = false
      }
    })
    
    // Close dropdowns on outside click
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.relative')) {
        this.showNotifications = false
        this.showUserMenu = false
      }
    })
    
    console.log('✅ App.vue initialization complete');
  },
  
  beforeUnmount() {
    // Clean up intervals and interceptors
    if (this.refreshTokenInterval) {
      clearInterval(this.refreshTokenInterval);
    }
    
    if (this.axiosInterceptor) {
      axios.interceptors.response.eject(this.axiosInterceptor);
    }
  }
}
</script>

<style>
/* Global styles */
* {
  box-sizing: border-box;
}

/* Smooth transitions for component switching */
.component-fade-enter-active,
.component-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.component-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.component-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Toast animation */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.animate-fade-in {
  animation: fade-in 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Custom scrollbar for main content */
main::-webkit-scrollbar {
  width: 8px;
}

main::-webkit-scrollbar-track {
  background: rgba(241, 245, 249, 0.5);
  border-radius: 4px;
}

main::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #cbd5e1, #94a3b8);
  border-radius: 4px;
}

main::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #94a3b8, #64748b);
}

/* Mobile sidebar styles */
@media (max-width: 1023px) {
  main {
    margin-left: 0 !important;
  }
  
  .mobile-open {
    transform: translateX(0) !important;
  }
}
</style>