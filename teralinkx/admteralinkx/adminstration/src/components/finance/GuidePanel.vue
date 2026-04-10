<template>
  <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800 p-4 mb-4">
    <button @click="open = !open" class="flex items-center justify-between w-full text-left">
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4 text-blue-600 dark:text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
        </svg>
        <span class="text-sm font-medium text-blue-900 dark:text-blue-100">{{ title }} — Guide</span>
      </div>
      <svg class="w-4 h-4 text-blue-500 transition-transform" :class="open ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
      </svg>
    </button>

    <div v-show="open" class="mt-4 space-y-3">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div v-for="term in terms" :key="term.label"
          class="bg-white dark:bg-slate-800 rounded-lg p-3 border"
          :class="`border-${term.color}-100 dark:border-${term.color}-900`">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-2 h-2 rounded-full" :class="`bg-${term.color}-500`"></div>
            <span class="text-xs font-semibold" :class="`text-${term.color}-900 dark:text-${term.color}-100`">{{ term.label }}</span>
          </div>
          <p class="text-xs text-slate-600 dark:text-slate-400">{{ term.description }}</p>
          <div v-if="term.formula" class="mt-1 bg-slate-50 dark:bg-slate-900 rounded p-1.5 font-mono text-[10px] text-slate-600 dark:text-slate-400">
            {{ term.formula }}
          </div>
        </div>
      </div>
      <div v-if="note" class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3 border border-amber-200 dark:border-amber-800 flex items-start gap-2">
        <svg class="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
          <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
        </svg>
        <p class="text-xs text-amber-800 dark:text-amber-200">{{ note }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GuidePanel',
  props: {
    title: { type: String, required: true },
    terms: { type: Array, default: () => [] },
    note:  { type: String, default: '' }
  },
  data() { return { open: false } }
}
</script>
