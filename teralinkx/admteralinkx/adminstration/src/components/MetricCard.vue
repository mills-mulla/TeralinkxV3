<template>
  <div class="group">
    <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 transition-all duration-200 hover:shadow-md">
      <!-- Header -->
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-slate-600 dark:text-slate-400 font-medium text-sm">{{ title }}</h3>
        <div class="w-9 h-9 rounded-lg flex items-center justify-center" :class="iconBgColor">
          <slot></slot>
        </div>
      </div>

      <!-- Value -->
      <div class="mb-3">
        <div class="font-semibold text-slate-900 dark:text-white" :class="valueSize">
          {{ formattedValue }}
        </div>
      </div>

      <!-- Trend -->
      <div class="flex items-center space-x-2">
        <div class="flex items-center space-x-1" :class="trendTextColor">
          <TrendIcon :trend="trend" />
          <span class="text-xs font-medium">{{ trendValue }}</span>
        </div>
        <span class="text-slate-400 dark:text-slate-500 text-xs">vs last week</span>
      </div>
    </div>
  </div>
</template>

<script>
import { h } from 'vue'

// Separate TrendIcon component using render function
const TrendIcon = {
  name: 'TrendIcon',
  props: {
    trend: {
      type: String,
      default: 'stable',
      validator: (val) => ['up', 'down', 'stable'].includes(val)
    }
  },
  render() {
    if (this.trend === 'up') {
      return h('svg', {
        class: 'w-4 h-4 text-emerald-600',
        fill: 'none',
        viewBox: '0 0 24 24',
        stroke: 'currentColor'
      }, [
        h('path', {
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          'stroke-width': '2',
          d: 'M5 10l7-7m0 0l7 7m-7-7v18'
        })
      ])
    } else if (this.trend === 'down') {
      return h('svg', {
        class: 'w-4 h-4 text-rose-600',
        fill: 'none',
        viewBox: '0 0 24 24',
        stroke: 'currentColor'
      }, [
        h('path', {
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          'stroke-width': '2',
          d: 'M19 14l-7 7m0 0l-7-7m7 7V3'
        })
      ])
    } else {
      return h('svg', {
        class: 'w-4 h-4 text-slate-600',
        fill: 'none',
        viewBox: '0 0 24 24',
        stroke: 'currentColor'
      }, [
        h('path', {
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          'stroke-width': '2',
          d: 'M5 12h14'
        })
      ])
    }
  }
}

export default {
  name: 'ModernMetricCard',
  components: {
    TrendIcon
  },
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    trend: {
      type: String,
      validator: (val) => ['up', 'down', 'stable'].includes(val),
      default: 'stable'
    },
    trendValue: {
      type: String,
      default: '0%'
    },
    color: {
      type: String,
      default: 'blue',
      validator: (val) => ['blue', 'emerald', 'green', 'purple', 'amber', 'indigo', 'cyan', 'rose'].includes(val)
    },
    formatted: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    formattedValue() {
      // Handle undefined/null values
      if (this.value === undefined || this.value === null) {
        return '0'
      }
      
      if (!this.formatted || typeof this.value !== 'number') {
        return this.value;
      }
      return new Intl.NumberFormat().format(this.value);
    },
    valueSize() {
      const length = String(this.formattedValue || '0').length;
      if (length > 12) return 'text-lg';
      if (length > 8) return 'text-xl';
      return 'text-2xl';
    },
    iconBgColor() {
      const colors = {
        blue: 'bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400',
        emerald: 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
        green: 'bg-green-50 dark:bg-green-500/10 text-green-600 dark:text-green-400',
        purple: 'bg-purple-50 dark:bg-purple-500/10 text-purple-600 dark:text-purple-400',
        amber: 'bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400',
        indigo: 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400',
        cyan: 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-600 dark:text-cyan-400',
        rose: 'bg-rose-50 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400'
      };
      return colors[this.color] || colors.blue;
    },
    trendTextColor() {
      const colors = {
        up: 'text-emerald-600 dark:text-emerald-400',
        down: 'text-rose-600 dark:text-rose-400',
        stable: 'text-slate-600 dark:text-slate-400'
      };
      return colors[this.trend];
    }
  }
}
</script>