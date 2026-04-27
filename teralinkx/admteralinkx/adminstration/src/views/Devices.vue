<template>
  <div class="space-y-4 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Devices</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Monitor and manage user devices</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAddModal" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Device
        </button>
        <button @click="refreshData" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
          <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-rose-600 dark:text-rose-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <div>
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load devices</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchDevices" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metric Pills -->
    <div class="flex items-center gap-2 flex-wrap">
      <div class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-xl">
        <span class="text-[10px] text-blue-600 dark:text-blue-400 font-medium">Total</span>
        <span class="text-sm font-bold text-blue-700 dark:text-blue-300">{{ stats.total_devices || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl">
        <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">Active</span>
        <span class="text-sm font-bold text-emerald-700 dark:text-emerald-300">{{ stats.active_devices || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-cyan-50 dark:bg-cyan-500/10 border border-cyan-200 dark:border-cyan-500/20 rounded-xl">
        <div class="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-pulse"></div>
        <span class="text-[10px] text-cyan-600 dark:text-cyan-400 font-medium">Online</span>
        <span class="text-sm font-bold text-cyan-700 dark:text-cyan-300">{{ stats.online_devices || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-purple-50 dark:bg-purple-500/10 border border-purple-200 dark:border-purple-500/20 rounded-xl">
        <span class="text-[10px] text-purple-600 dark:text-purple-400 font-medium">Trusted</span>
        <span class="text-sm font-bold text-purple-700 dark:text-purple-300">{{ stats.trusted_devices || 0 }}</span>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="space-y-3 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2 flex-wrap">
        <div class="flex-1 min-w-48">
          <input v-model="searchTerm" type="text" placeholder="Search MAC, name, model, account..." class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="blocked">Blocked</option>
        </select>
        <select v-model="typeFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Types</option>
          <option value="phone">Phone</option>
          <option value="laptop">Laptop</option>
          <option value="tablet">Tablet</option>
          <option value="desktop">Desktop</option>
        </select>
        <select v-model="trustedFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Trust</option>
          <option value="true">Trusted</option>
          <option value="false">Untrusted</option>
        </select>
      </div>

      <!-- Bulk Actions -->
      <div v-if="selectedIds.length" class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 rounded-lg">
        <span class="text-xs text-blue-700 dark:text-blue-400 font-medium">{{ selectedIds.length }} selected</span>
        <button @click="bulkAction('trust')" class="px-2 py-1 text-[10px] font-medium rounded bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400 hover:bg-purple-200">✅ Trust</button>
        <button @click="bulkAction('untrust')" class="px-2 py-1 text-[10px] font-medium rounded bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200">❌ Untrust</button>
        <button @click="bulkAction('block')" class="px-2 py-1 text-[10px] font-medium rounded bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400 hover:bg-red-200">🚫 Block</button>
        <button @click="bulkAction('unblock')" class="px-2 py-1 text-[10px] font-medium rounded bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-200">✅ Unblock</button>
        <button @click="selectedIds = []" class="ml-auto text-[10px] text-slate-500 hover:text-slate-700">Clear</button>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 w-6"><input type="checkbox" @change="toggleSelectAll" :checked="selectedIds.length === filteredDevices.length && filteredDevices.length > 0" class="rounded" /></th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">MAC Address</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Device Name</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Owner</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Type</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Platform</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Trusted</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Online</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Voucher</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Connections</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Last Seen</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="device in filteredDevices" :key="device.id" @click="openEditModal(device)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2" @click.stop><input type="checkbox" :value="device.id" v-model="selectedIds" class="rounded" /></td>
                <td class="px-3 py-2 text-xs font-mono text-slate-900 dark:text-white">{{ device.mac_address }}</td>
                <td class="px-3 py-2"><p class="text-xs font-medium text-slate-900 dark:text-white">{{ device.device_name || 'Unknown' }}</p><p class="text-[10px] text-slate-500">{{ device.device_model || '' }}</p></td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ device.user_account || 'N/A' }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300">{{ device.device_type || 'unknown' }}</span></td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400">{{ device.device_platform || 'N/A' }}</span></td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] rounded-full" :class="getStatusBadge(device.status)">{{ device.status }}</span></td>
                <td class="px-3 py-2"><span v-if="device.is_trusted" class="text-[10px] text-purple-600 dark:text-purple-400 font-medium">✓ Trusted</span><span v-else class="text-[10px] text-slate-400">-</span></td>
                <td class="px-3 py-2"><span class="flex items-center gap-1 text-xs" :class="device.is_online ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'"><span class="w-1.5 h-1.5 rounded-full" :class="device.is_online ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'"></span>{{ device.is_online ? 'Online' : 'Offline' }}</span></td>
                <td class="px-3 py-2"><span v-if="device.has_active_voucher" class="px-1.5 py-0.5 text-[10px] rounded-full bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400">✓</span><span v-else class="text-[10px] text-slate-400">-</span></td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ device.total_connections || 0 }}</td>
                <td class="px-3 py-2 text-xs text-slate-500 dark:text-slate-400">{{ formatDate(device.last_seen) }}</td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button v-if="device.status !== 'blocked'" @click.stop="blockDevice(device)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded" title="Block">
                      <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/></svg>
                    </button>
                    <button v-else @click.stop="unblockDevice(device)" class="p-1 hover:bg-emerald-100 dark:hover:bg-emerald-600 rounded" title="Unblock">
                      <svg class="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    </button>
                    <button @click.stop="openDeleteModal(device)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded" title="Delete">
                      <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit Device Modal -->
    <div v-if="showFormModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[88vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700 shrink-0">
          <div>
            <h2 class="text-sm font-semibold text-slate-900 dark:text-white">{{ selectedDevice?.device_name || formData.device_name || 'New Device' }}</h2>
            <p class="text-[10px] text-slate-500 dark:text-slate-400 font-mono">{{ selectedDevice?.mac_address || formData.mac_address || '' }} · {{ selectedDevice?.user_account || '' }}</p>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="selectedDevice?.id" class="px-2 py-0.5 text-[10px] rounded-full" :class="getStatusBadge(selectedDevice.status)">{{ selectedDevice.status }}</span>
            <button @click="closeFormModal" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"><svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></button>
          </div>
        </div>
        <!-- Body -->
        <div class="flex flex-1 overflow-hidden">
          <!-- Sidebar -->
          <div class="w-44 shrink-0 border-r border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 overflow-y-auto p-3 space-y-1">
            <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide px-1 mb-1">Sections</p>
            <button v-for="s in deviceSections" :key="s.id" @click="activeDeviceSection=s.id"
              class="w-full text-left px-2.5 py-2 text-xs rounded-lg transition-colors"
              :class="activeDeviceSection===s.id ? 'bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 font-medium' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'">
              {{ s.label }}
            </button>
            <div v-if="selectedDevice?.id" class="pt-2 mt-2 border-t border-slate-200 dark:border-slate-700 space-y-1">
              <button @click="blockDevice(selectedDevice)" v-if="selectedDevice.status!=='blocked'" class="w-full text-left px-2.5 py-2 text-xs rounded-lg bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400 hover:bg-red-100">🚫 Block</button>
              <button @click="unblockDevice(selectedDevice)" v-else class="w-full text-left px-2.5 py-2 text-xs rounded-lg bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-100">✅ Unblock</button>
            </div>
          </div>
          <!-- Right panel -->
          <div class="flex-1 overflow-y-auto p-4 space-y-3">

            <!-- 1. Device -->
            <div v-show="activeDeviceSection==='device'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="dOpen.device=!dOpen.device" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Device</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="dOpen.device?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="dOpen.device" class="p-4 grid grid-cols-2 gap-3">
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">MAC Address</label><input v-model="formData.mac_address" type="text" placeholder="00:11:22:33:44:55" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-mono" /></div>
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Device Name</label><input v-model="formData.device_name" type="text" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Type</label>
                  <select v-model="formData.device_type" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option value="phone">Phone</option><option value="laptop">Laptop</option><option value="tablet">Tablet</option><option value="desktop">Desktop</option><option value="router">Router</option>
                  </select>
                </div>
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Platform</label>
                  <select v-model="formData.device_platform" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option value="windows">Windows</option><option value="macos">macOS</option><option value="linux">Linux</option><option value="android">Android</option><option value="ios">iOS</option>
                  </select>
                </div>
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Model</label><input v-model="formData.device_model" type="text" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Manufacturer</label><input v-model="formData.manufacturer" type="text" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
              </div>
            </div>

            <!-- 2. Config -->
            <div v-show="activeDeviceSection==='config'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="dOpen.config=!dOpen.config" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Config</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="dOpen.config?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="dOpen.config" class="p-4 grid grid-cols-2 gap-3">
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Status</label>
                  <select v-model="formData.status" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white">
                    <option value="active">Active</option><option value="inactive">Inactive</option><option value="blocked">Blocked</option>
                  </select>
                </div>
                <div><label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Max Sessions</label><input v-model="formData.max_concurrent_sessions" type="number" class="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white" /></div>
                <div><label class="flex items-center gap-2 cursor-pointer mt-1"><input v-model="formData.is_trusted" type="checkbox" class="w-4 h-4 text-blue-600 rounded" /><span class="text-xs text-slate-700 dark:text-slate-300">Trusted</span></label></div>
                <div><label class="flex items-center gap-2 cursor-pointer mt-1"><input v-model="formData.auto_connect" type="checkbox" class="w-4 h-4 text-blue-600 rounded" /><span class="text-xs text-slate-700 dark:text-slate-300">Auto Connect</span></label></div>
              </div>
            </div>

            <!-- 3. Location -->
            <div v-show="activeDeviceSection==='location'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="dOpen.location=!dOpen.location" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Location</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="dOpen.location?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="dOpen.location" class="p-4 grid grid-cols-2 gap-3 text-xs">
                <div><span class="text-slate-500">Last Seen Location</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ selectedDevice?.last_seen_location_name || 'N/A' }}</p></div>
                <div><span class="text-slate-500">Favourite Location</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ selectedDevice?.favorite_location_name || 'N/A' }}</p></div>
              </div>
            </div>

            <!-- 4. Activity -->
            <div v-show="activeDeviceSection==='activity'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="dOpen.activity=!dOpen.activity" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Activity</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="dOpen.activity?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="dOpen.activity" class="p-4 grid grid-cols-2 gap-3 text-xs">
                <div><span class="text-slate-500">Last Seen</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ formatDate(selectedDevice?.last_seen) }}</p></div>
                <div><span class="text-slate-500">Total Connections</span><p class="font-bold text-blue-600 dark:text-blue-400 mt-0.5">{{ selectedDevice?.total_connections || 0 }}</p></div>
                <div><span class="text-slate-500">Online Now</span><p class="font-medium mt-0.5" :class="selectedDevice?.is_online ? 'text-emerald-600' : 'text-slate-400'">{{ selectedDevice?.is_online ? '✓ Online' : 'Offline' }}</p></div>
                <div><span class="text-slate-500">Session Limit</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ selectedDevice?.max_concurrent_sessions || 'N/A' }}</p></div>
              </div>
            </div>

            <!-- 5. Vouchers -->
            <div v-show="activeDeviceSection==='vouchers'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="dOpen.vouchers=!dOpen.vouchers" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Vouchers</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="dOpen.vouchers?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="dOpen.vouchers" class="p-4 text-xs">
                <div v-if="selectedDevice?.has_active_voucher" class="p-3 bg-purple-50 dark:bg-purple-500/10 rounded-lg">
                  <p class="text-purple-600 dark:text-purple-400 font-medium">✓ Active Voucher</p>
                  <p class="text-slate-700 dark:text-slate-300 mt-1 font-mono">{{ selectedDevice?.active_voucher_session || 'N/A' }}</p>
                </div>
                <p v-else class="text-slate-400">No active voucher</p>
              </div>
            </div>

            <!-- 6. History -->
            <div v-show="activeDeviceSection==='history'" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button @click="dOpen.history=!dOpen.history" class="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">History</span>
                <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="dOpen.history?'rotate-180':''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-show="dOpen.history" class="p-4 text-xs space-y-3">
                <div><span class="text-slate-500">Previous Owners</span><p class="font-medium text-slate-900 dark:text-white mt-0.5">{{ selectedDevice?.previous_owners?.length ? selectedDevice.previous_owners.join(', ') : 'None' }}</p></div>
                <div v-if="selectedDevice?.device_identification">
                  <span class="text-slate-500">Device Identification</span>
                  <pre class="text-[10px] bg-slate-50 dark:bg-slate-900 rounded-lg p-2 mt-1 overflow-x-auto text-slate-700 dark:text-slate-300">{{ JSON.stringify(selectedDevice.device_identification, null, 2) }}</pre>
                </div>
              </div>
            </div>

          </div>
        </div>
        <div class="flex items-center justify-end gap-2 px-5 py-3 border-t border-slate-200 dark:border-slate-700 shrink-0">
          <button @click="closeFormModal" class="px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
          <button @click="saveDevice" :disabled="saveLoading" class="px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg" :class="{'opacity-50':saveLoading}">{{ saveLoading ? 'Saving...' : (selectedDevice?.id ? 'Update' : 'Create') }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <ConfirmDialog :show="showDeleteModal" title="Delete Device" :message="`Delete device ${deviceToDelete?.device_name}?`" type="danger" @confirm="confirmDelete" @cancel="closeDeleteModal" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useOptimistic } from '../composables/useOptimistic'
