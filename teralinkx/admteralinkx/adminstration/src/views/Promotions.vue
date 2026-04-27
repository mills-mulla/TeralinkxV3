<template>
  <div class="space-y-4 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Promotions</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage featured promotions</p>
      </div>
      <div class="flex items-center gap-2">
        <template v-if="selectedIds.length">
          <span class="text-xs text-slate-500 dark:text-slate-400">{{ selectedIds.length }} selected</span>
          <button @click="bulkAction('activate')" class="px-2 py-1 text-[10px] font-medium rounded bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-200">Activate</button>
          <button @click="bulkAction('deactivate')" class="px-2 py-1 text-[10px] font-medium rounded bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400 hover:bg-amber-200">Deactivate</button>
          <button @click="bulkAction('delete')" class="px-2 py-1 text-[10px] font-medium rounded bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400 hover:bg-red-200">Delete</button>
        </template>
        <button @click="openAddModal" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
          Add Promotion
        </button>
        <button @click="refreshData" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
          <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
        </button>
      </div>
    </div>

    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-rose-600 dark:text-rose-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          <div>
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load promotions</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchPromotions" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <div class="flex items-center gap-2 flex-wrap">
      <div class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-xl">
        <span class="text-[10px] text-blue-600 dark:text-blue-400 font-medium">Total</span>
        <span class="text-sm font-bold text-blue-700 dark:text-blue-300">{{ stats.total_promotions || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl">
        <div class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
        <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">Active</span>
        <span class="text-sm font-bold text-emerald-700 dark:text-emerald-300">{{ stats.active_promotions || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-purple-50 dark:bg-purple-500/10 border border-purple-200 dark:border-purple-500/20 rounded-xl">
        <span class="text-[10px] text-purple-600 dark:text-purple-400 font-medium">👁 Views</span>
        <span class="text-sm font-bold text-purple-700 dark:text-purple-300">{{ stats.total_views || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-xl">
        <span class="text-[10px] text-amber-600 dark:text-amber-400 font-medium">⭐ Conversions</span>
        <span class="text-sm font-bold text-amber-700 dark:text-amber-300">{{ stats.total_conversions || 0 }}</span>
      </div>
    </div>

    <div class="space-y-3 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2">
        <div class="flex-1">
          <input v-model="searchTerm" type="text" placeholder="Search promotions..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 w-6"><input type="checkbox" @change="toggleSelectAll" :checked="selectedIds.length === filteredPromotions.length && filteredPromotions.length > 0" class="rounded" /></th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Promotion</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Type</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Package</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Performance</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Period</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="promo in filteredPromotions" :key="promo.id" @click="openEditModal(promo)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2" @click.stop><input type="checkbox" :value="promo.id" v-model="selectedIds" class="rounded" /></td>
                <td class="px-3 py-2">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
                      <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                    </div>
                    <div>
                      <p class="text-xs font-medium text-slate-900 dark:text-white">{{ promo.name }}</p>
                      <p class="text-[10px] text-slate-500 dark:text-slate-400">{{ promo.headline }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400">{{ promo.promotion_type }}</span></td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ promo.package_name || 'N/A' }}</td>
                <td class="px-3 py-2">
                  <div class="text-[10px] text-slate-900 dark:text-white">
                    <div>Views: {{ promo.views || 0 }}</div>
                    <div>Clicks: {{ promo.clicks || 0 }}</div>
                    <div>Conv: {{ promo.conversions || 0 }}</div>
                  </div>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">
                  <div class="text-[10px]">
                    <div>{{ formatDate(promo.start_date) }}</div>
                    <div>{{ formatDate(promo.end_date) }}</div>
                  </div>
                </td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="promo.is_active ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'">{{ promo.is_active ? 'Active' : 'Inactive' }}</span></td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button @click.stop="openEditModal(promo)" class="p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                      <svg class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                    </button>
                    <button @click.stop="openDeleteModal(promo)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
                      <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-end sm:items-center justify-end" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-900 w-full sm:w-[520px] h-full flex flex-col shadow-2xl">
        <div class="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-700 shrink-0">
          <div>
            <h2 class="text-sm font-semibold text-slate-900 dark:text-white">{{ selectedPromotion?.id ? 'Edit Promotion' : 'New Promotion' }}</h2>
            <p class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{{ selectedPromotion?.id ? selectedPromotion.name : 'Fill in promotion details' }}</p>
          </div>
          <button @click="closeFormModal" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg">
            <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto">
          <!-- Core -->
          <div class="border-b border-slate-200 dark:border-slate-700">
            <button @click="toggleSection('core')" class="w-full flex items-center justify-between px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">Core Details</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="openSection==='core'?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="openSection==='core'" class="px-5 pb-4 space-y-3">
              <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Name *</label><input v-model="formData.name" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
              <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Headline *</label><input v-model="formData.headline" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
              <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Description</label><textarea v-model="formData.description" rows="2" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"></textarea></div>
            </div>
          </div>
          <!-- Package & Coupon -->
          <div class="border-b border-slate-200 dark:border-slate-700">
            <button @click="toggleSection('package')" class="w-full flex items-center justify-between px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">Package & Coupon</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="openSection==='package'?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="openSection==='package'" class="px-5 pb-4 space-y-3">
              <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Type *</label>
                <select v-model="formData.promotion_type" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                  <option v-for="t in formOptions.promotion_types" :key="t.value" :value="t.value">{{ t.label }}</option>
                </select>
              </div>
              <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Package *</label>
                <select v-model="formData.package" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                  <option value="">Select package...</option>
                  <option v-for="p in formOptions.packages" :key="p.id" :value="p.id">{{ p.name }} — KSh {{ p.price }}</option>
                </select>
              </div>
              <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Coupon (optional)</label>
                <select v-model="formData.coupon" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                  <option :value="null">None</option>
                  <option v-for="c in formOptions.coupons" :key="c.id" :value="c.id">{{ c.code }} — {{ c.name }}</option>
                </select>
              </div>
            </div>
          </div>
          <!-- Schedule -->
          <div class="border-b border-slate-200 dark:border-slate-700">
            <button @click="toggleSection('schedule')" class="w-full flex items-center justify-between px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">Schedule</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="openSection==='schedule'?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="openSection==='schedule'" class="px-5 pb-4 space-y-3">
              <div class="grid grid-cols-2 gap-3">
                <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Start Date *</label><input v-model="formData.start_date" type="datetime-local" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">End Date *</label><input v-model="formData.end_date" type="datetime-local" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
              </div>
            </div>
          </div>
          <!-- Settings -->
          <div class="border-b border-slate-200 dark:border-slate-700">
            <button @click="toggleSection('settings')" class="w-full flex items-center justify-between px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">Settings</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="openSection==='settings'?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="openSection==='settings'" class="px-5 pb-4 space-y-3">
              <div class="grid grid-cols-2 gap-3">
                <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Display Order</label><input v-model="formData.display_order" type="number" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Button Text</label><input v-model="formData.button_text" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
              </div>
              <label class="flex items-center gap-2 cursor-pointer"><input v-model="formData.is_active" type="checkbox" class="w-4 h-4 rounded text-blue-600" /><span class="text-xs text-slate-700 dark:text-slate-300">Active</span></label>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 px-5 py-4 border-t border-slate-200 dark:border-slate-700 shrink-0">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg">Cancel</button>
          <button @click="savePromotion" :disabled="saveLoading" class="px-4 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg disabled:opacity-50">{{ saveLoading ? 'Saving...' : (selectedPromotion?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>

    <ConfirmDialog :show="showDeleteModal" title="Delete Promotion" :message="`Delete promotion ${promotionToDelete?.name}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useOptimistic } from '../composables/useOptimistic'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Promotions',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest, invalidateCache } = useApi()
    const promotions = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedPromotion = ref(null)
    const promotionToDelete = ref(null)
    const saveLoading = ref(false)
    const selectedIds = ref([])
    const openSection = ref('core')
    const formOptions = ref({ packages: [], coupons: [], promotion_types: [] })
    const formData = ref({ name: '', promotion_type: 'featured_coupon', package: '', coupon: null, headline: '', start_date: '', end_date: '', display_order: 0, button_text: 'Get Offer', is_active: true, description: '' })

    const filteredPromotions = computed(() => {
      let result = promotions.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(p => p.name?.toLowerCase().includes(term) || p.headline?.toLowerCase().includes(term))
      }
      if (statusFilter.value) result = result.filter(p => p.is_active === (statusFilter.value === 'true'))
      return result
    })

    const fetchPromotions = async () => {
      try {
        const data = await makeRequest('get', 'suapi/promotions/')
        promotions.value = data.results || data
      } catch (err) { console.error('Error:', err) }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/promotions/stats/')
      } catch (err) { console.error('Error:', err) }
    }

    const refreshData = () => Promise.all([fetchPromotions(), fetchStats()])
    const { optimisticRemove, optimisticUpdate } = useOptimistic(promotions, fetchPromotions, invalidateCache, 'suapi/promotions')
    const toggleSection = (s) => { openSection.value = openSection.value === s ? '' : s }
    const toggleSelectAll = (e) => { selectedIds.value = e.target.checked ? filteredPromotions.value.map(p => p.id) : [] }

    const fetchFormOptions = async () => {
      try {
        formOptions.value = await makeRequest('get', 'suapi/promotions/form_options/')
      } catch (e) { console.error(e) }
    }
    const formatDate = (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
    
    const openAddModal = () => {
      selectedPromotion.value = null
      openSection.value = 'core'
      formData.value = { name: '', promotion_type: 'featured_coupon', package: '', coupon: null, headline: '', start_date: '', end_date: '', display_order: 0, button_text: 'Get Offer', is_active: true, description: '' }
      showFormModal.value = true
    }
    
    const openEditModal = (promo) => {
      selectedPromotion.value = promo
      openSection.value = 'core'
      formData.value = { name: promo.name || '', promotion_type: promo.promotion_type || 'featured_coupon', package: promo.package || '', coupon: promo.coupon || null, headline: promo.headline || '', start_date: promo.start_date || '', end_date: promo.end_date || '', display_order: promo.display_order || 0, button_text: promo.button_text || 'Get Offer', is_active: promo.is_active ?? true, description: promo.description || '' }
      showFormModal.value = true
    }
    
    const closeFormModal = () => {
      showFormModal.value = false
      selectedPromotion.value = null
      formData.value = { name: '', promotion_type: 'featured_coupon', package: '', coupon: null, headline: '', start_date: '', end_date: '', display_order: 0, button_text: 'Get Offer', is_active: true, description: '' }
    }

    const savePromotion = async () => {
      saveLoading.value = true
      try {
        if (selectedPromotion.value?.id) {
          await makeRequest('patch', `suapi/promotions/${selectedPromotion.value.id}/`, formData.value)
        } else {
          await makeRequest('post', 'suapi/promotions/', formData.value)
        }
        await refreshData()
        closeFormModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || JSON.stringify(err.response?.data) || err.message))
      } finally {
        saveLoading.value = false
      }
    }

    const openDeleteModal = (promo) => { promotionToDelete.value = promo; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; promotionToDelete.value = null }

    const confirmDelete = async () => {
      const id = promotionToDelete.value.id
      optimisticRemove(id)
      closeDeleteModal()
      try {
        await makeRequest('delete', `suapi/promotions/${id}/`)
      } catch (err) {
        await refreshData()
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    const bulkAction = async (action) => {
      if (!selectedIds.value.length) return
      if (action === 'delete' && !confirm(`Delete ${selectedIds.value.length} promotions?`)) return
      if (action === 'delete') selectedIds.value.forEach(id => optimisticRemove(id))
      else selectedIds.value.forEach(id => optimisticUpdate(id, { is_active: action === 'activate' }))
      const ids = [...selectedIds.value]
      selectedIds.value = []
      try {
        await makeRequest('post', 'suapi/promotions/bulk_action/', { action, ids })
      } catch (err) {
        await refreshData()
        console.error(err)
      }
    }

    onMounted(() => { refreshData(); fetchFormOptions() })

    return {
      loading, error, promotions, stats, searchTerm, statusFilter, showFormModal, showDeleteModal, selectedPromotion, promotionToDelete,
      saveLoading, formData, filteredPromotions, fetchPromotions, refreshData, formatDate,
      openAddModal, openEditModal, closeFormModal, savePromotion, openDeleteModal, closeDeleteModal, confirmDelete,
      selectedIds, openSection, toggleSection, toggleSelectAll, bulkAction, formOptions
    }
  }
}
</script>

<style scoped>
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes slide-up { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fade-in 0.3s ease-out; }
.animate-slide-up { animation: slide-up 0.4s ease-out; }
</style>
