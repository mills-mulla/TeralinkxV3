<template>
  <div class="space-y-6">
    <GuidePanel title="Payroll Management" :terms="[
        { label: 'PAYE', color: 'blue', description: 'Pay As You Earn — income tax deducted from employee salary. Filed by 9th of following month.', formula: 'Kenya 2024 bands: 10%/25%/30%/32.5%/35% minus KES 2,400 relief' },
        { label: 'NHIF', color: 'emerald', description: 'National Hospital Insurance Fund. Income-based bands KES 150–1,700/month.' },
        { label: 'NSSF', color: 'amber', description: 'National Social Security Fund. 6% employee + 6% employer, capped at KES 2,160 each.' },
        { label: 'Net Pay', color: 'purple', description: 'Gross salary minus PAYE, NHIF, NSSF, and other deductions.' },
      ]" note="Payroll runs automatically on 25th of each month. All statutory deductions are calculated per Kenya 2024 regulations." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Payroll</h2>
      <div class="flex border border-slate-200 dark:border-slate-600 rounded-lg overflow-hidden">
        <button v-for="t in tabs" :key="t.id" @click="activeTab=t.id"
          class="px-4 py-2 text-sm font-medium transition-colors"
          :class="activeTab===t.id ? 'bg-blue-600 text-white' : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50'">
          {{ t.name }}
        </button>
      </div>
    </div>

    <!-- Employees Tab -->
    <div v-if="activeTab==='employees'">
      <div class="flex justify-end mb-4">
        <button @click="showAddEmp=true" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ Add Employee</button>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 dark:bg-slate-900">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Employee</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Title</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Department</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Gross Salary</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Est. Net</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="e in employees" :key="e.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
                <td class="px-4 py-3">
                  <p class="font-medium text-slate-900 dark:text-white">{{ e.full_name }}</p>
                  <p class="text-xs text-slate-400">{{ e.employee_number }}</p>
                </td>
                <td class="px-4 py-3 text-slate-600 dark:text-slate-400">{{ e.job_title }}</td>
                <td class="px-4 py-3 text-slate-600 dark:text-slate-400">{{ e.department || '—' }}</td>
                <td class="px-4 py-3 text-right font-semibold text-slate-900 dark:text-white">KES {{ fmt(e.gross_salary) }}</td>
                <td class="px-4 py-3 text-right text-emerald-600 dark:text-emerald-400">KES {{ fmt(e.payslip_preview && e.payslip_preview.net_pay) }}</td>
                <td class="px-4 py-3 text-center">
                  <button @click="deactivate(e.id)" class="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded text-xs hover:bg-red-200">Remove</button>
                </td>
              </tr>
              <tr v-if="!employees.length">
                <td colspan="6" class="px-4 py-8 text-center text-slate-400">No employees — add your first employee</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Payroll Runs Tab -->
    <div v-if="activeTab==='runs'">
      <div class="flex justify-end mb-4">
        <button @click="runPayroll" :disabled="running" class="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 disabled:opacity-50">
          {{ running ? 'Processing...' : 'Run Payroll (This Month)' }}
        </button>
      </div>
      <div class="space-y-3">
        <div v-for="run in runs" :key="run.id"
          class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 cursor-pointer hover:border-blue-300"
          @click="selectedRun = selectedRun?.id === run.id ? null : run">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-semibold text-slate-900 dark:text-white">{{ run.period_label }}</p>
              <p class="text-xs text-slate-500 mt-0.5">{{ run.employee_count }} employees</p>
            </div>
            <div class="text-right">
              <p class="font-bold text-slate-900 dark:text-white">KES {{ fmt(run.total_net) }} net</p>
              <p class="text-xs text-slate-500">KES {{ fmt(run.total_gross) }} gross</p>
            </div>
            <div class="flex items-center gap-2">
              <span class="px-2 py-1 rounded-full text-xs font-medium" :class="runStatusBadge(run.status)">{{ run.status_display }}</span>
              <button v-if="run.status==='processed'" @click.stop="approveRun(run.id)" class="px-3 py-1 bg-emerald-600 text-white rounded text-xs">Approve</button>
              <button v-if="run.status==='approved'" @click.stop="markRunPaid(run.id)" class="px-3 py-1 bg-blue-600 text-white rounded text-xs">Mark Paid</button>
            </div>
          </div>
          <!-- Payslip breakdown -->
          <div v-if="selectedRun && selectedRun.id === run.id && run.payslips" class="mt-4 border-t border-slate-200 dark:border-slate-700 pt-4">
            <div class="grid grid-cols-4 gap-2 text-xs text-slate-500 font-medium mb-2 px-2">
              <span>Employee</span><span class="text-right">Gross</span><span class="text-right">Deductions</span><span class="text-right">Net Pay</span>
            </div>
            <div v-for="p in run.payslips" :key="p.employee_number" class="grid grid-cols-4 gap-2 text-sm px-2 py-1 hover:bg-slate-50 dark:hover:bg-slate-700/50 rounded">
              <span class="text-slate-900 dark:text-white">{{ p.employee }}</span>
              <span class="text-right text-slate-600 dark:text-slate-400">{{ fmt(p.gross) }}</span>
              <span class="text-right text-red-600">{{ fmt(p.total_deductions) }}</span>
              <span class="text-right font-semibold text-emerald-600">{{ fmt(p.net_pay) }}</span>
            </div>
          </div>
        </div>
        <div v-if="!runs.length" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-8 text-center text-slate-400">
          No payroll runs yet
        </div>
      </div>
    </div>

    <!-- Calculator Tab -->
    <div v-if="activeTab==='calculator'">
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 max-w-lg">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-4">Salary Calculator</h3>
        <div class="mb-4">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Gross Monthly Salary (KES)</label>
          <input v-model="calcSalary" type="number" @input="calculate" placeholder="e.g. 50000"
            class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white"/>
        </div>
        <div v-if="calcResult" class="space-y-2">
          <div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-700">
            <span class="text-sm text-slate-600 dark:text-slate-400">Gross Salary</span>
            <span class="font-semibold text-slate-900 dark:text-white">KES {{ fmt(calcResult.gross_salary) }}</span>
          </div>
          <div class="flex justify-between py-1 text-sm">
            <span class="text-slate-500">PAYE</span>
            <span class="text-red-600">- KES {{ fmt(calcResult.paye) }}</span>
          </div>
          <div class="flex justify-between py-1 text-sm">
            <span class="text-slate-500">NHIF</span>
            <span class="text-red-600">- KES {{ fmt(calcResult.nhif) }}</span>
          </div>
          <div class="flex justify-between py-1 text-sm">
            <span class="text-slate-500">NSSF (Employee)</span>
            <span class="text-red-600">- KES {{ fmt(calcResult.nssf_employee) }}</span>
          </div>
          <div class="flex justify-between py-2 border-t border-slate-200 dark:border-slate-700 font-bold">
            <span class="text-slate-900 dark:text-white">Net Pay</span>
            <span class="text-emerald-600 text-lg">KES {{ fmt(calcResult.net_pay) }}</span>
          </div>
          <div class="flex justify-between py-1 text-xs text-slate-400">
            <span>Employer Total Cost (incl. NSSF employer)</span>
            <span>KES {{ fmt(calcResult.employer_total_cost) }}</span>
          </div>
          <div class="flex justify-between py-1 text-xs text-slate-400">
            <span>Effective Tax Rate</span>
            <span>{{ calcResult.effective_tax_rate }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Employee Modal -->
    <div v-if="showAddEmp" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showAddEmp=false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-2xl max-h-screen overflow-y-auto">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700 sticky top-0 bg-white dark:bg-slate-800">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Add Employee</h3>
          <button @click="showAddEmp=false" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">First Name *</label>
              <input v-model="empForm.first_name" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Last Name *</label>
              <input v-model="empForm.last_name" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">ID Number *</label>
              <input v-model="empForm.id_number" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">KRA PIN</label>
              <input v-model="empForm.kra_pin" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">NHIF Number</label>
              <input v-model="empForm.nhif_number" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">NSSF Number</label>
              <input v-model="empForm.nssf_number" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Job Title *</label>
              <input v-model="empForm.job_title" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Gross Salary (KES) *</label>
              <input v-model="empForm.gross_salary" type="number" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Bank Name</label>
              <input v-model="empForm.bank_name" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Bank Account</label>
              <input v-model="empForm.bank_account" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Start Date *</label>
            <input v-model="empForm.start_date" type="date" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
          <p v-if="empErr" class="text-sm text-red-600">{{ empErr }}</p>
        </div>
        <div class="flex justify-end gap-3 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="showAddEmp=false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="addEmployee" :disabled="savingEmp" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm disabled:opacity-50">{{ savingEmp ? 'Saving...' : 'Add Employee' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'Payroll',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return {
      activeTab: 'employees',
      tabs: [{ id: 'employees', name: '👥 Employees' }, { id: 'runs', name: '💰 Payroll Runs' }, { id: 'calculator', name: '🧮 Calculator' }],
      employees: [], runs: [], selectedRun: null,
      running: false, loading: false,
      calcSalary: '', calcResult: null,
      showAddEmp: false, savingEmp: false, empErr: '',
      empForm: { first_name: '', last_name: '', id_number: '', kra_pin: '', nhif_number: '', nssf_number: '', job_title: '', gross_salary: '', bank_name: '', bank_account: '', start_date: new Date().toISOString().split('T')[0] }
    }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    runStatusBadge(s) {
      return { draft: 'bg-slate-100 text-slate-700', processed: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               approved: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
               paid: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' }[s] || 'bg-slate-100 text-slate-800'
    },
    async loadEmployees() {
      try {
        const data = await this.makeRequest('get', 'api/finance/api/employees/', null, false)
        this.employees = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    },
    async loadRuns() {
      try {
        const data = await this.makeRequest('get', 'api/finance/api/payroll/', null, false)
        this.runs = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    },
    async runPayroll() {
      this.running = true
      try {
        const now = new Date()
        await this.makeRequest('post', 'api/finance/api/payroll/', { year: now.getFullYear(), month: now.getMonth() + 1 })
        await this.loadRuns()
        this.activeTab = 'runs'
      } catch (e) { console.error(e) }
      finally { this.running = false }
    },
    async approveRun(id) {
      try { await this.makeRequest('patch', `api/finance/api/payroll/${id}/`, { action: 'approve' }); await this.loadRuns() }
      catch (e) { console.error(e) }
    },
    async markRunPaid(id) {
      try { await this.makeRequest('patch', `api/finance/api/payroll/${id}/`, { action: 'mark_paid' }); await this.loadRuns() }
      catch (e) { console.error(e) }
    },
    async calculate() {
      if (!this.calcSalary || this.calcSalary < 1) { this.calcResult = null; return }
      try {
        this.calcResult = await this.makeRequest('post', 'api/finance/api/payroll/calculator/', { gross_salary: parseFloat(this.calcSalary) })
      } catch (e) { console.error(e) }
    },
    async deactivate(id) {
      if (!confirm('Deactivate this employee?')) return
      try { await this.makeRequest('delete', `api/finance/api/employees/${id}/`); await this.loadEmployees() }
      catch (e) { console.error(e) }
    },
    async addEmployee() {
      if (!this.empForm.first_name || !this.empForm.last_name || !this.empForm.id_number || !this.empForm.gross_salary) {
        this.empErr = 'First name, last name, ID number and salary are required'; return
      }
      this.savingEmp = true; this.empErr = ''
      try {
        await this.makeRequest('post', 'api/finance/api/employees/', this.empForm)
        this.showAddEmp = false
        await this.loadEmployees()
      } catch (e) { this.empErr = e.response?.data?.error || 'Failed to add employee' }
      finally { this.savingEmp = false }
    }
  },
  mounted() { this.loadEmployees(); this.loadRuns() },
  watch: { activeTab(t) { if (t === 'runs') this.loadRuns() } }
}
</script>
