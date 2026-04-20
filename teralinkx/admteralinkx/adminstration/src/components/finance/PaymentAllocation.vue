<template>
  <div class="space-y-6">
    <GuidePanel title="Payment Allocation" :terms="[
      { label: 'Allocation', color: 'blue', description: 'Maps a payment to specific invoices. Prevents double-counting and ensures accurate AR aging.' },
      { label: 'Unallocated', color: 'amber', description: 'Payments received but not yet matched to an invoice. Must be resolved for accurate books.' },
    ]" note="Allocate customer payments to open invoices. Partial allocations are supported." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Payment Allocation</h2>
      <button @click="load" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm hover:bg-slate-300">Refresh</button>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Payment Ref</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Customer</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Invoice</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Amount (KES)</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Date</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="a in allocations" :key="a.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-mono text-xs text-slate-600 dark:text-slate-400">{{ a.payment_reference }}</td>
              <td class="px-4 py-3 text-slate-700 dark:text-slate-300">{{ a.customer_name }}</td>
              <td class="px-4 py-3 font-mono text-xs text-slate-600 dark:text-slate-400">{{ a.invoice_number || '—' }}</td>
              <td class="px-4 py-3 text-right font-medium text-slate-900 dark:text-white">{{ fmt(a.allocated_amount) }}</td>
              <td class="px-4 py-3 text-xs text-slate-500">{{ fmtDate(a.allocated_at) }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded text-xs font-medium" :class="a.is_fully_allocated ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'">
                  {{ a.is_fully_allocated ? 'Allocated' : 'Partial' }}
                </span>
              </td>
            </tr>
            <tr v-if="!allocations.length">
              <td colspan="6" class="px-4 py-8 text-center text-slate-400">No allocations found</td>
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
  name: 'PaymentAllocation',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() { return { allocations: [] } },
  methods: {
    fmt(v) { return Number(v || 0).toLocaleString('en-KE', { minimumFractionDigits: 2 }) },
    fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' }) : '—' },
    async load() {
      try {
        const data = await this.makeRequest('get', 'api/finance/api/payment-allocation/', null, false)
        this.allocations = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    }
  },
  mounted() { this.load() }
}
</script>
