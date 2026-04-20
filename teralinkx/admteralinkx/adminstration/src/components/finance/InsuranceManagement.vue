<template>
  <div class="space-y-6">
    <GuidePanel title="Insurance Management" :terms="[
      { label: 'Premium', color: 'blue', description: 'Regular payment made to maintain insurance coverage. Recorded as a business expense.' },
      { label: 'Coverage', color: 'emerald', description: 'Maximum payout the insurer will provide in case of a claim.' },
    ]" note="Track all company insurance policies. Renewal alerts are sent 30 days before expiry." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Insurance Policies</h2>
      <button @click="showForm = !showForm" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ Add Policy</button>
    </div>

    <div v-if="showForm" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 space-y-3">
      <div class="grid grid-cols-2 gap-3">
        <div><label class="text-xs text-slate-500">Policy Name</label>
          <input v-model="form.name" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" /></div>
        <div><label class="text-xs text-slate-500">Provider</label>
          <input v-model="form.provider" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" /></div>
        <div><label class="text-xs text-slate-500">Policy Number</label>
          <input v-model="form.policy_number" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" /></div>
        <div><label class="text-xs text-slate-500">Type</label>
          <select v-model="form.policy_type" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
            <option value="property">Property</option>
            <option value="liability">Liability</option>
            <option value="vehicle">Vehicle</option>
            <option value="health">Health</option>
            <option value="cyber">Cyber</option>
          </select></div>
        <div><label class="text-xs text-slate-500">Annual Premium (KES)</label>
          <input type="number" v-model="form.annual_premium" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" /></div>
        <div><label class="text-xs text-slate-500">Coverage Amount (KES)</label>
          <input type="number" v-model="form.coverage_amount" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" /></div>
        <div><label class="text-xs text-slate-500">Start Date</label>
          <input type="date" v-model="form.start_date" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" /></div>
        <div><label class="text-xs text-slate-500">Expiry Date</label>
          <input type="date" v-model="form.expiry_date" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" /></div>
      </div>
      <button @click="save" class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">Save Policy</button>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Policy</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Provider</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Type</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Premium/yr</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Coverage</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Expires</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="p in policies" :key="p.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3"><p class="font-medium text-slate-900 dark:text-white">{{ p.name }}</p><p class="text-xs text-slate-500">{{ p.policy_number }}</p></td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400">{{ p.provider }}</td>
              <td class="px-4 py-3"><span class="px-2 py-1 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded text-xs capitalize">{{ p.policy_type }}</span></td>
              <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-300">{{ fmt(p.annual_premium) }}</td>
              <td class="px-4 py-3 text-right font-medium text-slate-900 dark:text-white">{{ fmt(p.coverage_amount) }}</td>
              <td class="px-4 py-3 text-xs text-slate-500">{{ fmtDate(p.expiry_date) }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded text-xs font-medium" :class="statusClass(p.status)">{{ p.status }}</span>
              </td>
            </tr>
            <tr v-if="!policies.length">
              <td colspan="7" class="px-4 py-8 text-center text-slate-400">No insurance policies found</td>
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
  name: 'InsuranceManagement',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return {
      policies: [], showForm: false,
      form: { name: '', provider: '', policy_number: '', policy_type: 'property', annual_premium: '', coverage_amount: '', start_date: '', expiry_date: '' }
    }
  },
  methods: {
    fmt(v) { return Number(v || 0).toLocaleString('en-KE', { minimumFractionDigits: 2 }) },
    fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' }) : '—' },
    statusClass(s) {
      return { active: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
               expired: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
               expiring_soon: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400' }[s] || 'bg-slate-100 text-slate-600'
    },
    async load() {
      try {
        const data = await this.makeRequest('get', 'api/finance/api/insurance/', null, false)
        this.policies = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    },
    async save() {
      try {
        await this.makeRequest('post', 'api/finance/api/insurance/', this.form, false)
        this.showForm = false
        this.form = { name: '', provider: '', policy_number: '', policy_type: 'property', annual_premium: '', coverage_amount: '', start_date: '', expiry_date: '' }
        this.load()
      } catch (e) { console.error(e) }
    }
  },
  mounted() { this.load() }
}
</script>
