<template>
  <nav class="fixed top-0 z-50 w-full backdrop-blur-lg bg-gradient-to-r from-blue-50/30 to-indigo-100/30 dark:from-gray-900/30 dark:to-gray-800/30">
    <div class="max-w-7xl mx-auto flex items-center justify-between px-4 py-2">
      <!-- Logo -->
      <div class="flex items-center space-x-2">
        <img :src="logoSrc" alt="Logo" class="h-12 w-auto object-contain" />
        <span class="text-gray-900 dark:text-white font-bold text-sm tracking-wide drop-shadow-sm">TERALINKX WAVES</span>
      </div>

      <!-- Actions -->
      <div class="flex items-center space-x-3">
        <!-- Navigation Links -->
        <div class="hidden md:flex items-center space-x-1">
          <router-link
            to="/dashboard"
            class="flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-white/30 dark:hover:bg-gray-700/30 transition-all duration-200"
            :class="{ 'bg-white/40 dark:bg-gray-700/40 text-blue-600 dark:text-blue-400': $route.path === '/dashboard' }"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
            </svg>
            <span class="text-sm font-medium">Dashboard</span>
          </router-link>
          
          <router-link
            to="/profile"
            class="flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-white/30 dark:hover:bg-gray-700/30 transition-all duration-200"
            :class="{ 'bg-white/40 dark:bg-gray-700/40 text-blue-600 dark:text-blue-400': $route.path === '/profile' }"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
            <span class="text-sm font-medium">Profile</span>
          </router-link>
          
          <router-link
            to="/settings"
            class="flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-white/30 dark:hover:bg-gray-700/30 transition-all duration-200"
            :class="{ 'bg-white/40 dark:bg-gray-700/40 text-blue-600 dark:text-blue-400': $route.path === '/settings' }"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11.03L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.22,8.95 2.27,9.22 2.46,9.37L4.57,11.03C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.22,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.68 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"/>
            </svg>
            <span class="text-sm font-medium">Settings</span>
          </router-link>
          
          <router-link
            to="/rewards"
            class="flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-white/30 dark:hover:bg-gray-700/30 transition-all duration-200"
            :class="{ 'bg-white/40 dark:bg-gray-700/40 text-purple-600 dark:text-purple-400': $route.path === '/rewards' }"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12A6,6 0 0,0 12,6M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8Z"/>
            </svg>
            <span class="text-sm font-medium">Rewards</span>
          </router-link>
        </div>

        <!-- Theme Toggle -->
        <button
          @click="toggleTheme"
          class="p-2 rounded-lg bg-gradient-to-r from-blue-500/90 to-purple-600/90 backdrop-blur-sm text-white hover:from-blue-600 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl border border-white/20"
        >
          <svg v-if="isDark" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m8.66-12.66l-.71.71M4.05 19.95l-.7-.71M21 12h-1M4 12H3m16.95 7.05l-.7-.71M4.05 4.05l.7.71M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <svg v-else class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a8 8 0 106.32 12.906 7.5 7.5 0 01-6.32-12.905z" />
          </svg>
        </button>

        <!-- Notifications -->
        <div class="relative">
          <button
            @click="toggleNotifications"
            class="relative p-2 rounded-lg bg-gradient-to-r from-green-500/90 to-emerald-600/90 backdrop-blur-sm text-white hover:from-green-600 hover:to-emerald-700 transition-all duration-300 shadow-lg hover:shadow-xl border border-white/20"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span v-if="unreadCount > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold shadow-lg">
              {{ unreadCount > 9 ? '9+' : unreadCount }}
            </span>
          </button>

          <!-- Notifications Dropdown -->
          <div v-if="showNotifications" class="absolute right-0 mt-2 w-300 backdrop-blur-xl bg-white/80 dark:bg-gray-800/80 border border-white/30 dark:border-gray-700/30 rounded-xl shadow-2xl z-50">
            <div class="px-4 py-3 border-b border-white/20 dark:border-gray-700/20">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white">Notifications</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ unreadCount }} unread</p>
            </div>
            
            <div class="max-h-80 overflow-y-auto">
              <div v-for="notification in notifications?.slice(0, 5) || []" :key="notification.id">
                <button @click="markAsRead(notification.id)" class="w-full text-left px-4 py-3 hover:bg-white/30 dark:hover:bg-gray-700/30 transition-colors">
                  <div class="flex space-x-3">
                    <span class="text-lg">🔔</span>
                    <div class="flex-1">
                      <p class="text-sm font-medium text-gray-900 dark:text-white">System Notification</p>
                      <p class="text-xs text-gray-600 dark:text-gray-300 mt-1">
                        {{ notification.message.substring(0, 100) }}...
                      </p>
                      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {{ new Date(notification.created_at).toLocaleDateString() }}
                      </p>
                    </div>
                    <div v-if="!notification.is_read" class="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                  </div>
                </button>
              </div>
              
              <div v-if="!notifications?.length" class="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                <p class="text-sm">No notifications</p>
              </div>
              
              <div v-if="notifications?.length > 0" class="border-t border-white/20 dark:border-gray-700/20">
                <button @click="goTo('/notifications')" class="w-full text-left px-4 py-2 text-blue-600 dark:text-blue-400 hover:bg-white/30 dark:hover:bg-gray-700/30 transition-colors">
                  View all notifications
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Mobile Menu -->
        <div class="relative md:hidden">
          <button
            @click="toggleMenu"
            class="p-2 rounded-lg bg-gradient-to-r from-indigo-500/90 to-purple-600/90 backdrop-blur-sm text-white hover:from-indigo-600 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl border border-white/20"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <!-- Mobile Menu Dropdown -->
          <div v-if="showMenu" class="absolute right-0 mt-2 w-44 backdrop-blur-xl bg-white/80 dark:bg-gray-800/80 border border-white/30 dark:border-gray-700/30 rounded-xl shadow-2xl z-50">
            <div class="py-1">
              <button @click="goTo('/dashboard')" class="w-full flex items-center space-x-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-white/30 dark:hover:bg-gray-700/30 transition-colors">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
                </svg>
                <span>Dashboard</span>
              </button>
              <button @click="goTo('/usevoucher')" class="w-full flex items-center space-x-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-white/30 dark:hover:bg-gray-700/30 transition-colors">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <span>Use Voucher</span>
              </button>
              <button @click="goTo('/profile')" class="w-full flex items-center space-x-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-white/30 dark:hover:bg-gray-700/30 transition-colors">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
                <span>Profile</span>
              </button>
              <button @click="goTo('/settings')" class="w-full flex items-center space-x-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-white/30 dark:hover:bg-gray-700/30 transition-colors">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11.03L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.22,8.95 2.27,9.22 2.46,9.37L4.57,11.03C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.22,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.68 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"/>
                </svg>
                <span>Settings</span>
              </button>
              <button @click="goTo('/rewards')" class="w-full flex items-center space-x-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-white/30 dark:hover:bg-gray-700/30 transition-colors">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12A6,6 0 0,0 12,6M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8Z"/>
                </svg>
                <span>Rewards</span>
              </button>
              <div class="border-t border-white/20 dark:border-gray-700/20 my-1"></div>
              <button @click="logout()" class="w-full flex items-center space-x-2 px-4 py-2 text-red-600 hover:bg-red-50/50 dark:hover:bg-red-900/20 transition-colors">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M16 17v-3H9v-4h7V7l5 5-5 5M14 2a2 2 0 012 2v2h-2V4H4v16h10v-2h2v2a2 2 0 01-2 2H4a2 2 0 01-2-2V4a2 2 0 012-2h10z"/>
                </svg>
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import logoImage from '@/assets/teralinkx2.png'
import { useDashboardStore } from '@/stores/dashboard'
import { api } from '@/services/api'

