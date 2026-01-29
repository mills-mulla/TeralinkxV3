<template>
  <!-- Console Overlay -->
  <div class="fixed inset-0 z-50 pointer-events-none">
    <!-- Console Panel -->
    <div 
      class="absolute bottom-0 right-0 w-full max-w-2xl h-96 bg-gray-900 border-l border-t border-gray-800 rounded-tl-lg shadow-2xl transform transition-transform duration-300 pointer-events-auto"
      :class="{ 'translate-y-0': devStore.showConsole, 'translate-y-full': !devStore.showConsole }"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-3 bg-gray-800 border-b border-gray-700">
        <div class="flex items-center space-x-3">
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span class="text-sm font-mono text-white">DEV CONSOLE</span>
          </div>
          <div class="flex items-center space-x-2">
            <span class="text-xs px-2 py-0.5 bg-gray-700 text-gray-300 rounded">
              {{ devStore.logs.length }} logs
            </span>
            <span 
              v-if="devStore.logs.length > 0"
              class="text-xs px-2 py-0.5 rounded"
              :class="{
                'bg-green-900 text-green-300': filter === 'all',
                'bg-blue-900 text-blue-300': filter === 'info',
                'bg-yellow-900 text-yellow-300': filter === 'warn',
                'bg-red-900 text-red-300': filter === 'error'
              }"
            >
              {{ filteredLogs.length }} filtered
            </span>
          </div>
        </div>
        
        <div class="flex items-center space-x-2">
          <!-- Filter Buttons -->
          <div class="flex space-x-1">
            <button
              v-for="filterOption in filterOptions"
              :key="filterOption.value"
              @click="filter = filterOption.value"
              class="text-xs px-2 py-1 rounded transition"
              :class="{
                'bg-gray-700 text-gray-300 hover:bg-gray-600': filter !== filterOption.value,
                'bg-blue-600 text-white': filter === filterOption.value
              }"
            >
              {{ filterOption.label }}
            </button>
          </div>
          
          <!-- Actions -->
          <div class="flex items-center space-x-2 border-l border-gray-700 pl-2">
            <button
              @click="togglePause"
              class="text-xs px-2 py-1 rounded transition"
              :class="{
                'bg-gray-700 text-gray-300 hover:bg-gray-600': !paused,
                'bg-yellow-600 text-white': paused
              }"
              :title="paused ? 'Resume logging' : 'Pause logging'"
            >
              {{ paused ? '▶' : '⏸' }}
            </button>
            <button
              @click="clearLogs"
              class="text-xs px-2 py-1 bg-red-700 hover:bg-red-600 text-white rounded transition"
              title="Clear all logs"
            >
              Clear
            </button>
            <button
              @click="exportLogs"
              class="text-xs px-2 py-1 bg-green-700 hover:bg-green-600 text-white rounded transition"
              title="Export logs"
            >
              Export
            </button>
            <button
              @click="devStore.toggleConsole()"
              class="text-gray-400 hover:text-white transition"
              title="Close console"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Log Area -->
      <div 
        ref="logContainer"
        class="h-64 overflow-y-auto bg-black font-mono text-xs p-4"
        @scroll="handleScroll"
      >
        <!-- No Logs Message -->
        <div 
          v-if="devStore.logs.length === 0"
          class="text-center text-gray-500 py-8"
        >
          <svg class="w-12 h-12 mx-auto mb-2 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p>No logs yet. Start interacting with the app.</p>
        </div>
        
        <!-- Log Entries -->
        <div v-else>
          <div 
            v-for="(log, index) in filteredLogs"
            :key="log.id"
            class="mb-1 py-1 px-2 rounded hover:bg-gray-800 transition-colors"
            :class="{
              'bg-gray-900': index % 2 === 0
            }"
          >
            <!-- Log Header -->
            <div class="flex items-center justify-between mb-0.5">
              <div class="flex items-center space-x-2">
                <!-- Timestamp -->
                <span class="text-gray-400">{{ formatTime(log.timestamp) }}</span>
                
                <!-- Log Level Badge -->
                <span 
                  class="px-1.5 py-0.5 text-xs rounded"
                  :class="{
                    'bg-blue-900 text-blue-300': log.level === 'info',
                    'bg-yellow-900 text-yellow-300': log.level === 'warn',
                    'bg-red-900 text-red-300': log.level === 'error',
                    'bg-green-900 text-green-300': log.level === 'success',
                    'bg-purple-900 text-purple-300': log.level === 'debug'
                  }"
                >
                  {{ log.level.toUpperCase() }}
                </span>
                
                <!-- Module/Component -->
                <span v-if="log.module" class="text-gray-500">[{{ log.module }}]</span>
              </div>
              
              <!-- Actions -->
              <div class="flex items-center space-x-1 opacity-0 hover:opacity-100 transition-opacity">
                <button
                  v-if="log.data"
                  @click="toggleExpand(log.id)"
                  class="text-gray-400 hover:text-white text-xs"
                >
                  {{ expandedLogs.includes(log.id) ? '▲' : '▼' }}
                </button>
                <button
                  @click="copyLog(log)"
                  class="text-gray-400 hover:text-white text-xs"
                  title="Copy log"
                >
                  📋
                </button>
              </div>
            </div>
            
            <!-- Log Message -->
            <div class="text-gray-300 mb-1">{{ log.message }}</div>
            
            <!-- Expanded Data -->
            <div 
              v-if="expandedLogs.includes(log.id) && log.data"
              class="mt-2 pl-4 border-l-2 border-gray-700"
            >
              <pre class="text-gray-400 text-xs overflow-x-auto">{{ formatData(log.data) }}</pre>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Input Area -->
      <div class="border-t border-gray-800 bg-gray-900">
        <!-- Command History -->
        <div 
          v-if="showHistory"
          class="max-h-32 overflow-y-auto border-b border-gray-800"
        >
          <div 
            v-for="(cmd, index) in commandHistory"
            :key="index"
            @click="selectCommand(cmd)"
            class="px-4 py-2 hover:bg-gray-800 cursor-pointer text-xs text-gray-300"
          >
            <span class="text-green-400">$</span> {{ cmd }}
          </div>
        </div>
        
        <!-- Input -->
        <div class="flex items-center px-4 py-2">
          <span class="text-green-400 mr-2">$</span>
          <input
            ref="commandInput"
            v-model="command"
            @keydown.enter="executeCommand"
            @keydown.up="navigateHistory(-1)"
            @keydown.down="navigateHistory(1)"
            @keydown.esc="clearCommand"
            class="flex-1 bg-transparent text-white outline-none font-mono text-sm"
            placeholder="Enter command..."
            :disabled="paused"
          />
          <button
            @click="executeCommand"
            class="ml-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition"
            :disabled="!command.trim() || paused"
          >
            Execute
          </button>
        </div>
      </div>
      
      <!-- Footer -->
      <div class="flex items-center justify-between px-4 py-2 bg-gray-800 border-t border-gray-700 text-xs text-gray-400">
        <div class="flex items-center space-x-4">
          <span>Log Level: {{ filter.toUpperCase() }}</span>
          <span>Auto-scroll: {{ autoScroll ? 'ON' : 'OFF' }}</span>
          <span v-if="paused" class="text-yellow-400">⏸ PAUSED</span>
        </div>
        <div class="flex items-center space-x-4">
          <span>Memory: {{ memoryUsage }}</span>
          <span>FPS: {{ fps }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useDevStore } from '@/stores/dev'
