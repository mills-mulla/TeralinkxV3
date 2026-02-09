<template>
  <div v-if="announcements.length > 0" class="w-full p-4">
    <ul class="space-y-4 max-h-60 overflow-y-auto pr-2">
      <li
        v-for="announcement in announcements"
        :key="announcement.id"
        :class="[
          'p-3 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 border-l-4 backdrop-blur-sm',
          getPriorityClass(announcement.priority),
          'bg-white/80 dark:bg-gray-800/80'
        ]"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-2 mb-2">
              <span class="text-lg">{{ getAnnouncementIcon(announcement.notification_type) }}</span>
              <h2 class="font-semibold text-sm text-gray-900 dark:text-white">
                {{ announcement.title }}
              </h2>
              <span :class="getScopeBadge(announcement.scope)" class="text-xs px-2 py-1 rounded-full font-medium">
                {{ announcement.scope.toUpperCase() }}
              </span>
            </div>
            
            <p class="text-sm text-gray-700 dark:text-gray-300 mb-2 whitespace-pre-line" v-html="decodeHtml(announcement.message)">
            </p>
            
            <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
              <div class="flex items-center space-x-4">
                <span class="flex items-center gap-1">
                  <i class="fas fa-clock"></i>
                  {{ formatDate(announcement.created_at) }}
                </span>
                <span v-if="announcement.expires_at" class="flex items-center gap-1 text-orange-600 dark:text-orange-400">
                  <i class="fas fa-hourglass-half"></i>
                  Expires {{ formatDate(announcement.expires_at) }}
                </span>
              </div>
              
              <button 
                v-if="announcement.action_url" 
                @click="handleAction(announcement)"
                class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium"
              >
                {{ announcement.action_text || 'Learn More' }} →
              </button>
            </div>
          </div>
          
          <button 
            @click="dismissAnnouncement(announcement.id)"
            class="ml-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            title="Dismiss"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const announcements = ref([])

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short'
  })
}

function getPriorityClass(priority) {
  const priorityMap = {
    'low': 'border-blue-500 bg-blue-50/50 dark:bg-blue-900/20',
    'medium': 'border-yellow-500 bg-yellow-50/50 dark:bg-yellow-900/20', 
    'high': 'border-orange-500 bg-orange-50/50 dark:bg-orange-900/20',
    'urgent': 'border-red-500 bg-red-50/50 dark:bg-red-900/20'
  }
  return priorityMap[priority] || priorityMap['medium']
}

function getScopeBadge(scope) {
  const scopeMap = {
    'global': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'client': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'user': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  }
  return scopeMap[scope] || scopeMap['global']
}

function getAnnouncementIcon(type) {
  const iconMap = {
    'announcement': '📢',
    'system': '⚙️',
    'maintenance': '🔧',
    'promotional': '🎉',
    'security': '🔒',
    'billing': '💳'
  }
  return iconMap[type] || '📢'
}

function handleAction(announcement) {
  if (announcement.action_url) {
    if (announcement.action_url.startsWith('http')) {
      window.open(announcement.action_url, '_blank')
    } else {
      window.location.href = announcement.action_url
    }
  }
}

function dismissAnnouncement(announcementId) {
  announcements.value = announcements.value.filter(a => a.id !== announcementId)
  markAsRead(announcementId)
}

async function markAsRead(notificationId) {
  try {
    await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/notifications/${notificationId}/read/`, {
      method: 'POST',
      headers: authStore.authHeaders
    })
  } catch (error) {
    console.error('Failed to mark announcement as read:', error)
  }
}

async function fetchAnnouncements() {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/notifications/announcements/`, {
      headers: authStore.authHeaders
    })

    if (response.ok) {
      const data = await response.json()
      announcements.value = Array.isArray(data) ? data : []
    }
  } catch (error) {
    console.error('❌ Failed to fetch announcements:', error)
    announcements.value = []
  }
}

function decodeHtml(html) {
  const txt = document.createElement('textarea')
  txt.innerHTML = html
  return txt.value
}

onMounted(() => {
  fetchAnnouncements()
})
</script>