const router = useRouter()
const dashboardStore = useDashboardStore()
const { notifications } = storeToRefs(dashboardStore)

const isDark = ref(false)
const showNotifications = ref(false)
const showMenu = ref(false)
const logoSrc = logoImage

const unreadCount = computed(() => {
  return notifications.value?.filter(n => !n.is_read)?.length || 0
})

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  showMenu.value = false
}

const toggleMenu = () => {
  showMenu.value = !showMenu.value
  showNotifications.value = false
}

const markAsRead = async (notificationId) => {
  try {
    const response = await api.post(`/api/notifications/${notificationId}/read/`)
    
    if (response.status === 200) {
      await dashboardStore.fetchDashboardData()
      showNotifications.value = false
    }
  } catch (error) {
    console.error('Error marking notification as read:', error)
  }
}

const logout = async () => {
  try {
    await api.post('/api/logout/')
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    localStorage.clear()
    sessionStorage.clear()
    window.location.href = '/'
  }
}

const goTo = (path) => {
  showMenu.value = false
  showNotifications.value = false
  router.push(path)
}

const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showNotifications.value = false
    showMenu.value = false
  }
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  if (saved) {
    isDark.value = saved === 'dark'
    document.documentElement.classList.toggle('dark', isDark.value)
  } else {
    const hour = new Date().getHours()
    isDark.value = hour >= 18 || hour < 6
    document.documentElement.classList.toggle('dark', isDark.value)
  }
  
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>