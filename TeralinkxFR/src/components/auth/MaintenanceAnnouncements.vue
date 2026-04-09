<template>
  <div v-if="announcements.length > 0" class="space-y-2">
    <div
      v-for="announcement in announcements"
      :key="announcement.id"
      :class="[
        'p-3 rounded-lg border',
        priorityClasses[announcement.priority] || priorityClasses.medium
      ]"
    >
      <div class="flex items-start space-x-2">
        <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <div class="flex-1 text-sm">
          <p class="font-medium">{{ announcement.title }}</p>
          <p class="text-xs mt-1 whitespace-pre-line" v-html="decodeHtml(announcement.message)"></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'

const announcements = ref([])

const priorityClasses = {
  high: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300',
  medium: 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800 text-orange-700 dark:text-orange-300',
  low: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300'
}

const fetchAnnouncements = async () => {
  try {
    const response = await api.get('/api/notifications/announcements/public/')
    if (response.status === 200) {
      announcements.value = response.data.filter(a => a.notification_type === 'maintenance')
    }
  } catch (error) {
    console.warn('Failed to fetch announcements:', error)
  }
}

const decodeHtml = (html) => {
  const txt = document.createElement('textarea')
  txt.innerHTML = html
  return txt.value
}

onMounted(() => {
  fetchAnnouncements()
})
</script>
