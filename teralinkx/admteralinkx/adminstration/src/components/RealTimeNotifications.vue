<template>
  <div class="fixed top-20 right-4 z-50 space-y-2 max-w-sm">
    <TransitionGroup name="notification">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 p-4 flex items-start gap-3"
      >
        <div class="flex-shrink-0">
          <svg v-if="notification.type === 'success'" class="w-6 h-6 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <svg v-else-if="notification.type === 'error'" class="w-6 h-6 text-rose-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <svg v-else-if="notification.type === 'warning'" class="w-6 h-6 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
          </svg>
          <svg v-else class="w-6 h-6 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-slate-900 dark:text-white">{{ notification.message }}</p>
          <p v-if="notification.details" class="text-xs text-slate-500 dark:text-slate-400 mt-1">{{ notification.details }}</p>
        </div>
        <button @click="removeNotification(notification.id)" class="flex-shrink-0 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { usePusher } from '../composables/usePusher'

export default {
  name: 'RealTimeNotifications',
  setup() {
    const { initPusher, subscribe, disconnect } = usePusher()
    const notifications = ref([])
    let notificationId = 0

    const addNotification = (data) => {
      const id = ++notificationId
      notifications.value.push({
        id,
        message: data.message || 'New notification',
        type: data.type || 'info',
        details: data.details || null
      })

      // Auto remove after 5 seconds
      setTimeout(() => {
        removeNotification(id)
      }, 5000)
    }

    const removeNotification = (id) => {
      const index = notifications.value.findIndex(n => n.id === id)
      if (index > -1) {
        notifications.value.splice(index, 1)
      }
    }

    onMounted(() => {
      // Initialize Pusher
      const userId = localStorage.getItem('userId') // Get from your auth system
      if (userId) {
        initPusher(userId)
        
        // Subscribe to admin channel for global notifications
        subscribe('admin-notifications', 'new-alert', (data) => {
          addNotification(data)
        })

        // Subscribe to user-specific channel
        subscribe(`user-${userId}`, 'new-alert', (data) => {
          addNotification(data)
        })
      }
    })

    onUnmounted(() => {
      disconnect()
    })

    return {
      notifications,
      removeNotification
    }
  }
}
</script>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
