<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center space-x-3 mb-6">
      <div class="p-2 bg-indigo-100 dark:bg-indigo-900/20 rounded-lg">
        <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 24 24">
          <path d="M4 6h18V4H4c-1.1 0-2 .9-2 2v11H0v3h14v-3H4V6zm19 2h-6c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h6c.55 0 1-.45 1-1V9c0-.55-.45-1-1-1zm-1 9h-4v-7h4v7z"/>
        </svg>
      </div>
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Connected Devices</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">Manage your authorized devices</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="animate-pulse space-y-4">
      <div v-for="i in 3" :key="i" class="flex items-center space-x-3 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
        <div class="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
        <div class="flex-1 space-y-2">
          <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-32"></div>
          <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-24"></div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="space-y-4">
      <div v-for="device in devices" :key="device.id" class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-indigo-100 dark:bg-indigo-900/20 rounded-full">
            <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 24 24">
              <path v-if="device.device_type === 'phone'" d="M7 2a2 2 0 00-2 2v16a2 2 0 002 2h10a2 2 0 002-2V4a2 2 0 00-2-2H7zM6 4a1 1 0 011-1h10a1 1 0 011 1v16a1 1 0 01-1 1H7a1 1 0 01-1-1V4z"/>
              <path v-else-if="device.device_type === 'laptop'" d="M4 5a2 2 0 00-2 2v8h20V7a2 2 0 00-2-2H4zM2 17h20v1a1 1 0 01-1 1H3a1 1 0 01-1-1v-1z"/>
              <path v-else d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          
          <div class="flex-1">
            <div class="flex items-center space-x-2">
              <input
                v-if="device.isEditing"
                v-model="device.editName"
                @keyup.enter="saveDeviceName(device)"
                @keyup.escape="cancelEdit(device)"
                class="text-sm font-medium px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              <p v-else class="text-sm font-medium text-gray-900 dark:text-white">
                {{ device.device_name }}
              </p>
              
              <button
                v-if="!device.isEditing"
                @click="startEdit(device)"
                class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                </svg>
              </button>
            </div>
            
            <p class="text-xs text-gray-600 dark:text-gray-400">
              {{ device.device_manufacturer }} • {{ formatDate(device.last_seen) }}
            </p>
          </div>
        </div>

        <div class="flex items-center space-x-3">
          <!-- Status Badge -->
          <span :class="getStatusClasses(device.status)" class="px-2 py-1 rounded-full text-xs font-medium">
            {{ device.status }}
          </span>

          <!-- Actions Menu -->
          <div class="relative">
            <button
              @click="toggleMenu(device.id)"
              class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
              </svg>
            </button>

            <div v-if="device.showMenu" class="absolute right-0 mt-1 w-40 bg-white dark:bg-gray-800 rounded-md shadow-lg z-10 border border-gray-200 dark:border-gray-700">
              <button
                v-if="device.status === 'active'"
                @click="handleAction('block', device.id)"
                class="w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                Block Device
              </button>
              <button
                v-else
                @click="handleAction('unblock', device.id)"
                class="w-full px-3 py-2 text-left text-sm text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20"
              >
                Unblock Device
              </button>
              
              <button
                @click="handleAction('trust', device.id, { trusted: !device.is_trusted })"
                class="w-full px-3 py-2 text-left text-sm text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20"
              >
                {{ device.is_trusted ? 'Remove Trust' : 'Trust Device' }}
              </button>
              
              <button
                @click="confirmRemove(device)"
                class="w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                Remove Device
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!devices.length" class="text-center py-8">
        <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
        <p class="text-gray-500 dark:text-gray-400">No devices found</p>
        <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">Devices will appear here when you sign in</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  devices: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['device-action'])

// Add reactive properties to devices
const devicesWithState = ref(props.devices.map(device => ({
  ...device,
  showMenu: false,
  isEditing: false,
  editName: device.device_name
})))

const toggleMenu = (deviceId) => {
  devicesWithState.value.forEach(device => {
    if (device.id === deviceId) {
      device.showMenu = !device.showMenu
    } else {
      device.showMenu = false
    }
  })
}

const startEdit = (device) => {
  device.isEditing = true
  device.editName = device.device_name
  device.showMenu = false
}

const saveDeviceName = (device) => {
  emit('device-action', 'update', device.id, { device_name: device.editName })
  device.device_name = device.editName
  device.isEditing = false
}

const cancelEdit = (device) => {
  device.isEditing = false
  device.editName = device.device_name
}

const handleAction = (action, deviceId, data = {}) => {
  emit('device-action', action, deviceId, data)
  // Close menu
  const device = devicesWithState.value.find(d => d.id === deviceId)
  if (device) device.showMenu = false
}

const confirmRemove = (device) => {
  if (confirm(`Are you sure you want to remove ${device.device_name}?`)) {
    handleAction('remove', device.id)
  }
}

const getStatusClasses = (status) => {
  return {
    'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400': status === 'active',
    'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': status === 'suspended',
    'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400': status === 'inactive'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}
</script>