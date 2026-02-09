import { ref, watch, onMounted } from 'vue'

const isDark = ref(false)
const isAuto = ref(true)

export function useTheme() {
  const setTheme = (dark) => {
    isDark.value = dark
    if (dark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }

  const toggleTheme = () => {
    isAuto.value = false
    localStorage.setItem('themeAuto', 'false')
    setTheme(!isDark.value)
  }

  const setAutoTheme = (auto) => {
    isAuto.value = auto
    localStorage.setItem('themeAuto', auto ? 'true' : 'false')
    if (auto) {
      applyAutoTheme()
    }
  }

  const applyAutoTheme = () => {
    const hour = new Date().getHours()
    // Dark theme from 6 PM (18:00) to 6 AM (6:00)
    const shouldBeDark = hour >= 18 || hour < 6
    setTheme(shouldBeDark)
  }

  const initTheme = () => {
    const savedAuto = localStorage.getItem('themeAuto')
    const savedTheme = localStorage.getItem('theme')
    
    if (savedAuto === 'false') {
      isAuto.value = false
      setTheme(savedTheme === 'dark')
    } else {
      isAuto.value = true
      applyAutoTheme()
      // Check every minute for time changes
      setInterval(applyAutoTheme, 60000)
    }
  }

  return {
    isDark,
    isAuto,
    toggleTheme,
    setAutoTheme,
    initTheme
  }
}
