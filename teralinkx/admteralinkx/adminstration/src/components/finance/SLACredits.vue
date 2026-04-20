<template>
  <div class="space-y-6">
    <GuidePanel title="SLA Credits" :terms="[
      { label: 'SLA Policy', color: 'blue', description: 'Defines uptime commitment (e.g. 99.9%) and credit percentage issued when breached.' },
      { label: 'Outage Event', color: 'red', description: 'Recorded downtime incident. System calculates credit owed based on duration and SLA policy.' },
    ]" note="Log outages to auto-calculate SLA credits. Credits are applied to next invoice." />

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- SLA Policies -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
        <div class="px-4 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
          <h3 class="font-semibold text-slate-900 dark:text-white">SLA Policies</h3>
          <button @click="loadPolicies" class="text-xs text-blue-600 hover:underline">Refresh</button>
        </div>
        <div class="divide-y divide-slate-200 dark:divide-slate-700">
          <div v-for="p in policies" :key="p.id" class="px-4 py-3 flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-slate-900 dark:text-white">{{ p.name }}</p>
              <p class="text-xs text-slate-500">Uptime: {{ p.uptime_commitment }}% · Credit: {{ p.credit_percentage }}%</p>
            </div>
            <span class="px-2 py-1 rounded text-xs font-medium" :class="p.is_active ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-slate-100 text-slate-600'">
              {{ p.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div v-if="!policies.length" class="px-4 py-6 text-center text-slate-400 text-sm">No policies</div>
        </div>
      </div>

      <!-- Outage Events -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
        <div class="px-4 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
          <h3 class="font-semibold text-slate-900 dark:text-white">Outage Events</h3>
          <button @click="showForm = !showForm" class="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700">+ Log Outage</button>
        </div>

        <div v-if="showForm" class="px-4 py-3 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 space-y-2">
          <select v-model="form.sla_policy" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
            <option value="">Select Policy</option>
            <option v-for="p in policies" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="text-xs text-slate-500">Start</label>
              <input type="datetime-local" v-model="form.start_time" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" />
            </div>
            <div>
              <label class="text-xs text-slate-500">End</label>
              <input type="datetime-local" v-model="form.end_time" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" />
            </div>
          </div>
          <input v-model="form.description" placeholder="Description" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" />
          <button @click="logOutage" class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">Save</button>
        </div>

        <div class="divide-y divide-slate-200 dark:divide-slate-700 max-h-64 overflow-y-auto">
          <div v-for="o in outages" :key="o.id" class="px-4 py-3">
            <div class="flex items-center justify-between">
              <p class="text-sm font-medium text-slate-900 dark:text-white">{{ o.policy_name }}</p>
              <span class="text-xs font-medium text-red-600">Credit: KES {{ fmt(o.credit_amount) }}</span>
            </div>
            <p class="text-xs text-slate-500 mt-1">{{ fmtDate(o.start_time) }} · {{ o.duration_hours }}h · {{ o.description }}</p>
          </div>
          <div v-if="!outages.length" class="px-4 py-6 text-center text-slate-400 text-sm">No outages logged</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'SLACredits',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return {
      policies: [], outages: [], showForm: false,
      form: { sla_policy: '', start_time: '', end_time: '', description: '' }
    }
  },
  methods: {
    fmt(v) { return Number(v || 0).toLocaleString('en-KE', { minimumFractionDigits: 2 }) },
    fmtDate(d) { return d ? new Date(d).toLocaleString('en-KE', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—' },
    async loadPolicies() {
      try {
        const data = await this.makeRequest('get', 'api/finance/api/sla/policies/', null, false)
        this.policies = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    },
    async loadOutages() {
      try {
        const data = await this.makeRequest('get', 'api/finance/api/sla/outages/', null, false)
        this.outages = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    },
    async logOutage() {
      try {
        await this.makeRequest('post', 'api/finance/api/sla/outages/', this.form, false)
        this.showForm = false
        this.form = { sla_policy: '', start_time: '', end_time: '', description: '' }
        this.loadOutages()
      } catch (e) { console.error(e) }
    }
  },
  mounted() { this.loadPolicies(); this.loadOutages() }
}
</script>
