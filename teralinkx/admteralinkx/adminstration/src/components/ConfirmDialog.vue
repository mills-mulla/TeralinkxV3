<template>
  <div v-if="show" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[70] flex items-center justify-center p-4" @click.self="cancel">
    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-sm w-full p-5">
      <div class="flex items-start gap-3 mb-4">
        <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" :class="iconBg">
          <svg class="w-5 h-5" :class="iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="type === 'danger'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            <path v-else-if="type === 'warning'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="flex-1">
          <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-1">{{ title }}</h3>
          <p class="text-xs text-slate-600 dark:text-slate-400">{{ message }}</p>
        </div>
      </div>
      <div class="flex gap-2">
        <button @click="cancel" class="flex-1 px-3 py-2 text-xs font-medium bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg transition-colors">
          {{ cancelText }}
        </button>
        <button @click="confirm" class="flex-1 px-3 py-2 text-xs font-medium text-white rounded-lg transition-colors" :class="confirmBtnClass">
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'ConfirmDialog',
  props: {
    show: Boolean,
    type: { type: String, default: 'info' }, // info, warning, danger
    title: { type: String, default: 'Confirm Action' },
    message: { type: String, default: 'Are you sure?' },
    confirmText: { type: String, default: 'Confirm' },
    cancelText: { type: String, default: 'Cancel' }
  },
  emits: ['confirm', 'cancel'],
  setup(props, { emit }) {
    const iconBg = computed(() => {
      const classes = {
        danger: 'bg-red-100 dark:bg-red-500/20',
        warning: 'bg-amber-100 dark:bg-amber-500/20',
        info: 'bg-blue-100 dark:bg-blue-500/20'
      }
      return classes[props.type] || classes.info
    })

    const iconColor = computed(() => {
      const classes = {
        danger: 'text-red-600 dark:text-red-400',
        warning: 'text-amber-600 dark:text-amber-400',
        info: 'text-blue-600 dark:text-blue-400'
      }
      return classes[props.type] || classes.info
    })

    const confirmBtnClass = computed(() => {
      const classes = {
        danger: 'bg-red-500 hover:bg-red-600',
        warning: 'bg-amber-500 hover:bg-amber-600',
        info: 'bg-blue-500 hover:bg-blue-600'
      }
      return classes[props.type] || classes.info
    })

    const confirm = () => emit('confirm')
    const cancel = () => emit('cancel')

    return { iconBg, iconColor, confirmBtnClass, confirm, cancel }
  }
}
</script>
