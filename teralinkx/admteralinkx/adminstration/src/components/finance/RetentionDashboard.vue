<template>
  <div class="space-y-6">
    <GuidePanel title="Retention Tasks" :terms="[
        { label: 'Priority Score', color: 'red', description: 'Urgency of the retention task. Higher = act sooner.', formula: '(MRR / 10,000 × 0.6) + (Churn Score × 0.4)' },
        { label: '20% Auto Discount', color: 'purple', description: 'Applied automatically for high-value customers (MRR > KES 5,000).' },
        { label: '10% SMS Offer', color: 'blue', description: 'Discount offer sent via SMS for medium-value customers (MRR KES 2,000–5,000).' },
        { label: 'Re-engagement SMS', color: 'amber', description: 'Re-engagement message sent for low-value customers.' },
        { label: 'Retained', color: 'emerald', description: 'Customer made a payment within 14 days of the offer.' },
        { label: 'Relocated', color: 'indigo', description: 'Customer moved outside coverage area — not actionable, excluded from churn stats.' }
      ]" note="Tasks are auto-created for high and critical risk customers. Refresh every 30 seconds." />

    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Retention Tasks</h2>
      <div class="flex items-center gap-3">
        <select v-model="filters.status" @change="loadTasks"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
        <select v-model="filters.sort" @change="sortTasks"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="priority">Sort by Priority</option>
          <option value="revenue">Sort by Revenue</option>
        </select>
        <button @click="loadTasks"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
          Refresh
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-3 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">Pending Tasks</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ stats.pending }}</p>
        <p class="text-xs text-slate-500 mt-1">awaiting action</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">Revenue at Risk</p>
        <p class="text-2xl font-bold text-red-600 dark:text-red-400 mt-1">KES {{ fmt(stats.total_revenue_at_risk) }}</p>
        <p class="text-xs text-slate-500 mt-1">across all tasks</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">Retention Rate</p>
        <p class="text-3xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{{ stats.retained }}%</p>
        <p class="text-xs text-slate-500 mt-1">of completed tasks</p>
      </div>
    </div>

    <!-- Tasks Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Tasks</h3>
        <span class="text-xs text-slate-500">{{ tasks.length }} tasks</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Priority</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Customer</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Action</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">MRR</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">At Risk</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Outcome</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="task in tasks" :key="task.id"
              class="hover:bg-slate-50 dark:hover:bg-slate-700/50"
              :class="priorityRow(task.priority_score)">
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-bold" :class="priorityBadge(task.priority_score)">
                  {{ task.priority_score?.toFixed(2) }}
                </span>
              </td>
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">
                {{ task.customer?.account || task.customer?.id }}
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded text-xs font-medium">
                  {{ formatAction(task.action_type) }}
                </span>
              </td>
              <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-300">
                KES {{ fmt(task.monthly_recurring_revenue) }}
              </td>
              <td class="px-4 py-3 text-right font-semibold text-red-600 dark:text-red-400">
                KES {{ fmt(task.revenue_at_risk) }}
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded text-xs font-semibold" :class="statusBadge(task.status)">
                  {{ task.status }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span v-if="task.outcome !== 'pending'" class="px-2 py-1 rounded text-xs font-semibold" :class="outcomeBadge(task.outcome)">
                  {{ task.outcome }}
                </span>
                <span v-else class="text-slate-400 text-xs">—</span>
              </td>
            </tr>
            <tr v-if="!tasks.length">
              <td colspan="7" class="px-4 py-8 text-center text-slate-400 text-sm">No tasks found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import GuidePanel from './GuidePanel.vue'
import { useApi } from '../../composables/useApi'

export default {
  name: 'RetentionDashboard',
  components: { GuidePanel },
  setup() {
    const { makeRequest } = useApi()
    const tasks = ref([])
    const filters = ref({ status: 'pending', sort: 'priority' })
    const stats = ref({ pending: 0, total_revenue_at_risk: 0, retained: 0 })
    let timer = null

    const fmt = (n) => new Intl.NumberFormat('en-KE').format(Math.round(n || 0))

    const priorityBadge = (score) => {
      if (score >= 0.7) return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
      if (score >= 0.5) return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400'
      if (score >= 0.3) return 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
    }

    const priorityRow = (score) => {
      if (score >= 0.7) return 'border-l-2 border-red-500'
      if (score >= 0.5) return 'border-l-2 border-orange-500'
      return ''
    }

    const statusBadge = (s) => ({
      pending:     'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
      in_progress: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
      completed:   'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
      failed:      'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    }[s] || 'bg-slate-100 text-slate-800')

    const outcomeBadge = (o) => ({
      retained:  'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
      churned:   'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
      relocated: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400',
    }[o] || 'bg-slate-100 text-slate-800')

    const formatAction = (type) => ({
      auto_discount_20: '20% Discount',
      sms_discount_10:  '10% SMS',
      sms_reengagement: 'Re-engage SMS',
      manual_outreach:  'Manual',
    }[type] || type)

    const sortTasks = () => {
      if (filters.value.sort === 'priority') {
        tasks.value.sort((a, b) => b.priority_score - a.priority_score)
      } else {
        tasks.value.sort((a, b) => b.revenue_at_risk - a.revenue_at_risk)
      }
    }

    const loadTasks = async () => {
      try {
        const data = await makeRequest('get', `api/finance/api/retention-tasks/?status=${filters.value.status}`)
        tasks.value = Array.isArray(data) ? data : (data.results || [])
        sortTasks()
        stats.value.pending = tasks.value.filter(t => t.status === 'pending').length
        stats.value.total_revenue_at_risk = tasks.value.reduce((sum, t) => sum + parseFloat(t.revenue_at_risk || 0), 0)
        const completed = tasks.value.filter(t => t.outcome !== 'pending')
        const retained = completed.filter(t => t.outcome === 'retained').length
        stats.value.retained = completed.length > 0 ? ((retained / completed.length) * 100).toFixed(1) : 0
      } catch (e) { console.error('Failed to load tasks:', e) }
    }

    onMounted(() => {
      loadTasks()
      timer = setInterval(loadTasks, 30000)
    })

    onUnmounted(() => { clearInterval(timer) })

    return { tasks, filters, stats, fmt, priorityBadge, priorityRow, statusBadge, outcomeBadge, formatAction, loadTasks, sortTasks }
  }
}
</script>
