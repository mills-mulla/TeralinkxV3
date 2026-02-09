<template>
  <aside class="w-64 bg-white dark:bg-slate-900 shadow-xl flex flex-col h-screen fixed left-0 top-0 border-r border-slate-200 dark:border-slate-800 transition-colors duration-300">
    <!-- Header -->
    <div class="p-5 border-b border-slate-200 dark:border-slate-800">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-sm">
          <span class="text-lg">🌊</span>
        </div>
        <div>
          <h1 class="text-base font-semibold text-slate-900 dark:text-white">
            Teralinkx
          </h1>
          <p class="text-slate-500 dark:text-slate-400 text-xs">Analytics</p>
        </div>
      </div>
    </div>
    
    <!-- Navigation Menu -->
    <nav class="flex-1 py-6 overflow-y-auto">
      <div class="px-4 space-y-1">
        <!-- Main Section -->
        <div class="px-3 py-2">
          <h3 class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide">Main</h3>
        </div>
        
        <button
          v-for="item in mainMenuItems"
          :key="item.id"
          @click="selectComponent(item.component)"
          class="w-full flex items-center px-3 py-2 text-slate-600 dark:text-slate-400 rounded-lg transition-all duration-200 text-left group text-sm"
          :class="{
            'bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 font-medium': activeComponent === item.component,
            'hover:bg-slate-100 dark:hover:bg-slate-800': activeComponent !== item.component
          }"
        >
          <span class="text-base mr-3">{{ item.icon }}</span>
          <span class="flex-1">{{ item.name }}</span>
          <span 
            v-if="item.notification"
            class="bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5 min-w-5 text-center"
          >
            {{ item.notification }}
          </span>
        </button>

        <!-- Support Section -->
        <div class="px-3 py-2 mt-4">
          <h3 class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide">Support</h3>
        </div>
        
        <button
          v-for="item in supportMenuItems"
          :key="item.id"
          @click="selectComponent(item.component)"
          class="w-full flex items-center px-3 py-2 text-slate-600 dark:text-slate-400 rounded-lg transition-all duration-200 text-left group text-sm"
          :class="{
            'bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 font-medium': activeComponent === item.component,
            'hover:bg-slate-100 dark:hover:bg-slate-800': activeComponent !== item.component
          }"
        >
          <span class="text-base mr-3">{{ item.icon }}</span>
          <span>{{ item.name }}</span>
        </button>
      </div>
    </nav>

    <!-- Footer Section -->
    <div class="p-4 border-t border-slate-200 dark:border-slate-800 space-y-3">
      <!-- Theme Toggle -->
      <div class="bg-slate-100 dark:bg-slate-800 rounded-lg p-3">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-medium text-slate-600 dark:text-slate-400">Theme</span>
          <button
            @click="toggleTheme"
            class="p-1.5 rounded-md hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          >
            <span class="text-lg">{{ isDark ? '🌙' : '☀️' }}</span>
          </button>
        </div>
        <label class="flex items-center cursor-pointer">
          <input
            type="checkbox"
            v-model="isAuto"
            @change="setAutoTheme"
            class="w-3.5 h-3.5 rounded border-slate-300 dark:border-slate-600 text-blue-600 focus:ring-blue-500 focus:ring-offset-0"
          />
          <span class="ml-2 text-xs text-slate-600 dark:text-slate-400">Auto (6AM-6PM)</span>
        </label>
      </div>

      <!-- Status -->
      <div class="flex items-center justify-between text-xs">
        <div class="flex items-center">
          <div class="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-1.5 animate-pulse"></div>
          <span class="text-slate-600 dark:text-slate-400">Online</span>
        </div>
        <span class="text-slate-500 dark:text-slate-500 font-mono">v2.1.0</span>
      </div>
    </div>

    <!-- Mobile Overlay -->
    <div 
      v-if="isMobileOpen" 
      class="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
      @click="closeMobileSidebar"
    ></div>
  </aside>

  <!-- Mobile Menu Button -->
  <button
    v-if="isMobile"
    @click="toggleMobileSidebar"
    class="fixed top-4 left-4 z-50 p-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl shadow-2xl lg:hidden hover:scale-105 transition-transform duration-300"
  >
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  </button>
</template>

<script>
import { useTheme } from '../composables/useTheme'

