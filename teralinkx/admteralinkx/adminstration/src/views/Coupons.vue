<template>
  <div class="space-y-4 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Coupons</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage discount coupons</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAddModal" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
          Add Coupon
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load coupons</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchCoupons" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up">
      <ModernMetricCard title="Total" :value="stats.total_coupons" color="blue">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Active" :value="stats.active_coupons" color="emerald">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Reward" :value="stats.reward_coupons" color="purple">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Valid" :value="stats.valid_coupons" color="amber">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
      </ModernMetricCard>
    </div>

    <div class="space-y-3 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2">
        <div class="flex-1">
          <input v-model="searchTerm" type="text" placeholder="Search coupons..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
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
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Code</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Name</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Type</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Discount</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Usage</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Valid Until</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="coupon in filteredCoupons" :key="coupon.id" @click="openEditModal(coupon)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center">
                      <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2z"/></svg>
                    </div>
                    <p class="text-xs font-medium text-slate-900 dark:text-white font-mono">{{ coupon.code }}</p>
                  </div>
                </td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ coupon.name }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400">{{ coupon.coupon_type }}</span></td>
                <td class="px-3 py-2 text-xs font-semibold text-slate-900 dark:text-white">{{ formatDiscount(coupon) }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ coupon.current_uses || 0 }} / {{ coupon.max_uses }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ formatDate(coupon.valid_until) }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="coupon.is_active ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'">{{ coupon.is_active ? 'Active' : 'Inactive' }}</span></td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button @click.stop="openEditModal(coupon)" class="p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                      <svg class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                    </button>
                    <button @click.stop="openDeleteModal(coupon)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
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
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">{{ selectedCoupon?.id ? 'Edit Coupon' : 'Add Coupon' }}</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <div class="p-5 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div class="grid grid-cols-2 gap-4">
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Code *</label><input v-model="formData.code" type="text" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Name *</label><input v-model="formData.name" type="text" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Type *</label><select v-model="formData.coupon_type" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"><option value="percentage">Percentage</option><option value="fixed">Fixed Amount</option><option value="package">Package Upgrade</option></select></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Discount Value *</label><input v-model="formData.discount_value" type="number" step="0.01" required class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Max Uses</label><input v-model="formData.max_uses" type="number" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Valid Until</label><input v-model="formData.valid_until" type="datetime-local" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
            <div class="flex items-center"><label class="flex items-center gap-2 cursor-pointer"><input v-model="formData.is_active" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" /><span class="text-xs text-slate-700 dark:text-slate-300">Active</span></label></div>
            <div class="flex items-center"><label class="flex items-center gap-2 cursor-pointer"><input v-model="formData.is_reward" type="checkbox" class="w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded" /><span class="text-xs text-slate-700 dark:text-slate-300">Reward Coupon</span></label></div>
            <div class="col-span-2"><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label><textarea v-model="formData.description" rows="3" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"></textarea></div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveCoupon" :disabled="saveLoading" class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg" :class="{ 'opacity-50': saveLoading }">{{ saveLoading ? 'Saving...' : (selectedCoupon?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>

    <ConfirmDialog :show="showDeleteModal" title="Delete Coupon" :message="`Delete coupon ${couponToDelete?.code}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Coupons',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const coupons = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedCoupon = ref(null)
    const couponToDelete = ref(null)
    const saveLoading = ref(false)
    const formData = ref({ code: '', name: '', coupon_type: 'percentage', discount_value: 0, max_uses: 100, valid_until: '', is_active: true, is_reward: false, description: '' })

    const filteredCoupons = computed(() => {
      let result = coupons.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(c => c.code?.toLowerCase().includes(term) || c.name?.toLowerCase().includes(term))
      }
      if (statusFilter.value) result = result.filter(c => c.is_active === (statusFilter.value === 'true'))
      return result
    })

    const fetchCoupons = async () => {
      try {
        const data = await makeRequest('get', 'suapi/coupons/')
        coupons.value = data.results || data
      } catch (err) { console.error('Error:', err) }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/coupons/stats/')
      } catch (err) { console.error('Error:', err) }
    }

    const refreshData = () => Promise.all([fetchCoupons(), fetchStats()])
    const formatDate = (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
    const formatDiscount = (coupon) => coupon.coupon_type === 'percentage' ? `${coupon.discount_value}%` : `KSh ${coupon.discount_value}`
    
    const openAddModal = () => {
      selectedCoupon.value = null
      formData.value = { code: '', name: '', coupon_type: 'percentage', discount_value: 0, max_uses: 100, valid_until: '', is_active: true, is_reward: false, description: '' }
      showFormModal.value = true
    }
    
    const openEditModal = (coupon) => {
      selectedCoupon.value = coupon
      formData.value = { code: coupon.code || '', name: coupon.name || '', coupon_type: coupon.coupon_type || 'percentage', discount_value: coupon.discount_value || 0, max_uses: coupon.max_uses || 100, valid_until: coupon.valid_until || '', is_active: coupon.is_active || false, is_reward: coupon.is_reward || false, description: coupon.description || '' }
      showFormModal.value = true
    }
    
    const closeFormModal = () => {
      showFormModal.value = false
      selectedCoupon.value = null
      formData.value = { code: '', name: '', coupon_type: 'percentage', discount_value: 0, max_uses: 100, valid_until: '', is_active: true, is_reward: false, description: '' }
    }

    const saveCoupon = async () => {
      saveLoading.value = true
      try {
        if (selectedCoupon.value?.id) {
          await makeRequest('patch', `suapi/coupons/${selectedCoupon.value.id}/`, formData.value)
        } else {
          await makeRequest('post', 'suapi/coupons/', formData.value)
        }
        await refreshData()
        closeFormModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || JSON.stringify(err.response?.data) || err.message))
      } finally {
        saveLoading.value = false
      }
    }

    const openDeleteModal = (coupon) => { couponToDelete.value = coupon; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; couponToDelete.value = null }

    const confirmDelete = async () => {
      try {
        await makeRequest('delete', `suapi/coupons/${couponToDelete.value.id}/`)
        await refreshData()
        closeDeleteModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    onMounted(refreshData)

    return {
      loading, error, coupons, stats, searchTerm, statusFilter, showFormModal, showDeleteModal, selectedCoupon, couponToDelete,
      saveLoading, formData, filteredCoupons, fetchCoupons, refreshData, formatDate, formatDiscount,
      openAddModal, openEditModal, closeFormModal, saveCoupon, openDeleteModal, closeDeleteModal, confirmDelete
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
