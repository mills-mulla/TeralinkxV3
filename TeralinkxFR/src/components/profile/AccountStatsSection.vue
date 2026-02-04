<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center space-x-3 mb-6">
      <div class="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
        <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
          <path d="M16,11V3H8V9H2V21H22V11H16M10,5H14V9H10V5M4,11H6V19H4V11M8,11H10V19H8V11M12,11H14V19H12V11M16,11H18V19H16V11M20,11V19H20V11Z"/>
        </svg>
      </div>
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Usage Statistics</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">Your account activity overview</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="animate-pulse">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="space-y-2">
          <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-16"></div>
          <div class="h-6 bg-gray-300 dark:bg-gray-600 rounded w-20"></div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-6">
      <StatCard
        title="Today"
        :value="formatBytes(stats.dailyUsage || 0)"
        color="blue"
      />
      <StatCard
        title="This Week"
        :value="formatBytes(stats.weeklyUsage || 0)"
        color="green"
      />
      <StatCard
        title="This Month"
        :value="formatBytes(stats.monthlyUsage || 0)"
        color="purple"
      />
      <StatCard
        title="Total"
        :value="formatBytes(stats.totalUsage || 0)"
        color="orange"
      />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  stats: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const formatBytes = (bytes) => {
  const num = Number(bytes) || 0
  if (num === 0) return '0 B'
  if (num < 1024) return num + ' B'
  if (num < 1024 * 1024) return (num / 1024).toFixed(1) + ' KB'
  if (num < 1024 * 1024 * 1024) return (num / (1024 * 1024)).toFixed(1) + ' MB'
  return (num / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
}
</script>

<script>
// StatCard component
const StatCard = {
  props: {
    title: String,
    value: String,
    color: String
  },
  template: `
    <div class="text-center">
      <p :class="colorClasses" class="text-lg font-bold">{{ value }}</p>
      <p class="text-xs text-gray-600 dark:text-gray-300 mt-1">{{ title }}</p>
    </div>
  `,
  computed: {
    colorClasses() {
      const colors = {
        blue: 'text-blue-600 dark:text-blue-400',
        green: 'text-green-600 dark:text-green-400',
        purple: 'text-purple-600 dark:text-purple-400',
        orange: 'text-orange-600 dark:text-orange-400'
      }
      return colors[this.color] || colors.blue
    }
  }
}
</script>