import { useToast } from '@/composables/useToast'

const devStore = useDevStore()
const { showSuccess, showError } = useToast()

// Refs
const logContainer = ref(null)
const commandInput = ref(null)
const filter = ref('all')
const paused = ref(false)
const autoScroll = ref(true)
const expandedLogs = ref([])
const command = ref('')
const showHistory = ref(false)
const historyIndex = ref(-1)
const fps = ref(0)
const memoryUsage = ref('N/A')

// Filter options
const filterOptions = ref([
  { value: 'all', label: 'All' },
  { value: 'info', label: 'Info' },
  { value: 'warn', label: 'Warn' },
  { value: 'error', label: 'Error' },
  { value: 'debug', label: 'Debug' }
])

// Computed
const filteredLogs = computed(() => {
  if (filter.value === 'all') return devStore.logs
  return devStore.logs.filter(log => log.level === filter.value)
})

const commandHistory = computed(() => devStore.commandHistory)

// Methods
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit',
    fractionalSecondDigits: 3 
  })
}

const formatData = (data) => {
  try {
    if (typeof data === 'string') return data
    return JSON.stringify(data, null, 2)
  } catch (e) {
    return String(data)
  }
}

const toggleExpand = (logId) => {
  const index = expandedLogs.value.indexOf(logId)
  if (index === -1) {
    expandedLogs.value.push(logId)
  } else {
    expandedLogs.value.splice(index, 1)
  }
}

const copyLog = async (log) => {
  try {
    const text = `${formatTime(log.timestamp)} [${log.level}] ${log.message}`
    await navigator.clipboard.writeText(text)
    showSuccess('Log copied to clipboard')
  } catch (err) {
    showError('Failed to copy log')
  }
}

const clearLogs = () => {
  devStore.clearLogs()
  expandedLogs.value = []
}

