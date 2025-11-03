<template>
  <aside class="w-64 bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900/80 text-white shadow-2xl flex flex-col h-screen fixed left-0 top-0 backdrop-blur-lg border-r border-slate-700/50">
    <!-- Header -->
    <div class="p-6 border-b border-slate-700/50 bg-slate-800/30 backdrop-blur-sm">
      <div class="flex items-center space-x-3">
        <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
          <span class="text-xl">🌊</span>
        </div>
        <div>
          <h1 class="text-lg font-bold text-white bg-gradient-to-r from-blue-400 to-purple-300 bg-clip-text text-transparent">
            Teralinkx Waves
          </h1>
          <p class="text-slate-400 text-xs mt-1 font-light">Analytics Platform</p>
        </div>
      </div>
    </div>
    
    <!-- Navigation Menu -->
    <nav class="flex-1 py-6 overflow-y-auto">
      <div class="px-4 space-y-1">
        <!-- Main Section -->
        <div class="px-3 py-3">
          <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider font-light">MAIN NAVIGATION</h3>
        </div>
        
        <button
          v-for="item in mainMenuItems"
          :key="item.id"
          @click="selectComponent(item.component)"
          class="w-full flex items-center px-4 py-3 text-slate-300 rounded-2xl transition-all duration-300 text-left group relative overflow-hidden"
          :class="{
            'bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-white shadow-lg border border-blue-500/30': activeComponent === item.component,
            'hover:bg-slate-700/50 hover:text-white hover:translate-x-2': activeComponent !== item.component
          }"
        >
          <!-- Active indicator -->
          <div 
            v-if="activeComponent === item.component"
            class="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-blue-400 to-purple-500 rounded-r-full"
          ></div>
          
          <span 
            class="text-lg mr-4 transition-all duration-300 group-hover:scale-110 relative z-10"
            :class="{ 
              'scale-110': activeComponent === item.component,
              'text-blue-400': activeComponent === item.component
            }"
          >
            {{ item.icon }}
          </span>
          <span class="font-medium flex-1 relative z-10" :class="{ 'text-white': activeComponent === item.component }">
            {{ item.name }}
          </span>
          <span 
            v-if="item.notification"
            class="bg-gradient-to-r from-red-500 to-pink-600 text-white text-xs rounded-full px-2 py-1 min-w-6 text-center shadow-lg relative z-10"
          >
            {{ item.notification }}
          </span>
        </button>

        <!-- Support Section -->
        <div class="px-3 py-3 mt-6">
          <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider font-light">SUPPORT</h3>
        </div>
        
        <button
          v-for="item in supportMenuItems"
          :key="item.id"
          @click="selectComponent(item.component)"
          class="w-full flex items-center px-4 py-3 text-slate-300 rounded-2xl transition-all duration-300 text-left group relative overflow-hidden"
          :class="{
            'bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-white shadow-lg border border-blue-500/30': activeComponent === item.component,
            'hover:bg-slate-700/50 hover:text-white hover:translate-x-2': activeComponent !== item.component
          }"
        >
          <!-- Active indicator -->
          <div 
            v-if="activeComponent === item.component"
            class="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-blue-400 to-purple-500 rounded-r-full"
          ></div>
          
          <span 
            class="text-lg mr-4 transition-all duration-300 group-hover:scale-110 relative z-10"
            :class="{ 
              'scale-110': activeComponent === item.component,
              'text-blue-400': activeComponent === item.component
            }"
          >
            {{ item.icon }}
          </span>
          <span class="font-medium relative z-10" :class="{ 'text-white': activeComponent === item.component }">
            {{ item.name }}
          </span>
        </button>
      </div>
    </nav>

    <!-- Footer Section -->
    <div class="p-4 border-t border-slate-700/50 bg-slate-800/30 backdrop-blur-sm">
      <!-- Refresh Button -->
      <button
        @click="refreshData"
        class="w-full flex items-center justify-center px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:from-blue-500 hover:to-purple-500 transition-all duration-300 shadow-lg hover:shadow-xl mb-4 group hover:scale-105"
      >
        <span class="group-hover:animate-spin mr-2 transition-transform duration-300">🔄</span>
        <span class="font-semibold">Refresh Data</span>
      </button>
      
      <!-- Quick Stats -->
      <div class="bg-slate-800/50 rounded-2xl p-4 mb-4 border border-slate-700/30 backdrop-blur-sm">
        <div class="flex justify-between items-center">
          <div class="text-slate-300">
            <div class="font-semibold text-sm text-white">System Status</div>
            <div class="flex items-center mt-2">
              <div class="w-2 h-2 bg-emerald-500 rounded-full mr-2 animate-pulse"></div>
              <span class="text-xs text-slate-400">All Systems Operational</span>
            </div>
          </div>
          <div class="text-right">
            <div class="text-slate-300 font-semibold text-sm">Last Update</div>
            <div class="text-blue-400 text-xs font-mono">{{ lastUpdateTime }}</div>
          </div>
        </div>
      </div>

      <!-- About Section -->
      <div class="text-xs text-slate-400 space-y-3">
        <div>
          <p class="font-semibold text-slate-300 mb-2 flex items-center">
            <span class="text-blue-400 mr-1">💡</span>
            Contribute
          </p>
          <p class="text-slate-500 font-light">Teralinkx Data Visualisation Platform</p>
        </div>
        
        <div>
          <p class="font-semibold text-slate-300 mb-2 flex items-center">
            <span class="text-blue-400 mr-1">ℹ️</span>
            About
          </p>
          <p class="text-slate-500 font-light">
            Maintained by <strong class="text-slate-300">Nomad Ghost</strong>
          </p>
          <a 
            href="https://millsmulla.onrender.com" 
            class="text-blue-400 hover:text-blue-300 transition-colors duration-200 block mt-1 font-light hover:underline"
            target="_blank"
          >
            millsmulla.onrender.com
          </a>
        </div>

        <!-- Version Info -->
        <div class="pt-3 border-t border-slate-700/50">
          <div class="flex justify-between items-center">
            <span class="text-slate-500 font-mono">v2.1.0</span>
            <span class="text-emerald-400 flex items-center text-xs">
              <div class="w-1.5 h-1.5 bg-emerald-400 rounded-full mr-1 animate-pulse"></div>
              Live
            </span>
          </div>
        </div>
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
export default {
  name: 'Sidebar',
  emits: ['component-selected', 'refresh-data'],
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
          notification: '12'
        },
        { 
          id: 3, 
          name: 'Transactions', 
          icon: '💳', 
          component: 'Transactions',
          notification: '3'
        },
        { 
          id: 4, 
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