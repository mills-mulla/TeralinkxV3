<!-- TeralinkxFR/src/components/AuthRecoveryOverlay.vue - Transparent Recovery UI -->
<template>
  <div v-if="isRecovering" class="auth-recovery-overlay">
    <div class="recovery-modal">
      <div class="recovery-content">
        <!-- Recovery Animation -->
        <div class="recovery-animation">
          <div class="recovery-spinner" :class="{ 'success': recoverySuccess, 'error': recoveryError }">
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
          </div>
        </div>
        
        <!-- Recovery Status -->
        <div class="recovery-status">
          <h3 class="recovery-title">{{ recoveryTitle }}</h3>
          <p class="recovery-message">{{ recoveryMessage }}</p>
        </div>
        
        <!-- Progress Bar -->
        <div class="recovery-progress" v-if="!recoveryError && !recoverySuccess">
          <div class="progress-track">
            <div 
              class="progress-bar" 
              :style="{ width: `${recoveryProgress}%` }"
            ></div>
          </div>
          <div class="progress-text">{{ Math.round(recoveryProgress) }}%</div>
        </div>
        
        <!-- Strategy List -->
        <div class="recovery-strategies" v-if="showStrategies">
          <div 
            v-for="(strategy, index) in strategies" 
            :key="strategy.name"
            class="strategy-item"
            :class="{ 
              'active': currentStrategyIndex === index,
              'completed': strategy.completed,
              'failed': strategy.failed 
            }"
          >
            <div class="strategy-icon">
              <i v-if="strategy.completed" class="icon-check"></i>
              <i v-else-if="strategy.failed" class="icon-x"></i>
              <div v-else-if="currentStrategyIndex === index" class="mini-spinner"></div>
              <i v-else class="icon-clock"></i>
            </div>
            <span class="strategy-name">{{ strategy.displayName }}</span>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="recovery-actions" v-if="showActions">
          <button 
            v-if="showManualOption" 
            @click="manualReauth" 
            class="btn btn-primary"
          >
            Sign in manually
          </button>
          
          <button 
            v-if="showRetryOption" 
            @click="retryRecovery" 
            class="btn btn-secondary"
          >
            Try again
          </button>
          
          <button 
            v-if="showCancelOption" 
            @click="cancelRecovery" 
            class="btn btn-ghost"
          >
            Cancel
          </button>
        </div>
        
        <!-- Debug Info (dev only) -->
        <div v-if="isDev && debugInfo" class="recovery-debug">
          <details>
            <summary>Debug Information</summary>
            <pre>{{ JSON.stringify(debugInfo, null, 2) }}</pre>
          </details>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth_resilient'

