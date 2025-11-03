<template>
  
  <nav class="fixed top-0 z-50 w-full bg-white dark:bg-gray-900 px-4 p-2 border-b border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-300">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <!-- Logo -->
      <div class="flex items-center space-x-2 cursor-pointer select-none">
        <img
          :src="logoSrc"
          alt="Logo"
          class="h-12 w-auto object-contain"
        />
        <span class="text-gray-900  dark:text-white font-bold text-sm tracking-wide">TERALINKX WAVES</span>
      </div>

      <!-- Right Side Icons -->
      <div class="flex items-center space-x-4 relative">
        <!-- Theme Toggle -->
        <button
          @click="toggleTheme"
          class="text-green-600 dark:text-yellow-300 hover:text-green-700 dark:hover:text-yellow-400 transition"
          aria-label="Toggle theme"
        >
          <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 3v1m0 16v1m8.66-12.66l-.71.71M4.05 19.95l-.7-.71M21 12h-1M4 12H3m16.95 7.05l-.7-.71M4.05 4.05l.7.71M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a8 8 0 106.32 12.906 7.5 7.5 0 01-6.32-12.905z" />
          </svg>
        </button>

        <!-- Notifications Button -->
        <button
          aria-label="Notifications"
          class="text-green-600 dark:text-green-300 hover:text-green-700 dark:hover:text-green-400"
          @click="toggleNotificationDropdown"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        </button>

        <!-- Notification Dropdown -->
        <div class="relative">
          <transition name="fade">
            <div
              v-if="notificationDropdownOpen"
              class="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded shadow-lg z-50"
            >
              <ul class="text-sm text-gray-700 dark:text-gray-100 divide-y divide-gray-100 dark:divide-gray-700">
                <li v-for="notification in notifications" :key="notification.id">
                  <button class="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700">
                    {{ notification.message }}
                  </button>
                </li>
                <li v-if="notifications.length === 0" class="px-4 py-2 text-gray-500">
                  No notifications
                </li>
              </ul>
            </div>
          </transition>
        </div>

        <!-- Dropdown Menu -->
        <div class="relative">
          <button
            @click="toggleDropdown"
            aria-label="Toggle menu"
            class="text-green-600 dark:text-green-300 hover:text-green-700 dark:hover:text-green-400"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <!-- Dropdown Items -->
          <transition name="fade">

            <div
              v-if="menuOpen"
              class="absolute right-0 mt-2 w-44 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded shadow-lg z-50"
            >
              <ul class="text-sm text-gray-700 dark:text-gray-100 divide-y divide-gray-100 dark:divide-gray-700">
                <li>
                  <button @click="goTo('/dashboard')" class="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700">
                    Dashboard
                  </button>
                </li>
                <li>
                  <button @click="goTo('/usevoucher')" class="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700">
                    Use Voucher
                  </button>
                </li>
                <li>
                  <button @click="goTo('/profile')" class="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700">
                    Profile
                  </button>
                </li>
                <li>
                  <button @click="goTo('/settings')" class="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700">
                    Settings
                  </button>
                </li>
                <li>
                  <button @click="logout()" class="w-full text-left px-4 py-2 text-red-600 hover:bg-gray-50 dark:hover:bg-gray-700">
                    Logout
                  </button>
                </li>
              </ul>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import logoImage from '@/assets/teralinkx2.png'
import { useCsrfTokenStore } from '@/stores/useCsrf'


const router = useRouter()

const isDark = ref(false)
const menuOpen = ref(false)
const logoSrc = logoImage

const toggleDropdown = () => {
  menuOpen.value = !menuOpen.value
}

const logout = async () => {
  const token = localStorage.getItem('authToken')
  const boundMac = sessionStorage.getItem('hs_mac') || localStorage.getItem('hs_mac')
  const boundIp = sessionStorage.getItem('hs_ip') || localStorage.getItem('hs_ip')

  if (!boundMac || !boundIp) {
    console.error('IP or MAC address not found')
    return
  }

  const csrfStore = useCsrfTokenStore()
  await csrfStore.fetchCsrf()

  const payload = {
    bound_mac: boundMac,
    bound_ip: boundIp
  }

  try {
    const disconnect = () =>
      axios.post(`${import.meta.env.VITE_API_PROD_URL}/api/disconnect/`, payload, {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfStore.csrfToken,
          Authorization: `Token ${token}`
        }
      })

    const revokeToken = () =>
      axios.post(`${import.meta.env.VITE_API_PROD_URL}/api/logout/`, {}, {
        headers: {
          Authorization: `Token ${token}`
        }
      })

    await Promise.allSettled([disconnect(), revokeToken()])

    localStorage.clear()
    sessionStorage.clear()
    window.location.href = '/'
  } catch (error) {
    console.error('Logout error:', error)
    localStorage.clear()
    sessionStorage.clear()
    window.location.href = '/'
  }
}

const goTo = (path) => {
  menuOpen.value = false
  router.push(path)
}

const applyTheme = (dark) => {
  const root = document.documentElement
  if (dark) {
    root.classList.add('dark')
    localStorage.setItem('theme', 'dark')
    isDark.value = true
  } else {
    root.classList.remove('dark')
    localStorage.setItem('theme', 'light')
    isDark.value = false
  }
}

const detectTimeTheme = () => {
  const hour = new Date().getHours()
  return hour < 6 || hour >= 18  // Dark mode from 6PM to 6AM
}

const toggleTheme = () => {
  applyTheme(!isDark.value)
  localStorage.setItem('themeOverride', 'true') // User manually toggled theme
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  const userOverridden = localStorage.getItem('themeOverride') === 'true'

  if (saved && userOverridden) {
    applyTheme(saved === 'dark')
  } else {
    // No manual override: apply time-based theme
    const darkByTime = detectTimeTheme()
    applyTheme(darkByTime)
    localStorage.removeItem('themeOverride')  // Reset override so auto works next time
  }
})

// Notifications

const notificationDropdownOpen = ref(false);
const notifications = ref([]); // Array to store fetched notifications

const toggleNotificationDropdown = () => {
  notificationDropdownOpen.value = !notificationDropdownOpen.value;

  // Fetch notifications when the dropdown is opened
  if (notificationDropdownOpen.value) {
    fetchNotifications();
  }
};

const fetchNotifications = async () => {
  try {
    
    const response = await fetch(`${import.meta.env.VITE_API_PROD_URL}/api/notifications/?account=${localStorage.getItem('account')}`,
      {
        headers: {
          Authorization: `Token ${localStorage.getItem('authToken')}`,
        },
      }
    ); 
    if (response.ok) {
      const data = await response.json();
      notifications.value = data.notifications; // Set notifications data; make sure you're accessing the correct field
    } else {
      console.error('Failed to fetch notifications');
    }
  } catch (error) {
    console.error('Error fetching notifications:', error);
  }
};

</script>


<style scoped >
.fade-enter-active,.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
