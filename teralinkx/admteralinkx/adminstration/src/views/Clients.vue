<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-600 bg-clip-text text-transparent mb-2">
            👥 Client Management
          </h1>
          <p class="text-slate-600 font-light">Manage and monitor client accounts and profiles</p>
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
            <h3 class="text-rose-800 font-semibold">Failed to load client data</h3>
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
        <p class="mt-4 text-slate-500 font-light">Loading client data...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="!loading" class="space-y-8">
      <!-- Quick Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <ModernMetricCard
          title="Total Clients"
          :value="stats.totalClients"
          trend="up"
          trendValue="12.5%"
          icon="👥"
          color="blue"
          :formatted="true"
        />
        
        <ModernMetricCard
          title="Active Clients"
          :value="stats.activeClients"
          trend="up"
          trendValue="8.2%"
          icon="🟢"
          color="emerald"
          :formatted="true"
        />
        
        <ModernMetricCard
          title="Total Balance"
          :value="`KSh ${formatNumber(stats.totalBalance)}`"
          trend="up"
          trendValue="18.7%"
          icon="💰"
          color="amber"
          :formatted="false"
        />
        
        <ModernMetricCard
          title="Inactive Clients"
          :value="stats.inactiveClients"
          trend="down"
          trendValue="2.1%"
          icon="⏸️"
          color="rose"
          :formatted="true"
        />
      </div>

      <!-- Search and Actions -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div class="flex-1">
            <div class="relative">
              <MagnifyingGlassIcon class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                v-model="searchTerm"
                type="text"
                placeholder="Search by account, IP, voucher, status, username, email..."
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
              <span>Add Client</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Clients Table -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-200/60">
          <h3 class="text-lg font-semibold text-slate-800 flex items-center">
            <TableCellsIcon class="w-5 h-5 text-slate-600 mr-2" />
            Client Records ({{ filteredClients.length }} found)
          </h3>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 border-b border-slate-200/60">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Account</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Username</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Tier</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Points</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Balance</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Status</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200/60">
              <tr 
                v-for="client in paginatedClients" 
                :key="client.id"
                class="hover:bg-slate-50 transition-colors duration-200"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{{ client.account }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{{ client.username || client.user?.username || 'N/A' }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getTierBadgeClass(client.reward_tier)" class="px-2 py-1 text-xs font-medium rounded-full">
                    {{ getTierEmoji(client.reward_tier) }} {{ formatTier(client.reward_tier) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600 font-medium">
                  🏆 {{ formatNumber(client.reward_points || 0) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600 font-medium">
                  KSh {{ formatNumber(client.balance || 0) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getStatusBadgeClass(client.status)" class="px-2 py-1 text-xs font-medium rounded-full">
                    {{ formatStatus(client.status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex space-x-2">
                    <button
                      @click="openEditForm(client)"
                      class="text-blue-600 hover:text-blue-800 transition-colors duration-200 p-1 rounded"
                      title="Edit Client"
                    >
                      <PencilSquareIcon class="w-4 h-4" />
                    </button>
                    <button
                      @click="openDeleteConfirm(client)"
                      class="text-rose-600 hover:text-rose-800 transition-colors duration-200 p-1 rounded"
                      title="Delete Client"
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
        <div v-if="filteredClients.length === 0" class="text-center py-12">
          <div class="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <UserGroupIcon class="w-8 h-8 text-slate-400" />
          </div>
          <h3 class="text-lg font-semibold text-slate-600 mb-2">No clients found</h3>
          <p class="text-slate-500 mb-4">No clients match your search criteria.</p>
          <button
            @click="clearSearch"
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            Clear search and try again
          </button>
        </div>

        <!-- Pagination -->
        <div v-if="filteredClients.length > 0" class="px-6 py-4 border-t border-slate-200/60 flex items-center justify-between">
          <div class="text-sm text-slate-600">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredClients.length }} entries
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
    </div>

    <!-- Client Form Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-slate-200/60">
          <h3 class="text-xl font-semibold text-slate-800 flex items-center">
            {{ formData.id ? '✏️ Edit Client' : '➕ Add New Client' }}
          </h3>
        </div>
        
        <div class="p-6">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Profile Image Section -->
            <div class="lg:col-span-1">
              <div class="space-y-4">
                <h4 class="font-semibold text-slate-700 flex items-center">
                  <PhotoIcon class="w-5 h-5 text-slate-600 mr-2" />
                  Profile Image
                </h4>
                
                <div class="border-2 border-dashed border-slate-300 rounded-2xl p-6 text-center hover:border-blue-500 transition-colors duration-300">
                  <div v-if="!previewImage && !formData.image" class="space-y-3">
                    <PhotoIcon class="w-12 h-12 text-slate-400 mx-auto" />
                    <p class="text-sm text-slate-600">Upload profile image</p>
                    <p class="text-xs text-slate-500">JPG, PNG, GIF up to 5MB</p>
                    <input
                      type="file"
                      ref="fileInput"
                      @change="handleImageUpload"
                      accept=".jpg,.jpeg,.png,.gif"
                      class="hidden"
                    />
                    <button
                      @click="$refs.fileInput.click()"
                      class="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors duration-300 text-sm"
                    >
                      Choose File
                    </button>
                  </div>
                  <div v-else class="space-y-3">
                    <img 
                      :src="previewImage || (formData.image ? `data:image/jpeg;base64,${formData.image}` : '')" 
                      alt="Profile preview"
                      class="w-32 h-32 rounded-2xl object-cover mx-auto shadow-lg"
                    />
                    <button
                      @click="removeImage"
                      class="px-3 py-1 bg-rose-100 text-rose-700 rounded-lg hover:bg-rose-200 transition-colors duration-300 text-sm"
                    >
                      Remove Image
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Client Details Form -->
            <div class="lg:col-span-2">
              <h4 class="font-semibold text-slate-700 mb-4 flex items-center">
                <UserCircleIcon class="w-5 h-5 text-slate-600 mr-2" />
                Client Details
              </h4>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Linked User Account *</label>
                  <select
                    v-model="formData.user_id"
                    class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                  >
                    <option value="">Select a user</option>
                    <option v-for="user in userOptions" :key="user.id" :value="user.id">
                      {{ user.username }} ({{ user.email }})
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Account Number *</label>
                  <input
                    v-model="formData.account"
                    type="text"
                    placeholder="Enter unique account identifier"
                    class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Current IP Address</label>
                  <input
                    v-model="formData.current_ip_address"
                    type="text"
                    placeholder="e.g., 192.168.1.100"
                    class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Bound IP Address</label>
                  <input
                    v-model="formData.bound_ip"
                    type="text"
                    placeholder="e.g., 192.168.1.100"
                    class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Active Voucher</label>
                  <input
                    v-model="formData.active_voucher"
                    type="text"
                    placeholder="Enter voucher code"
                    class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Account Status *</label>
                  <select
                    v-model="formData.status"
                    class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="suspended">Suspended</option>
                    <option value="pending">Pending</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Account Balance *</label>
                  <input
                    v-model="formData.balance"
                    type="number"
                    step="0.01"
                    min="0"
                    class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">OTP Code</label>
                  <input
                    v-model="formData.otp"
                    type="text"
                    placeholder="One-time password"
                    class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                  />
                </div>
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
              @click="saveClient"
              :disabled="saveLoading"
              :class="[
                'px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl flex items-center space-x-2',
                saveLoading ? 'opacity-50 cursor-not-allowed' : 'hover:from-blue-500 hover:to-purple-500'
              ]"
            >
              <ArrowPathIcon v-if="saveLoading" class="w-4 h-4 animate-spin" />
              <span>{{ formData.id ? 'Update Client' : 'Create Client' }}</span>
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
          <h3 class="text-lg font-semibold text-slate-800 text-center mb-2">Delete Client</h3>
          <p class="text-slate-600 text-center mb-6">
            Are you sure you want to delete client <strong>"{{ clientToDelete?.account }}"</strong>? This action cannot be undone.
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
import { ref, computed, onMounted } from 'vue'
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
  PhotoIcon,
  UserCircleIcon,
  ExclamationTriangleIcon,
  UserGroupIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'Clients',
  components: {
    ModernMetricCard,
    MagnifyingGlassIcon,
    PlusIcon,
    TableCellsIcon,
    PencilSquareIcon,
    TrashIcon,
    ChevronLeftIcon,
    ChevronRightIcon,
    PhotoIcon,
    UserCircleIcon,
    ExclamationTriangleIcon,
    UserGroupIcon,
    ArrowPathIcon
  },
  setup() {
    const { loading, error, makeRequest } = useApi()
    
    // Reactive data
    const clients = ref([])
    const searchTerm = ref('')
    const showFormModal = ref(false)
    const showDeleteModal = ref(false)
    const clientToDelete = ref(null)
    const currentPage = ref(1)
    const pageSize = 10
    const fileInput = ref(null)
    const previewImage = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)
    
    // Form data
    const formData = ref({
      id: null,
      user_id: null,
      account: '',
      current_ip_address: '',
      active_voucher: '',
      balance: 0,
      status: 'active',
      bound_ip: '',
      otp: '',
      image: null
    })

    // Mock data - replace with actual API calls
    const userOptions = ref([
      { id: 1, username: 'john_doe', email: 'john@example.com' },
      { id: 2, username: 'jane_smith', email: 'jane@example.com' },
      { id: 3, username: 'mike_wilson', email: 'mike@example.com' }
    ])

    // Computed properties
    const stats = computed(() => {
      const totalClients = clients.value.length
      const activeClients = clients.value.filter(c => c.status === 'active').length
      const inactiveClients = totalClients - activeClients
      
      // Fix for Decimal strings like "0.00"
      const totalBalance = clients.value.reduce((sum, client) => {
        if (!client.balance) return sum + 0
        
        // Handle decimal strings like "0.00", "1500.50", etc.
        const balanceStr = String(client.balance).trim()
        
        // Remove any non-numeric characters except decimal point and minus
        const cleanBalance = balanceStr.replace(/[^\d.-]/g, '')
        
        // Parse as float - this will handle "0.00", "1500.50" correctly
        const balanceValue = parseFloat(cleanBalance)
        
        // Return 0 if parsing fails, otherwise the parsed value
        return sum + (isNaN(balanceValue) ? 0 : balanceValue)
      }, 0)

      return {
        totalClients,
        activeClients,
        totalBalance,
        inactiveClients
      }
    })
    const filteredClients = computed(() => {
      if (!searchTerm.value) return clients.value
      
      const term = searchTerm.value.toLowerCase()
      return clients.value.filter(client => 
        client.account?.toLowerCase().includes(term) ||
        client.current_ip_address?.toLowerCase().includes(term) ||
        client.active_voucher?.toLowerCase().includes(term) ||
        client.status?.toLowerCase().includes(term) ||
        client.bound_ip?.toLowerCase().includes(term) ||
        client.otp?.toLowerCase().includes(term) ||
        client.username?.toLowerCase().includes(term) ||
        client.email?.toLowerCase().includes(term)
      )
    })

    const totalPages = computed(() => Math.ceil(filteredClients.value.length / pageSize))
    const startIndex = computed(() => (currentPage.value - 1) * pageSize)
    const endIndex = computed(() => Math.min(startIndex.value + pageSize, filteredClients.value.length))
    const paginatedClients = computed(() => 
      filteredClients.value.slice(startIndex.value, endIndex.value)
    )

    // Methods
    const formatNumber = (num) => {
      return new Intl.NumberFormat().format(num)
    }

    const formatStatus = (status) => {
      const statusMap = {
        active: 'Active',
        inactive: 'Inactive',
        suspended: 'Suspended',
        pending: 'Pending'
      }
      return statusMap[status] || status
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        active: 'bg-emerald-100 text-emerald-800',
        inactive: 'bg-slate-100 text-slate-800',
        suspended: 'bg-rose-100 text-rose-800',
        pending: 'bg-amber-100 text-amber-800'
      }
      return classes[status] || 'bg-slate-100 text-slate-800'
    }

    const getTierBadgeClass = (tier) => {
      const classes = {
        bronze: 'bg-orange-100 text-orange-800',
        silver: 'bg-slate-200 text-slate-800',
        gold: 'bg-yellow-100 text-yellow-800',
        platinum: 'bg-purple-100 text-purple-800'
      }
      return classes[tier] || 'bg-slate-100 text-slate-600'
    }

    const getTierEmoji = (tier) => {
      const emojis = {
        bronze: '🥉',
        silver: '🥈',
        gold: '🥇',
        platinum: '💎'
      }
      return emojis[tier] || '⭐'
    }

    const formatTier = (tier) => {
      if (!tier) return 'Bronze'
      return tier.charAt(0).toUpperCase() + tier.slice(1)
    }

    const handleSearch = () => {
      currentPage.value = 1
    }

    const clearSearch = () => {
      searchTerm.value = ''
      currentPage.value = 1
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
        user_id: null,
        account: '',
        current_ip_address: '',
        active_voucher: '',
        balance: 0,
        status: 'active',
        bound_ip: '',
        otp: '',
        image: null
      }
      previewImage.value = null
      showFormModal.value = true
    }

    const openEditForm = (client) => {
      formData.value = { ...client }
      previewImage.value = null
      showFormModal.value = true
    }

    const closeFormModal = () => {
      showFormModal.value = false
      formData.value = {
        id: null,
        user_id: null,
        account: '',
        current_ip_address: '',
        active_voucher: '',
        balance: 0,
        status: 'active',
        bound_ip: '',
        otp: '',
        image: null
      }
      previewImage.value = null
    }

    const openDeleteConfirm = (client) => {
      clientToDelete.value = client
      showDeleteModal.value = true
    }

    const closeDeleteModal = () => {
      showDeleteModal.value = false
      clientToDelete.value = null
    }

    const handleImageUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          previewImage.value = e.target.result
          // In a real app, you would convert to base64 and store in formData.image
        }
        reader.readAsDataURL(file)
      }
    }

    const removeImage = () => {
      previewImage.value = null
      formData.value.image = null
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    const saveClient = async () => {
      if (!formData.value.account || !formData.value.user_id) {
        alert('Account number and user selection are required fields!')
        return
      }

      saveLoading.value = true

      try {
        const endpoint = formData.value.id 
          ? `suapi/clients/${formData.value.id}/`
          : 'suapi/clients/'
        
        const method = formData.value.id ? 'put' : 'post'
        
        const data = await makeRequest(method, endpoint, formData.value)
        
        if (formData.value.id) {
          // Update existing client
          const index = clients.value.findIndex(c => c.id === formData.value.id)
          if (index !== -1) {
            clients.value[index] = { ...data }
          }
        } else {
          // Create new client
          clients.value.unshift(data)
        }
        
        showFormModal.value = false
        // Show success message (you might want to use a toast notification)
        console.log('Client saved successfully!')
      } catch (error) {
        console.error('Error saving client:', error)
        alert('Error saving client: ' + (error.response?.data?.error || error.message))
      } finally {
        saveLoading.value = false
      }
    }

    const confirmDelete = async () => {
      if (!clientToDelete.value) return

      deleteLoading.value = true

      try {
        await makeRequest('delete', `suapi/clients/${clientToDelete.value.id}/`)
        
        clients.value = clients.value.filter(c => c.id !== clientToDelete.value.id)
        showDeleteModal.value = false
        clientToDelete.value = null
        console.log('Client deleted successfully!')
      } catch (error) {
        console.error('Error deleting client:', error)
        alert('Error deleting client: ' + (error.response?.data?.error || error.message))
      } finally {
        deleteLoading.value = false
      }
    }

    // API Methods
    const fetchClients = async () => {
      try {
        const data = await makeRequest('get', 'suapi/clients/')
        clients.value = data.clients || data
      } catch (error) {
        console.error('Error fetching clients:', error)
        throw error
      }
    }

    const fetchAllData = async () => {
      try {
        await fetchClients()
      } catch (error) {
        console.error('Error fetching client data:', error)
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
      clients,
      searchTerm,
      showFormModal,
      showDeleteModal,
      clientToDelete,
      currentPage,
      fileInput,
      previewImage,
      saveLoading,
      deleteLoading,
      formData,
      userOptions,
      stats,
      filteredClients,
      totalPages,
      startIndex,
      endIndex,
      paginatedClients,
      formatNumber,
      formatStatus,
      getStatusBadgeClass,
      getTierBadgeClass,
      getTierEmoji,
      formatTier,
      handleSearch,
      clearSearch,
      nextPage,
      previousPage,
      openCreateForm,
      openEditForm,
      closeFormModal,
      openDeleteConfirm,
      closeDeleteModal,
      handleImageUpload,
      removeImage,
      saveClient,
      confirmDelete,
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