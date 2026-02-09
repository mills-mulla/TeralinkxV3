<template>
  <div v-if="show" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
      <div class="p-6">
        <div :class="`w-12 h-12 ${iconBgColor} rounded-2xl flex items-center justify-center mx-auto mb-4`">
          <component :is="icon" :class="`w-6 h-6 ${iconColor}`" />
        </div>
        <h3 class="text-lg font-semibold text-slate-800 text-center mb-2">{{ title }}</h3>
        <p class="text-slate-600 text-center mb-6" v-html="message"></p>
        <div class="flex space-x-3">
          <button
            @click="$emit('cancel')"
            class="flex-1 px-4 py-2 border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50 transition-all duration-300"
          >
            {{ cancelText }}
          </button>
          <button
            @click="$emit('confirm')"
            :disabled="loading"
            :class="[
              'flex-1 px-4 py-2 text-white rounded-lg transition-all duration-300 flex items-center justify-center space-x-2',
              loading ? `${confirmBgColor} opacity-50 cursor-not-allowed` : `${confirmBgColor} ${confirmHoverColor}`
            ]"
          >
            <ArrowPathIcon v-if="loading" class="w-4 h-4 animate-spin" />
            <span>{{ confirmText }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import {
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'ConfirmDialog',
  components: {
    ArrowPathIcon
  },
  props: {
    show: { type: Boolean, required: true },
    title: { type: String, required: true },
    message: { type: String, required: true },
    type: { type: String, default: 'danger' }, // danger, warning, success, info
    confirmText: { type: String, default: 'Confirm' },
    cancelText: { type: String, default: 'Cancel' },
    loading: { type: Boolean, default: false }
  },
  emits: ['confirm', 'cancel'],
  setup(props) {
    const icon = computed(() => {
      switch (props.type) {
        case 'danger':
        case 'warning':
          return ExclamationTriangleIcon
        case 'success':
          return CheckCircleIcon
        case 'info':
          return InformationCircleIcon
        default:
          return ExclamationTriangleIcon
      }
    })
    
    const iconBgColor = computed(() => {
      switch (props.type) {
        case 'danger':
          return 'bg-rose-100'
        case 'warning':
          return 'bg-amber-100'
        case 'success':
          return 'bg-emerald-100'
        case 'info':
          return 'bg-blue-100'
        default:
          return 'bg-rose-100'
      }
    })
    
    const iconColor = computed(() => {
      switch (props.type) {
        case 'danger':
          return 'text-rose-600'
        case 'warning':
          return 'text-amber-600'
        case 'success':
          return 'text-emerald-600'
        case 'info':
          return 'text-blue-600'
        default:
          return 'text-rose-600'
      }
    })
    
    const confirmBgColor = computed(() => {
      switch (props.type) {
        case 'danger':
          return 'bg-rose-600'
        case 'warning':
          return 'bg-amber-600'
        case 'success':
          return 'bg-emerald-600'
        case 'info':
          return 'bg-blue-600'
        default:
          return 'bg-rose-600'
      }
    })
    
    const confirmHoverColor = computed(() => {
      switch (props.type) {
        case 'danger':
          return 'hover:bg-rose-700'
        case 'warning':
          return 'hover:bg-amber-700'
        case 'success':
          return 'hover:bg-emerald-700'
        case 'info':
          return 'hover:bg-blue-700'
        default:
          return 'hover:bg-rose-700'
      }
    })
    
    return {
      icon,
      iconBgColor,
      iconColor,
      confirmBgColor,
      confirmHoverColor
    }
  }
}
</script>
