<template>
  <div class="space-y-6">
    <GuidePanel title="Purchase Orders" :terms="[
        { label: 'PO Workflow', color: 'blue', description: 'Draft → Submitted → Approved → Received → Invoiced → Paid.' },
        { label: '3-Way Match', color: 'emerald', description: 'PO matches Goods Receipt matches Vendor Invoice. Prevents unauthorized payments.' },
      ]" note="All purchases above KES 10,000 should have a PO before committing to the vendor." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Purchase Orders</h2>
      <div class="flex gap-3">
        <select v-model="filters.status" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="">All</option>
          <option value="submitted">Submitted</option>
          <option value="approved">Approved</option>
          <option value="received">Received</option>
          <option value="paid">Paid</option>
        </select>
        <button @click="showAdd=true" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ New PO</button>
      </div>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">PO #</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Vendor</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Department</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Amount</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Delivery</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="po in orders" :key="po.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-mono text-xs text-slate-700 dark:text-slate-300">{{ po.po_number }}</td>
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ po.vendor_name }}</td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400">{{ po.department || '—' }}</td>
              <td class="px-4 py-3 text-right font-semibold text-slate-900 dark:text-white">KES {{ fmt(po.total_amount) }}</td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400 text-xs">{{ po.expected_delivery || '—' }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-medium" :class="statusBadge(po.status)">{{ po.status_display }}</span>
              </td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button v-if="po.status === 'submitted'" @click="doAction(po.id,'approve')" class="px-2 py-1 bg-blue-600 text-white rounded text-xs">Approve</button>
                  <button v-if="po.status === 'approved'" @click="doAction(po.id,'receive')" class="px-2 py-1 bg-emerald-600 text-white rounded text-xs">Received</button>
                  <button v-if="!['paid','cancelled'].includes(po.status)" @click="doAction(po.id,'cancel')" class="px-2 py-1 bg-red-600 text-white rounded text-xs">Cancel</button>
                </div>
              </td>
            </tr>
            <tr v-if="!orders.length">
              <td colspan="7" class="px-4 py-8 text-center text-slate-400">No purchase orders</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add PO Modal -->
    <div v-if="showAdd" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showAdd=false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-lg">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">New Purchase Order</h3>
          <button @click="showAdd=false" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Vendor Name *</label>
              <input v-model="form.vendor_name" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Expected Delivery</label>
              <input v-model="form.expected_delivery" type="date" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Notes</label>
            <textarea v-model="form.notes" rows="2" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm resize-none"></textarea>
          </div>
          <!-- Line Items -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium text-slate-700 dark:text-slate-300">Line Items</label>
              <button @click="addLine" class="text-xs text-blue-600 hover:underline">+ Add Item</button>
            </div>
            <div v-for="(item, i) in form.line_items" :key="i" class="grid grid-cols-4 gap-2 mb-2">
              <input v-model="item.description" placeholder="Description" class="col-span-2 px-2 py-1.5 border border-slate-200 dark:border-slate-600 rounded bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-xs"/>
              <input v-model.number="item.quantity" type="number" placeholder="Qty" @input="calcLine(item)" class="px-2 py-1.5 border border-slate-200 dark:border-slate-600 rounded bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-xs"/>
              <input v-model.number="item.unit_price" type="number" placeholder="Price" @input="calcLine(item)" class="px-2 py-1.5 border border-slate-200 dark:border-slate-600 rounded bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-xs"/>
            </div>
            <p class="text-sm font-semibold text-slate-900 dark:text-white text-right">Total: KES {{ fmt(poTotal) }}</p>
          </div>
          <p v-if="err" class="text-sm text-red-600">{{ err }}</p>
        </div>
        <div class="flex justify-end gap-3 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="showAdd=false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="save" :disabled="saving" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm disabled:opacity-50">{{ saving ? 'Saving...' : 'Submit PO' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'PurchaseOrders',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return { orders: [], loading: false, filters: { status: '' }, showAdd: false, saving: false, err: '',
             form: { vendor_name: '', expected_delivery: '', notes: '', line_items: [{ description: '', quantity: 1, unit_price: 0, total: 0 }] } }
  },
  computed: {
    poTotal() { return this.form.line_items.reduce((s, i) => s + (i.total || 0), 0) }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    calcLine(item) { item.total = (item.quantity || 0) * (item.unit_price || 0) },
    addLine() { this.form.line_items.push({ description: '', quantity: 1, unit_price: 0, total: 0 }) },
    statusBadge(s) {
      return { draft: 'bg-slate-100 text-slate-700', submitted: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               approved: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
               received: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
               paid: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
               cancelled: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' }[s] || 'bg-slate-100 text-slate-800'
    },
    async load() {
      try {
        const url = this.filters.status ? `api/finance/api/purchase-orders/?status=${this.filters.status}` : 'api/finance/api/purchase-orders/'
        const data = await this.makeRequest('get', url, null, false)
        this.orders = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    },
    async doAction(id, act) {
      try { await this.makeRequest('patch', `api/finance/api/purchase-orders/${id}/`, { action: act }); await this.load() }
      catch (e) { console.error(e) }
    },
    async save() {
      if (!this.form.vendor_name) { this.err = 'Vendor name required'; return }
      this.saving = true; this.err = ''
      try { await this.makeRequest('post', 'api/finance/api/purchase-orders/', this.form); this.showAdd = false; await this.load() }
      catch (e) { this.err = e.response?.data?.error || 'Failed' }
      finally { this.saving = false }
    }
  },
  mounted() { this.load() }
}
</script>
