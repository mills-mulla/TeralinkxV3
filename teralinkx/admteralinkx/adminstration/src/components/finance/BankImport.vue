<template>
  <div class="space-y-6">
    <GuidePanel title="Bank Statement Import" :terms="[
        { label: 'CSV Import', color: 'blue', description: 'Upload bank statement CSV. Supports Equity, KCB, Co-op, and M-Pesa formats.' },
        { label: 'Auto-Reconciliation', color: 'emerald', description: 'After parsing, system automatically matches entries to payment transactions.' },
        { label: 'Confidence Score', color: 'amber', description: '85%+ = auto-matched. 60-84% = review queue. Below 60% = manual.' },
      ]" note="Paste CSV content or upload file. System detects bank format automatically." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Bank Statement Import</h2>
      <button @click="showUpload=true" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">📤 Import Statement</button>
    </div>

    <!-- Import History -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Import History</h3>
      </div>
      <div class="divide-y divide-slate-200 dark:divide-slate-700">
        <div v-for="s in statements" :key="s.id"
          class="px-4 py-3 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-700/50 cursor-pointer"
          @click="viewEntries(s.id)">
          <div>
            <p class="text-sm font-medium text-slate-900 dark:text-white">{{ s.filename }}</p>
            <p class="text-xs text-slate-500 mt-0.5">{{ s.bank_display }} · {{ s.period_start }} to {{ s.period_end }}</p>
          </div>
          <div class="text-right">
            <span class="px-2 py-1 rounded-full text-xs font-medium" :class="statusBadge(s.status)">{{ s.status }}</span>
            <p class="text-xs text-slate-400 mt-1">{{ s.parsed_entries }} entries</p>
          </div>
        </div>
        <div v-if="!statements.length" class="px-4 py-8 text-center text-slate-400 text-sm">No statements imported yet</div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUpload" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showUpload=false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-lg">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Import Bank Statement</h3>
          <button @click="showUpload=false" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Bank</label>
            <select v-model="form.bank" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm">
              <option value="equity">Equity Bank</option>
              <option value="kcb">KCB Bank</option>
              <option value="coop">Co-op Bank</option>
              <option value="mpesa">M-Pesa Statement</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">CSV Content *</label>
            <!-- Drag & Drop Zone -->
            <div class="border-2 border-dashed rounded-lg p-4 text-center mb-2 transition-colors cursor-pointer"
              :class="dragging ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-slate-300 dark:border-slate-600 hover:border-blue-400'"
              @dragover.prevent="dragging=true" @dragleave="dragging=false"
              @drop.prevent="onDrop" @click="$refs.fileInput.click()">
              <p class="text-sm text-slate-500">{{ dragging ? 'Drop file here' : '📂 Drag & drop CSV or click to browse' }}</p>
              <input ref="fileInput" type="file" accept=".csv,.txt" class="hidden" @change="onFileSelect" />
            </div>
            <textarea v-model="form.csv_content" rows="6" placeholder="Or paste CSV content here..."
              class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-xs font-mono resize-none"></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Filename</label>
            <input v-model="form.filename" type="text" placeholder="statement.csv"
              class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
          <p v-if="err" class="text-sm text-red-600">{{ err }}</p>
          <p v-if="result" class="text-sm text-emerald-600">{{ result }}</p>
        </div>
        <div class="flex justify-end gap-3 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="showUpload=false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="upload" :disabled="uploading" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm disabled:opacity-50">{{ uploading ? 'Importing...' : 'Import & Reconcile' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'BankImport',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return { statements: [], loading: false, showUpload: false, uploading: false, err: '', result: '', dragging: false,
             form: { bank: 'equity', csv_content: '', filename: 'statement.csv' } }
  },
  methods: {
    statusBadge(s) {
      return { uploaded: 'bg-slate-100 text-slate-700', parsed: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               completed: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
               failed: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' }[s] || 'bg-slate-100 text-slate-800'
    },
    onDrop(e) {
      this.dragging = false
      const file = e.dataTransfer.files[0]
      if (file) this.readFile(file)
    },
    onFileSelect(e) {
      const file = e.target.files[0]
      if (file) this.readFile(file)
    },
    readFile(file) {
      this.form.filename = file.name
      const reader = new FileReader()
      reader.onload = (e) => { this.form.csv_content = e.target.result }
      reader.readAsText(file)
    },
    async load() {
      try { const data = await this.makeRequest('get', 'api/finance/api/bank-statements/', null, false); this.statements = data.results || [] }
      catch (e) { console.error(e) }
    },
    async upload() {
      if (!this.form.csv_content.trim()) { this.err = 'CSV content required'; return }
      this.uploading = true; this.err = ''; this.result = ''
      try {
        const r = await this.makeRequest('post', 'api/finance/api/bank-statements/', this.form)
        this.result = `Imported ${r.entries_parsed} entries${r.reconciliation_job ? ` — Reconciliation job: ${r.reconciliation_job} (${r.auto_match_rate}% matched)` : ''}`
        await this.load()
      } catch (e) { this.err = e.response?.data?.error || 'Import failed' }
      finally { this.uploading = false }
    },
    viewEntries(id) { window.open(`/api/finance/api/bank-statements/${id}/`, '_blank') }
  },
  mounted() { this.load() }
}
</script>
