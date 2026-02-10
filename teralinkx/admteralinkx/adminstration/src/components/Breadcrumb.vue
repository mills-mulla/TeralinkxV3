<template>
  <nav class="flex items-center space-x-2 text-sm">
    <button 
      @click="$emit('navigate', 'Dashboard')"
      class="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
    >
      🏠 Home
    </button>
    <span class="text-slate-400 dark:text-slate-600">/</span>
    <span class="text-slate-900 dark:text-white font-medium">{{ currentPage }}</span>
  </nav>
</template>

<script>
export default {
  name: 'Breadcrumb',
  props: {
    currentPage: {
      type: String,
      required: true
    }
  },
  emits: ['navigate']
}
</script>
