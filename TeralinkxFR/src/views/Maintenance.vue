<!-- src/views/Maintenance.vue - System Maintenance Page -->
<template>
  <div class="maintenance-container">
    <div class="maintenance-content">
      <!-- Animated Icon -->
      <div class="maintenance-icon">
        <svg width="120" height="120" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="maintenance-svg">
          <path d="M22.7 19L13.6 9.9C14.5 7.6 14 4.9 12.1 3C10.1 1 7.1 1 5.1 3S3.1 7.9 5.1 9.9C7 11.8 9.6 12.3 11.9 11.4L21 20.5C21.4 20.9 21.4 21.6 21 22C20.6 21.6 19.9 21.6 19.5 21.2L19.5 21.2L22.7 19ZM6.5 8.5C5.1 7.1 5.1 4.9 6.5 3.5S10.4 2.1 11.8 3.5C13.2 4.9 13.2 7.1 11.8 8.5C10.4 9.9 8.2 9.9 6.8 8.5H6.5Z" fill="#f59e0b"/>
          <circle cx="12" cy="12" r="10" stroke="#f59e0b" stroke-width="2" fill="none" opacity="0.2" class="maintenance-circle"/>
        </svg>
      </div>

      <!-- Title -->
      <h1 class="maintenance-title">System Maintenance</h1>
      
      <!-- Message -->
      <p class="maintenance-message">
        We're currently performing scheduled maintenance to improve your experience.
        Please check back in a few minutes.
      </p>

      <!-- Status -->
      <div class="maintenance-status">
        <div class="status-item">
          <div class="status-dot" :class="{ 'active': maintenanceStatus.database }"></div>
          <span>Database</span>
        </div>
        <div class="status-item">
          <div class="status-dot" :class="{ 'active': maintenanceStatus.api }"></div>
          <span>API Services</span>
        </div>
        <div class="status-item">
          <div class="status-dot" :class="{ 'active': maintenanceStatus.auth }"></div>
          <span>Authentication</span>
        </div>
      </div>

      <!-- Estimated Time -->
      <div class="maintenance-time" v-if="estimatedCompletion">
        <p><strong>Estimated completion:</strong> {{ estimatedCompletion }}</p>
        <div class="countdown" v-if="countdown">
          <span>{{ countdown }}</span>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="maintenance-progress">
        <div class="progress-track">
          <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
        </div>
        <p class="progress-text">{{ Math.round(progress) }}% Complete</p>
      </div>

      <!-- Actions -->
      <div class="maintenance-actions">
        <button @click="checkStatus" class="btn btn-primary" :disabled="checking">
          <svg v-if="checking" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spin">
            <path d="M12 2V6M12 18V22M4.93 4.93L7.76 7.76M16.24 16.24L19.07 19.07M2 12H6M18 12H22M4.93 19.07L7.76 16.24M16.24 7.76L19.07 4.93" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 12S5 4 12 4S23 12 23 12S19 20 12 20S1 12 1 12Z" stroke="currentColor" stroke-width="2" fill="none"/>
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
          {{ checking ? 'Checking...' : 'Check Status' }}
        </button>
        
        <button @click="goToStatus" class="btn btn-secondary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" fill="currentColor"/>
          </svg>
          Status Page
        </button>
      </div>

      <!-- Updates -->
      <div class="maintenance-updates" v-if="updates.length > 0">
        <h3>Recent Updates</h3>
        <div class="update-list">
          <div v-for="update in updates" :key="update.id" class="update-item">
            <div class="update-time">{{ formatTime(update.timestamp) }}</div>
            <div class="update-message">{{ update.message }}</div>
          </div>
        </div>
      </div>

      <!-- Contact Info -->
      <div class="maintenance-contact">
        <p>Need immediate assistance?</p>
        <div class="contact-links">
          <a href="mailto:support@teralinkxwaves.uk" class="contact-link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 4H20C21.1 4 22 4.9 22 6V18C22 19.1 21.1 20 20 20H4C2.9 20 2 19.1 2 18V6C2 4.9 2.9 4 4 4Z" stroke="currentColor" stroke-width="2" fill="none"/>
              <polyline points="22,6 12,13 2,6" stroke="currentColor" stroke-width="2"/>
            </svg>
            Email Support
          </a>
          <a href="tel:+254700000000" class="contact-link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 16.92V19.92C22 20.52 21.39 21 20.92 21C9.11 21 1 12.89 1 1.08C1 0.61 1.48 0 2.08 0H5.08C5.68 0 6.08 0.4 6.08 1C6.08 3.25 6.5 5.45 7.34 7.47C7.43 7.7 7.33 7.96 7.14 8.15L5.79 9.5C7.24 12.41 9.59 14.76 12.5 16.21L13.85 14.86C14.04 14.67 14.3 14.57 14.53 14.66C16.55 15.5 18.75 15.92 21 15.92C21.6 15.92 22 16.32 22 16.92Z" fill="currentColor"/>
            </svg>
            Call Support
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'

