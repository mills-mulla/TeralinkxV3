<template>
  <div class="space-y-6">
    <GuidePanel title="Multi-Branch Management" :terms="[
      { label: 'Branch', color: 'blue', description: 'A physical or logical business unit. Each branch tracks its own revenue, expenses, and headcount.' },
      { label: 'Cost Centre', color: 'purple', description: 'Accounting code used to allocate costs to a specific branch for P&L reporting.' },
    ]" note="Manage all company branches. Each branch has its own cost centre for financial reporting." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Branches</h2>
      <button @click="showForm = !showForm" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ Add Branch</button>
    </div>

    <div v-if="showForm" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 space-y-3">
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-xs text-slate-500">Branch Name</label>
          <input v-model="form.name" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" />
        </div>
        <div>
          <label class="text-xs text-slate-500">Code</label>
          <input v-model="form.code" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" />
        </div>
        <div>
          <label class="text-xs text-slate-500">Location</label>
          <input v-model="form.location" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" />
        </div>
        <div>
          <label class="text-xs text-slate-500">Manager</label>
          <input v-model="form.manager_name" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" />
        </div>
      </div>
      <button @click="save" class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">Save Branch</button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="b in branches" :key="b.id" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="font-semibold text-slate-900 dark:text-white">{{ b.name }}</h3>
            <p class="text-xs text-slate-500">{{ b.code }} · {{ b.location }}</p>
          </div>
          <span class="px-2 py-1 rounded text-xs font-medium" :class="b.is_active ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-slate-100 text-slate-600'">
            {{ b.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>
        <div class="space-y-1 text-sm">
          <div class="flex justify-between"><span class="text-slate-500">Manager</span><span class="text-slate-700 dark:text-slate-300">{{ b.manager_name || '—' }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Revenue</span><span class="font-medium text-emerald-600">KES {{ fmt(b.total_revenue) }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Expenses</span><span class="font-medium text-red-500">KES {{ fmt(b.total_expenses) }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Headcount</span><span class="text-slate-700 dark:text-slate-300">{{ b.headcount || 0 }}</span></div>
        </div>
      </div>
      <div v-if="!branches.length" class="col-span-3 text-center py-12 text-slate-400">No branches found</div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'MultiBranch',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return {
      branches: [], showForm: false,
      form: { name: '', code: '', location: '', manager_name: '' }
    }
  },
  methods: {
    fmt(v) { return Number(v || 0).toLocaleString('en-KE', { minimumFractionDigits: 2 }) },
    async load() {
      try {
        const data = await this.makeRequest('get', 'api/finance/api/branches/', null, false)
        this.branches = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    },
    async save() {
      try {
        await this.makeRequest('post', 'api/finance/api/branches/', this.form, false)
        this.showForm = false
        this.form = { name: '', code: '', location: '', manager_name: '' }
        this.load()
      } catch (e) { console.error(e) }
    }
  },
  mounted() { this.load() }
}
</script>