const exportLogs = () => {
  const logsText = devStore.logs
    .map(log => `${formatTime(log.timestamp)} [${log.level}] ${log.message}`)
    .join('\n')
  
  const blob = new Blob([logsText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `teralinkx-console-${new Date().toISOString().slice(0, 10)}.log`
  a.click()
  URL.revokeObjectURL(url)
  
  showSuccess('Logs exported')
}

const togglePause = () => {
  paused.value = !paused.value
  if (paused.value) {
    devStore.addLog('SYSTEM', 'Console logging paused', 'warn')
  } else {
    devStore.addLog('SYSTEM', 'Console logging resumed', 'success')
  }
}

const executeCommand = () => {
  if (!command.value.trim()) return
  
  const cmd = command.value.trim()
  
  // Add to history
  devStore.addCommand(cmd)
  
  // Execute command
  handleCommand(cmd)
  
  // Clear input
  command.value = ''
  historyIndex.value = -1
}

const handleCommand = (cmd) => {
  devStore.addLog('COMMAND', `$ ${cmd}`, 'info')
  
  // Parse command
  const [action, ...args] = cmd.toLowerCase().split(' ')
  
  switch (action) {
    case 'help':
      devStore.addLog('SYSTEM', 'Available commands:', 'info')
      devStore.addLog('SYSTEM', '  help - Show this help', 'info')
      devStore.addLog('SYSTEM', '  clear - Clear console', 'info')
      devStore.addLog('SYSTEM', '  pause - Pause logging', 'info')
      devStore.addLog('SYSTEM', '  filter <level> - Filter logs', 'info')
      devStore.addLog('SYSTEM', '  test - Run tests', 'info')
      devStore.addLog('SYSTEM', '  memory - Show memory usage', 'info')
      break
      
    case 'clear':
      clearLogs()
      break
      
    case 'pause':
      togglePause()
      break
      
    case 'filter':
      if (args[0] && filterOptions.value.some(f => f.value === args[0])) {
        filter.value = args[0]
        devStore.addLog('SYSTEM', `Filter set to: ${args[0]}`, 'success')
      } else {
        devStore.addLog('SYSTEM', `Invalid filter. Use: ${filterOptions.value.map(f => f.value).join(', ')}`, 'error')
      }
      break
      
    case 'test':
      devStore.addLog('TEST', 'Running test command...', 'info')
      // Add more test commands here
      break
      
    case 'memory':
      updateMemoryUsage()
      break
      
    default:
      devStore.addLog('SYSTEM', `Unknown command: ${action}. Type 'help' for available commands.`, 'error')
  }
}

const selectCommand = (cmd) => {
  command.value = cmd
  showHistory.value = false
  nextTick(() => {
    commandInput.value?.focus()
  })
}

const navigateHistory = (direction) => {
  if (commandHistory.value.length === 0) return
  
  historyIndex.value += direction
  
  if (historyIndex.value < 0) {
    historyIndex.value = commandHistory.value.length - 1
  } else if (historyIndex.value >= commandHistory.value.length) {
    historyIndex.value = 0
  }
  
  command.value = commandHistory.value[historyIndex.value] || ''
}

const clearCommand = () => {
  command.value = ''
  historyIndex.value = -1
}

const handleScroll = () => {
  if (!logContainer.value) return
  
  const { scrollTop, scrollHeight, clientHeight } = logContainer.value
  autoScroll.value = Math.abs(scrollHeight - clientHeight - scrollTop) < 10
}

const scrollToBottom = () => {
  if (logContainer.value && autoScroll.value) {
    nextTick(() => {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    })
  }
}

const updateMemoryUsage = () => {
  if ('memory' in performance) {
    const mem = performance.memory
    memoryUsage.value = `${Math.round(mem.usedJSHeapSize / 1048576)}MB`
  }
}

const updateFPS = () => {
  let lastTime = performance.now()
  let frames = 0
  
  const loop = () => {
    const currentTime = performance.now()
    frames++
    
    if (currentTime > lastTime + 1000) {
      fps.value = Math.round((frames * 1000) / (currentTime - lastTime))
      frames = 0
      lastTime = currentTime
    }
    
    requestAnimationFrame(loop)
  }
  
  loop()
}

// Watch for new logs
watch(() => devStore.logs.length, () => {
  if (!paused.value) {
    scrollToBottom()
  }
})

// Lifecycle
onMounted(() => {
  updateFPS()
  
  // Focus input when console opens
  if (devStore.showConsole) {
    nextTick(() => {
      commandInput.value?.focus()
    })
  }
})

// Watch console state
watch(() => devStore.showConsole, (show) => {
  if (show) {
    nextTick(() => {
      commandInput.value?.focus()
      scrollToBottom()
    })
  }
})
</script>

<style scoped>
/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1f2937;
}

::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}

/* Log text selection */
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>