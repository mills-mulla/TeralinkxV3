import { ref, watch } from 'vue'

const isDark = ref(false)
const isAuto = ref(false)

export function useTheme() {
  const setTheme = (dark) => {
    console.log('🎨 Setting theme to:', dark ? 'dark' : 'light')
    isDark.value = dark
    
    // Force update the DOM
    const html = document.documentElement
    if (dark) {
      html.classList.add('dark')
      console.log('✅ Added dark class to html')
    } else {
      html.classList.remove('dark')
      console.log('✅ Removed dark class from html')
    }
    
    localStorage.setItem('theme', dark ? 'dark' : 'light')
    console.log('💾 Saved theme to localStorage:', dark ? 'dark' : 'light')
  }

  const toggleTheme = () => {
    console.log('🔄 Toggle theme clicked')
    isAuto.value = false
    localStorage.setItem('themeAuto', 'false')
    setTheme(!isDark.value)
  }

  const setAutoTheme = (auto) => {
    console.log('⚙️ Set auto theme:', auto)
    isAuto.value = auto
    localStorage.setItem('themeAuto', auto ? 'true' : 'false')
    if (auto) {
      applyAutoTheme()
    }
  }

  const applyAutoTheme = () => {
    const hour = new Date().getHours()
    const shouldBeDark = hour >= 18 || hour < 6
    console.log('🕐 Auto theme - Hour:', hour, 'Should be dark:', shouldBeDark)
    setTheme(shouldBeDark)
  }

  const initTheme = () => {
    console.log('🚀 Initializing theme...')
    const savedAuto = localStorage.getItem('themeAuto')
    const savedTheme = localStorage.getItem('theme')
    console.log('📦 Saved auto:', savedAuto, 'Saved theme:', savedTheme)
    
    if (savedAuto === 'true') {
      isAuto.value = true
      applyAutoTheme()
      setInterval(applyAutoTheme, 60000)
    } else if (savedTheme) {
      isAuto.value = false
      setTheme(savedTheme === 'dark')
    } else {
      isAuto.value = false
      setTheme(false)
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
