<template>
  <div class="space-y-4 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Transactions</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">All transaction types</p>
      </div>
      <button @click="refreshData" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
        <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
      </button>
    </div>

    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-rose-600 dark:text-rose-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          <div>
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load transactions</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="refreshData" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up">
      <ModernMetricCard title="Total Revenue" :value="formatCurrency(stats.total_revenue)" color="emerald">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.16z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Completed" :value="stats.completed_count" color="blue">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Pending" :value="stats.pending_count" color="amber">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm4.2 14.2L11 13V7h1.5v5.2l4.5 2.7-.8 1.3z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Failed" :value="stats.failed_count" color="rose">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
      </ModernMetricCard>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden animate-slide-up" style="animation-delay: 0.1s">
      <div class="border-b border-slate-200 dark:border-slate-700">
        <div class="flex overflow-x-auto">
          <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id" class="px-4 py-2.5 text-xs font-medium whitespace-nowrap transition-colors" :class="activeTab === tab.id ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'">
            {{ tab.label }}
          </button>
        </div>
      </div>

      <div class="p-4 space-y-3">
        <div class="flex flex-wrap items-center gap-2">
          <input v-model="searchTerm" type="text" placeholder="Search transactions..." class="flex-1 min-w-[200px] px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
          
          <select v-if="activeTab === 'queue'" v-model="statusFilter" class="px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
          
          <select v-if="activeTab === 'payments'" v-model="paymentMethodFilter" class="px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
            <option value="">All Methods</option>
            <option value="mpesa">M-Pesa</option>
            <option value="mpesa+balance">M-Pesa + Balance</option>
            <option value="balance">Balance</option>
          </select>
          
          <input v-model="dateFrom" type="date" class="px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" placeholder="From" />
          <input v-model="dateTo" type="date" class="px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" placeholder="To" />
          
          <button @click="exportCSV" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-medium">
            <svg class="w-3 h-3 inline mr-1" fill="currentColor" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11zM8 15.01l1.41 1.41L11 14.84V19h2v-4.16l1.59 1.59L16 15.01 12.01 11z"/></svg>
            Export
          </button>
        </div>
        
        <!-- Pagination -->
        <div v-if="totalCount > pageSize" class="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
          <span>Showing {{ ((currentPage - 1) * pageSize) + 1 }} - {{ Math.min(currentPage * pageSize, totalCount) }} of {{ totalCount }}</span>
          <div class="flex gap-1">
            <button @click="currentPage = Math.max(1, currentPage - 1)" :disabled="currentPage === 1" class="px-2 py-1 bg-slate-100 dark:bg-slate-700 rounded disabled:opacity-50">Prev</button>
            <button @click="currentPage = Math.min(Math.ceil(totalCount / pageSize), currentPage + 1)" :disabled="currentPage >= Math.ceil(totalCount / pageSize)" class="px-2 py-1 bg-slate-100 dark:bg-slate-700 rounded disabled:opacity-50">Next</button>
          </div>
        </div>

        <div v-if="activeTab === 'payments'" class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Transaction ID</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Amount</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Method</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Date</th>
                <th v-if="canEdit" class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="txn in filteredPayments" :key="txn.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                <td class="px-3 py-2 text-xs font-mono text-slate-900 dark:text-white">{{ txn.transaction_id?.substring(0, 12) }}...</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ txn.initiator }}</td>
                <td class="px-3 py-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400">{{ formatCurrency(txn.amount) }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400">{{ txn.payment_method }}</span></td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="getStatusClass(txn.status)">{{ txn.status }}</span></td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatDate(txn.created_at) }}</td>
                <td v-if="canEdit" class="px-3 py-2">
                  <button @click="openEditPayment(txn)" class="px-2 py-1 text-[10px] font-medium rounded bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600">Edit</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="activeTab === 'balance'" class="overflow-x-auto">
          <div v-if="canEdit" class="flex justify-end mb-2">
            <button @click="openBalanceModal()" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-medium">+ Manual Adjustment</button>
          </div>
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Type</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Amount</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Balance Before</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Balance After</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Description</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="txn in filteredBalance" :key="txn.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ txn.user_account || txn.user }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400">{{ txn.transaction_type }}</span></td>
                <td class="px-3 py-2 text-xs font-semibold" :class="txn.credit > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'">{{ txn.credit > 0 ? '+' : '-' }}{{ formatCurrency(Math.abs(txn.credit || txn.debit)) }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatCurrency(txn.balance_before) }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatCurrency(txn.balance_after) }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ txn.description }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatDate(txn.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="activeTab === 'queue'">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 w-6"></th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Type</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Package</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Price</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Method</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Retries</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Date</th>
                <th v-if="canEdit" class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="txn in filteredQueue" :key="txn.id">
                <tr @click="toggleExpand(txn.id)" class="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                  <td class="px-3 py-2">
                    <svg class="w-3 h-3 text-slate-400 transition-transform" :class="expandedRow === txn.id ? 'rotate-90' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                  </td>
                  <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-indigo-100 dark:bg-indigo-500/20 text-indigo-700 dark:text-indigo-400">{{ txn.queue_type }}</span></td>
                  <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ txn.initiator }}</td>
                  <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ txn.package }}</td>
                  <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ formatCurrency(txn.price) }}</td>
                  <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ txn.method }}</td>
                  <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="getQueueStatusClass(txn.status)">{{ txn.status }}</span></td>
                  <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ txn.retry_count }}/{{ txn.max_retries }}</td>
                  <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatDate(txn.created_at) }}</td>
                  <td v-if="canEdit" class="px-3 py-2" @click.stop>
                    <div class="flex items-center gap-1">
                      <button v-if="txn.checkout_request_id" @click="queryMpesa(txn)" :disabled="actionLoading === txn.id" class="px-2 py-1 text-[10px] font-medium rounded bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-500/30 disabled:opacity-50">Query</button>
                      <button v-if="txn.status === 'failed' && txn.retry_count < txn.max_retries" @click="retryTransaction(txn)" :disabled="actionLoading === txn.id" class="px-2 py-1 text-[10px] font-medium rounded bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400 hover:bg-amber-200 dark:hover:bg-amber-500/30 disabled:opacity-50">{{ txn.checkout_request_id ? 'Query & Retry' : 'Retry' }}</button>
                      <button @click="openModal(txn, 'processed')" :disabled="actionLoading === txn.id" class="px-2 py-1 text-[10px] font-medium rounded bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-200 dark:hover:bg-emerald-500/30 disabled:opacity-50">Complete</button>
                      <button @click="openModal(txn, 'failed')" :disabled="actionLoading === txn.id" class="px-2 py-1 text-[10px] font-medium rounded bg-rose-100 dark:bg-rose-500/20 text-rose-700 dark:text-rose-400 hover:bg-rose-200 dark:hover:bg-rose-500/30 disabled:opacity-50">Fail</button>
                    </div>
                  </td>
                </tr>
                <tr v-if="expandedRow === txn.id" class="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-700">
                  <td :colspan="canEdit ? 10 : 9" class="px-6 py-3">
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
                      <div>
                        <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-0.5">Checkout Request ID</p>
                        <p class="font-mono text-slate-900 dark:text-white break-all">{{ txn.checkout_request_id || '—' }}</p>
                      </div>
                      <div>
                        <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-0.5">Failure Reason</p>
                        <p class="text-rose-600 dark:text-rose-400">{{ txn.failure_reason || '—' }}</p>
                      </div>
                      <div>
                        <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-0.5">Expires At</p>
                        <p class="text-slate-900 dark:text-white">{{ txn.expires_at ? formatDate(txn.expires_at) : '—' }}</p>
                      </div>
                      <div>
                        <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-0.5">Failure Category</p>
                        <p class="text-slate-900 dark:text-white">{{ txn.failure_category || '—' }}</p>
                      </div>
                      <div>
                        <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-0.5">Error Code</p>
                        <p class="font-mono text-slate-900 dark:text-white">{{ txn.error_code || '—' }}</p>
                      </div>
                      <div v-if="txn.gateway_result_data">
                        <p class="text-[10px] text-slate-500 dark:text-slate-400 mb-0.5">Gateway Result</p>
                        <p class="font-mono text-slate-600 dark:text-slate-400 text-[10px] break-all">{{ JSON.stringify(txn.gateway_result_data).substring(0, 120) }}...</p>
                      </div>
                    </div>
                    <div v-if="canEdit" class="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 flex justify-end">
                      <button @click.stop="openEditQueue(txn)" class="px-3 py-1.5 text-xs font-medium rounded-lg bg-blue-600 hover:bg-blue-700 text-white">Edit Transaction</button>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>

          <!-- Note Modal -->
          <div v-if="modal.show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 w-full max-w-md mx-4">
              <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-1">
                {{ modal.action === 'processed' ? 'Force Complete' : 'Force Fail' }} — {{ modal.txn?.initiator }}
              </h3>
              <p class="text-xs text-slate-500 dark:text-slate-400 mb-3">This action will be logged. A reason is required.</p>
              <textarea v-model="modal.note" rows="3" placeholder="Reason for override..." class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white resize-none"></textarea>
              <p v-if="modal.error" class="text-xs text-rose-500 mt-1">{{ modal.error }}</p>
              <div class="flex justify-end gap-2 mt-3">
                <button @click="modal.show = false" class="px-3 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">Cancel</button>
                <button @click="submitOverride" :disabled="actionLoading" class="px-3 py-1.5 text-xs font-medium rounded-lg text-white disabled:opacity-50" :class="modal.action === 'processed' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-rose-600 hover:bg-rose-700'">
                  {{ actionLoading ? 'Submitting...' : 'Confirm' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Query M-Pesa Result -->
          <div v-if="queryResult" class="mt-3 p-3 rounded-lg border text-xs" :class="queryResult.result_code === '0' ? 'bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/20 text-emerald-800 dark:text-emerald-400' : 'bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/20 text-amber-800 dark:text-amber-400'">
            <div class="flex justify-between items-start">
              <div>
                <p class="font-medium">M-Pesa Query Result</p>
                <p class="mt-0.5">{{ queryResult.message }}</p>
                <p v-if="queryResult.action_taken" class="mt-0.5 text-emerald-600 dark:text-emerald-400">✅ {{ queryResult.action_taken.replace(/_/g, ' ') }}</p>
              </div>
              <button @click="queryResult = null" class="text-slate-400 hover:text-slate-600">✕</button>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'analytics'" class="space-y-4">
          <div v-if="failureAnalytics" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-slate-50 dark:bg-slate-900 rounded-lg p-4">
              <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-3">Failures by Category</h3>
              <div class="space-y-2">
                <div v-for="item in failureAnalytics.by_category" :key="item.failure_category" class="flex justify-between text-xs">
                  <span class="text-slate-600 dark:text-slate-400">{{ item.failure_category || 'uncategorized' }}</span>
                  <span class="font-semibold text-slate-900 dark:text-white">{{ item.count }}</span>
                </div>
              </div>
            </div>
            
            <div class="bg-slate-50 dark:bg-slate-900 rounded-lg p-4">
              <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-3">Failures by Queue Type</h3>
              <div class="space-y-2">
                <div v-for="item in failureAnalytics.by_queue_type" :key="item.queue_type" class="flex justify-between text-xs">
                  <span class="text-slate-600 dark:text-slate-400">{{ item.queue_type }}</span>
                  <span class="font-semibold text-slate-900 dark:text-white">{{ item.count }}</span>
                </div>
              </div>
            </div>
            
            <div class="bg-slate-50 dark:bg-slate-900 rounded-lg p-4">
              <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-3">Retry Analysis</h3>
              <div class="space-y-2">
                <div v-for="item in failureAnalytics.retry_analysis" :key="item.retry_count" class="flex justify-between text-xs">
                  <span class="text-slate-600 dark:text-slate-400">{{ item.retry_count }} retries</span>
                  <span class="font-semibold text-slate-900 dark:text-white">{{ item.count }}</span>
                </div>
              </div>
            </div>
            
            <div class="bg-slate-50 dark:bg-slate-900 rounded-lg p-4">
              <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-3">Summary</h3>
              <div class="space-y-2 text-xs">
                <div class="flex justify-between">
                  <span class="text-slate-600 dark:text-slate-400">Total Failures (30d)</span>
                  <span class="font-semibold text-rose-600 dark:text-rose-400">{{ failureAnalytics.total_failures }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-600 dark:text-slate-400">Avg Retry Count</span>
                  <span class="font-semibold text-slate-900 dark:text-white">{{ avgRetryCount }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'points'" class="overflow-x-auto">
          <div v-if="canEdit" class="flex justify-end mb-2">
            <button @click="openPointsModal()" class="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-medium">+ Award / Deduct Points</button>
          </div>
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Type</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Points</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Description</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="txn in filteredPoints" :key="txn.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ txn.user_account || txn.user }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400">{{ txn.transaction_type }}</span></td>
                <td class="px-3 py-2 text-xs font-semibold" :class="txn.points > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'">{{ txn.points > 0 ? '+' : '' }}{{ txn.points }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ txn.description }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatDate(txn.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- Edit Payment Modal -->
  <div v-if="paymentModal.show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 w-full max-w-md mx-4">
      <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-3">Edit Payment — {{ paymentModal.txn?.initiator }}</h3>
      <div class="space-y-3">
        <div>
          <label class="text-[10px] text-slate-500 dark:text-slate-400">Status</label>
          <select v-model="paymentModal.status" class="w-full mt-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white">
            <option value="completed">Completed</option>
            <option value="refunded">Refunded</option>
            <option value="partially_refunded">Partially Refunded</option>
          </select>
        </div>
        <div>
          <label class="text-[10px] text-slate-500 dark:text-slate-400">Description</label>
          <textarea v-model="paymentModal.description" rows="2" class="w-full mt-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white resize-none"></textarea>
        </div>
        <p v-if="paymentModal.error" class="text-xs text-rose-500">{{ paymentModal.error }}</p>
      </div>
      <div class="flex justify-end gap-2 mt-4">
        <button @click="paymentModal.show = false" class="px-3 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">Cancel</button>
        <button @click="submitEditPayment" :disabled="actionLoading" class="px-3 py-1.5 text-xs font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50">{{ actionLoading ? 'Saving...' : 'Save' }}</button>
      </div>
    </div>
  </div>

  <!-- Balance Adjustment Modal -->
  <div v-if="balanceModal.show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 w-full max-w-md mx-4">
      <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-3">Manual Balance Adjustment</h3>
      <div class="space-y-3">
        <div>
          <label class="text-[10px] text-slate-500 dark:text-slate-400">Account (username)</label>
          <input v-model="balanceModal.account" type="text" placeholder="e.g. CLI000003" class="w-full mt-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white" />
        </div>
        <div>
          <label class="text-[10px] text-slate-500 dark:text-slate-400">Type</label>
          <select v-model="balanceModal.type" class="w-full mt-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white">
            <option value="adjustment">Adjustment</option>
            <option value="bonus">Bonus Credit</option>
            <option value="penalty">Penalty Charge</option>
            <option value="refund">Refund</option>
          </select>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="text-[10px] text-slate-500 dark:text-slate-400">Credit (add)</label>
            <input v-model="balanceModal.credit" type="number" min="0" step="0.01" class="w-full mt-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white" />
          </div>
          <div>
            <label class="text-[10px] text-slate-500 dark:text-slate-400">Debit (subtract)</label>
            <input v-model="balanceModal.debit" type="number" min="0" step="0.01" class="w-full mt-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white" />
          </div>
        </div>
        <div>
          <label class="text-[10px] text-slate-500 dark:text-slate-400">Description</label>
          <input v-model="balanceModal.description" type="text" class="w-full mt-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white" />
        </div>
        <p v-if="balanceModal.error" class="text-xs text-rose-500">{{ balanceModal.error }}</p>
      </div>
      <div class="flex justify-end gap-2 mt-4">
        <button @click="balanceModal.show = false" class="px-3 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">Cancel</button>
        <button @click="submitBalanceAdjustment" :disabled="actionLoading" class="px-3 py-1.5 text-xs font-medium bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg disabled:opacity-50">{{ actionLoading ? 'Saving...' : 'Submit' }}</button>
      </div>
    </div>
  </div>

  <!-- Points Modal -->
  <div v-if="pointsModal.show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 w-full max-w-md mx-4">
      <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-3">Award / Deduct Points</h3>
      <div class="space-y-3">
        <div>
          <label class="text-[10px] text-slate-500 dark:text-slate-400">Account (username)</label>
          <input v-model="pointsModal.account" type="text" placeholder="e.g. CLI000003" class="w-full mt-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white" />
        </div>
        <div>
          <label class="text-[10px] text-slate-500 dark:text-slate-400">Type</label>
          <select v-model="pointsModal.type" class="w-full mt-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white">
            <option value="earned_achievement">Award (Achievement)</option>
            <option value="earned_referral">Award (Referral)</option>
            <option value="expired">Deduct (Expired)</option>
          </select>
        </div>
        <div>
          <label class="text-[10px] text-slate-500 dark:text-slate-400">Points (positive = award, negative = deduct)</label>
          <input v-model="pointsModal.points" type="number" class="w-full mt-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white" />
        </div>
        <div>
          <label class="text-[10px] text-slate-500 dark:text-slate-400">Description</label>
          <input v-model="pointsModal.description" type="text" class="w-full mt-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white" />
        </div>
        <p v-if="pointsModal.error" class="text-xs text-rose-500">{{ pointsModal.error }}</p>
      </div>
      <div class="flex justify-end gap-2 mt-4">
        <button @click="pointsModal.show = false" class="px-3 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">Cancel</button>
        <button @click="submitPoints" :disabled="actionLoading" class="px-3 py-1.5 text-xs font-medium bg-amber-600 hover:bg-amber-700 text-white rounded-lg disabled:opacity-50">{{ actionLoading ? 'Saving...' : 'Submit' }}</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'

export default {
  name: 'Transactions',
  components: { ModernMetricCard },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const activeTab = ref('queue')
    const searchTerm = ref('')
    const statusFilter = ref('')
    const paymentMethodFilter = ref('')
    const dateFrom = ref('')
    const dateTo = ref('')
    const stats = ref({ total_revenue: 0, completed_count: 0, pending_count: 0, failed_count: 0 })
    
    // Pagination
    const currentPage = ref(1)
    const pageSize = ref(50)
    const totalCount = ref(0)
    const payments = ref([])
    const balance = ref([])
    const queue = ref([])
    const points = ref([])
    const expandedRow = ref(null)
    const actionLoading = ref(null)
    const queryResult = ref(null)
    const modal = ref({ show: false, txn: null, action: '', note: '', error: '' })

    const storedUser = (() => {
      try { return JSON.parse(localStorage.getItem('user')) || {} } catch { return {} }
    })()
    // canEdit: true for any logged-in admin (is_superuser, is_staff, or role-based)
    const canEdit = !!(storedUser.is_superuser || storedUser.is_staff || storedUser.role === 'superadmin' || storedUser.role === 'finance_manager' || localStorage.getItem('access_token'))

    const tabs = [
      { id: 'queue', label: 'Transaction Queue' },
      { id: 'payments', label: 'Payment Transactions' },
      { id: 'balance', label: 'Balance Transactions' },
      { id: 'points', label: 'Point Transactions' },
      { id: 'analytics', label: 'Failure Analytics' }
    ]

    const filteredPayments = computed(() => {
      let result = payments.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(t => 
          t.transaction_id?.toLowerCase().includes(term) || 
          t.initiator?.toLowerCase().includes(term)
        )
      }
      return result
    })

    const filteredBalance = computed(() => {
      let result = balance.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(t => 
          t.user_account?.toLowerCase().includes(term) || 
          t.description?.toLowerCase().includes(term)
        )
      }
      return result
    })

    const filteredQueue = computed(() => {
      let result = queue.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(t => 
          t.initiator?.toLowerCase().includes(term) || 
          t.package?.toLowerCase().includes(term)
        )
      }
      if (statusFilter.value) {
        result = result.filter(t => t.status === statusFilter.value)
      }
      return result
    })

    const filteredPoints = computed(() => {
      let result = points.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(t => 
          t.user_account?.toLowerCase().includes(term) || 
          t.description?.toLowerCase().includes(term)
        )
      }
      return result
    })

    const fetchPayments = async () => {
      try {
        let url = `suapi/payment-transactions/?page=${currentPage.value}&page_size=${pageSize.value}`
        if (paymentMethodFilter.value) url += `&payment_method=${paymentMethodFilter.value}`
        if (dateFrom.value) url += `&created_at__gte=${dateFrom.value}`
        if (dateTo.value) url += `&created_at__lte=${dateTo.value}`
        
        const data = await makeRequest('get', url)
        payments.value = data.results || data
        totalCount.value = data.count || payments.value.length
      } catch (err) { console.error('Error:', err) }
    }

    const fetchBalance = async () => {
      try {
        let url = `suapi/balance-transactions/?page=${currentPage.value}&page_size=${pageSize.value}`
        if (dateFrom.value) url += `&created_at__gte=${dateFrom.value}`
        if (dateTo.value) url += `&created_at__lte=${dateTo.value}`
        
        const data = await makeRequest('get', url)
        balance.value = data.results || data
        totalCount.value = data.count || balance.value.length
      } catch (err) { console.error('Error:', err) }
    }

    const fetchQueue = async () => {
      try {
        let url = `suapi/transaction-queue/?page=${currentPage.value}&page_size=${pageSize.value}`
        if (statusFilter.value) url += `&status=${statusFilter.value}`
        if (dateFrom.value) url += `&created_at__gte=${dateFrom.value}`
        if (dateTo.value) url += `&created_at__lte=${dateTo.value}`
        
        const data = await makeRequest('get', url, null, false)
        queue.value = data.results || data
        totalCount.value = data.count || queue.value.length
      } catch (err) { console.error('Error:', err) }
    }
    
    const fetchStats = async () => {
      try {
        const data = await makeRequest('get', 'suapi/transactions/stats/')
        stats.value = data
      } catch (err) { 
        console.error('Error fetching stats:', err)
        // Fallback to queue-derived stats
        const q = queue.value
        stats.value = {
          failed_count: q.filter(t => t.status === 'failed').length,
          pending_count: q.filter(t => t.status === 'pending' || t.status === 'processing').length,
          completed_count: q.filter(t => t.status === 'completed' || t.status === 'processed').length,
          total_revenue: q.filter(t => t.status === 'completed' || t.status === 'processed').reduce((s, t) => s + parseFloat(t.price || 0), 0)
        }
      }
    }

    const toggleExpand = (id) => {
      expandedRow.value = expandedRow.value === id ? null : id
    }

    const openModal = (txn, action) => {
      modal.value = { show: true, txn, action, note: '', error: '' }
    }

    const submitOverride = async () => {
      if (!modal.value.note.trim()) {
        modal.value.error = 'Note is required'
        return
      }
      actionLoading.value = modal.value.txn.id
      try {
        await makeRequest('post', `suapi/transaction-queue/${modal.value.txn.id}/update_status/`, {
          status: modal.value.action,
          note: modal.value.note
        }, false)
        modal.value.show = false
        await fetchQueue()
      } catch (err) {
        modal.value.error = err.response?.data?.error || 'Request failed'
      } finally {
        actionLoading.value = null
      }
    }

    const queryMpesa = async (txn) => {
      actionLoading.value = txn.id
      queryResult.value = null
      try {
        const data = await makeRequest('post', `suapi/transaction-queue/${txn.id}/query_mpesa/`, {}, false)
        queryResult.value = data
        await fetchQueue()
      } catch (err) {
        queryResult.value = { result_code: 'ERR', message: err.response?.data?.error || 'Query failed' }
      } finally {
        actionLoading.value = null
      }
    }

    const fetchPoints = async () => {
      try {
        let url = `suapi/point-transactions-txn/?page=${currentPage.value}&page_size=${pageSize.value}`
        if (dateFrom.value) url += `&created_at__gte=${dateFrom.value}`
        if (dateTo.value) url += `&created_at__lte=${dateTo.value}`
        
        const data = await makeRequest('get', url)
        points.value = data.results || data
        totalCount.value = data.count || points.value.length
      } catch (err) { console.error('Error:', err) }
    }
    
    const failureAnalytics = ref(null)
    const fetchFailureAnalytics = async () => {
      try {
        const data = await makeRequest('get', 'suapi/transaction-queue/failure_analytics/', null, false)
        failureAnalytics.value = data
      } catch (err) { console.error('failure analytics error:', err) }
    }

    // Payment edit modal
    const paymentModal = ref({ show: false, txn: null, status: '', description: '', error: '' })
    const openEditPayment = (txn) => {
      paymentModal.value = { show: true, txn, status: txn.status, description: txn.description || '', error: '' }
    }
    const submitEditPayment = async () => {
      actionLoading.value = true
      try {
        await makeRequest('patch', `suapi/payment-transactions/${paymentModal.value.txn.id}/`, {
          status: paymentModal.value.status,
          description: paymentModal.value.description
        })
        paymentModal.value.show = false
        await fetchPayments()
      } catch (err) {
        paymentModal.value.error = err.response?.data?.error || 'Save failed'
      } finally { actionLoading.value = null }
    }

    // Balance adjustment modal
    const balanceModal = ref({ show: false, account: '', type: 'adjustment', credit: 0, debit: 0, description: '', error: '' })
    const openBalanceModal = () => {
      balanceModal.value = { show: true, account: '', type: 'adjustment', credit: 0, debit: 0, description: '', error: '' }
    }
    const submitBalanceAdjustment = async () => {
      if (!balanceModal.value.account || !balanceModal.value.description) {
        balanceModal.value.error = 'Account and description are required'
        return
      }
      actionLoading.value = true
      try {
        await makeRequest('post', 'suapi/balance-transactions/', {
          user_account: balanceModal.value.account,
          transaction_type: balanceModal.value.type,
          credit: parseFloat(balanceModal.value.credit) || 0,
          debit: parseFloat(balanceModal.value.debit) || 0,
          description: balanceModal.value.description,
          balance_before: 0
        })
        balanceModal.value.show = false
        await fetchBalance()
      } catch (err) {
        balanceModal.value.error = err.response?.data ? JSON.stringify(err.response.data) : 'Save failed'
      } finally { actionLoading.value = null }
    }

    // Points modal
    const pointsModal = ref({ show: false, account: '', type: 'earned_achievement', points: 0, description: '', error: '' })
    const openPointsModal = () => {
      pointsModal.value = { show: true, account: '', type: 'earned_achievement', points: 0, description: '', error: '' }
    }
    const submitPoints = async () => {
      if (!pointsModal.value.account || !pointsModal.value.description || !pointsModal.value.points) {
        pointsModal.value.error = 'All fields are required'
        return
      }
      actionLoading.value = true
      try {
        await makeRequest('post', 'suapi/point-transactions-txn/', {
          user_account: pointsModal.value.account,
          transaction_type: pointsModal.value.type,
          points: parseInt(pointsModal.value.points),
          description: pointsModal.value.description
        })
        pointsModal.value.show = false
        await fetchPoints()
      } catch (err) {
        pointsModal.value.error = err.response?.data ? JSON.stringify(err.response.data) : 'Save failed'
      } finally { actionLoading.value = null }
    }

    const retryTransaction = async (txn) => {
      // For M-Pesa transactions, query first to get real status before re-queuing
      if (txn.checkout_request_id) {
        actionLoading.value = txn.id
        queryResult.value = null
        try {
          const data = await makeRequest('post', `suapi/transaction-queue/${txn.id}/query_mpesa/`, {}, false)
          queryResult.value = data
          await fetchQueue()
        } catch (err) {
          queryResult.value = { result_code: 'ERR', message: err.response?.data?.error || 'Query failed' }
        } finally {
          actionLoading.value = null
        }
      } else {
        // No checkout_request_id (non-M-Pesa) — just re-queue
        if (!confirm(`Re-queue transaction for ${txn.initiator}?`)) return
        actionLoading.value = txn.id
        try {
          await makeRequest('post', `suapi/transaction-queue/${txn.id}/retry/`, {}, false)
          await fetchQueue()
        } catch (err) {
          alert(err.response?.data?.error || 'Retry failed')
        } finally {
          actionLoading.value = null
        }
      }
    }
    
    const exportCSV = () => {
      let data = []
      let headers = []
      
      if (activeTab.value === 'payments') {
        headers = ['Transaction ID', 'User', 'Amount', 'Method', 'Status', 'Date']
        data = filteredPayments.value.map(t => [
          t.transaction_id, t.initiator, t.amount, t.payment_method, t.status, formatDate(t.created_at)
        ])
      } else if (activeTab.value === 'balance') {
        headers = ['User', 'Type', 'Amount', 'Balance Before', 'Balance After', 'Description', 'Date']
        data = filteredBalance.value.map(t => [
          t.user_account || t.user, t.transaction_type, t.credit > 0 ? t.credit : -t.debit,
          t.balance_before, t.balance_after, t.description, formatDate(t.created_at)
        ])
      } else if (activeTab.value === 'queue') {
        headers = ['Type', 'User', 'Package', 'Price', 'Method', 'Status', 'Retries', 'Date']
        data = filteredQueue.value.map(t => [
          t.queue_type, t.initiator, t.package, t.price, t.method, t.status,
          `${t.retry_count}/${t.max_retries}`, formatDate(t.created_at)
        ])
      } else if (activeTab.value === 'points') {
        headers = ['User', 'Type', 'Points', 'Description', 'Date']
        data = filteredPoints.value.map(t => [
          t.user_account || t.user, t.transaction_type, t.points, t.description, formatDate(t.created_at)
        ])
      }
      
      const csv = [headers, ...data].map(row => row.join(',')).join('\n')
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${activeTab.value}_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
    }
    
    const avgRetryCount = computed(() => {
      if (!failureAnalytics.value?.retry_analysis?.length) return 0
      const total = failureAnalytics.value.retry_analysis.reduce((sum, item) => sum + (item.retry_count * item.count), 0)
      const count = failureAnalytics.value.retry_analysis.reduce((sum, item) => sum + item.count, 0)
      return count > 0 ? (total / count).toFixed(2) : 0
    })
    
    const refreshData = async () => {
      currentPage.value = 1
      await fetchStats()
      if (activeTab.value === 'analytics') {
        await fetchFailureAnalytics()
      } else {
        await Promise.all([fetchPayments(), fetchBalance(), fetchQueue(), fetchPoints()])
      }
    }

    const formatCurrency = (amount) => {
      if (!amount) return 'KSh 0'
      return `KSh ${parseFloat(amount).toLocaleString()}`
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleString('en-US', { 
        month: 'short', day: 'numeric', year: 'numeric', 
        hour: '2-digit', minute: '2-digit' 
      })
    }

    const getStatusClass = (status) => {
      const classes = {
        completed: 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        refunded: 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        partially_refunded: 'bg-orange-100 dark:bg-orange-500/20 text-orange-700 dark:text-orange-400'
      }
      return classes[status] || 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'
    }

    const getQueueStatusClass = (status) => {
      const classes = {
        pending: 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        processing: 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400',
        completed: 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        failed: 'bg-rose-100 dark:bg-rose-500/20 text-rose-700 dark:text-rose-400',
        processed: 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400'
      }
      return classes[status] || 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'
    }

    watch(activeTab, async () => {
      currentPage.value = 1
      if (activeTab.value === 'analytics') await fetchFailureAnalytics()
      else if (activeTab.value === 'payments') await fetchPayments()
      else if (activeTab.value === 'balance') await fetchBalance()
      else if (activeTab.value === 'queue') await fetchQueue()
      else if (activeTab.value === 'points') await fetchPoints()
    })
    
    watch([currentPage, statusFilter, paymentMethodFilter, dateFrom, dateTo], async () => {
      if (activeTab.value === 'payments') await fetchPayments()
      else if (activeTab.value === 'balance') await fetchBalance()
      else if (activeTab.value === 'queue') await fetchQueue()
      else if (activeTab.value === 'points') await fetchPoints()
    })
    
    onMounted(async () => {
      await fetchStats()
      await Promise.all([fetchPayments(), fetchBalance(), fetchQueue(), fetchPoints()])
    })

    return {
      loading, error, activeTab, searchTerm, statusFilter, paymentMethodFilter, dateFrom, dateTo,
      stats, tabs, currentPage, pageSize, totalCount,
      filteredPayments, filteredBalance, filteredQueue, filteredPoints,
      refreshData, formatCurrency, formatDate, getStatusClass, getQueueStatusClass,
      expandedRow, toggleExpand, canEdit, actionLoading, modal, openModal, submitOverride,
      queryMpesa, queryResult, retryTransaction, exportCSV,
      failureAnalytics, avgRetryCount,
      paymentModal, openEditPayment, submitEditPayment,
      balanceModal, openBalanceModal, submitBalanceAdjustment,
      pointsModal, openPointsModal, submitPoints
    }
  }
}
</script>

<style scoped>
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes slide-up { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fade-in 0.3s ease-out; }
.animate-slide-up { animation: slide-up 0.4s ease-out; }
</style>