export default {
  name: 'Sidebar',
  emits: ['component-selected', 'refresh-data'],
  setup() {
    const { isDark, isAuto, toggleTheme, setAutoTheme } = useTheme()
    return { isDark, isAuto, toggleTheme, setAutoTheme }
  },
  data() {
    return {
      activeComponent: 'Dashboard',
      isMobileOpen: false,
      isMobile: false,
      lastUpdateTime: 'Just now',
      mainMenuItems: [
        { 
          id: 1, 
          name: 'Dashboard', 
          icon: '📊', 
          component: 'Dashboard',
          notification: null
        },
        { 
          id: 2, 
          name: 'Clients', 
          icon: '👥', 
          component: 'Clients',
          notification: null
        },
        { 
          id: 3, 
          name: 'Users', 
          icon: '🔐', 
          component: 'Users',
          notification: null
        },
        { 
          id: 4, 
          name: 'Devices', 
          icon: '📱', 
          component: 'Devices',
          notification: null
        },
        { 
          id: 5, 
          name: 'Sessions', 
          icon: '🔌', 
          component: 'Sessions',
          notification: null
        },
        { 
          id: 6, 
          name: 'Packages', 
          icon: '📦', 
          component: 'Packages',
          notification: null
        },
        { 
          id: 7, 
          name: 'Vouchers', 
          icon: '🎫', 
          component: 'Vouchers',
          notification: null
        },
        { 
          id: 8, 
          name: 'Coupons', 
          icon: '🎟️', 
          component: 'Coupons',
          notification: null
        },
        { 
          id: 9, 
          name: 'Promotions', 
          icon: '🎁', 
          component: 'Promotions',
          notification: null
        },
        { 
          id: 10, 
          name: 'Points', 
          icon: '🏆', 
          component: 'PointTransactions',
          notification: null
        },
        { 
          id: 11, 
          name: 'Locations', 
          icon: '📍', 
          component: 'Locations',
          notification: null
        },
        { 
          id: 12, 
          name: 'Transactions', 
          icon: '💳', 
          component: 'Transactions',
          notification: null
        },
        { 
          id: 13, 
          name: 'Refunds', 
          icon: '🔄', 
          component: 'Refunds',
          notification: null
        }
      ],
      supportMenuItems: [
        { 
          id: 5, 
          name: 'Auth', 
          icon: '📚', 
          component: 'Auth',
          notification: null
        },
        { 
          id: 6, 
          name: 'Gallery', 
          icon: '🖼️', 
          component: 'Gallery',
          notification: null
        },
        { 
          id: 7, 
          name: 'Vision', 
          icon: '🎯', 
          component: 'Vision',
          notification: null
        },
        { 
          id: 8, 
          name: 'About', 
          icon: 'ℹ️', 
          component: 'About',
          notification: null
        }
      ]
    }
  },
  methods: {
    setAutoTheme() {
      this.setAutoTheme(this.isAuto)
    },
    selectComponent(componentName) {
      this.activeComponent = componentName;
      this.$emit('component-selected', componentName);
      
      // Close mobile sidebar after selection
      if (this.isMobile) {
        this.isMobileOpen = false;
      }
    },
    
    refreshData() {
      this.lastUpdateTime = new Date().toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
      });
      this.$emit('refresh-data');
      
      // Add visual feedback
      const button = event?.target;
      if (button) {
        button.classList.add('animate-pulse');
        setTimeout(() => {
          button.classList.remove('animate-pulse');
        }, 1000);
      }
    },
    
    toggleMobileSidebar() {
      this.isMobileOpen = !this.isMobileOpen;
    },
    
    closeMobileSidebar() {
      this.isMobileOpen = false;
    },
    
    checkMobile() {
      this.isMobile = window.innerWidth < 1024; // lg breakpoint
      if (!this.isMobile) {
        this.isMobileOpen = false;
      }
    },
    
    updateLastUpdateTime() {
      const now = new Date();
      this.lastUpdateTime = now.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit'
      });
    }
  },
  mounted() {
    // Set initial active component
    this.$emit('component-selected', this.activeComponent);
    
    // Setup mobile detection
    this.checkMobile();
    window.addEventListener('resize', this.checkMobile);
    
    // Update time every minute
    this.updateLastUpdateTime();
    setInterval(this.updateLastUpdateTime, 60000);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkMobile);
  }
}
</script>

<style scoped>
/* Custom scrollbar for sidebar */
aside nav::-webkit-scrollbar {
  width: 4px;
}

aside nav::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
}

aside nav::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #3b82f6, #8b5cf6);
  border-radius: 2px;
}

aside nav::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #2563eb, #7c3aed);
}

/* Glass morphism effect */
aside {
  background: linear-gradient(135deg, 
    rgba(15, 23, 42, 0.95) 0%,
    rgba(30, 41, 59, 0.9) 50%,
    rgba(30, 58, 138, 0.85) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

/* Mobile sidebar animation */
aside {
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 50;
}

@media (max-width: 1023px) {
  aside {
    transform: translateX(-100%);
  }
  
  aside.mobile-open {
    transform: translateX(0);
  }
}

/* Smooth hover effects */
button {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Gradient text effect */
.gradient-text {
  background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>