export default {
  name: 'AuthRecoveryOverlay',
  
  setup() {
    const authStore = useAuthStore()
    
    // State
    const isRecovering = ref(false)
    const recoveryMessage = ref('Attempting automatic reconnection...')
    const recoveryProgress = ref(0)
    const recoverySuccess = ref(false)
    const recoveryError = ref(false)
    const currentStrategyIndex = ref(-1)
    const showStrategies = ref(false)
    const debugInfo = ref(null)
    
    // Recovery strategies
    const strategies = ref([
      {
        name: 'refresh_token',
        displayName: 'Token refresh',
        duration: 2000,
        completed: false,
        failed: false
      },
      {
        name: 'device_auto_auth',
        displayName: 'Device recognition',
        duration: 3000,
        completed: false,
        failed: false
      },
      {
        name: 'enhanced_device_auth',
        displayName: 'Enhanced device auth',
        duration: 4000,
        completed: false,
        failed: false
      },
      {
        name: 'session_recovery',
        displayName: 'Session recovery',
        duration: 2000,
        completed: false,
        failed: false
      }
    ])
    
    // Computed
    const recoveryTitle = computed(() => {
      if (recoverySuccess.value) return 'Reconnected!'
      if (recoveryError.value) return 'Connection Failed'
      return 'Reconnecting...'
    })
    
    const showActions = computed(() => {
      return recoveryError.value || recoverySuccess.value
    })
    
    const showManualOption = computed(() => {
      return recoveryError.value
    })
    
    const showRetryOption = computed(() => {
      return recoveryError.value
    })
    
    const showCancelOption = computed(() => {
      return isRecovering.value && !recoverySuccess.value
    })
    
    const isDev = computed(() => {
      return import.meta.env.DEV
    })
    
    // Methods
    const startRecovery = async (reason = 'unknown') => {
      console.log(`🔧 Starting recovery UI for reason: ${reason}`)
      
      // Reset state
      isRecovering.value = true
      recoverySuccess.value = false
      recoveryError.value = false
      recoveryProgress.value = 0
      currentStrategyIndex.value = -1
      showStrategies.value = true
      
      // Reset strategies
      strategies.value.forEach(strategy => {
        strategy.completed = false
        strategy.failed = false
      })
      
      debugInfo.value = {
        reason: reason,
        startTime: new Date().toISOString(),
        userAgent: navigator.userAgent,
        onLine: navigator.onLine
      }
      
      try {
        // Simulate recovery process with visual feedback
        for (let i = 0; i < strategies.value.length; i++) {
          const strategy = strategies.value[i]
          currentStrategyIndex.value = i
          
          recoveryMessage.value = `Trying ${strategy.displayName}...`
          
          // Simulate strategy execution time
          await new Promise(resolve => setTimeout(resolve, strategy.duration))
          
          // Update progress
          recoveryProgress.value = ((i + 1) / strategies.value.length) * 100
          
          // For demo purposes, let's say first strategy succeeds
          if (i === 0) {
            strategy.completed = true
            await completeRecovery('Token refresh successful')
            return
          } else {
            strategy.failed = true
          }
        }
        
        // All strategies failed
        await failRecovery('All recovery methods failed')
        
      } catch (error) {
        console.error('Recovery UI error:', error)
        await failRecovery(`Recovery error: ${error.message}`)
      }
    }
    
    const completeRecovery = async (message) => {
      recoverySuccess.value = true
      recoveryMessage.value = message
      currentStrategyIndex.value = -1
      
      // Auto-hide after success
      setTimeout(() => {
        isRecovering.value = false
      }, 2000)
    }
    
    const failRecovery = async (message) => {
      recoveryError.value = true
      recoveryMessage.value = message
      currentStrategyIndex.value = -1
      showStrategies.value = false
    }
    
    const manualReauth = () => {
      console.log('🔐 User chose manual re-authentication')
      isRecovering.value = false
      
      // Redirect to login
      window.location.href = '/'
    }
    
    const retryRecovery = () => {
      console.log('🔄 User chose to retry recovery')
      startRecovery('user_retry')
    }
    
    const cancelRecovery = () => {
      console.log('❌ User cancelled recovery')
      isRecovering.value = false
      
      // Clear auth and redirect
      authStore.clearAuth()
      window.location.href = '/'
    }
    
    // Listen for health monitoring events
    const handleHealthEvent = (event) => {
      const { type, data } = event.detail
      
      switch (type) {
        case 'backend_restart':
          startRecovery('backend_restart')
          break
          
        case 'recovery_failed':
          failRecovery('Automatic recovery failed')
          break
          
        case 'recovered':
          completeRecovery('Connection restored successfully')
          break
          
        case 'offline':
          startRecovery('network_offline')
          break
      }
    }
    
    // Lifecycle
    onMounted(() => {
      window.addEventListener('tokenHealthEvent', handleHealthEvent)
      
      // For demo purposes, start recovery after 2 seconds
      if (isDev.value) {
        setTimeout(() => {
          startRecovery('demo')
        }, 2000)
      }
    })
    
    onUnmounted(() => {
      window.removeEventListener('tokenHealthEvent', handleHealthEvent)
    })
    
    return {
      // State
      isRecovering,
      recoveryMessage,
      recoveryProgress,
      recoverySuccess,
      recoveryError,
      currentStrategyIndex,
      showStrategies,
      strategies,
      debugInfo,
      
      // Computed
      recoveryTitle,
      showActions,
      showManualOption,
      showRetryOption,
      showCancelOption,
      isDev,
      
      // Methods
      startRecovery,
      manualReauth,
      retryRecovery,
      cancelRecovery
    }
  }
}
</script>

<style scoped>
.auth-recovery-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.3s ease-out;
}

.recovery-modal {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

.recovery-content {
  text-align: center;
}

.recovery-animation {
  margin-bottom: 1.5rem;
}

.recovery-spinner {
  position: relative;
  width: 60px;
  height: 60px;
  margin: 0 auto;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-ring:nth-child(2) {
  animation-delay: -0.3s;
  border-top-color: #8b5cf6;
}

.spinner-ring:nth-child(3) {
  animation-delay: -0.6s;
  border-top-color: #06d6a0;
}

.recovery-spinner.success .spinner-ring {
  border-top-color: #10b981;
  animation: none;
}

.recovery-spinner.error .spinner-ring {
  border-top-color: #ef4444;
  animation: none;
}

.recovery-status {
  margin-bottom: 1.5rem;
}

.recovery-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.recovery-message {
  color: #6b7280;
  margin: 0;
}

.recovery-progress {
  margin-bottom: 1.5rem;
}

.progress-track {
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.875rem;
  color: #6b7280;
}

.recovery-strategies {
  margin-bottom: 1.5rem;
  text-align: left;
}

.strategy-item {
  display: flex;
  align-items: center;
  padding: 0.5rem 0;
  transition: all 0.2s ease;
}

.strategy-item.active {
  color: #3b82f6;
  font-weight: 500;
}

.strategy-item.completed {
  color: #10b981;
}

.strategy-item.failed {
  color: #ef4444;
  opacity: 0.6;
}

.strategy-icon {
  width: 20px;
  height: 20px;
  margin-right: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.strategy-name {
  font-size: 0.875rem;
}

.recovery-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-ghost {
  background: transparent;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.btn-ghost:hover {
  background: #f9fafb;
}

.recovery-debug {
  margin-top: 1rem;
  text-align: left;
}

.recovery-debug details {
  font-size: 0.75rem;
}

.recovery-debug pre {
  background: #f3f4f6;
  padding: 0.5rem;
  border-radius: 4px;
  overflow-x: auto;
  max-height: 200px;
}

/* Icons (using simple CSS shapes) */
.icon-check::before {
  content: '✓';
  color: #10b981;
}

.icon-x::before {
  content: '✗';
  color: #ef4444;
}

.icon-clock::before {
  content: '○';
  color: #6b7280;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>