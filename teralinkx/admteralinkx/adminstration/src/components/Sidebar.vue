<template>
  <div>
    <!-- Mobile Overlay -->
    <div 
      v-if="isMobileOpen && isMobile" 
      class="fixed inset-0 bg-black/60 backdrop-blur-sm lg:hidden"
      style="z-index: 45;"
      @click="$emit('close-mobile')"
    ></div>
    
    <!-- Sidebar -->
    <aside 
      class="bg-white dark:bg-slate-900 shadow-xl flex flex-col h-screen fixed left-0 top-0 border-r border-slate-200 dark:border-slate-800 transition-all duration-300"
      :class="{
        '-translate-x-full lg:translate-x-0': !isMobileOpen,
        'translate-x-0': isMobileOpen,
        'w-56': !isCollapsed,
        'w-16': isCollapsed
      }"
      style="z-index: 50;"
    >
      <!-- Header -->
      <div class="p-5 border-b border-slate-200 dark:border-slate-700 bg-gradient-to-r from-blue-500/10 to-purple-600/10">
        <div v-if="!isCollapsed" class="flex items-center space-x-3">
          <img src="/src/assets/logo/teralinkx2.png" alt="Teralinkx Logo" class="h-10 w-auto object-contain" />
          <div>
            <h1 class="text-base font-bold text-slate-900 dark:text-white">TERALINKX</h1>
            <p class="text-slate-500 dark:text-slate-400 text-xs font-medium">Admin Panel</p>
          </div>
        </div>
        <div v-else class="flex justify-center">
          <img src="/src/assets/logo/teralinkx2.png" alt="Logo" class="h-10 w-10 object-contain" />
        </div>
      </div>
      
      <!-- Quick Stats -->
      <div v-if="!isCollapsed" class="p-4 border-b border-slate-200 dark:border-slate-800">
        <div class="grid grid-cols-2 gap-2">
          <div class="bg-blue-50 dark:bg-blue-500/10 rounded-lg p-2">
            <p class="text-xs text-blue-600 dark:text-blue-400 font-medium">Active Users</p>
            <p class="text-lg font-bold text-blue-700 dark:text-blue-300">{{ stats.activeUsers }}</p>
          </div>
          <div class="bg-emerald-50 dark:bg-emerald-500/10 rounded-lg p-2">
            <p class="text-xs text-emerald-600 dark:text-emerald-400 font-medium">Sessions</p>
            <p class="text-lg font-bold text-emerald-700 dark:text-emerald-300">{{ stats.activeSessions }}</p>
          </div>
          <div class="bg-purple-50 dark:bg-purple-500/10 rounded-lg p-2">
            <p class="text-xs text-purple-600 dark:text-purple-400 font-medium">Devices</p>
            <p class="text-lg font-bold text-purple-700 dark:text-purple-300">{{ stats.activeDevices }}</p>
          </div>
          <div class="bg-amber-50 dark:bg-amber-500/10 rounded-lg p-2">
            <p class="text-xs text-amber-600 dark:text-amber-400 font-medium">Refunds</p>
            <p class="text-lg font-bold text-amber-700 dark:text-amber-300">{{ stats.pendingRefunds }}</p>
          </div>
        </div>
      </div>
      
      <!-- Navigation Menu -->
      <nav class="flex-1 py-6 overflow-y-auto">
        <div class="px-4 space-y-1">
          <!-- Overview Section -->
          <div v-if="!isCollapsed" class="px-3 py-2">
            <h3 class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide">Overview</h3>
          </div>
          <button
            v-for="item in overviewItems"
            :key="item.id"
            @click="selectComponent(item.component)"
            :title="isCollapsed ? item.name : ''"
            class="w-full flex items-center rounded-xl transition-all duration-200 text-left group text-sm relative overflow-hidden"
            :class="[
              isCollapsed ? 'px-2 py-2.5 justify-center' : 'px-3 py-2.5',
              activeComponent === item.component
                ? 'font-medium shadow-sm'
                : 'hover:bg-slate-100 dark:hover:bg-slate-800'
            ]"
            :style="activeComponent === item.component ? `background: ${item.color}; color: white;` : ''"
          >
            <span :class="isCollapsed ? '' : 'mr-3'" v-html="item.icon" :style="activeComponent === item.component ? 'color: white;' : `color: ${item.color}`"></span>
            <span v-if="!isCollapsed" class="flex-1">{{ item.name }}</span>
          </button>

          <!-- User Management Section -->
          <div v-if="!isCollapsed" class="px-3 py-2 mt-4">
            <h3 class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide">User Management</h3>
          </div>
          <div v-else class="border-t border-slate-200 dark:border-slate-700 my-2"></div>
          <button
            v-for="item in userManagementItems"
            :key="item.id"
            @click="selectComponent(item.component)"
            :title="isCollapsed ? item.name : ''"
            class="w-full flex items-center rounded-xl transition-all duration-200 text-left group text-sm relative overflow-hidden"
            :class="[
              isCollapsed ? 'px-2 py-2.5 justify-center' : 'px-3 py-2.5',
              activeComponent === item.component
                ? 'font-medium shadow-sm'
                : 'hover:bg-slate-100 dark:hover:bg-slate-800'
            ]"
            :style="activeComponent === item.component ? `background: ${item.color}; color: white;` : ''"
          >
            <span :class="isCollapsed ? '' : 'mr-3'" v-html="item.icon" :style="activeComponent === item.component ? 'color: white;' : `color: ${item.color}`"></span>
            <span v-if="!isCollapsed" class="flex-1">{{ item.name }}</span>
            <span 
              v-if="!isCollapsed && getBadgeCount(item.component) > 0"
              class="text-xs rounded-full px-2 py-0.5 min-w-5 text-center font-bold shadow-sm"
              :style="activeComponent === item.component ? 'background-color: white; color: ' + item.color : `background-color: ${item.color}; color: white;`"
            >
              {{ getBadgeCount(item.component) }}
            </span>
          </button>

          <!-- Products & Services Section -->
          <div v-if="!isCollapsed" class="px-3 py-2 mt-4">
            <h3 class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide">Products & Services</h3>
          </div>
          <div v-else class="border-t border-slate-200 dark:border-slate-700 my-2"></div>
          <button
            v-for="item in productsItems"
            :key="item.id"
            @click="selectComponent(item.component)"
            :title="isCollapsed ? item.name : ''"
            class="w-full flex items-center rounded-xl transition-all duration-200 text-left group text-sm relative overflow-hidden"
            :class="[
              isCollapsed ? 'px-2 py-2.5 justify-center' : 'px-3 py-2.5',
              activeComponent === item.component
                ? 'font-medium shadow-sm'
                : 'hover:bg-slate-100 dark:hover:bg-slate-800'
            ]"
            :style="activeComponent === item.component ? `background: ${item.color}; color: white;` : ''"
          >
            <span :class="isCollapsed ? '' : 'mr-3'" v-html="item.icon" :style="activeComponent === item.component ? 'color: white;' : `color: ${item.color}`"></span>
            <span v-if="!isCollapsed" class="flex-1">{{ item.name }}</span>
          </button>

          <!-- Financial Section -->
          <div v-if="!isCollapsed" class="px-3 py-2 mt-4">
            <h3 class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide">Financial</h3>
          </div>
          <div v-else class="border-t border-slate-200 dark:border-slate-700 my-2"></div>
          <button
            v-for="item in financialItems"
            :key="item.id"
            @click="selectComponent(item.component)"
            :title="isCollapsed ? item.name : ''"
            class="w-full flex items-center rounded-xl transition-all duration-200 text-left group text-sm relative overflow-hidden"
            :class="[
              isCollapsed ? 'px-2 py-2.5 justify-center' : 'px-3 py-2.5',
              activeComponent === item.component
                ? 'font-medium shadow-sm'
                : 'hover:bg-slate-100 dark:hover:bg-slate-800'
            ]"
            :style="activeComponent === item.component ? `background: ${item.color}; color: white;` : ''"
          >
            <span :class="isCollapsed ? '' : 'mr-3'" v-html="item.icon" :style="activeComponent === item.component ? 'color: white;' : `color: ${item.color}`"></span>
            <span v-if="!isCollapsed" class="flex-1">{{ item.name }}</span>
            <span 
              v-if="!isCollapsed && getBadgeCount(item.component) > 0"
              class="text-xs rounded-full px-2 py-0.5 min-w-5 text-center font-bold shadow-sm"
              :style="activeComponent === item.component ? 'background-color: white; color: ' + item.color : `background-color: ${item.color}; color: white;`"
            >
              {{ getBadgeCount(item.component) }}
            </span>
          </button>

          <!-- Network Section -->
          <div v-if="!isCollapsed" class="px-3 py-2 mt-4">
            <h3 class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide">Network</h3>
          </div>
          <div v-else class="border-t border-slate-200 dark:border-slate-700 my-2"></div>
          <button
            v-for="item in networkItems"
            :key="item.id"
            @click="selectComponent(item.component)"
            :title="isCollapsed ? item.name : ''"
            class="w-full flex items-center rounded-xl transition-all duration-200 text-left group text-sm relative overflow-hidden"
            :class="[
              isCollapsed ? 'px-2 py-2.5 justify-center' : 'px-3 py-2.5',
              activeComponent === item.component
                ? 'font-medium shadow-sm'
                : 'hover:bg-slate-100 dark:hover:bg-slate-800'
            ]"
            :style="activeComponent === item.component ? `background: ${item.color}; color: white;` : ''"
          >
            <span :class="isCollapsed ? '' : 'mr-3'" v-html="item.icon" :style="activeComponent === item.component ? 'color: white;' : `color: ${item.color}`"></span>
            <span v-if="!isCollapsed" class="flex-1">{{ item.name }}</span>
          </button>

          <!-- Support Section -->
          <div v-if="!isCollapsed" class="px-3 py-2 mt-4">
            <h3 class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide">Support</h3>
          </div>
          <div v-else class="border-t border-slate-200 dark:border-slate-700 my-2"></div>
          <button
            v-for="item in supportMenuItems"
            :key="item.id"
            @click="selectComponent(item.component)"
            :title="isCollapsed ? item.name : ''"
            class="w-full flex items-center rounded-xl transition-all duration-200 text-left group text-sm"
            :class="[
              isCollapsed ? 'px-2 py-2.5 justify-center' : 'px-3 py-2.5',
              activeComponent === item.component
                ? 'bg-gradient-to-r from-slate-500/10 to-slate-600/10 text-slate-700 dark:text-slate-300 font-medium shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
            ]"
          >
            <span :class="isCollapsed ? '' : 'mr-3'" v-html="item.icon"></span>
            <span v-if="!isCollapsed">{{ item.name }}</span>
          </button>
        </div>
      </nav>

      <!-- Footer Section -->
      <div class="border-t border-slate-200 dark:border-slate-800">
        <!-- Collapse Button -->
        <button @click="toggleSidebar" class="w-full p-2 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors flex items-center justify-center text-slate-600 dark:text-slate-400 hidden lg:flex border-b border-slate-200 dark:border-slate-800">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="isCollapsed ? 'M13 5l7 7-7 7M5 5l7 7-7 7' : 'M11 19l-7-7 7-7M19 19l-7-7 7-7'" />
          </svg>
        </button>
        
        <div class="p-4 space-y-3">
        <!-- Theme Toggle -->
        <div v-if="!isCollapsed" class="bg-gradient-to-r from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-700 rounded-xl p-3 shadow-sm">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">Theme</span>
            <button
              @click="toggleTheme"
              class="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
            >
              <svg v-if="isDark" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m8.66-12.66l-.71.71M4.05 19.95l-.7-.71M21 12h-1M4 12H3m16.95 7.05l-.7-.71M4.05 4.05l.7.71M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a8 8 0 106.32 12.906 7.5 7.5 0 01-6.32-12.905z" />
              </svg>
            </button>
          </div>
          <label class="flex items-center cursor-pointer">
            <input
              type="checkbox"
              v-model="isAuto"
              @change="handleAutoThemeChange"
              class="w-4 h-4 rounded border-slate-300 dark:border-slate-600 text-blue-600 focus:ring-blue-500 focus:ring-offset-0"
            />
            <span class="ml-2 text-xs text-slate-600 dark:text-slate-400">Auto (6AM-6PM)</span>
          </label>
        </div>
        <div v-else class="flex justify-center">
          <button
            @click="toggleTheme"
            class="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
          >
            <svg v-if="isDark" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m8.66-12.66l-.71.71M4.05 19.95l-.7-.71M21 12h-1M4 12H3m16.95 7.05l-.7-.71M4.05 4.05l.7.71M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a8 8 0 106.32 12.906 7.5 7.5 0 01-6.32-12.905z" />
            </svg>
          </button>
        </div>

        <!-- Status -->
        <div v-if="!isCollapsed" class="flex items-center justify-between text-xs">
          <div class="flex items-center">
            <div class="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-1.5 animate-pulse"></div>
            <span class="text-slate-600 dark:text-slate-400">Online</span>
          </div>
          <span class="text-slate-500 dark:text-slate-500 font-mono">v2.1.0</span>
        </div>
        <div v-else class="flex justify-center">
          <div class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
        </div>
      </div>
      </div>
    </aside>
  </div>
