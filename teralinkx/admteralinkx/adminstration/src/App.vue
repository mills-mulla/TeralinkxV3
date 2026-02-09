<template>
  <div id="app" class="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
    <!-- Show main layout when authenticated -->
    <div v-if="authChecked">
      <div v-if="isAuthenticated" class="min-h-screen">
        <!-- Sidebar Component -->
        <Sidebar 
          @component-selected="setActiveComponent"
          @refresh-data="refreshData"
          :class="{ 'mobile-open': isMobileSidebarOpen }"
          :user="user"
        />

        <!-- Main Content Area -->
        <main class="lg:ml-64 transition-all duration-300 min-h-screen" :class="{ 'ml-0': !isMobileSidebarOpen }">
          <!-- Header with user info and logout -->
          <header class="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-40 transition-colors duration-300">
            <div class="px-6 py-4 flex justify-between items-center">
              <div class="flex items-center space-x-4">
                <button 
                  @click="toggleMobileSidebar"
                  class="lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                >
                  <svg class="w-6 h-6 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                  </svg>
                </button>
                <h1 class="text-xl font-semibold text-slate-900 dark:text-white capitalize">
                  {{ activeComponent.replace(/([A-Z])/g, ' $1').trim() }}
                </h1>
              </div>

              <div class="flex items-center space-x-4">
                <div class="text-right">
                  <p class="text-sm font-medium text-slate-900 dark:text-white">{{ user?.username }}</p>
                  <p class="text-xs text-slate-500 dark:text-slate-400 capitalize">{{ user?.role || 'Administrator' }}</p>
                </div>
                <button 
                  @click="handleLogout"
                  class="px-4 py-2 text-sm text-rose-600 dark:text-rose-400 hover:text-rose-700 dark:hover:text-rose-300 border border-rose-300 dark:border-rose-700 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-500/10 transition-all duration-200 flex items-center space-x-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                  </svg>
                  <span>Logout</span>
                </button>
              </div>
            </div>
          </header>

          <!-- Main Content -->
          <div class="p-6">
            <transition name="component-fade" mode="out-in">
              <component :is="activeComponent" :key="activeComponent" />
            </transition>
          </div>
        </main>

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
        <p class="text-slate-500 dark:text-slate-400 text-sm mt-2">Please wait</p>
      </div>
    </div>
  </div>
</template>

<script>
import { useTheme } from './composables/useTheme'
import Sidebar from './components/Sidebar.vue'
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
import Auth from './views/Auth.vue'

// Axios configuration for JWT
import axios from 'axios';

// Set base URL and default headers
axios.defaults.baseURL = 'https://service.teralinkxwaves.uk';
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
    Dashboard,
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
    Auth,
  },
  data() {
    return {
      activeComponent: 'Dashboard',
      isMobileSidebarOpen: false,
      showToast: false,
      toastMessage: '',
      isAuthenticated: false,
      authChecked: false,
      user: null,
      refreshTokenInterval: null,
      axiosInterceptor: null
    }
  },
  methods: {
    setActiveComponent(componentName) {
      this.activeComponent = componentName;
      // Close mobile sidebar when component changes on mobile
      if (window.innerWidth < 1024) {
        this.isMobileSidebarOpen = false;
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
      closeMobileSidebar: () => this.isMobileSidebarOpen = false,
      openMobileSidebar: () => this.isMobileSidebarOpen = true
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