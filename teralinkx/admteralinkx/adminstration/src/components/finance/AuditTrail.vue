<template>
  <div class="space-y-6">
    <GuidePanel title="Audit Trail" :terms="[
        { label: 'Immutable Log', color: 'blue', description: 'Every financial record change is permanently logged. Cannot be deleted or modified.' },
        { label: 'KRA Compliance', color: 'amber', description: 'Audit trail satisfies KRA requirement to track all financial record changes.' },
      ]" note="Filter by model, user, or action. Export CSV for KRA audit submissions." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Audit Trail</h2>
      <div class="flex gap-3">
        <select v-model="filters.model" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="">All Models</option>
          <option value="Invoice">Invoice</option>
          <option value="Expense">Expense</option>
          <option value="PayrollRun">Payroll</option>
          <option value="VATReturn">VAT Return</option>
          <option value="PurchaseOrder">Purchase Order</option>
          <option value="FinancialYear">Financial Year</option>
        </select>
        <select v-model="filters.action" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="">All Actions</option>
          <option value="create">Create</option>
          <option value="update">Update</option>
          <option value="approve">Approve</option>
          <option value="file">File</option>
          <option value="pay">Pay</option>
        </select>
        <button @click="load" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm hover:bg-slate-300">Refresh</button>
      </div>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">When</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Model</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Record</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Action</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">By</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Description</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="log in logs" :key="log.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 text-xs text-slate-500">{{ fmtDate(log.changed_at) }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded text-xs">{{ log.model_name }}</span>
              </td>
              <td class="px-4 py-3 font-mono text-xs text-slate-600 dark:text-slate-400">#{{ log.record_id }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded text-xs font-medium" :class="actionBadge(log.action)">{{ log.action_display }}</span>
              </td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400 text-xs">{{ log.changed_by }}</td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400 text-xs">{{ log.description || '—' }}</td>
            </tr>
            <tr v-if="!logs.length">
              <td colspan="6" class="px-4 py-8 text-center text-slate-400">No audit logs found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'AuditTrail',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() { return { logs: [], loading: false, filters: { model: '', action: '' } } },
  methods: {
    fmtDate(d) { return d ? new Date(d).toLocaleString('en-KE', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—' },
    actionBadge(a) {
      return { create: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
               update: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               approve: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
               delete: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
               file: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
               pay: 'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-400' }[a] || 'bg-slate-100 text-slate-800'
    },
    async load() {
      try {
        let url = 'api/finance/api/audit-log/?'
        if (this.filters.model) url += `model=${this.filters.model}&`
        if (this.filters.action) url += `action=${this.filters.action}&`
        const data = await this.makeRequest('get', url, null, false)
        this.logs = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    }
  },
  mounted() { this.load() }
}
</script>
