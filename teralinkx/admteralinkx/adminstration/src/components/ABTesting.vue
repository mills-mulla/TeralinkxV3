<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-slate-900 dark:text-white">A/B Testing Experiments</h2>
      <button @click="showModal = true" class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded-lg transition-colors">
        New Experiment
      </button>
    </div>

    <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>

    <div v-else class="space-y-4">
      <div
        v-for="exp in data.experiments"
        :key="exp.id"
        class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5"
      >
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-sm font-medium text-slate-900 dark:text-white">{{ exp.name }}</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Started: {{ exp.start_date }}</p>
          </div>
          <span class="px-3 py-1 rounded-full text-xs font-medium" :class="getStatusBadge(exp.status)">
            {{ exp.status }}
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div
            v-for="variant in exp.variants"
            :key="variant.name"
            class="p-4 rounded-lg border-2"
            :class="variant.name === exp.winner ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10' : 'border-slate-200 dark:border-slate-700'"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-slate-900 dark:text-white">{{ variant.name }}</span>
              <svg v-if="variant.name === exp.winner" class="w-5 h-5 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <div class="space-y-2">
              <div class="flex justify-between text-xs">
                <span class="text-slate-600 dark:text-slate-400">Participants</span>
                <span class="font-semibold text-slate-900 dark:text-white">{{ variant.participants }}</span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-slate-600 dark:text-slate-400">Conversions</span>
                <span class="font-semibold text-slate-900 dark:text-white">{{ variant.conversions }}</span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-slate-600 dark:text-slate-400">Conv. Rate</span>
                <span class="font-bold text-blue-600 dark:text-blue-400">{{ variant.conversion_rate }}%</span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-slate-600 dark:text-slate-400">Revenue</span>
                <span class="font-semibold text-emerald-600 dark:text-emerald-400">KSh {{ formatNumber(variant.revenue) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
            </svg>
            <span class="text-xs text-slate-600 dark:text-slate-400">Statistical Confidence</span>
          </div>
          <span class="text-sm font-bold" :class="exp.confidence >= 95 ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'">
            {{ exp.confidence }}%
          </span>
        </div>
      </div>
    </div>

    <!-- New Experiment Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full">
        <div class="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Create New Experiment</h2>
          <button @click="closeModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Experiment Name *</label>
            <input v-model="formData.name" type="text" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" placeholder="e.g., Homepage Banner Test" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Package *</label>
              <select v-model="formData.package_id" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                <option value="">Select Package</option>
                <option v-for="pkg in packages" :key="pkg.id" :value="pkg.id">{{ pkg.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Promotion Type *</label>
              <select v-model="formData.promotion_type" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                <option value="discount">Discount</option>
                <option value="bonus_data">Bonus Data</option>
                <option value="extended_validity">Extended Validity</option>
                <option value="free_trial">Free Trial</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Discount % *</label>
              <input v-model="formData.discount_percentage" type="number" min="0" max="100" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Priority</label>
              <input v-model="formData.priority" type="number" min="0" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Start Date *</label>
              <input v-model="formData.start_date" type="date" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">End Date *</label>
              <input v-model="formData.end_date" type="date" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
          </div>
          <div>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="formData.is_active" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" />
              <span class="text-sm text-slate-700 dark:text-slate-300">Active</span>
            </label>
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeModal" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="createExperiment" :disabled="saveLoading" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Creating...' : 'Create' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ABTesting',
  props: {
    data: {
      type: Object,
      default: () => ({ experiments: [] })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh'],
  data() {
    return {
      showModal: false,
      saveLoading: false,
      packages: [],
      formData: {
        name: '',
        package_id: '',
        promotion_type: 'discount',
        discount_percentage: 10,
        priority: 1,
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date(Date.now() + 30*24*60*60*1000).toISOString().split('T')[0],
        is_active: true
      }
    }
  },
  mounted() {
    this.fetchPackages()
  },
  methods: {
    async fetchPackages() {
      try {
        const response = await fetch('https://service.teralinkxwaves.uk/suapi/packages/', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        })
        if (response.ok) {
          const data = await response.json()
          this.packages = data.results || data
        }
      } catch (error) {
        console.error('Error fetching packages:', error)
      }
    },
    closeModal() {
      this.showModal = false
      this.formData = {
        name: '',
        package_id: '',
        promotion_type: 'discount',
        discount_percentage: 10,
        priority: 1,
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date(Date.now() + 30*24*60*60*1000).toISOString().split('T')[0],
        is_active: true
      }
    },
    async createExperiment() {
      if (!this.formData.name || !this.formData.package_id) {
        alert('Please fill in all required fields')
        return
      }
      
      this.saveLoading = true
      try {
        const response = await fetch('https://service.teralinkxwaves.uk/suapi/promotions/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify(this.formData)
        })
        
        if (response.ok) {
          this.$emit('refresh')
          this.closeModal()
        } else {
          const error = await response.json()
          alert('Error: ' + (error.message || 'Failed to create experiment'))
        }
      } catch (error) {
        console.error('Error creating experiment:', error)
        alert('Failed to create experiment')
      } finally {
        this.saveLoading = false
      }
    },
    getStatusBadge(status) {
      const badges = {
        'running': 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400',
        'completed': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'ended': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'paused': 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        'draft': 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400',
        'scheduled': 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400'
      }
      return badges[status] || 'bg-slate-100 dark:bg-slate-700'
    },
    formatNumber(num) {
      return new Intl.NumberFormat().format(num)
    }
  }
}
</script>
