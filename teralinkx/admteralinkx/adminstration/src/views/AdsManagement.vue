<template>
  <div class="space-y-6">
    <!-- Header with Stats -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Advertisements Management</h1>
        <p class="text-sm text-slate-600 dark:text-slate-400 mt-1">Manage your advertising campaigns</p>
      </div>
      <button @click="showCreateModal = true" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        Create Ad
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-4 text-white">
        <p class="text-blue-100 text-xs mb-1">Total Ads</p>
        <p class="text-3xl font-bold">{{ stats.total || 0 }}</p>
        <p class="text-xs text-blue-100 mt-1">{{ stats.active || 0 }} active</p>
      </div>
      <div class="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-4 text-white">
        <p class="text-emerald-100 text-xs mb-1">Impressions</p>
        <p class="text-3xl font-bold">{{ formatNumber(stats.total_impressions || 0) }}</p>
        <p class="text-xs text-emerald-100 mt-1">{{ recentActivity.impressions || 0 }} this week</p>
      </div>
      <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-4 text-white">
        <p class="text-purple-100 text-xs mb-1">Clicks</p>
        <p class="text-3xl font-bold">{{ formatNumber(stats.total_clicks || 0) }}</p>
        <p class="text-xs text-purple-100 mt-1">{{ stats.avg_ctr || 0 }}% CTR</p>
      </div>
      <div class="bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl p-4 text-white">
        <p class="text-amber-100 text-xs mb-1">Total Spent</p>
        <p class="text-3xl font-bold">{{ formatMoney(stats.total_spent || 0) }}</p>
        <p class="text-xs text-amber-100 mt-1">of {{ formatMoney(stats.total_budget || 0) }}</p>
      </div>
      <div class="bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-xl p-4 text-white">
        <p class="text-cyan-100 text-xs mb-1">New This Week</p>
        <p class="text-3xl font-bold">{{ recentActivity.new_ads || 0 }}</p>
        <p class="text-xs text-cyan-100 mt-1">{{ recentActivity.clicks || 0 }} clicks</p>
      </div>
    </div>

    <!-- Analytics Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Performance by Type -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Performance by Ad Type</h3>
        <div class="space-y-3">
          <div v-for="(data, type) in analyticsByType" :key="type" class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <span class="px-2 py-1 text-xs rounded-full" :class="getTypeColor(type)">{{ type }}</span>
                <span class="text-xs text-slate-500 dark:text-slate-400">{{ data.count }} ads</span>
              </div>
              <div class="flex items-center gap-4 text-xs text-slate-600 dark:text-slate-400">
                <span>{{ formatNumber(data.impressions) }} views</span>
                <span>{{ formatNumber(data.clicks) }} clicks</span>
                <span class="font-semibold" :class="data.ctr > 5 ? 'text-emerald-600' : 'text-slate-600'">{{ data.ctr }}% CTR</span>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ formatMoney(data.spent) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Performers -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Top Performing Ads</h3>
        <div class="space-y-3">
          <div v-for="(ad, index) in topPerformers" :key="ad.id" class="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm" :class="index === 0 ? 'bg-yellow-400 text-yellow-900' : index === 1 ? 'bg-slate-300 text-slate-700' : index === 2 ? 'bg-amber-600 text-white' : 'bg-slate-200 text-slate-600'">
              {{ index + 1 }}
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-slate-900 dark:text-white">{{ ad.title }}</p>
              <div class="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400 mt-1">
                <span>{{ formatNumber(ad.impressions) }} views</span>
                <span>{{ formatNumber(ad.clicks) }} clicks</span>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm font-bold text-emerald-600 dark:text-emerald-400">{{ ad.ctr }}%</p>
              <p class="text-xs text-slate-500 dark:text-slate-400">CTR</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Ads Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700">
        <input v-model="searchQuery" type="text" placeholder="Search ads..." class="w-full px-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-sm" />
      </div>

      <div v-if="loading" class="p-12 text-center">
        <div class="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto"></div>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Ad</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Type</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Campaign</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Performance</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Budget</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Status</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="ad in filteredAds" :key="ad.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <img v-if="ad.image" :src="ad.image" class="w-12 h-12 rounded object-cover" />
                  <div class="w-12 h-12 bg-slate-200 dark:bg-slate-700 rounded flex items-center justify-center" v-else>
                    <svg class="w-6 h-6 text-slate-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                    </svg>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-slate-900 dark:text-white">{{ ad.title }}</p>
                    <p class="text-xs text-slate-500 dark:text-slate-400">{{ ad.brand_name }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 text-xs rounded-full" :class="getTypeColor(ad.ad_type)">
                  {{ ad.ad_type }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-slate-900 dark:text-white">{{ ad.campaign_name || 'N/A' }}</td>
              <td class="px-4 py-3">
                <div class="text-xs">
                  <p class="text-slate-900 dark:text-white">{{ formatNumber(ad.impressions) }} views</p>
                  <p class="text-slate-500">{{ formatNumber(ad.clicks) }} clicks ({{ ad.performance?.click_through_rate || 0 }}%)</p>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="text-xs">
                  <p class="text-slate-900 dark:text-white">KES {{ formatNumber(ad.budget) }}</p>
                  <p class="text-slate-500">Spent: {{ formatNumber(ad.total_spent) }}</p>
                </div>
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 text-xs rounded-full" :class="getStatusColor(ad.status)">
                  {{ ad.status }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button @click="editAd(ad)" class="p-2 hover:bg-blue-100 dark:hover:bg-blue-600 rounded">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                  </button>
                  <button @click="deleteAd(ad)" class="p-2 hover:bg-red-100 dark:hover:bg-red-600 rounded">
                    <svg class="w-4 h-4 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || selectedAd" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">{{ selectedAd ? 'Edit' : 'Create' }} Advertisement</h2>
          <button @click="closeModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-140px)] space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Title *</label>
              <input v-model="formData.title" type="text" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Ad Type *</label>
              <select v-model="formData.ad_type" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg">
                <option value="banner">Banner</option>
                <option value="video">Video</option>
                <option value="audio">Audio</option>
                <option value="popup">Popup</option>
                <option value="native">Native</option>
                <option value="carousel">Carousel</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Status *</label>
              <select v-model="formData.status" required class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg">
                <option value="draft">Draft</option>
                <option value="active">Active</option>
                <option value="paused">Paused</option>
                <option value="expired">Expired</option>
              </select>
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Caption</label>
              <textarea v-model="formData.caption" rows="2" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg"></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Campaign Name</label>
              <input v-model="formData.campaign_name" type="text" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Brand Name</label>
              <input v-model="formData.brand_name" type="text" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">CTA Text</label>
              <input v-model="formData.cta_text" type="text" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">CTA URL</label>
              <input v-model="formData.cta_url" type="url" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Budget (KES)</label>
              <input v-model="formData.budget" type="number" step="0.01" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Priority</label>
              <select v-model="formData.priority" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg">
                <option :value="1">Low</option>
                <option :value="2">Medium</option>
                <option :value="3">High</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Start Date</label>
              <input v-model="formData.start_date" type="datetime-local" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">End Date</label>
              <input v-model="formData.end_date" type="datetime-local" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg" />
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeModal" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveAd" :disabled="saveLoading" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Saving...' : 'Save' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdsManagement',
  data() {
    return {
      ads: [],
      stats: {},
      analyticsByType: {},
      topPerformers: [],
      recentActivity: {},
      loading: false,
      saveLoading: false,
      searchQuery: '',
      showCreateModal: false,
      selectedAd: null,
      formData: {
        title: '',
        caption: '',
        ad_type: 'banner',
        status: 'draft',
        campaign_name: '',
        brand_name: '',
        cta_text: 'Learn More',
        cta_url: '',
        budget: 0,
        priority: 2,
        start_date: '',
        end_date: ''
      }
    }
  },
  computed: {
    filteredAds() {
      if (!this.searchQuery) return this.ads
      const query = this.searchQuery.toLowerCase()
      return this.ads.filter(ad =>
        ad.title.toLowerCase().includes(query) ||
        ad.campaign_name?.toLowerCase().includes(query) ||
        ad.brand_name?.toLowerCase().includes(query)
      )
    }
  },
  mounted() {
    this.fetchAds()
  },
  methods: {
    async fetchAds() {
      this.loading = true
      try {
        const response = await fetch('https://srv.teralinkxwaves.uk/api/ads/manage/', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        })
        const data = await response.json()
        this.ads = data.ads || []
        this.stats = data.stats || {}
        this.analyticsByType = data.analytics_by_type || {}
        this.topPerformers = data.top_performers || []
        this.recentActivity = data.recent_activity || {}
      } catch (error) {
        console.error('Error fetching ads:', error)
      } finally {
        this.loading = false
      }
    },
    editAd(ad) {
      this.selectedAd = ad
      this.formData = {
        title: ad.title,
        caption: ad.caption,
        ad_type: ad.ad_type,
        status: ad.status,
        campaign_name: ad.campaign_name || '',
        brand_name: ad.brand_name || '',
        cta_text: ad.cta_text,
        cta_url: ad.cta_url,
        budget: ad.budget,
        priority: ad.priority,
        start_date: ad.start_date ? ad.start_date.slice(0, 16) : '',
        end_date: ad.end_date ? ad.end_date.slice(0, 16) : ''
      }
    },
    async saveAd() {
      this.saveLoading = true
      try {
        const url = this.selectedAd
          ? `https://srv.teralinkxwaves.uk/api/ads/manage/${this.selectedAd.id}/`
          : 'https://srv.teralinkxwaves.uk/api/ads/manage/'
        const method = this.selectedAd ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify(this.formData)
        })
        
        if (response.ok) {
          await this.fetchAds()
          this.closeModal()
        } else {
          alert('Error saving ad')
        }
      } catch (error) {
        console.error('Error saving ad:', error)
        alert('Error saving ad')
      } finally {
        this.saveLoading = false
      }
    },
    async deleteAd(ad) {
      if (!confirm(`Delete "${ad.title}"?`)) return
      
      try {
        const response = await fetch(`https://srv.teralinkxwaves.uk/api/ads/manage/${ad.id}/`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        })
        
        if (response.ok) {
          await this.fetchAds()
        }
      } catch (error) {
        console.error('Error deleting ad:', error)
      }
    },
    closeModal() {
      this.showCreateModal = false
      this.selectedAd = null
      this.formData = {
        title: '',
        caption: '',
        ad_type: 'banner',
        status: 'draft',
        campaign_name: '',
        brand_name: '',
        cta_text: 'Learn More',
        cta_url: '',
        budget: 0,
        priority: 2,
        start_date: '',
        end_date: ''
      }
    },
    getTypeColor(type) {
      const colors = {
        banner: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
        video: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400',
        audio: 'bg-pink-100 dark:bg-pink-900/30 text-pink-700 dark:text-pink-400',
        popup: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400',
        native: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400',
        carousel: 'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-400'
      }
      return colors[type] || 'bg-slate-100 dark:bg-slate-700'
    },
    getStatusColor(status) {
      const colors = {
        draft: 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400',
        active: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400',
        paused: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400',
        expired: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
      }
      return colors[status] || 'bg-slate-100 dark:bg-slate-700'
    },
    formatNumber(num) {
      return new Intl.NumberFormat().format(num || 0)
    },
    formatMoney(num) {
      return 'KES ' + new Intl.NumberFormat().format(Math.round(num || 0))
    }
  }
}
</script>
