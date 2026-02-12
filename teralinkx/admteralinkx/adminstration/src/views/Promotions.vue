<template>
  <div class="space-y-4 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Promotions</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage featured promotions</p>
      </div>
      <div class="flex items-center gap-2">
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

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up">
      <ModernMetricCard title="Total" :value="stats.total_promotions" color="blue">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Active" :value="stats.active_promotions" color="emerald">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Views" :value="stats.total_views" color="purple">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Conversions" :value="stats.total_conversions" color="amber">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
      </ModernMetricCard>
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

    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">{{ selectedPromotion?.id ? 'Edit Promotion' : 'Add Promotion' }}</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <div class="p-5 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2"><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Name *</label><input v-model="formData.name" type="text" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Type *</label><select v-model="formData.promotion_type" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"><option value="featured_coupon">Featured with Coupon</option><option value="bundle">Bundle</option><option value="seasonal">Seasonal</option><option value="flash_sale">Flash Sale</option><option value="new_arrival">New Arrival</option><option value="best_seller">Best Seller</option></select></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Package ID *</label><input v-model="formData.package" type="number" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div class="col-span-2"><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Headline *</label><input v-model="formData.headline" type="text" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Start Date *</label><input v-model="formData.start_date" type="datetime-local" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">End Date *</label><input v-model="formData.end_date" type="datetime-local" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Display Order</label><input v-model="formData.display_order" type="number" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div class="flex items-center"><label class="flex items-center gap-2 cursor-pointer"><input v-model="formData.is_active" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" /><span class="text-xs text-slate-700 dark:text-slate-300">Active</span></label></div>
            <div class="col-span-2"><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label><textarea v-model="formData.description" rows="3" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"></textarea></div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="savePromotion" :disabled="saveLoading" class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Saving...' : (selectedPromotion?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>

    <ConfirmDialog :show="showDeleteModal" title="Delete Promotion" :message="`Delete promotion ${promotionToDelete?.name}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Promotions',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const promotions = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedPromotion = ref(null)
    const promotionToDelete = ref(null)
    const saveLoading = ref(false)
    const formData = ref({ name: '', promotion_type: 'featured_coupon', package: '', headline: '', start_date: '', end_date: '', display_order: 0, is_active: true, description: '' })

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
    const formatDate = (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
    
    const openAddModal = () => {
      selectedPromotion.value = null
      formData.value = { name: '', promotion_type: 'featured_coupon', package: '', headline: '', start_date: '', end_date: '', display_order: 0, is_active: true, description: '' }
      showFormModal.value = true
    }
    
    const openEditModal = (promo) => {
      selectedPromotion.value = promo
      formData.value = { name: promo.name || '', promotion_type: promo.promotion_type || 'featured_coupon', package: promo.package || '', headline: promo.headline || '', start_date: promo.start_date || '', end_date: promo.end_date || '', display_order: promo.display_order || 0, is_active: promo.is_active || false, description: promo.description || '' }
      showFormModal.value = true
    }
    
    const closeFormModal = () => {
      showFormModal.value = false
      selectedPromotion.value = null
      formData.value = { name: '', promotion_type: 'featured_coupon', package: '', headline: '', start_date: '', end_date: '', display_order: 0, is_active: true, description: '' }
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
      try {
        await makeRequest('delete', `suapi/promotions/${promotionToDelete.value.id}/`)
        await refreshData()
        closeDeleteModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    onMounted(refreshData)

    return {
      loading, error, promotions, stats, searchTerm, statusFilter, showFormModal, showDeleteModal, selectedPromotion, promotionToDelete,
      saveLoading, formData, filteredPromotions, fetchPromotions, refreshData, formatDate,
      openAddModal, openEditModal, closeFormModal, savePromotion, openDeleteModal, closeDeleteModal, confirmDelete
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
