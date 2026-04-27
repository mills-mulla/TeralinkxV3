<template>
  <div class="space-y-4 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Coupons</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage discount coupons</p>
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

    <div class="flex items-center gap-2 flex-wrap">
      <div class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-xl">
        <span class="text-[10px] text-blue-600 dark:text-blue-400 font-medium">Total</span>
        <span class="text-sm font-bold text-blue-700 dark:text-blue-300">{{ stats.total_coupons || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl">
        <div class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
        <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">Active</span>
        <span class="text-sm font-bold text-emerald-700 dark:text-emerald-300">{{ stats.active_coupons || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-purple-50 dark:bg-purple-500/10 border border-purple-200 dark:border-purple-500/20 rounded-xl">
        <span class="text-[10px] text-purple-600 dark:text-purple-400 font-medium">Reward</span>
        <span class="text-sm font-bold text-purple-700 dark:text-purple-300">{{ stats.reward_coupons || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-xl">
        <span class="text-[10px] text-amber-600 dark:text-amber-400 font-medium">Valid</span>
        <span class="text-sm font-bold text-amber-700 dark:text-amber-300">{{ stats.valid_coupons || 0 }}</span>
      </div>
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
                <th class="px-3 py-2 w-6"><input type="checkbox" @change="toggleSelectAll" :checked="selectedIds.length === filteredCoupons.length && filteredCoupons.length > 0" class="rounded" /></th>
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
                <td class="px-3 py-2" @click.stop><input type="checkbox" :value="coupon.id" v-model="selectedIds" class="rounded" /></td>
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

    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-end sm:items-center justify-end" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-900 w-full sm:w-[520px] h-full flex flex-col shadow-2xl">
        <!-- Modal Header -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-700 shrink-0">
          <div>
            <h2 class="text-sm font-semibold text-slate-900 dark:text-white">{{ selectedCoupon?.id ? 'Edit Coupon' : 'New Coupon' }}</h2>
            <p class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{{ selectedCoupon?.id ? selectedCoupon.code : 'Fill in coupon details' }}</p>
          </div>
          <button @click="closeFormModal" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg">
            <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <!-- Sections -->
        <div class="flex-1 overflow-y-auto">
          <!-- Section: Core -->
          <div class="border-b border-slate-200 dark:border-slate-700">
            <button @click="toggleSection('core')" class="w-full flex items-center justify-between px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">Core Details</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="openSection==='core'?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="openSection==='core'" class="px-5 pb-4 space-y-3">
              <div class="grid grid-cols-2 gap-3">
                <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Code *</label><input v-model="formData.code" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-mono" /></div>
                <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Name *</label><input v-model="formData.name" type="text" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
              </div>
              <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Description</label><textarea v-model="formData.description" rows="2" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"></textarea></div>
            </div>
          </div>
          <!-- Section: Discount -->
          <div class="border-b border-slate-200 dark:border-slate-700">
            <button @click="toggleSection('discount')" class="w-full flex items-center justify-between px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">Discount</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="openSection==='discount'?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="openSection==='discount'" class="px-5 pb-4 space-y-3">
              <div class="grid grid-cols-2 gap-3">
                <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Type *</label>
                  <select v-model="formData.coupon_type" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option value="percentage">Percentage</option>
                    <option value="fixed">Fixed Amount</option>
                    <option value="package">Package Upgrade</option>
                  </select>
                </div>
                <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Value *</label><input v-model="formData.discount_value" type="number" step="0.01" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
              </div>
            </div>
          </div>
          <!-- Section: Limits -->
          <div class="border-b border-slate-200 dark:border-slate-700">
            <button @click="toggleSection('limits')" class="w-full flex items-center justify-between px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">Usage Limits</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="openSection==='limits'?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="openSection==='limits'" class="px-5 pb-4 space-y-3">
              <div class="grid grid-cols-2 gap-3">
                <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Max Uses</label><input v-model="formData.max_uses" type="number" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Per User</label><input v-model="formData.max_uses_per_user" type="number" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Valid From</label><input v-model="formData.valid_from" type="datetime-local" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="block text-[10px] font-medium text-slate-600 dark:text-slate-400 mb-1">Valid Until</label><input v-model="formData.valid_until" type="datetime-local" class="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
              </div>
            </div>
          </div>
          <!-- Section: Settings -->
          <div class="border-b border-slate-200 dark:border-slate-700">
            <button @click="toggleSection('settings')" class="w-full flex items-center justify-between px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">Settings</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="openSection==='settings'?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div v-show="openSection==='settings'" class="px-5 pb-4 space-y-3">
              <label class="flex items-center gap-2 cursor-pointer"><input v-model="formData.is_active" type="checkbox" class="w-4 h-4 rounded text-blue-600" /><span class="text-xs text-slate-700 dark:text-slate-300">Active</span></label>
              <label class="flex items-center gap-2 cursor-pointer"><input v-model="formData.is_reward" type="checkbox" class="w-4 h-4 rounded text-blue-600" /><span class="text-xs text-slate-700 dark:text-slate-300">Reward Coupon</span></label>
            </div>
          </div>
        </div>
        <!-- Footer -->
        <div class="flex items-center justify-end gap-2 px-5 py-4 border-t border-slate-200 dark:border-slate-700 shrink-0">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg">Cancel</button>
          <button @click="saveCoupon" :disabled="saveLoading" class="px-4 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg disabled:opacity-50">{{ saveLoading ? 'Saving...' : (selectedCoupon?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>

    <ConfirmDialog :show="showDeleteModal" title="Delete Coupon" :message="`Delete coupon ${couponToDelete?.code}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useOptimistic } from '../composables/useOptimistic'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Coupons',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest, invalidateCache } = useApi()
    const coupons = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const selectedCoupon = ref(null)
    const couponToDelete = ref(null)
    const saveLoading = ref(false)
    const selectedIds = ref([])
    const openSection = ref('core')
    const formData = ref({ code: '', name: '', coupon_type: 'percentage', discount_value: 0, max_uses: 100, max_uses_per_user: 1, valid_from: '', valid_until: '', is_active: true, is_reward: false, description: '' })

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
    const { optimisticRemove, optimisticUpdate } = useOptimistic(coupons, fetchCoupons, invalidateCache, 'suapi/coupons')
    const toggleSection = (s) => { openSection.value = openSection.value === s ? '' : s }
    const toggleSelectAll = (e) => { selectedIds.value = e.target.checked ? filteredCoupons.value.map(c => c.id) : [] }
    const formatDate = (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
    const formatDiscount = (coupon) => coupon.coupon_type === 'percentage' ? `${coupon.discount_value}%` : `KSh ${coupon.discount_value}`
    
    const openAddModal = () => {
      selectedCoupon.value = null
      openSection.value = 'core'
      formData.value = { code: '', name: '', coupon_type: 'percentage', discount_value: 0, max_uses: 100, max_uses_per_user: 1, valid_from: '', valid_until: '', is_active: true, is_reward: false, description: '' }
      showFormModal.value = true
    }
    
    const openEditModal = (coupon) => {
      selectedCoupon.value = coupon
      openSection.value = 'core'
      formData.value = { code: coupon.code || '', name: coupon.name || '', coupon_type: coupon.coupon_type || 'percentage', discount_value: coupon.discount_value || 0, max_uses: coupon.max_uses || 100, max_uses_per_user: coupon.max_uses_per_user || 1, valid_from: coupon.valid_from || '', valid_until: coupon.valid_until || '', is_active: coupon.is_active ?? true, is_reward: coupon.is_reward || false, description: coupon.description || '' }
      showFormModal.value = true
    }
    
    const closeFormModal = () => {
      showFormModal.value = false
      selectedCoupon.value = null
      formData.value = { code: '', name: '', coupon_type: 'percentage', discount_value: 0, max_uses: 100, max_uses_per_user: 1, valid_from: '', valid_until: '', is_active: true, is_reward: false, description: '' }
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
      const id = couponToDelete.value.id
      optimisticRemove(id)
      closeDeleteModal()
      try {
        await makeRequest('delete', `suapi/coupons/${id}/`)
      } catch (err) {
        await refreshData()
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    const bulkAction = async (action) => {
      if (!selectedIds.value.length) return
      if (action === 'delete' && !confirm(`Delete ${selectedIds.value.length} coupons?`)) return
      if (action === 'delete') selectedIds.value.forEach(id => optimisticRemove(id))
      else selectedIds.value.forEach(id => optimisticUpdate(id, { is_active: action === 'activate' }))
      const ids = [...selectedIds.value]
      selectedIds.value = []
      try {
        await makeRequest('post', 'suapi/coupons/bulk_action/', { action, ids })
      } catch (err) {
        await refreshData()
        console.error(err)
      }
    }

    onMounted(refreshData)

    return {
      loading, error, coupons, stats, searchTerm, statusFilter, showFormModal, showDeleteModal, selectedCoupon, couponToDelete,
      saveLoading, formData, filteredCoupons, fetchCoupons, refreshData, formatDate, formatDiscount,
      openAddModal, openEditModal, closeFormModal, saveCoupon, openDeleteModal, closeDeleteModal, confirmDelete,
      selectedIds, openSection, toggleSection, toggleSelectAll, bulkAction
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
