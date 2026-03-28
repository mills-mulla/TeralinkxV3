<template>
  <div class="space-y-6">
    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-blue-100 text-sm font-medium">Total Revenue</p>
            <p class="text-3xl font-bold mt-2">KES {{ formatNumber(totalRevenue) }}</p>
          </div>
          <svg class="w-12 h-12 text-blue-200" fill="currentColor" viewBox="0 0 20 20">
            <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-emerald-100 text-sm font-medium">Active Streams</p>
            <p class="text-3xl font-bold mt-2">{{ activeStreamsCount }}</p>
          </div>
          <svg class="w-12 h-12 text-emerald-200" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 0l-2 2a1 1 0 101.414 1.414L8 10.414l1.293 1.293a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-purple-100 text-sm font-medium">Avg Growth</p>
            <p class="text-3xl font-bold mt-2">{{ avgGrowth.toFixed(1) }}%</p>
          </div>
          <svg class="w-12 h-12 text-purple-200" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl p-6 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-amber-100 text-sm font-medium">Target Achievement</p>
            <p class="text-3xl font-bold mt-2">{{ avgAchievement.toFixed(0) }}%</p>
          </div>
          <svg class="w-12 h-12 text-amber-200" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Revenue Streams Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
      <div class="p-6 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
        <h2 class="text-xl font-bold text-slate-900 dark:text-white">Revenue Streams</h2>
        <button @click="openAddModal" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Stream
        </button>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Category</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Current Revenue</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Target</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Achievement</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Growth</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="stream in data" :key="stream.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-slate-900 dark:text-white">{{ stream.name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getCategoryColor(stream.category)">
                  {{ stream.category_display }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-slate-900 dark:text-white">KES {{ formatNumber(stream.current_revenue) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-slate-600 dark:text-slate-400">KES {{ formatNumber(stream.target_revenue) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <div class="flex-1 bg-slate-200 dark:bg-slate-700 rounded-full h-2 w-24">
                    <div 
                      class="h-2 rounded-full transition-all" 
                      :class="getAchievementColor(stream.achievement)"
                      :style="{ width: Math.min(stream.achievement, 100) + '%' }"
                    ></div>
                  </div>
                  <span class="text-sm font-medium text-slate-900 dark:text-white">{{ stream.achievement.toFixed(0) }}%</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-1">
                  <svg v-if="stream.growth > 0" class="w-4 h-4 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
                  </svg>
                  <svg v-else-if="stream.growth < 0" class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                  </svg>
                  <span class="text-sm font-medium" :class="stream.growth > 0 ? 'text-emerald-600 dark:text-emerald-400' : stream.growth < 0 ? 'text-red-600 dark:text-red-400' : 'text-slate-600 dark:text-slate-400'">
                    {{ stream.growth.toFixed(1) }}%
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span v-if="stream.is_active" class="px-2 py-1 text-xs font-medium rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
                  Active
                </span>
                <span v-else class="px-2 py-1 text-xs font-medium rounded-full bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-400">
                  Inactive
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <div class="flex items-center justify-end gap-2">
                  <button @click="openEditModal(stream)" class="p-2 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button @click="openDeleteModal(stream)" class="p-2 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
                    <svg class="w-4 h-4 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Form Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full">
        <div class="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">{{ selectedStream ? 'Edit Revenue Stream' : 'Add Revenue Stream' }}</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Name *</label>
            <input v-model="formData.name" type="text" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Category *</label>
              <select v-model="formData.category" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                <option value="voucher_sales">Voucher Sales</option>
                <option value="package_sales">Package Sales</option>
                <option value="usage_charges">Usage Charges</option>
                <option value="premium_services">Premium Services</option>
                <option value="ads_revenue">Ads Revenue</option>
                <option value="value_added">Value Added</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Target Revenue (KES) *</label>
              <input v-model="formData.target_revenue" type="number" step="0.01" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Description</label>
            <textarea v-model="formData.description" rows="3" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"></textarea>
          </div>
          <div>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="formData.is_active" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" />
              <span class="text-sm text-slate-700 dark:text-slate-300">Active Stream</span>
            </label>
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveStream" :disabled="saveLoading" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Saving...' : 'Save' }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeDeleteModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-md w-full">
        <div class="p-6">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Delete Revenue Stream</h3>
              <p class="text-sm text-slate-600 dark:text-slate-400 mt-1">Are you sure you want to delete "{{ streamToDelete?.name }}"?</p>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeDeleteModal" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="confirmDelete" :disabled="deleteLoading" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg" :class="{ 'opacity-50': deleteLoading }">{{ deleteLoading ? 'Deleting...' : 'Delete' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RevenueStreams',
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },
  emits: ['refresh'],
  data() {
    return {
      showFormModal: false,
      showDeleteModal: false,
      selectedStream: null,
      streamToDelete: null,
      saveLoading: false,
      deleteLoading: false,
      formData: {
        name: '',
        category: 'voucher_sales',
        target_revenue: 0,
        description: '',
        is_active: true
      }
    }
  },
  computed: {
    totalRevenue() {
      return this.data.reduce((sum, stream) => sum + (stream.current_revenue || 0), 0)
    },
    activeStreamsCount() {
      return this.data.filter(s => s.is_active).length
    },
    avgGrowth() {
      const activeStreams = this.data.filter(s => s.is_active)
      if (activeStreams.length === 0) return 0
      return activeStreams.reduce((sum, s) => sum + (s.growth || 0), 0) / activeStreams.length
    },
    avgAchievement() {
      const activeStreams = this.data.filter(s => s.is_active)
      if (activeStreams.length === 0) return 0
      return activeStreams.reduce((sum, s) => sum + (s.achievement || 0), 0) / activeStreams.length
    }
  },
  methods: {
    formatNumber(num) {
      return new Intl.NumberFormat('en-KE').format(num || 0)
    },
    getCategoryColor(category) {
      const colors = {
        'voucher_sales': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
        'package_sales': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
        'usage_charges': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
        'premium_services': 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
        'ads_revenue': 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-400',
        'value_added': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-400',
        'other': 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-400'
      }
      return colors[category] || colors.other
    },
    getAchievementColor(achievement) {
      if (achievement >= 100) return 'bg-emerald-500'
      if (achievement >= 75) return 'bg-blue-500'
      if (achievement >= 50) return 'bg-amber-500'
      return 'bg-red-500'
    },
    openAddModal() {
      this.selectedStream = null
      this.formData = {
        name: '',
        category: 'voucher_sales',
        target_revenue: 0,
        description: '',
        is_active: true
      }
      this.showFormModal = true
    },
    openEditModal(stream) {
      this.selectedStream = stream
      this.formData = {
        name: stream.name,
        category: stream.category,
        target_revenue: stream.target_revenue,
        description: stream.description || '',
        is_active: stream.is_active
      }
      this.showFormModal = true
    },
    closeFormModal() {
      this.showFormModal = false
      this.selectedStream = null
    },
    async saveStream() {
      this.saveLoading = true
      try {
        const url = this.selectedStream 
          ? `https://srv.teralinkxwaves.uk/api/finance/api/revenue-streams/${this.selectedStream.id}/`
          : 'https://srv.teralinkxwaves.uk/api/finance/api/revenue-streams/'
        const method = this.selectedStream ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify(this.formData)
        })
        
        if (!response.ok) throw new Error('Failed to save')
        this.$emit('refresh')
        this.closeFormModal()
      } catch (error) {
        console.error('Error saving stream:', error)
        alert('Failed to save revenue stream')
      } finally {
        this.saveLoading = false
      }
    },
    openDeleteModal(stream) {
      this.streamToDelete = stream
      this.showDeleteModal = true
    },
    closeDeleteModal() {
      this.showDeleteModal = false
      this.streamToDelete = null
    },
    async confirmDelete() {
      this.deleteLoading = true
      try {
        const response = await fetch(`https://srv.teralinkxwaves.uk/api/finance/api/revenue-streams/${this.streamToDelete.id}/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        
        if (!response.ok) throw new Error('Failed to delete')
        this.$emit('refresh')
        this.closeDeleteModal()
      } catch (error) {
        console.error('Error deleting stream:', error)
        alert('Failed to delete revenue stream')
      } finally {
        this.deleteLoading = false
      }
    }
  }
}
</script>
