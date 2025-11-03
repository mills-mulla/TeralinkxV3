<template>
  <div v-if="announcements.length > 0" class="w-full p-4">
    <ul class="space-y-4 max-h-60 overflow-y-auto pr-2">
      <li
        v-for="(announcement, index) in announcements"
        :key="index"
        :class="[
          'p-3 rounded shadow hover:shadow-md transition border-l-4',
          getPriorityClass(announcement.priority)
        ]"
      >
        <h2 class="font-semibold text-sm">
          {{ announcement.title }}
        </h2>
        <small class="text-gray-500 flex items-center gap-1 mt-1">
          <i class="fas fa-clock text-2xs"></i>
          {{ formatDate(announcement.created_at) }}
        </small>
        <p class="text-sm text-gray-700 mt-1">
          {{ announcement.content }}
        </p>

        <p class="text-2xs text-gray-700 mt-1">
          From {{ announcement.start_date }} to {{ announcement.end_date }}
        </p>


      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const announcements = ref([])

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short'
  })
}

// Map numeric priority to Tailwind alert colors
function getPriorityClass(priority) {
  if (priority <= 1) {
    return 'bg-blue-100 text-blue-800 border-blue-500' // Info
  } else if (priority <= 2.5) {
    return 'bg-yellow-100 text-yellow-800 border-yellow-500' // Warning
  } else {
    return 'bg-red-100 text-red-800 border-red-500' // Danger
  }
}

async function checkAnnouncements() {
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/announcements/`, {
      headers: {
        Authorization: `Token ${localStorage.getItem('authToken')}`
      }
    })

    if (Array.isArray(response.data)) {
      const now = new Date()
      announcements.value = response.data.filter(a => {
        const start = a.start_date ? new Date(a.start_date) : null
        const end = a.end_date ? new Date(a.end_date) : null
        return a.is_active && (!start || start <= now) && (!end || end >= now)
      })
    }
  } catch (error) {
    console.error('❌ Failed to fetch announcements:', error)
    announcements.value = []
  }
}

onMounted(() => {
  checkAnnouncements()
})
</script>
