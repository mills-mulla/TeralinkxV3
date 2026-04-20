<template>
  <div class="space-y-6">
    <GuidePanel title="Asset Register" :terms="[
        { label: 'Straight-Line Depreciation', color: 'blue', description: 'Equal depreciation each month over useful life.', formula: '(Cost − Salvage) ÷ (Years × 12)' },
        { label: 'Reducing Balance', color: 'amber', description: '20% per year on current book value. Higher depreciation early on.' },
        { label: 'Book Value', color: 'emerald', description: 'Current value after accumulated depreciation. Purchase cost minus total depreciation to date.' },
        { label: 'Disposal Gain/Loss', color: 'purple', description: 'Difference between disposal proceeds and book value at time of disposal.' },
      ]" note="Depreciation is posted automatically on 1st of each month as an expense. Book values update automatically." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Asset Register</h2>
      <div class="flex gap-3">
        <select v-model="filters.category" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="">All Categories</option>
          <option value="network_equipment">Network Equipment</option>
          <option value="computers">Computers & IT</option>
          <option value="vehicles">Vehicles</option>
          <option value="furniture">Furniture</option>
          <option value="other">Other</option>
        </select>
        <button @click="showAdd=true" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ Add Asset</button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4" v-if="summary">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Total Assets</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">{{ summary.total_assets }}</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Purchase Cost</p>
        <p class="text-xl font-bold text-blue-600 dark:text-blue-400 mt-1">KES {{ fmt(summary.total_purchase_cost) }}</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Book Value</p>
        <p class="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">KES {{ fmt(summary.total_book_value) }}</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Monthly Depreciation</p>
        <p class="text-xl font-bold text-amber-600 dark:text-amber-400 mt-1">KES {{ fmt(summary.monthly_depreciation_expense) }}</p>
      </div>
    </div>

    <!-- Assets Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Asset</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Category</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Cost</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Book Value</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Monthly Dep.</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Remaining</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="a in assets" :key="a.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3">
                <p class="font-medium text-slate-900 dark:text-white">{{ a.name }}</p>
                <p class="text-xs text-slate-400">{{ a.asset_number }}</p>
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded text-xs bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300">{{ a.category_display }}</span>
              </td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">KES {{ fmt(a.purchase_cost) }}</td>
              <td class="px-4 py-3 text-right font-semibold text-emerald-600 dark:text-emerald-400">KES {{ fmt(a.current_book_value) }}</td>
              <td class="px-4 py-3 text-right text-amber-600 dark:text-amber-400">KES {{ fmt(a.monthly_depreciation) }}</td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400 text-xs">{{ a.remaining_life_months }} months</td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button @click="viewSchedule(a)" class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded text-xs hover:bg-blue-200">Schedule</button>
                  <button @click="dispose(a)" class="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded text-xs hover:bg-red-200">Dispose</button>
                </div>
              </td>
            </tr>
            <tr v-if="!assets.length">
              <td colspan="7" class="px-4 py-8 text-center text-slate-400">No assets registered</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Asset Modal -->
    <div v-if="showAdd" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showAdd=false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-lg">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Add Asset</h3>
          <button @click="showAdd=false" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Asset Name *</label>
            <input v-model="form.name" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Category</label>
              <select v-model="form.category" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm">
                <option value="network_equipment">Network Equipment</option>
                <option value="computers">Computers & IT</option>
                <option value="vehicles">Vehicles</option>
                <option value="furniture">Furniture</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Depreciation Method</label>
              <select v-model="form.depreciation_method" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm">
                <option value="straight_line">Straight Line</option>
                <option value="reducing_balance">Reducing Balance</option>
                <option value="none">None (Land)</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Purchase Cost (KES) *</label>
              <input v-model="form.purchase_cost" type="number" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Purchase Date *</label>
              <input v-model="form.purchase_date" type="date" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Useful Life (Years)</label>
              <input v-model="form.useful_life_years" type="number" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Salvage Value (KES)</label>
              <input v-model="form.salvage_value" type="number" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <p v-if="err" class="text-sm text-red-600">{{ err }}</p>
        </div>
        <div class="flex justify-end gap-3 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="showAdd=false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="save" :disabled="saving" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm disabled:opacity-50">{{ saving ? 'Saving...' : 'Add Asset' }}</button>
        </div>
      </div>
    </div>

    <!-- Depreciation Schedule Modal -->
    <div v-if="scheduleAsset" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="scheduleAsset=null">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <div>
            <h3 class="text-lg font-semibold text-slate-900 dark:text-white">{{ scheduleAsset.name }}</h3>
            <p class="text-xs text-slate-500">{{ scheduleAsset.asset_number }} · {{ scheduleAsset.depreciation_method_display }} · {{ scheduleAsset.useful_life_years }}yr life</p>
          </div>
          <button @click="scheduleAsset=null" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="grid grid-cols-3 gap-4 p-4 border-b border-slate-200 dark:border-slate-700">
          <div class="text-center"><p class="text-xs text-slate-500">Purchase Cost</p><p class="font-bold text-slate-900 dark:text-white">KES {{ fmt(scheduleAsset.purchase_cost) }}</p></div>
          <div class="text-center"><p class="text-xs text-slate-500">Book Value</p><p class="font-bold text-emerald-600">KES {{ fmt(scheduleAsset.current_book_value) }}</p></div>
          <div class="text-center"><p class="text-xs text-slate-500">Monthly Dep.</p><p class="font-bold text-amber-600">KES {{ fmt(scheduleAsset.monthly_depreciation) }}</p></div>
        </div>
        <div class="overflow-y-auto flex-1">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 dark:bg-slate-900 sticky top-0">
              <tr>
                <th class="px-4 py-2 text-left text-xs font-medium text-slate-500 uppercase">Month</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-slate-500 uppercase">Depreciation</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-slate-500 uppercase">Accumulated</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-slate-500 uppercase">Book Value</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="row in depSchedule" :key="row.month" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
                <td class="px-4 py-2 text-slate-600 dark:text-slate-400">{{ row.month }}</td>
                <td class="px-4 py-2 text-right text-amber-600">{{ fmt(row.depreciation) }}</td>
                <td class="px-4 py-2 text-right text-slate-600 dark:text-slate-400">{{ fmt(row.accumulated) }}</td>
                <td class="px-4 py-2 text-right font-medium text-emerald-600">{{ fmt(row.book_value) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'AssetRegister',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return {
      assets: [], summary: null, loading: false, filters: { category: '' },
      showAdd: false, saving: false, err: '',
      scheduleAsset: null, depSchedule: [],
      form: { name: '', category: 'network_equipment', depreciation_method: 'straight_line', purchase_cost: '', purchase_date: new Date().toISOString().split('T')[0], useful_life_years: 5, salvage_value: 0 }
    }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    viewSchedule(asset) {
      this.scheduleAsset = asset
      // Generate schedule client-side from asset data (no extra API call needed)
      const months = (asset.useful_life_years || 5) * 12
      const cost = parseFloat(asset.purchase_cost || 0)
      const salvage = parseFloat(asset.salvage_value || 0)
      const method = asset.depreciation_method
      const startDate = new Date(asset.purchase_date || Date.now())
      let bookValue = cost
      let accumulated = 0
      this.depSchedule = []
      for (let i = 1; i <= months; i++) {
        const d = new Date(startDate)
        d.setMonth(d.getMonth() + i)
        let dep
        if (method === 'straight_line') {
          dep = (cost - salvage) / months
        } else {
          dep = bookValue * 0.20 / 12
        }
        dep = Math.max(0, Math.min(dep, bookValue - salvage))
        accumulated += dep
        bookValue -= dep
        this.depSchedule.push({
          month: d.toLocaleDateString('en-KE', { month: 'short', year: 'numeric' }),
          depreciation: dep,
          accumulated,
          book_value: bookValue
        })
        if (bookValue <= salvage) break
      }
    },
    async load() {
      try {
        const url = this.filters.category ? `api/finance/api/assets/?category=${this.filters.category}` : 'api/finance/api/assets/'
        const data = await this.makeRequest('get', url, null, false)
        this.summary = data.summary
        this.assets = data.assets || []
      } catch (e) { console.error(e) }
    },
    async save() {
      if (!this.form.name || !this.form.purchase_cost) { this.err = 'Name and cost required'; return }
      this.saving = true; this.err = ''
      try { await this.makeRequest('post', 'api/finance/api/assets/', this.form); this.showAdd = false; await this.load() }
      catch (e) { this.err = e.response?.data?.error || 'Failed' }
      finally { this.saving = false }
    },
    async dispose(asset) {
      const val = prompt(`Disposal value for ${asset.name} (current book value: KES ${this.fmt(asset.current_book_value)}):`)
      if (!val) return
      const date = prompt('Disposal date (YYYY-MM-DD):', new Date().toISOString().split('T')[0])
      if (!date) return
      try {
        const r = await this.makeRequest('patch', `api/finance/api/assets/${asset.id}/`, { action: 'dispose', disposal_date: date, disposal_value: parseFloat(val) })
        alert(`Asset disposed. Gain/Loss: KES ${this.fmt(r.gain_loss)}`)
        await this.load()
      } catch (e) { console.error(e) }
    }
  },
  mounted() { this.load() }
}
</script>
