<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-600 bg-clip-text text-transparent mb-2">
            💰 Transaction Records
          </h1>
          <p class="text-slate-600 font-light">Manage and monitor all transaction activities</p>
        </div>
        <div class="flex items-center space-x-3">
          <div class="relative">
            <div class="w-3 h-3 bg-emerald-500 rounded-full animate-ping absolute -top-1 -right-1"></div>
            <div class="w-2 h-2 bg-emerald-500 rounded-full absolute -top-0.5 -right-0.5"></div>
            <button 
              @click="refreshData"
              class="p-2 hover:bg-white/50 rounded-xl transition-all duration-300 backdrop-blur-sm"
              title="Refresh data"
            >
              <ArrowPathIcon class="w-6 h-6 text-slate-600" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 border border-rose-200 rounded-2xl p-6 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <ExclamationTriangleIcon class="w-6 h-6 text-rose-600" />
          <div>
            <h3 class="text-rose-800 font-semibold">Failed to load transaction data</h3>
            <p class="text-rose-600 text-sm">{{ error }}</p>
          </div>
        </div>
        <button 
          @click="fetchAllData"
          class="px-4 py-2 bg-rose-600 text-white rounded-lg hover:bg-rose-700 transition-colors duration-200 flex items-center space-x-2"
        >
          <ArrowPathIcon class="w-4 h-4" />
          <span>Retry</span>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !error" class="flex items-center justify-center py-20">
      <div class="text-center">
        <div class="relative">
          <div class="w-16 h-16 border-4 border-blue-200 rounded-full"></div>
          <div class="w-16 h-16 border-4 border-transparent border-t-blue-500 rounded-full animate-spin absolute top-0 left-0"></div>
        </div>
        <p class="mt-4 text-slate-500 font-light">Loading transaction data...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="!loading" class="space-y-8">
      <!-- Search Section -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div class="flex-1">
            <div class="relative">
              <MagnifyingGlassIcon class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                v-model="searchTerm"
                type="text"
                placeholder="Search across all fields (ID, amount, initiator, description, etc.)"
                class="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                @input="handleSearch"
              />
            </div>
          </div>
          <div class="flex space-x-3">
            <button
              @click="clearSearch"
              class="px-4 py-3 border border-slate-300 text-slate-600 rounded-xl hover:bg-slate-50 transition-all duration-300 flex items-center space-x-2"
            >
              <ArrowPathIcon class="w-4 h-4" />
              <span>Clear</span>
            </button>
            <button
              @click="openCreateForm"
              class="px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-500 hover:to-purple-500 transition-all duration-300 flex items-center space-x-2 shadow-lg hover:shadow-xl"
            >
              <PlusIcon class="w-4 h-4" />
              <span>Add Transaction</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Transaction Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <ModernMetricCard
          title="Total Transactions"
          :value="stats.totalCount"
          trend="up"
          trendValue="12.5%"
          icon="📊"
          color="blue"
          :formatted="true"
        />
        
        <ModernMetricCard
          title="Total Amount"
          :value="`KSh ${formatNumber(stats.totalAmount)}`"
          trend="up"
          trendValue="18.7%"
          icon="💰"
          color="cyan"
          :formatted="false"
        />
        
        <ModernMetricCard
          title="Successful"
          :value="stats.successfulCount"
          trend="up"
          trendValue="8.2%"
          icon="✅"
          color="emerald"
          :formatted="true"
        />
        
        <ModernMetricCard
          title="Failed"
          :value="stats.failedCount"
          trend="down"
          trendValue="2.1%"
          icon="❌"
          color="rose"
          :formatted="true"
        />
      </div>

      <!-- Transactions Table -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-200/60 flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <h3 class="text-lg font-semibold text-slate-800 flex items-center">
              <TableCellsIcon class="w-5 h-5 text-slate-600 mr-2" />
              Transaction Records ({{ filteredTransactions.length }} found)
            </h3>
            
            <!-- Items per page selector -->
            <div class="flex items-center space-x-2">
              <span class="text-sm text-slate-600">Show:</span>
              <select
                v-model="itemsPerPage"
                @change="handleItemsPerPageChange"
                class="text-sm border border-slate-300 rounded-lg px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="15">15</option>
                <option value="20">20</option>
              </select>
              <span class="text-sm text-slate-600">per page</span>
            </div>
          </div>
          <button
            @click="exportToCSV"
            class="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-all duration-300 flex items-center space-x-2 text-sm"
          >
            <ArrowDownTrayIcon class="w-4 h-4" />
            <span>Export CSV</span>
          </button>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 border-b border-slate-200/60">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Transaction ID</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Initiator</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Amount</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Status</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Description</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Time</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200/60">
              <tr 
                v-for="transaction in paginatedTransactions" 
                :key="transaction.id"
                class="hover:bg-slate-50 transition-colors duration-200"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                  {{ transaction.transaction_id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                  {{ transaction.initiator }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600 font-medium">
                  KSh {{ formatNumber(transaction.amount || 0) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getStatusBadgeClass(transaction.result_code)" class="px-2 py-1 text-xs font-medium rounded-full flex items-center space-x-1 w-fit">
                    <CheckCircleIcon v-if="transaction.result_code === 0" class="w-3 h-3" />
                    <XCircleIcon v-else class="w-3 h-3" />
                    <span>{{ formatStatus(transaction.result_code) }}</span>
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-slate-600 max-w-xs truncate">
                  {{ transaction.result_desc || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                  {{ formatDate(transaction.transaction_time) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex space-x-2">
                    <button
                      @click="openEditForm(transaction)"
                      class="text-blue-600 hover:text-blue-800 transition-colors duration-200 p-1 rounded"
                      title="Edit Transaction"
                    >
                      <PencilSquareIcon class="w-4 h-4" />
                    </button>
                    <button
                      @click="openDeleteConfirm(transaction)"
                      class="text-rose-600 hover:text-rose-800 transition-colors duration-200 p-1 rounded"
                      title="Delete Transaction"
                    >
                      <TrashIcon class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty State -->
        <div v-if="filteredTransactions.length === 0" class="text-center py-12">
          <div class="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <CreditCardIcon class="w-8 h-8 text-slate-400" />
          </div>
          <h3 class="text-lg font-semibold text-slate-600 mb-2">No transactions found</h3>
          <p class="text-slate-500 mb-4">No transactions match your search criteria.</p>
          <button
            @click="clearSearch"
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            Clear search and try again
          </button>
        </div>

        <!-- Pagination -->
        <div v-if="filteredTransactions.length > 0" class="px-6 py-4 border-t border-slate-200/60 flex items-center justify-between">
          <div class="text-sm text-slate-600">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredTransactions.length }} entries
          </div>
          <div class="flex space-x-2">
            <button
              @click="previousPage"
              :disabled="currentPage === 1"
              :class="[
                'px-3 py-2 rounded-lg border transition-all duration-300',
                currentPage === 1 
                  ? 'border-slate-300 text-slate-400 cursor-not-allowed' 
                  : 'border-slate-300 text-slate-600 hover:bg-slate-50'
              ]"
            >
              <ChevronLeftIcon class="w-4 h-4" />
            </button>
            <button
              @click="nextPage"
              :disabled="currentPage >= totalPages"
              :class="[
                'px-3 py-2 rounded-lg border transition-all duration-300',
                currentPage >= totalPages
                  ? 'border-slate-300 text-slate-400 cursor-not-allowed' 
                  : 'border-slate-300 text-slate-600 hover:bg-slate-50'
              ]"
            >
              <ChevronRightIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Analytics Charts -->
      <div v-if="filteredTransactions.length > 0" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Status Distribution -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6">
          <h3 class="text-lg font-semibold text-slate-800 mb-4 flex items-center">
            <ChartPieIcon class="w-5 h-5 text-slate-600 mr-2" />
            Transaction Status Distribution
          </h3>
          <div class="h-80">
            <apexchart
              v-if="statusChartSeries.length > 0"
              type="donut"
              height="100%"
              :options="statusChartOptions"
              :series="statusChartSeries"
            />
            <div v-else class="h-full flex items-center justify-center bg-slate-50 rounded-lg">
              <p class="text-slate-500">No chart data available</p>
            </div>
          </div>
        </div>

        <!-- Amount Distribution -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6">
          <h3 class="text-lg font-semibold text-slate-800 mb-4 flex items-center">
            <ChartBarIcon class="w-5 h-5 text-slate-600 mr-2" />
            Transaction Amount Distribution
          </h3>
          <div class="h-80">
            <apexchart
              v-if="amountChartSeries[0]?.data?.length > 0"
              type="bar"
              height="100%"
              :options="amountChartOptions"
              :series="amountChartSeries"
            />
            <div v-else class="h-full flex items-center justify-center bg-slate-50 rounded-lg">
              <p class="text-slate-500">No chart data available</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Transaction Form Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-slate-200/60">
          <h3 class="text-xl font-semibold text-slate-800 flex items-center">
            {{ formData.id ? '✏️ Edit Transaction' : '➕ Create New Transaction' }}
          </h3>
        </div>
        
        <div class="p-6">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Transaction Details -->
            <div class="space-y-4">
              <h4 class="font-semibold text-slate-700 flex items-center">
                <CreditCardIcon class="w-5 h-5 text-slate-600 mr-2" />
                Transaction Details
              </h4>
              
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Transaction ID *</label>
                <input
                  v-model="formData.transaction_id"
                  type="text"
                  placeholder="e.g., TXN_001_2024"
                  class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Initiator *</label>
                <input
                  v-model="formData.initiator"
                  type="text"
                  placeholder="e.g., Customer Name or System"
                  class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Amount *</label>
                <input
                  v-model="formData.amount"
                  type="number"
                  step="0.01"
                  min="0"
                  class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Balance</label>
                <input
                  v-model="formData.balance"
                  type="number"
                  step="0.01"
                  min="0"
                  class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                />
              </div>
            </div>

            <!-- Status & Metadata -->
            <div class="space-y-4">
              <h4 class="font-semibold text-slate-700 flex items-center">
                <ChartBarIcon class="w-5 h-5 text-slate-600 mr-2" />
                Status & Metadata
              </h4>

              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Result Code *</label>
                <select
                  v-model="formData.result_code"
                  class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                >
                  <option value="0">0 - Success</option>
                  <option value="1">1 - Failed</option>
                  <option value="2">2 - Pending</option>
                  <option value="3">3 - Cancelled</option>
                  <option value="4">4 - Timeout</option>
                  <option value="5">5 - Unknown</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Result Description *</label>
                <textarea
                  v-model="formData.result_desc"
                  placeholder="Describe the transaction outcome..."
                  rows="3"
                  class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                ></textarea>
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Merchant Request ID</label>
                <input
                  v-model="formData.merchant_request_id"
                  type="text"
                  placeholder="Optional merchant reference"
                  class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Checkout Request ID</label>
                <input
                  v-model="formData.checkout_request_id"
                  type="text"
                  placeholder="Optional checkout reference"
                  class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                />
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex justify-end space-x-3 mt-6 pt-6 border-t border-slate-200/60">
            <button
              @click="closeFormModal"
              class="px-6 py-2 border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50 transition-all duration-300"
            >
              Cancel
            </button>
            <button
              @click="saveTransaction"
              :disabled="saveLoading"
              :class="[
                'px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl flex items-center space-x-2',
                saveLoading ? 'opacity-50 cursor-not-allowed' : 'hover:from-blue-500 hover:to-purple-500'
              ]"
            >
              <ArrowPathIcon v-if="saveLoading" class="w-4 h-4 animate-spin" />
              <span>{{ formData.id ? 'Update Transaction' : 'Create Transaction' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div class="p-6">
          <div class="w-12 h-12 bg-rose-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <ExclamationTriangleIcon class="w-6 h-6 text-rose-600" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 text-center mb-2">Delete Transaction</h3>
          <p class="text-slate-600 text-center mb-6">
            Are you sure you want to delete transaction <strong>"{{ transactionToDelete?.transaction_id }}"</strong>? This action cannot be undone.
          </p>
          <div class="flex space-x-3">
            <button
              @click="closeDeleteModal"
              class="flex-1 px-4 py-2 border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50 transition-all duration-300"
            >
              Cancel
            </button>
            <button
              @click="confirmDelete"
              :disabled="deleteLoading"
              :class="[
                'flex-1 px-4 py-2 text-white rounded-lg transition-all duration-300 flex items-center justify-center space-x-2',
                deleteLoading ? 'bg-rose-400 cursor-not-allowed' : 'bg-rose-600 hover:bg-rose-700'
              ]"
            >
              <ArrowPathIcon v-if="deleteLoading" class="w-4 h-4 animate-spin" />
              <span>Delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import ModernMetricCard from '../components/MetricCard.vue'
import { useApi } from '../composables/useApi'

import {
  MagnifyingGlassIcon,
  PlusIcon,
  TableCellsIcon,
  PencilSquareIcon,
  TrashIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CreditCardIcon,
  ChartPieIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  ArrowDownTrayIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'Transactions',
  components: {
    ModernMetricCard,
    MagnifyingGlassIcon,
    PlusIcon,
    TableCellsIcon,
    PencilSquareIcon,
    TrashIcon,
    ChevronLeftIcon,
    ChevronRightIcon,
    CreditCardIcon,
    ChartPieIcon,
    ChartBarIcon,
    ExclamationTriangleIcon,
    ArrowPathIcon,
    ArrowDownTrayIcon,
    CheckCircleIcon,
    XCircleIcon,
    apexchart: VueApexCharts,
  },
  setup() {
    const { loading, error, makeRequest } = useApi()
    
    // Reactive data
    const transactions = ref([])
    const searchTerm = ref('')
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const transactionToDelete = ref(null)
    const currentPage = ref(1)
    const itemsPerPage = ref(5) // Default to 5 items per page
    const saveLoading = ref(false)
    const deleteLoading = ref(false)

    // Chart data - using ref instead of computed for options
    const statusChartSeries = ref([0, 0])
    const amountChartSeries = ref([{ name: 'Transaction Count', data: [] }])

    // Static chart options - defined as plain objects
    const statusChartOptions = {
      chart: {
        type: 'donut',
        height: '100%'
      },
      colors: ['#10B981', '#EF4444'],
      labels: ['Successful', 'Failed'],
      legend: {
        position: 'bottom',
        fontSize: '12px',
        labels: { colors: '#6B7280' }
      },
      plotOptions: {
        pie: {
          donut: {
            size: '65%',
            labels: {
              show: true,
              total: {
                show: true,
                label: 'Total',
                color: '#6B7280'
              }
            }
          }
        }
      },
      dataLabels: { 
        enabled: true,
        formatter: function (val) {
          return Math.round(val) + "%"
        }
      },
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            width: 200
          },
          legend: {
            position: 'bottom'
          }
        }
      }]
    }

    // Dynamic amount chart options
    const amountChartOptions = ref({
      chart: {
        type: 'bar',
        height: '100%',
        toolbar: { show: false }
      },
      colors: ['#8B5CF6'],
      plotOptions: {
        bar: {
          borderRadius: 4,
          columnWidth: '60%',
        }
      },
      dataLabels: { 
        enabled: true,
        formatter: function(val) {
          return val > 0 ? val : ''
        }
      },
      xaxis: {
        categories: [], // Will be populated dynamically
        labels: {
          style: { colors: '#6B7280', fontSize: '10px' },
          rotate: -45
        }
      },
      yaxis: {
        title: {
          text: 'Number of Transactions',
          style: { color: '#6B7280', fontSize: '12px' }
        },
        labels: {
          style: { colors: '#6B7280', fontSize: '11px' }
        }
      },
      tooltip: {
        y: {
          formatter: (value) => `${value} transaction${value !== 1 ? 's' : ''}`
        }
      },
      grid: {
        borderColor: '#F3F4F6',
        strokeDashArray: 4,
      }
    })
    
    // Form data
    const formData = ref({
      id: null,
      transaction_id: '',
      initiator: '',
      amount: 0,
      balance: 0,
      result_code: 0,
      result_desc: '',
      merchant_request_id: '',
      checkout_request_id: ''
    })

    // Function to calculate dynamic ranges based on data
    const calculateDynamicRanges = (transactions) => {
      if (transactions.length === 0) {
        return { ranges: ['No Data'], counts: [0] }
      }

      const amounts = transactions
        .map(t => parseFloat(t.amount) || 0)
        .filter(amount => amount >= 0)
        .sort((a, b) => a - b)

      if (amounts.length === 0) {
        return { ranges: ['No Valid Data'], counts: [0] }
      }

      const minAmount = amounts[0]
      const maxAmount = amounts[amounts.length - 1]
      
      // Calculate optimal range size based on data spread
      const dataRange = maxAmount - minAmount
      let rangeSize
      
      if (dataRange <= 50) {
        rangeSize = 5 // Small spread: 5 KSh ranges
      } else if (dataRange <= 200) {
        rangeSize = 10 // Medium spread: 10 KSh ranges  
      } else if (dataRange <= 1000) {
        rangeSize = 50 // Larger spread: 50 KSh ranges
      } else {
        rangeSize = 100 // Very large spread: 100 KSh ranges
      }

      // Calculate number of ranges (aim for 8-12 ranges for good visualization)
      const numRanges = Math.min(Math.max(8, Math.ceil(dataRange / rangeSize)), 15)
      
      // Adjust range size to get better distribution
      const adjustedRangeSize = Math.ceil(dataRange / numRanges)
      
      // Create ranges
      const ranges = []
      const counts = new Array(numRanges).fill(0)
      
      let currentStart = Math.floor(minAmount / adjustedRangeSize) * adjustedRangeSize
      if (currentStart > 0 && minAmount > 0) {
        currentStart = 0 // Always start from 0 for better readability
      }
      
      for (let i = 0; i < numRanges; i++) {
        const rangeStart = currentStart + (i * adjustedRangeSize)
        const rangeEnd = rangeStart + adjustedRangeSize - 1
        
        if (i === numRanges - 1) {
          ranges.push(`${rangeStart}+`)
        } else {
          ranges.push(`${rangeStart}-${rangeEnd}`)
        }
        
        // Count transactions in this range
        amounts.forEach(amount => {
          if (i === numRanges - 1) {
            // Last range includes everything from start to infinity
            if (amount >= rangeStart) {
              counts[i]++
            }
          } else {
            if (amount >= rangeStart && amount <= rangeEnd) {
              counts[i]++
            }
          }
        })
      }
      
      return { ranges, counts }
    }

    // Update chart data when transactions change
    watch(transactions, (newTransactions) => {
      if (newTransactions.length > 0) {
        // Update status chart
        const successful = newTransactions.filter(t => t.result_code === 0).length
        const failed = newTransactions.filter(t => t.result_code !== 0).length
        statusChartSeries.value = [successful, failed]
        
        // Calculate dynamic ranges based on actual data
        const { ranges, counts } = calculateDynamicRanges(newTransactions)
        
        // Update chart options with dynamic categories
        amountChartOptions.value = {
          ...amountChartOptions.value,
          xaxis: {
            ...amountChartOptions.value.xaxis,
            categories: ranges
          }
        }
        
        amountChartSeries.value = [{
          name: 'Transaction Count',
          data: counts
        }]
        
      } else {
        // Reset charts if no data
        statusChartSeries.value = [0, 0]
        amountChartSeries.value = [{ name: 'Transaction Count', data: [] }]
        amountChartOptions.value = {
          ...amountChartOptions.value,
          xaxis: {
            ...amountChartOptions.value.xaxis,
            categories: ['No Data']
          }
        }
      }
    }, { immediate: true })

    // Computed properties
    const stats = computed(() => {
      const totalCount = transactions.value.length
      const successfulCount = transactions.value.filter(t => t.result_code === 0).length
      const failedCount = totalCount - successfulCount
      
      // Fix for decimal strings like "0.00"
      const totalAmount = transactions.value.reduce((sum, transaction) => {
        if (!transaction.amount) return sum + 0
        
        // Handle decimal strings like "0.00", "1500.50", etc.
        const amountStr = String(transaction.amount).trim()
        const cleanAmount = amountStr.replace(/[^\d.-]/g, '')
        const amountValue = parseFloat(cleanAmount)
        
        return sum + (isNaN(amountValue) ? 0 : amountValue)
      }, 0)

      return {
        totalCount,
        successfulCount,
        failedCount,
        totalAmount
      }
    })

    const filteredTransactions = computed(() => {
      if (!searchTerm.value) return transactions.value
      
      const term = searchTerm.value.toLowerCase()
      return transactions.value.filter(transaction => 
        transaction.transaction_id?.toLowerCase().includes(term) ||
        transaction.initiator?.toLowerCase().includes(term) ||
        transaction.amount?.toString().includes(term) ||
        transaction.balance?.toString().includes(term) ||
        transaction.result_code?.toString().includes(term) ||
        transaction.result_desc?.toLowerCase().includes(term) ||
        transaction.merchant_request_id?.toLowerCase().includes(term) ||
        transaction.checkout_request_id?.toLowerCase().includes(term) ||
        transaction.transaction_time?.toString().includes(term)
      )
    })

    const totalPages = computed(() => Math.ceil(filteredTransactions.value.length / itemsPerPage.value))
    const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage.value)
    const endIndex = computed(() => Math.min(startIndex.value + itemsPerPage.value, filteredTransactions.value.length))
    const paginatedTransactions = computed(() => 
      filteredTransactions.value.slice(startIndex.value, endIndex.value)
    )

    // Methods
    const formatNumber = (num) => {
      // Handle NaN, null, undefined, empty strings
      if (num === null || num === undefined || num === '' || isNaN(num)) {
        return '0.00'
      }
      
      // If it's already a number, format it directly
      if (typeof num === 'number') {
        return new Intl.NumberFormat('en-KE', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }).format(num)
      }
      
      // If it's a string, clean and parse it
      if (typeof num === 'string') {
        const cleanNum = num.replace(/[^\d.-]/g, '')
        const parsed = parseFloat(cleanNum)
        
        if (isNaN(parsed)) {
          return '0.00'
        }
        
        return new Intl.NumberFormat('en-KE', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }).format(parsed)
      }
      
      // Fallback
      return '0.00'
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      try {
        return new Date(dateString).toLocaleString('en-KE', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        return 'Invalid Date'
      }
    }

    const formatStatus = (resultCode) => {
      const statusMap = {
        0: 'Success',
        1: 'Failed',
        2: 'Pending',
        3: 'Cancelled',
        4: 'Timeout',
        5: 'Unknown'
      }
      return statusMap[resultCode] || `Code ${resultCode}`
    }

    const getStatusBadgeClass = (resultCode) => {
      const classes = {
        0: 'bg-emerald-100 text-emerald-800',
        1: 'bg-rose-100 text-rose-800',
        2: 'bg-amber-100 text-amber-800',
        3: 'bg-slate-100 text-slate-800',
        4: 'bg-orange-100 text-orange-800',
        5: 'bg-gray-100 text-gray-800'
      }
      return classes[resultCode] || 'bg-gray-100 text-gray-800'
    }

    const handleSearch = () => {
      currentPage.value = 1
    }

    const clearSearch = () => {
      searchTerm.value = ''
      currentPage.value = 1
    }

    const handleItemsPerPageChange = () => {
      currentPage.value = 1 // Reset to first page when changing items per page
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }

    const previousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }

    const openCreateForm = () => {
      formData.value = {
        id: null,
        transaction_id: '',
        initiator: '',
        amount: 0,
        balance: 0,
        result_code: 0,
        result_desc: '',
        merchant_request_id: '',
        checkout_request_id: ''
      }
      showFormModal.value = true
    }

    const openEditForm = (transaction) => {
      formData.value = { ...transaction }
      showFormModal.value = true
    }

    const closeFormModal = () => {
      showFormModal.value = false
      formData.value = {
        id: null,
        transaction_id: '',
        initiator: '',
        amount: 0,
        balance: 0,
        result_code: 0,
        result_desc: '',
        merchant_request_id: '',
        checkout_request_id: ''
      }
    }

    const openDeleteConfirm = (transaction) => {
      transactionToDelete.value = transaction
      showDeleteModal.value = true
    }

    const closeDeleteModal = () => {
      showDeleteModal.value = false
      transactionToDelete.value = null
    }

    const saveTransaction = async () => {
      if (!formData.value.transaction_id || !formData.value.initiator || !formData.value.result_desc) {
        alert('Please fill in all required fields!')
        return
      }

      saveLoading.value = true

      try {
        const endpoint = formData.value.id 
          ? `suapi/transactions/${formData.value.id}/`
          : 'suapi/transactions/'
        
        const method = formData.value.id ? 'put' : 'post'
        
        const data = await makeRequest(method, endpoint, formData.value)
        
        if (formData.value.id) {
          // Update existing transaction
          const index = transactions.value.findIndex(t => t.id === formData.value.id)
          if (index !== -1) {
            transactions.value[index] = { ...data }
          }
        } else {
          // Create new transaction
          transactions.value.unshift(data)
        }
        
        showFormModal.value = false
        console.log('Transaction saved successfully!')
      } catch (error) {
        console.error('Error saving transaction:', error)
        alert('Error saving transaction: ' + (error.response?.data?.error || error.message))
      } finally {
        saveLoading.value = false
      }
    }

    const confirmDelete = async () => {
      if (!transactionToDelete.value) return

      deleteLoading.value = true

      try {
        await makeRequest('delete', `suapi/transactions/${transactionToDelete.value.id}/`)
        
        transactions.value = transactions.value.filter(t => t.id !== transactionToDelete.value.id)
        showDeleteModal.value = false
        transactionToDelete.value = null
        console.log('Transaction deleted successfully!')
      } catch (error) {
        console.error('Error deleting transaction:', error)
        alert('Error deleting transaction: ' + (error.response?.data?.error || error.message))
      } finally {
        deleteLoading.value = false
      }
    }

    const exportToCSV = () => {
      const csvContent = "data:text/csv;charset=utf-8," 
        + ["Transaction ID,Initiator,Amount,Status,Description,Time"]
        .concat(filteredTransactions.value.map(t => 
          `"${t.transaction_id}","${t.initiator}",${t.amount},"${formatStatus(t.result_code)}","${t.result_desc}","${t.transaction_time}"`
        ))
        .join("\n")
      
      const encodedUri = encodeURI(csvContent)
      const link = document.createElement("a")
      link.setAttribute("href", encodedUri)
      link.setAttribute("download", `transactions_export_${new Date().toISOString().split('T')[0]}.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    // API Methods
    const fetchTransactions = async () => {
      try {
        const data = await makeRequest('get', 'suapi/transactions/')
        transactions.value = data.transactions || data
      } catch (error) {
        console.error('Error fetching transactions:', error)
        throw error
      }
    }

    const fetchAllData = async () => {
      try {
        await fetchTransactions()
      } catch (error) {
        console.error('Error fetching transaction data:', error)
        throw error
      }
    }

    const refreshData = () => {
      fetchAllData()
    }

    // Initialize data
    onMounted(async () => {
      await fetchAllData()
    })

    return {
      loading,
      error,
      transactions,
      searchTerm,
      showFormModal,
      showDeleteModal,
      transactionToDelete,
      currentPage,
      itemsPerPage,
      saveLoading,
      deleteLoading,
      formData,
      stats,
      filteredTransactions,
      totalPages,
      startIndex,
      endIndex,
      paginatedTransactions,
      statusChartSeries,
      statusChartOptions,
      amountChartSeries,
      amountChartOptions,
      formatNumber,
      formatDate,
      formatStatus,
      getStatusBadgeClass,
      handleSearch,
      clearSearch,
      handleItemsPerPageChange,
      nextPage,
      previousPage,
      openCreateForm,
      openEditForm,
      closeFormModal,
      openDeleteConfirm,
      closeDeleteModal,
      saveTransaction,
      confirmDelete,
      exportToCSV,
      fetchAllData,
      refreshData
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(241, 245, 249, 0.5);
}

::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.3);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.5);
}
</style>