import ModernMetricCard from '../components/MetricCard.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export default {
  name: 'Devices',
  components: { ModernMetricCard, ConfirmDialog },
  setup() {
    const { loading, error, makeRequest, invalidateCache } = useApi()
    const devices = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const statusFilter = ref('')
    const typeFilter = ref('')
    const trustedFilter = ref('')
    const selectedIds = ref([])

    const toggleSelectAll = (e) => {
      selectedIds.value = e.target.checked ? filteredDevices.value.map(d => d.id) : []
    }

    const bulkAction = async (action) => {
      if (!selectedIds.value.length) return
      try {
        const endpoint = action === 'block' ? 'block' : action === 'unblock' ? 'unblock' : null
        if (endpoint) {
          await Promise.all(selectedIds.value.map(id => makeRequest('post', `suapi/devices/${id}/${endpoint}/`, { reason: 'Bulk admin action' })))
        } else if (action === 'trust') {
          await Promise.all(selectedIds.value.map(id => makeRequest('patch', `suapi/devices/${id}/`, { is_trusted: true })))
        } else if (action === 'untrust') {
          await Promise.all(selectedIds.value.map(id => makeRequest('patch', `suapi/devices/${id}/`, { is_trusted: false })))
        }
        selectedIds.value = []
        await refreshData()
      } catch (e) { console.error(e) }
    }

    const formatDate = (d) => d ? new Date(d).toLocaleDateString() : 'N/A'
    const showFormModal = ref(false)
    const activeDeviceSection = ref('device')
    const dOpen = { device: true, config: true, location: false, activity: false, vouchers: false, history: false }
    const deviceSections = [
      { id: 'device',   label: '📱 Device' },
      { id: 'config',   label: '⚙️ Config' },
      { id: 'location', label: '📍 Location' },
      { id: 'activity', label: '📊 Activity' },
      { id: 'vouchers', label: '🎫 Vouchers' },
      { id: 'history',  label: '📜 History' },
    ]
    const showDeleteModal = ref(false)
    const selectedDevice = ref(null)
    const deviceToDelete = ref(null)
    const saveLoading = ref(false)
    const deleteLoading = ref(false)
    const formData = ref({
      mac_address: '',
      device_name: '',
      device_type: 'phone',
      device_platform: 'android',
      status: 'active',
      is_trusted: false
    })

    const filteredDevices = computed(() => {
      let result = devices.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(d => d.mac_address?.toLowerCase().includes(term) || d.device_name?.toLowerCase().includes(term) || d.user_account?.toLowerCase().includes(term) || d.device_model?.toLowerCase().includes(term))
      }
      if (statusFilter.value) result = result.filter(d => d.status === statusFilter.value)
      if (typeFilter.value) result = result.filter(d => d.device_type === typeFilter.value)
      if (trustedFilter.value) result = result.filter(d => d.is_trusted === (trustedFilter.value === 'true'))
      return result
    })

    const fetchDevices = async () => {
      try {
        const data = await makeRequest('get', 'suapi/devices/')
        devices.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/devices/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchDevices(), fetchStats()])
    const { optimisticRemove, optimisticUpdate } = useOptimistic(devices, fetchDevices, invalidateCache, 'suapi/devices')
    
    const openAddModal = () => {
      selectedDevice.value = null
      formData.value = {
        mac_address: '',
        device_name: '',
        device_type: 'phone',
        device_platform: 'android',
        status: 'active',
        is_trusted: false
      }
      showFormModal.value = true
    }
    
    const openEditModal = (device) => {
      selectedDevice.value = device
      activeDeviceSection.value = 'device'
      formData.value = {
        mac_address: device.mac_address || '',
        device_name: device.device_name || '',
        device_type: device.device_type || 'phone',
        device_platform: device.device_platform || 'android',
        device_model: device.device_model || '',
        manufacturer: device.manufacturer || '',
        status: device.status || 'active',
        is_trusted: device.is_trusted || false,
        auto_connect: device.auto_connect || false,
        max_concurrent_sessions: device.max_concurrent_sessions || 1
      }
      showFormModal.value = true
    }

    const closeFormModal = () => {
      showFormModal.value = false
      selectedDevice.value = null
      formData.value = { mac_address: '', device_name: '', device_type: 'phone', device_platform: 'android', device_model: '', manufacturer: '', status: 'active', is_trusted: false, auto_connect: false, max_concurrent_sessions: 1 }
    }

    const saveDevice = async () => {
      saveLoading.value = true
      try {
        if (selectedDevice.value?.id) {
          await makeRequest('patch', `suapi/devices/${selectedDevice.value.id}/`, formData.value)
        } else {
          await makeRequest('post', 'suapi/devices/', formData.value)
        }
        await refreshData()
        closeFormModal()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        saveLoading.value = false
      }
    }

    const blockDevice = async (device) => {
      optimisticUpdate(device.id, { status: 'blocked' })
      try {
        await makeRequest('post', `suapi/devices/${device.id}/block/`, { reason: 'Admin action' })
      } catch (err) {
        await refreshData() // rollback
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    const unblockDevice = async (device) => {
      optimisticUpdate(device.id, { status: 'active' })
      try {
        await makeRequest('post', `suapi/devices/${device.id}/unblock/`, { reason: 'Admin action' })
      } catch (err) {
        await refreshData() // rollback
        alert('Error: ' + (err.response?.data?.error || err.message))
      }
    }

    const openDeleteModal = (device) => { deviceToDelete.value = device; showDeleteModal.value = true }
    const closeDeleteModal = () => { showDeleteModal.value = false; deviceToDelete.value = null }

    const confirmDelete = async () => {
      deleteLoading.value = true
      const id = deviceToDelete.value.id
      optimisticRemove(id)
      closeDeleteModal()
      try {
        await makeRequest('delete', `suapi/devices/${id}/`)
      } catch (err) {
        await refreshData() // rollback
        alert('Error: ' + (err.response?.data?.error || err.message))
      } finally {
        deleteLoading.value = false
      }
    }

    const getStatusBadge = (status) => {
      const badges = {
        'active': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'inactive': 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400',
        'suspended': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400'
      }
      return badges[status] || badges.inactive
    }

    onMounted(refreshData)

    return {
      loading, error, devices, stats, searchTerm, statusFilter, typeFilter, trustedFilter,
      selectedIds, toggleSelectAll, bulkAction, formatDate,
      activeDeviceSection, dOpen, deviceSections,
      showFormModal, showDeleteModal, selectedDevice, deviceToDelete,
      saveLoading, deleteLoading, formData, filteredDevices, fetchDevices, refreshData,
      openAddModal, openEditModal, closeFormModal, saveDevice, blockDevice, unblockDevice, openDeleteModal, closeDeleteModal, confirmDelete, getStatusBadge
    }
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

.animate-slide-up {
  animation: slide-up 0.4s ease-out;
}
</style>
