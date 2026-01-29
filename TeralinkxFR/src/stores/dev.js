// stores/dev.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDevStore = defineStore('dev', () => {
  // State
  const showDevTools = ref(false)
  const showConsole = ref(false)
  const logs = ref([])
  const commandHistory = ref([])
  const sessionId = ref('')
  
  // Max logs to keep
  const MAX_LOGS = 1000
  
  // Getters
  const logCount = computed(() => logs.value.length)
  const hasLogs = computed(() => logs.value.length > 0)
  const lastLog = computed(() => logs.value[logs.value.length - 1])
  const errorLogs = computed(() => logs.value.filter(log => log.level === 'error'))
  const warningLogs = computed(() => logs.value.filter(log => log.level === 'warn'))

  // Actions
  const toggleDevTools = () => {
    showDevTools.value = !showDevTools.value
    if (showDevTools.value) {
      addLog('DEV', 'Developer tools enabled', 'info')
    }
  }

  const toggleConsole = () => {
    showConsole.value = !showConsole.value
    if (showConsole.value) {
      addLog('CONSOLE', 'Developer console opened', 'info')
    }
  }

  const addLog = (module, message, level = 'info', data = null) => {
    const logEntry = {
      id: Date.now() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toISOString(),
      module,
      message,
      level,
      data
    }
    
    logs.value.unshift(logEntry)
    
    // Keep only max logs
    if (logs.value.length > MAX_LOGS) {
      logs.value = logs.value.slice(0, MAX_LOGS)
    }
    
    // Also log to browser console in development
    if (import.meta.env.DEV) {
      const consoleMethod = level === 'error' ? 'error' :
                          level === 'warn' ? 'warn' :
                          level === 'debug' ? 'debug' : 'log'
      
      console[consoleMethod](`[${module}] ${message}`, data || '')
    }
  }

  const addCommand = (command) => {
    commandHistory.value.unshift(command)
    
    // Keep only last 50 commands
    if (commandHistory.value.length > 50) {
      commandHistory.value = commandHistory.value.slice(0, 50)
    }
  }

  const clearLogs = () => {
    logs.value = []
    addLog('SYSTEM', 'Logs cleared', 'info')
  }

  const clearHistory = () => {
    commandHistory.value = []
  }

  const generateSessionId = () => {
    const timestamp = Date.now().toString(36)
    const random = Math.random().toString(36).substr(2, 9)
    sessionId.value = `dev_${timestamp}_${random}`
    return sessionId.value
  }

  const exportLogs = () => {
    const logsText = logs.value
      .map(log => `${log.timestamp} [${log.level}] [${log.module}] ${log.message}`)
      .join('\n')
    
    return logsText
  }

  const importLogs = (logsText) => {
    const lines = logsText.split('\n')
    lines.forEach(line => {
      // Parse log line and add to logs
      // This is a simplified parser
      const match = line.match(/^(.+?) \[(.+?)\] \[(.+?)\] (.+)$/)
      if (match) {
        const [, timestamp, level, module, message] = match
        addLog(module, message, level)
      }
    })
  }

  // Initialize
  const initialize = () => {
    generateSessionId()
    
    // Add initial log
    addLog('SYSTEM', 'Dev store initialized', 'info', {
      sessionId: sessionId.value,
      timestamp: new Date().toISOString()
    })
  }

  return {
    // State
    showDevTools,
    showConsole,
    logs,
    commandHistory,
    sessionId,
    
    // Getters
    logCount,
    hasLogs,
    lastLog,
    errorLogs,
    warningLogs,
    
    // Actions
    toggleDevTools,
    toggleConsole,
    addLog,
    addCommand,
    clearLogs,
    clearHistory,
    generateSessionId,
    exportLogs,
    importLogs,
    initialize
  }
})