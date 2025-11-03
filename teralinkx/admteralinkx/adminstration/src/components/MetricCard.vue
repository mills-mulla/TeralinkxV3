<template>
  <div class="group relative">
    <div class="absolute inset-0 bg-gradient-to-br from-white to-slate-50 rounded-2xl shadow-sm border border-slate-200/60 transform group-hover:scale-105 group-hover:shadow-xl transition-all duration-500"></div>
    
    <div class="relative bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-slate-200/40 group-hover:border-slate-300/60 transition-all duration-500">
      <!-- Header -->
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-slate-600 font-medium text-sm">{{ title }}</h3>
        <div class="w-10 h-10 rounded-xl flex items-center justify-center shadow-sm" :class="iconBgColor">
          <span class="text-lg">{{ icon }}</span>
        </div>
      </div>

      <!-- Value -->
      <div class="mb-3">
        <div class="text-2xl font-bold text-slate-800" :class="valueSize">
          {{ formattedValue }}
        </div>
      </div>

      <!-- Trend -->
      <div class="flex items-center space-x-2">
        <div class="flex items-center space-x-1" :class="trendTextColor">
          <TrendIcon :trend="trend" />
          <span class="text-sm font-medium">{{ trendValue }}</span>
        </div>
        <span class="text-slate-400 text-sm">vs last week</span>
      </div>

      <!-- Decorative elements -->
      <div class="absolute bottom-0 right-0 w-16 h-16 rounded-tl-full" :class="gradientBg" opacity="10"></div>
    </div>
  </div>
</template>

<script>
// Separate TrendIcon component
const TrendIcon = {
  name: 'TrendIcon',
  props: {
    trend: {
      type: String,
      default: 'stable',
      validator: (val) => ['up', 'down', 'stable'].includes(val)
    }
  },
  template: `
    <svg 
      v-if="trend === 'up'" 
      class="w-4 h-4 text-emerald-600" 
      fill="none" 
      viewBox="0 0 24 24" 
      stroke="currentColor"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
    </svg>
    <svg 
      v-else-if="trend === 'down'" 
      class="w-4 h-4 text-rose-600" 
      fill="none" 
      viewBox="0 0 24 24" 
      stroke="currentColor"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
    </svg>
    <svg 
      v-else 
      class="w-4 h-4 text-slate-600" 
      fill="none" 
      viewBox="0 0 24 24" 
      stroke="currentColor"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14" />
    </svg>
  `
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
    icon: {
      type: String,
      default: '📊'
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
      if (!this.formatted || typeof this.value !== 'number') {
        return this.value;
      }
      return new Intl.NumberFormat().format(this.value);
    },
    valueSize() {
      const length = this.formattedValue.toString().length;
      if (length > 12) return 'text-xl';
      if (length > 8) return 'text-2xl';
      return 'text-3xl';
    },
    iconBgColor() {
      const colors = {
        blue: 'bg-blue-50 text-blue-600',
        emerald: 'bg-emerald-50 text-emerald-600',
        green: 'bg-green-50 text-green-600',
        purple: 'bg-purple-50 text-purple-600',
        amber: 'bg-amber-50 text-amber-600',
        indigo: 'bg-indigo-50 text-indigo-600',
        cyan: 'bg-cyan-50 text-cyan-600',
        rose: 'bg-rose-50 text-rose-600'
      };
      return colors[this.color] || colors.blue;
    },
    gradientBg() {
      const gradients = {
        blue: 'bg-gradient-to-br from-blue-500 to-cyan-500',
        emerald: 'bg-gradient-to-br from-emerald-500 to-teal-500',
        green: 'bg-gradient-to-br from-green-500 to-emerald-500',
        purple: 'bg-gradient-to-br from-purple-500 to-pink-500',
        amber: 'bg-gradient-to-br from-amber-500 to-orange-500',
        indigo: 'bg-gradient-to-br from-indigo-500 to-purple-500',
        cyan: 'bg-gradient-to-br from-cyan-500 to-blue-500',
        rose: 'bg-gradient-to-br from-rose-500 to-pink-500'
      };
      return gradients[this.color] || gradients.blue;
    },
    trendTextColor() {
      const colors = {
        up: 'text-emerald-600',
        down: 'text-rose-600',
        stable: 'text-slate-600'
      };
      return colors[this.trend];
    }
  }
}
</script>