export default {
  name: 'Maintenance',
  
  setup() {
    // State
    const checking = ref(false)
    const progress = ref(0)
    const maintenanceStatus = ref({
      database: false,
      api: false,
      auth: false
    })
    const updates = ref([
      {
        id: 1,
        timestamp: Date.now() - 300000, // 5 minutes ago
        message: 'Maintenance started - Database optimization in progress'
      },
      {
        id: 2,
        timestamp: Date.now() - 180000, // 3 minutes ago
        message: 'API services temporarily unavailable'
      }
    ])
    
    let progressInterval = null
    let statusInterval = null

    // Computed
    const estimatedCompletion = computed(() => {
      const now = new Date()
      const completion = new Date(now.getTime() + (30 * 60 * 1000)) // 30 minutes from now
      return completion.toLocaleTimeString()
    })

    const countdown = computed(() => {
      const now = new Date()
      const completion = new Date(now.getTime() + (30 * 60 * 1000))
      const diff = completion.getTime() - now.getTime()
      
      if (diff <= 0) return null
      
      const minutes = Math.floor(diff / 60000)
      const seconds = Math.floor((diff % 60000) / 1000)
      
      return `${minutes}:${seconds.toString().padStart(2, '0')}`
    })

    // Methods
    const checkStatus = async () => {
      checking.value = true
      
      try {
        // Simulate status check
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Check if maintenance is over
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/status/`, {
          method: 'GET',
          timeout: 5000
        })
        
        if (response.ok) {
          const data = await response.json()
          
          if (!data.maintenance_mode) {
            // Maintenance is over, redirect to home
            window.location.href = '/'
            return
          }
          
          // Update status
          maintenanceStatus.value = {
            database: data.services?.database === 'online',
            api: data.services?.api === 'online',
            auth: data.services?.auth === 'online'
          }
        }
        
      } catch (error) {
        console.log('Status check failed:', error)
        // Add update about failed check
        updates.value.unshift({
          id: Date.now(),
          timestamp: Date.now(),
          message: 'Status check failed - maintenance likely still in progress'
        })
      } finally {
        checking.value = false
      }
    }

    const goToStatus = () => {
      window.open('https://status.teralinkxwaves.uk', '_blank')
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString()
    }

    const simulateProgress = () => {
      // Simulate maintenance progress
      progressInterval = setInterval(() => {
        if (progress.value < 90) {
          progress.value += Math.random() * 2
        }
      }, 5000)
    }

    const autoCheckStatus = () => {
      // Auto-check status every 30 seconds
      statusInterval = setInterval(() => {
        checkStatus()
      }, 30000)
    }

    // Lifecycle
    onMounted(() => {
      document.title = 'System Maintenance - TeralinkX'
      
      // Start progress simulation
      simulateProgress()
      
      // Start auto status checking
      autoCheckStatus()
      
      // Initial status check
      setTimeout(() => {
        checkStatus()
      }, 2000)
    })

    onUnmounted(() => {
      if (progressInterval) clearInterval(progressInterval)
      if (statusInterval) clearInterval(statusInterval)
    })

    return {
      checking,
      progress,
      maintenanceStatus,
      updates,
      estimatedCompletion,
      countdown,
      checkStatus,
      goToStatus,
      formatTime
    }
  }
}
</script>

<style scoped>
.maintenance-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  padding: 1rem;
}

.maintenance-content {
  background: white;
  border-radius: 16px;
  padding: 3rem 2rem;
  max-width: 600px;
  width: 100%;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.maintenance-icon {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
}

.maintenance-svg {
  animation: maintenance-pulse 2s ease-in-out infinite;
}

.maintenance-circle {
  animation: maintenance-rotate 3s linear infinite;
}

.maintenance-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.maintenance-message {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.maintenance-status {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #4b5563;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ef4444;
  transition: background-color 0.3s ease;
}

.status-dot.active {
  background: #10b981;
  animation: status-pulse 2s ease-in-out infinite;
}

.maintenance-time {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
  color: #92400e;
}

.countdown {
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 0.5rem;
  font-family: 'Courier New', monospace;
}

.maintenance-progress {
  margin-bottom: 2rem;
}

.progress-track {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #d97706);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-text {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.maintenance-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #f59e0b;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
  transform: translateY(-1px);
}

.maintenance-updates {
  text-align: left;
  margin-bottom: 2rem;
}

.maintenance-updates h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.update-list {
  max-height: 200px;
  overflow-y: auto;
}

.update-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem;
  border-left: 3px solid #f59e0b;
  background: #fef3c7;
  margin-bottom: 0.5rem;
  border-radius: 0 8px 8px 0;
}

.update-time {
  font-size: 0.75rem;
  color: #92400e;
  font-weight: 500;
  min-width: 80px;
}

.update-message {
  font-size: 0.875rem;
  color: #92400e;
}

.maintenance-contact {
  border-top: 1px solid #e5e7eb;
  padding-top: 2rem;
  color: #6b7280;
}

.maintenance-contact p {
  margin-bottom: 1rem;
}

.contact-links {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.contact-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
  border: 1px solid #3b82f6;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.contact-link:hover {
  background: #3b82f6;
  color: white;
}

/* Animations */
@keyframes maintenance-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes maintenance-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes status-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .maintenance-content {
    padding: 2rem 1rem;
  }
  
  .maintenance-title {
    font-size: 1.5rem;
  }
  
  .maintenance-status {
    gap: 1rem;
  }
  
  .maintenance-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  .contact-links {
    flex-direction: column;
  }
}
</style>