</template>

<script>
import { useTheme } from '../composables/useTheme'

export default {
  name: 'Sidebar',
  props: {
    stats: {
      type: Object,
      default: () => ({
        activeUsers: 0,
        activeSessions: 0,
        activeDevices: 0,
        pendingRefunds: 0
      })
    },
    isMobileOpen: {
      type: Boolean,
      default: false
    }
  },
  emits: ['component-selected', 'refresh-data', 'close-mobile', 'sidebar-toggle'],
  setup() {
    const { isDark, isAuto, toggleTheme, setAutoTheme } = useTheme()
    
    const handleAutoThemeChange = () => {
      setAutoTheme(isAuto.value)
    }
    
    return { isDark, isAuto, toggleTheme, setAutoTheme, handleAutoThemeChange }
  },
  data() {
    return {
      activeComponent: 'Dashboard',
      isMobile: false,
      isCollapsed: false,
      overviewItems: [
        { id: 1, name: 'Dashboard', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/></svg>', component: 'Dashboard', color: '#3b82f6' },
        { id: 2, name: 'Analytics', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>', component: 'Analytics', color: '#8b5cf6' },
      ],
      userManagementItems: [
        { id: 3, name: 'Clients', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>', component: 'Clients', color: '#10b981' },
        { id: 4, name: 'Users', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>', component: 'Users', color: '#a855f7' },
        { id: 5, name: 'Devices', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/></svg>', component: 'Devices', color: '#06b6d4' },
        { id: 6, name: 'Sessions', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>', component: 'Sessions', color: '#f97316' },
      ],
      productsItems: [
        { id: 7, name: 'Packages', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/></svg>', component: 'Packages', color: '#6366f1' },
        { id: 8, name: 'Vouchers', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/></svg>', component: 'Vouchers', color: '#ec4899' },
        { id: 9, name: 'Coupons', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/></svg>', component: 'Coupons', color: '#f43f5e' },
        { id: 10, name: 'Promotions', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-5.5-2.5l7.51-3.49L17.5 6.5 9.99 9.99 6.5 17.5zm5.5-6.6c.61 0 1.1.49 1.1 1.1s-.49 1.1-1.1 1.1-1.1-.49-1.1-1.1.49-1.1 1.1-1.1z"/></svg>', component: 'Promotions', color: '#f59e0b' },
      ],
      financialItems: [
        { id: 11, name: 'Transactions', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/></svg>', component: 'Transactions', color: '#14b8a6' },
        { id: 12, name: 'Refunds', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg>', component: 'Refunds', color: '#ef4444' }
      ],
      networkItems: [
        { id: 13, name: 'Locations', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>', component: 'Locations', color: '#22c55e' },
      ],
      supportMenuItems: [
        { id: 14, name: 'Documentation', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>', component: 'Auth' },
        { id: 15, name: 'Help Center', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/></svg>', component: 'Gallery' },
        { id: 16, name: 'System Info', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M13 2.05v3.03c3.39.49 6 3.39 6 6.92 0 .9-.18 1.75-.48 2.54l2.6 1.53c.56-1.24.88-2.62.88-4.07 0-5.18-3.95-9.45-9-9.95zM12 19c-3.87 0-7-3.13-7-7 0-3.53 2.61-6.43 6-6.92V2.05c-5.06.5-9 4.76-9 9.95 0 5.52 4.47 10 9.99 10 3.31 0 6.24-1.61 8.06-4.09l-2.6-1.53C16.17 17.98 14.21 19 12 19z"/></svg>', component: 'Vision' },
        { id: 17, name: 'About', icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>', component: 'About' }
      ]
    }
  },
  methods: {
    selectComponent(componentName) {
      this.activeComponent = componentName;
      this.$emit('component-selected', componentName);
      if (this.isMobile) {
        this.$emit('close-mobile');
      }
    },
    
    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed;
      this.$emit('sidebar-toggle', this.isCollapsed);
    },
    
    getBadgeCount(component) {
      const badges = {
        'Users': this.stats.activeUsers,
        'Sessions': this.stats.activeSessions,
        'Devices': this.stats.activeDevices,
        'Refunds': this.stats.pendingRefunds
      }
      return badges[component] || 0
    },
    
    checkMobile() {
      this.isMobile = window.innerWidth < 1024;
    }
  },
  mounted() {
    this.$emit('component-selected', this.activeComponent);
    this.checkMobile();
    window.addEventListener('resize', this.checkMobile);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkMobile);
  }
}
</script>

<style scoped>
aside nav::-webkit-scrollbar {
  width: 3px;
}

aside nav::-webkit-scrollbar-track {
  background: transparent;
}

aside nav::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #3b82f6, #8b5cf6);
  border-radius: 2px;
  transition: background 0.3s ease;
}

aside nav::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #2563eb, #7c3aed);
}

button {
  transition: all 0.2s ease;
}

/* Smooth animations */
aside {
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

aside * {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
</style>
