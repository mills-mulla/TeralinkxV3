import { ref, onMounted } from 'vue'

export function usePerformance() {
  const metrics = ref({
    fcp: 0,
    lcp: 0,
    fid: 0,
    cls: 0,
    ttfb: 0
  })

  onMounted(() => {
    if (typeof window === 'undefined' || !window.performance) return

    // First Contentful Paint
    const paintEntries = performance.getEntriesByType('paint')
    const fcpEntry = paintEntries.find(entry => entry.name === 'first-contentful-paint')
    if (fcpEntry) metrics.value.fcp = Math.round(fcpEntry.startTime)

    // Time to First Byte
    const navEntry = performance.getEntriesByType('navigation')[0]
    if (navEntry) metrics.value.ttfb = Math.round(navEntry.responseStart - navEntry.requestStart)

    // Largest Contentful Paint
    if ('PerformanceObserver' in window) {
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries()
          const lastEntry = entries[entries.length - 1]
          metrics.value.lcp = Math.round(lastEntry.startTime)
        })
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] })
      } catch (e) {
        // Observer not supported
      }
    }
  })

  return { metrics }
}
