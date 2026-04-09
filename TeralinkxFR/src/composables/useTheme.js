import { ref, onMounted, onUnmounted } from 'vue'

const isDark = ref(false)

export function useTheme() {
  let themeInterval = null

  const updateTheme = () => {
    const hour = new Date().getHours()
    // Dark mode from 6 PM (18:00) to 6 AM (06:00)
    const shouldBeDark = hour >= 18 || hour < 6
    
    if (shouldBeDark !== isDark.value) {
      isDark.value = shouldBeDark
      document.documentElement.classList.toggle('dark', shouldBeDark)
    }
  }

  const initTheme = () => {
    updateTheme()
    // Check every minute for theme changes
    themeInterval = setInterval(updateTheme, 60000)
  }

  const cleanup = () => {
    if (themeInterval) {
      clearInterval(themeInterval)
      themeInterval = null
    }
  }

  onMounted(initTheme)
  onUnmounted(cleanup)

  return {
    isDark,
    updateTheme,
    cleanup
  }
}