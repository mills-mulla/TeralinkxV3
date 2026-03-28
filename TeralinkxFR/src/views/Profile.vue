<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-800 pt-16">
    <NavBar @toggleMenu="$emit('toggleMenu')" @logout="$emit('logout')" />
    
    <div class="sm:max-w-md md:max-w-lg lg:max-xl mx-auto px-2 mt-1 mb-8">
      <!-- Page Header -->
      <header class="mb-8 transform transition-all duration-500 animate-fade-in">
        <div class="flex items-center space-x-3 mb-2">
          <div class="p-2 bg-blue-500 rounded-lg transition-all duration-300 hover:bg-blue-600 hover:scale-110 hover:rotate-3">
            <svg class="w-6 h-6 text-white transition-transform duration-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
          <div class="transition-all duration-300 hover:translate-x-1">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Profile Settings</h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 transition-colors duration-300">Manage your account information and preferences</p>
          </div>
        </div>
      </header>

      <!-- Profile Content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Profile Overview Card -->
        <div class="lg:col-span-1 transform transition-all duration-500 animate-slide-in-left">
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 transform transition-all duration-300 hover:shadow-lg hover:scale-[1.02]">
            <div class="flex flex-col items-center space-y-4">
              <!-- Profile Image -->
              <div class="relative group">
                <div class="w-24 h-24 rounded-full overflow-hidden border-4 border-blue-500 shadow-lg transition-all duration-300 group-hover:border-blue-600 group-hover:shadow-xl">
                  <img
                    v-if="user.profileImage"
                    :src="user.profileImage"
                    :alt="user.displayName"
                    class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                  />
                  <div
                    v-else
                    class="w-full h-full bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-gray-700 dark:to-gray-600 flex items-center justify-center transition-all duration-300 group-hover:from-blue-200 group-hover:to-indigo-200"
                  >
                    <svg class="w-12 h-12 text-blue-600 dark:text-blue-400 transition-transform duration-300 group-hover:scale-110" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                  </div>
                </div>
                
                <!-- Upload Button -->
                <label class="absolute -bottom-2 -right-2 bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-full cursor-pointer shadow-lg transition-all duration-300 hover:scale-110 hover:shadow-xl transform">
                  <svg class="w-4 h-4 transition-transform duration-200 hover:rotate-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  <input type="file" accept="image/*" @change="handleImageUpload" class="hidden" />
                </label>
              </div>

              <!-- User Info -->
              <div class="text-center space-y-2">
                <h2 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">{{ user.displayName }}</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400 transition-colors duration-300">{{ user.phone }}</p>
                <p class="text-xs text-gray-500 transition-colors duration-300">{{ user.accountNumber }}</p>
                <span :class="statusClasses" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium transition-all duration-300 hover:scale-105">
                  {{ user.status }}
                </span>
              </div>

              <!-- Quick Stats -->
              <div class="w-full pt-4 border-t border-gray-200 dark:border-gray-700 transition-colors duration-300">
                <div class="grid grid-cols-3 lg:flex lg:flex-col gap-4 text-center">
                  <div class="group cursor-pointer">
                    <div class="flex items-center justify-center space-x-1 mb-1">
                      <svg class="w-4 h-4" :class="balanceColor" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.16z"/>
                      </svg>
                      <p class="text-lg font-semibold transition-all duration-300 group-hover:scale-110" :class="balanceColor">KSh {{ formatCurrency(user.balance) }}</p>
                    </div>
                    <p class="text-xs text-gray-500 dark:text-gray-400 transition-colors duration-300">Balance</p>
                  </div>
                  <div class="group cursor-pointer">
                    <div class="flex items-center justify-center space-x-1 mb-1">
                      <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
                      </svg>
                      <p class="text-lg font-semibold text-blue-600 dark:text-blue-400 transition-all duration-300 group-hover:scale-110">{{ formatBytes(totalDataUsed) }}</p>
                    </div>
                    <p class="text-xs text-gray-500 dark:text-gray-400 transition-colors duration-300">Data Used</p>
                  </div>
                  <div class="group cursor-pointer">
                    <div class="flex items-center justify-center space-x-1 mb-1">
                      <svg class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M4 6h18V4H4c-1.1 0-2 .9-2 2v11H0v3h14v-3H4V6zm19 2h-6c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h6c.55 0 1-.45 1-1V9c0-.55-.45-1-1-1zm-1 9h-4v-7h4v7z"/>
                      </svg>
                      <p class="text-lg font-semibold text-purple-600 dark:text-purple-400 transition-all duration-300 group-hover:scale-110">{{ activeDevicesCount }}</p>
                    </div>
                    <p class="text-xs text-gray-500 dark:text-gray-400 transition-colors duration-300">Devices</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6 transform transition-all duration-700 animate-slide-in-right">
          <!-- Personal Information -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 transform transition-all duration-300 hover:shadow-lg animate-fade-in-up" style="animation-delay: 0.2s">
            <div class="flex items-center space-x-3 mb-4 group">
              <div class="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg transition-all duration-300 group-hover:bg-blue-200 dark:group-hover:bg-blue-800/30">
                <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 transition-transform duration-300 group-hover:scale-110" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
              <div class="transition-transform duration-300 group-hover:translate-x-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white transition-colors duration-300">Personal Information</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 transition-colors duration-300">Update your personal details</p>
              </div>
            </div>
            
            <div class="space-y-4">
              <div class="group">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 transition-colors duration-300 group-focus-within:text-blue-600">Display Name</label>
                <input
                  v-model="editedDisplayName"
                  @input="debouncedUpdate('display_name', $event.target.value)"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 transition-all duration-300 hover:border-blue-400 focus:border-transparent transform focus:scale-[1.01]"
                />
              </div>
              
              <div class="group">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 transition-colors duration-300">Phone Number</label>
                <input
                  :value="user.phone"
                  type="tel"
                  readonly
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-500 cursor-not-allowed transition-all duration-300"
                />
              </div>
            </div>
          </div>

          <!-- Security Settings -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 transform transition-all duration-300 hover:shadow-lg animate-fade-in-up" style="animation-delay: 0.4s">
            <div class="flex items-center space-x-3 mb-4 group">
              <div class="p-2 bg-red-100 dark:bg-red-900/20 rounded-lg transition-all duration-300 group-hover:bg-red-200 dark:group-hover:bg-red-800/30">
                <svg class="w-5 h-5 text-red-600 dark:text-red-400 transition-transform duration-300 group-hover:scale-110" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11H16V16H8V11H9.2V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.4,8.7 10.4,10V11H13.6V10C13.6,8.7 12.8,8.2 12,8.2Z"/>
                </svg>
              </div>
              <div class="transition-transform duration-300 group-hover:translate-x-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white transition-colors duration-300">Security Settings</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 transition-colors duration-300">Manage your account security</p>
              </div>
            </div>
            
            <div class="space-y-4">
              <div class="group">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 transition-colors duration-300 group-focus-within:text-blue-600">New Password</label>
                <input
                  v-model="newPassword"
                  type="password"
                  placeholder="Enter new password"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 transition-all duration-300 hover:border-blue-400 focus:border-transparent transform focus:scale-[1.01]"
                />
                <button
                  v-if="newPassword"
                  @click="updatePassword"
                  class="mt-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-all duration-300 hover:scale-105 hover:shadow-lg transform"
                >
                  Update Password
                </button>
              </div>
              
              <div class="flex items-center justify-between group">
                <div class="transition-transform duration-300 group-hover:translate-x-1">
                  <h4 class="text-sm font-medium text-gray-900 dark:text-white transition-colors duration-300">Two-Factor Authentication</h4>
                  <p class="text-xs text-gray-600 dark:text-gray-400 transition-colors duration-300">Add extra security to your account</p>
                </div>
                <button
                  @click="toggle2FA"
                  :class="user.twoFactorEnabled ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'"
                  class="relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-300 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  <span
                    :class="user.twoFactorEnabled ? 'translate-x-6' : 'translate-x-1'"
                    class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-300"
                  />
                </button>
              </div>
            </div>
          </div>

          <!-- Data Usage Statistics -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center space-x-3 mb-4">
              <div class="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M16,11V3H8V9H2V21H22V11H16M10,5H14V9H10V5M4,11H6V19H4V11M8,11H10V19H8V11M12,11H14V19H12V11M16,11H18V19H16V11M20,11V19H20V11Z"/>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Usage Statistics</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">Your data consumption overview</p>
              </div>
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="text-center">
                <p class="text-lg font-bold text-blue-600 dark:text-blue-400">{{ formatBytes(dailyUsage) }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-300">Today</p>
              </div>
              <div class="text-center">
                <p class="text-lg font-bold text-green-600 dark:text-green-400">{{ formatBytes(weeklyUsage) }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-300">Week</p>
              </div>
              <div class="text-center">
                <p class="text-lg font-bold text-purple-600 dark:text-purple-400">{{ formatBytes(monthlyUsage) }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-300">Month</p>
              </div>
              <div class="text-center">
                <p class="text-lg font-bold text-orange-600 dark:text-orange-400">{{ formatBytes(totalDataUsed) }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-300">Total</p>
              </div>
            </div>
          </div>

          <!-- Device Management -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 ">
            <div class="flex items-center space-x-3 mb-4">
              <div class="p-2 bg-indigo-100 dark:bg-indigo-900/20 rounded-lg">
                <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M4 6h18V4H4c-1.1 0-2 .9-2 2v11H0v3h14v-3H4V6zm19 2h-6c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h6c.55 0 1-.45 1-1V9c0-.55-.45-1-1-1zm-1 9h-4v-7h4v7z"/>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Connected Devices</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">Manage your authorized devices</p>
              </div>
            </div>
            
            <div class="space-y-3">
              <div v-for="device in devices" :key="device.id" class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="p-2 bg-indigo-100 dark:bg-indigo-900/20 rounded-full">
                    <svg class="w-4 h-4 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 24 24">
                      <path v-if="device.device_type === 'phone'" d="M7 2a2 2 0 00-2 2v16a2 2 0 002 2h10a2 2 0 002-2V4a2 2 0 00-2-2H7z"/>
                      <path v-else-if="device.device_type === 'laptop'" d="M4 5a2 2 0 00-2 2v8h20V7a2 2 0 00-2-2H4z"/>
                      <path v-else d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/>
                    </svg>
                  </div>
                  
                  <div>
                    <div class="flex items-center space-x-2">
                      <input
                        v-if="device.isEditing"
                        v-model="device.editName"
                        @keyup.enter="saveDeviceName(device)"
                        @keyup.escape="cancelEditDevice(device)"
                        class="text-sm font-medium px-2 py-1 border rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                      <p v-else class="text-sm font-medium text-gray-900 dark:text-white">{{ device.device_name }}</p>
                      
                      <button
                        v-if="!device.isEditing"
                        @click="startEditDevice(device)"
                        class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      >
                        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z"/>
                        </svg>
                      </button>
                    </div>
                    <p class="text-xs text-gray-600 dark:text-gray-400">{{ device.device_manufacturer }} • {{ formatDate(device.last_seen) }}</p>
                  </div>
                </div>

                <div class="flex items-center space-x-2">
                  <span :class="getDeviceStatusClasses(device.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ device.status }}
                  </span>
                  
                  <div class="relative">
                    <button @click="toggleDeviceMenu(device.id)" class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
                      </svg>
                    </button>

                    <div v-if="device.showMenu" class="absolute right-0 mt-1 w-32 bg-white dark:bg-gray-800 rounded-md shadow-lg z-10 border">
                      <button
                        v-if="device.status === 'active'"
                        @click="blockDevice(device)"
                        class="w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                      >
                        Block Device
                      </button>
                      <button
                        v-else
                        @click="unblockDevice(device)"
                        class="w-full px-3 py-2 text-left text-sm text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20"
                      >
                        Unblock Device
                      </button>
                      <button
                        @click="trustDevice(device)"
                        class="w-full px-3 py-2 text-left text-sm text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20"
                      >
                        {{ device.is_trusted ? 'Remove Trust' : 'Trust Device' }}
                      </button>
                      <button
                        @click="removeDevice(device)"
                        class="w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                      >
                        Remove Device
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Empty State -->
              <div v-if="!devices.length" class="text-center py-8">
                <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
                <p class="text-gray-500 dark:text-gray-400">No devices found</p>
                <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">Devices will appear here when you sign in</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Save Status -->
      <div v-if="saving" class="fixed bottom-4 right-4 bg-white dark:bg-gray-800 border rounded-lg shadow-lg p-4 flex items-center space-x-3 z-50">
        <div class="animate-spin">
          <svg class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <span class="text-sm font-medium text-gray-900 dark:text-white">Saving changes...</span>
      </div>
    </div>

    <fooTr />

    <!-- Advanced Image Crop Modal -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div v-if="showCropModal" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[95vh] overflow-hidden transform transition-all duration-300">
          <!-- Header -->
          <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-xl font-bold text-gray-800 dark:text-white transition-colors duration-300">Crop Profile Image</h3>
            <button @click="cancelCrop" class="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200 hover:scale-110">
              <svg class="w-6 h-6 transition-transform duration-200 hover:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          
          <div class="p-6 space-y-6">
            <!-- Crop Controls -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="space-y-2 group">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors duration-300 group-hover:text-blue-600">Aspect Ratio</label>
                <select v-model="cropSettings.aspectRatio" class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-all duration-300 hover:border-blue-400 focus:ring-2 focus:ring-blue-500">
                  <option value="1:1">Square (1:1)</option>
                  <option value="4:3">Standard (4:3)</option>
                  <option value="16:9">Wide (16:9)</option>
                  <option value="free">Free Form</option>
                </select>
              </div>
              
              <div class="space-y-2 group">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors duration-300 group-hover:text-blue-600">Zoom</label>
                <input v-model.number="cropSettings.zoom" type="range" min="0.5" max="3" step="0.1" class="w-full transition-all duration-300 hover:scale-105">
              </div>
              
              <div class="space-y-2 group">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors duration-300 group-hover:text-blue-600">Quality</label>
                <select v-model="cropSettings.quality" class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-all duration-300 hover:border-blue-400 focus:ring-2 focus:ring-blue-500">
                  <option value="0.9">High (90%)</option>
                  <option value="0.8">Medium (80%)</option>
                  <option value="0.7">Low (70%)</option>
                </select>
              </div>
              
              <div class="space-y-2 group">
                <label class="text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors duration-300 group-hover:text-blue-600">Grid</label>
                <button @click="cropSettings.showGrid = !cropSettings.showGrid" :class="cropSettings.showGrid ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'" class="w-full px-3 py-2 text-sm rounded-lg font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg">
                  {{ cropSettings.showGrid ? 'Hide Grid' : 'Show Grid' }}
                </button>
              </div>
            </div>
            
            <!-- Crop Area -->
            <div class="relative bg-gray-100 dark:bg-gray-700 rounded-xl overflow-hidden border-2 border-dashed border-gray-300 dark:border-gray-600 transition-all duration-300 hover:border-blue-400">
              <canvas
                ref="cropCanvas"
                @mousedown="startCrop"
                @mousemove="updateCrop"
                @mouseup="endCrop"
                @mouseleave="endCrop"
                @touchstart="startCrop"
                @touchmove="updateCrop"
                @touchend="endCrop"
                width="600"
                height="400"
                class="w-full h-full cursor-crosshair touch-none transition-transform duration-200 hover:scale-[1.01]"
              />
              
              <!-- Crop Info -->
              <div class="absolute top-4 left-4 bg-black bg-opacity-75 text-white px-3 py-2 rounded-lg text-sm transition-all duration-300 hover:bg-opacity-90">
                <div>{{ Math.round(cropData.width) }} × {{ Math.round(cropData.height) }}px</div>
                <div class="text-xs opacity-75">{{ cropSettings.aspectRatio }} • {{ Math.round(cropSettings.zoom * 100) }}%</div>
              </div>
            </div>
            
            <!-- Preview -->
            <div class="flex items-center space-x-4">
              <div class="text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors duration-300">Preview:</div>
              <div class="w-16 h-16 rounded-full overflow-hidden border-2 border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-700 transition-all duration-300 hover:scale-110 hover:border-blue-400">
                <canvas ref="previewCanvas" width="64" height="64" class="w-full h-full"/>
              </div>
              <div class="flex-1 text-sm text-gray-500 dark:text-gray-400 transition-colors duration-300">
                This is how your profile image will appear
              </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="flex space-x-3">
              <button @click="resetCrop" class="flex-1 px-4 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg transform">
                Reset
              </button>
              <button @click="applyCrop" class="flex-1 px-4 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg transform">
                Apply & Save
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import { useToast } from '@/composables/useToast'
import NavBar from '@/components/NavBar.vue'
import fooTr from '@/components/Footer.vue'

// Composables
const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const { showSuccess, showError } = useToast()

// State
const loading = ref(false)
const saving = ref(false)
const editedDisplayName = ref('')
const newPassword = ref('')
const devices = ref([])
const totalDataUsed = ref(0)
const dailyUsage = ref(0)
const weeklyUsage = ref(0)
const monthlyUsage = ref(0)

// Image cropping state
const showCropModal = ref(false)
const selectedImageFile = ref(null)
const cropCanvas = ref(null)
const previewCanvas = ref(null)
const originalImage = ref(null)
const cropData = ref({ x: 50, y: 50, width: 200, height: 200 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const cropSettings = ref({
  aspectRatio: '1:1',
  zoom: 1,
  rotation: 0,
  quality: 0.9,
  showGrid: true
})

// Computed
const user = computed(() => ({
  displayName: dashboardStore.clientName || authStore.user?.client?.display_name || 'User',
  phone: authStore.user?.phone || dashboardStore.phoneNumber || '',
  accountNumber: dashboardStore.account || authStore.user?.client?.account || '',
  profileImage: dashboardStore.userImage || authStore.user?.client?.profile_image,
  status: dashboardStore.status || authStore.user?.client?.status || 'active',
  twoFactorEnabled: authStore.user?.client?.two_factor_enabled || false,
  balance: dashboardStore.balance || 0,
  createdAt: authStore.user?.date_joined
}))

const activeDevicesCount = computed(() => {
  return devices.value.filter(d => d.status === 'active').length
})

const balanceColor = computed(() => {
  const bal = user.value.balance
  if (bal >= 30) return 'text-green-600 dark:text-green-400'
  if (bal >= 10) return 'text-orange-600 dark:text-orange-400'
  return 'text-red-600 dark:text-red-400'
})

const statusClasses = computed(() => {
  const status = user.value.status
  return {
    'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400': status === 'active',
    'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': status === 'suspended',
    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400': status === 'pending'
  }
})

// Methods
const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedImageFile.value = file
    showCropModal.value = true
    
    // Load image for cropping
    const reader = new FileReader()
    reader.onload = (e) => {
      originalImage.value = new Image()
      originalImage.value.onload = () => {
        setTimeout(() => initializeCrop(), 100)
      }
      originalImage.value.src = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const uploadImage = async (file) => {
  try {
    saving.value = true
    const formData = new FormData()
    formData.append('profile_image', file)

    const headers = { ...authStore.authHeaders }
    delete headers['Content-Type']

    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/profile/image/`, {
      method: 'POST',
      headers,
      body: formData
    })

    if (response.status === 200) {
      showSuccess('Profile image updated!')
      await refreshData()
    } else {
      throw new Error('Failed to update image')
    }
  } catch (error) {
    showError('Failed to update profile image')
  } finally {
    saving.value = false
  }
}

let updateTimeout = null
const debouncedUpdate = (field, value) => {
  if (updateTimeout) clearTimeout(updateTimeout)
  updateTimeout = setTimeout(() => {
    updateField(field, value)
  }, 1000)
}

const updateField = async (field, value) => {
  try {
    saving.value = true
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/profile/update/`, {
      method: 'PATCH',
      headers: {
        ...authStore.authHeaders,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ [field]: value })
    })

    if (response.status === 200) {
      showSuccess(`${field.replace('_', ' ')} updated successfully!`)
      await refreshData()
    } else {
      throw new Error(`Failed to update ${field}`)
    }
  } catch (error) {
    showError(`Failed to update ${field.replace('_', ' ')}`)
  } finally {
    saving.value = false
  }
}

const updatePassword = async () => {
  if (!newPassword.value) return
  
  await updateField('password', newPassword.value)
  newPassword.value = ''
}

const toggle2FA = async () => {
  await updateField('two_factor_enabled', !user.value.twoFactorEnabled)
}

const refreshData = async () => {
  await Promise.all([
    authStore.initialize(),
    dashboardStore.fetchDashboardData()
  ])
}

// Device management methods
const loadDevices = async () => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/devices/`, {
      headers: authStore.authHeaders
    })
    
    if (response.status === 200) {
      const data = response.data
      devices.value = data.map(device => ({
        ...device,
        showMenu: false,
        isEditing: false,
        editName: device.device_name
      }))
    }
  } catch (error) {
    console.error('Failed to load devices:', error)
  }
}

const toggleDeviceMenu = (deviceId) => {
  devices.value.forEach(device => {
    if (device.id === deviceId) {
      device.showMenu = !device.showMenu
    } else {
      device.showMenu = false
    }
  })
}

const startEditDevice = (device) => {
  device.isEditing = true
  device.editName = device.device_name
  device.showMenu = false
}

const saveDeviceName = async (device) => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/devices/${device.id}/update/`, {
      method: 'PATCH',
      headers: {
        ...authStore.authHeaders,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ device_name: device.editName })
    })
    
    if (response.status === 200) {
      device.device_name = device.editName
      device.isEditing = false
      showSuccess('Device name updated successfully!')
    } else {
      throw new Error('Failed to update device name')
    }
  } catch (error) {
    showError('Failed to update device name')
  }
}

const cancelEditDevice = (device) => {
  device.isEditing = false
  device.editName = device.device_name
}

const blockDevice = async (device) => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/devices/${device.id}/block/`, {
      method: 'POST',
      headers: authStore.authHeaders
    })
    
    if (response.status === 200) {
      device.status = 'suspended'
      device.showMenu = false
      showSuccess('Device blocked successfully!')
    }
  } catch (error) {
    showError('Failed to block device')
  }
}

const unblockDevice = async (device) => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/devices/${device.id}/unblock/`, {
      method: 'POST',
      headers: authStore.authHeaders
    })
    
    if (response.status === 200) {
      device.status = 'active'
      device.showMenu = false
      showSuccess('Device unblocked successfully!')
    }
  } catch (error) {
    showError('Failed to unblock device')
  }
}

const trustDevice = async (device) => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/devices/${device.id}/trust/`, {
      method: 'POST',
      headers: {
        ...authStore.authHeaders,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ is_trusted: !device.is_trusted })
    })
    
    if (response.status === 200) {
      device.is_trusted = !device.is_trusted
      device.showMenu = false
      showSuccess(`Device ${device.is_trusted ? 'trusted' : 'untrusted'} successfully!`)
    }
  } catch (error) {
    showError('Failed to update device trust')
  }
}

const removeDevice = async (device) => {
  if (!confirm(`Are you sure you want to remove ${device.device_name}?`)) return
  
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/devices/${device.id}/remove/`, {
      method: 'DELETE',
      headers: authStore.authHeaders
    })
    
    if (response.status === 200) {
      devices.value = devices.value.filter(d => d.id !== device.id)
      showSuccess('Device removed successfully!')
    }
  } catch (error) {
    showError('Failed to remove device')
  }
}

const getDeviceStatusClasses = (status) => {
  return {
    'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400': status === 'active',
    'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': status === 'suspended',
    'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400': status === 'inactive'
  }
}

// Utility functions
const formatBytes = (bytes) => {
  const num = Number(bytes) || 0
  if (num === 0) return '0 B'
  if (num < 1024) return num + ' B'
  if (num < 1024 * 1024) return (num / 1024).toFixed(1) + ' KB'
  if (num < 1024 * 1024 * 1024) return (num / (1024 * 1024)).toFixed(1) + ' MB'
  return (num / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatMemberDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long'
  })
}

// Image cropping methods
const initializeCrop = () => {
  if (!cropCanvas.value || !originalImage.value) return
  
  const canvas = cropCanvas.value
  const ctx = canvas.getContext('2d')
  const img = originalImage.value
  
  canvas.width = 600
  canvas.height = 400
  
  const scale = Math.min(canvas.width / img.width, canvas.height / img.height) * 0.8
  const scaledWidth = img.width * scale
  const scaledHeight = img.height * scale
  const offsetX = (canvas.width - scaledWidth) / 2
  const offsetY = (canvas.height - scaledHeight) / 2
  
  const cropSize = Math.min(scaledWidth, scaledHeight) * 0.8
  cropData.value = {
    x: offsetX + (scaledWidth - cropSize) / 2,
    y: offsetY + (scaledHeight - cropSize) / 2,
    width: cropSize,
    height: cropSize,
    imageOffsetX: offsetX,
    imageOffsetY: offsetY,
    imageWidth: scaledWidth,
    imageHeight: scaledHeight,
    scale: scale
  }
  
  drawCropOverlay()
  updatePreview()
}

const drawCropOverlay = () => {
  if (!cropCanvas.value || !originalImage.value) return
  
  const canvas = cropCanvas.value
  const ctx = canvas.getContext('2d')
  const img = originalImage.value
  const crop = cropData.value
  
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(img, crop.imageOffsetX, crop.imageOffsetY, crop.imageWidth, crop.imageHeight)
  
  // Overlay
  ctx.fillStyle = 'rgba(0, 0, 0, 0.6)'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  
  // Clear crop area
  ctx.clearRect(crop.x, crop.y, crop.width, crop.height)
  
  // Redraw image in crop area
  const sx = (crop.x - crop.imageOffsetX) / crop.scale
  const sy = (crop.y - crop.imageOffsetY) / crop.scale
  const sw = crop.width / crop.scale
  const sh = crop.height / crop.scale
  
  ctx.drawImage(img, sx, sy, sw, sh, crop.x, crop.y, crop.width, crop.height)
  
  // Crop border
  ctx.strokeStyle = '#3b82f6'
  ctx.lineWidth = 2
  ctx.strokeRect(crop.x, crop.y, crop.width, crop.height)
  
  // Grid if enabled
  if (cropSettings.value.showGrid) {
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)'
    ctx.lineWidth = 1
    
    for (let i = 1; i < 3; i++) {
      const x = crop.x + (crop.width / 3) * i
      ctx.beginPath()
      ctx.moveTo(x, crop.y)
      ctx.lineTo(x, crop.y + crop.height)
      ctx.stroke()
    }
    
    for (let i = 1; i < 3; i++) {
      const y = crop.y + (crop.height / 3) * i
      ctx.beginPath()
      ctx.moveTo(crop.x, y)
      ctx.lineTo(crop.x + crop.width, y)
      ctx.stroke()
    }
  }
}

const updatePreview = () => {
  if (!previewCanvas.value || !originalImage.value) return
  
  const canvas = previewCanvas.value
  const ctx = canvas.getContext('2d')
  const img = originalImage.value
  const crop = cropData.value
  
  canvas.width = 64
  canvas.height = 64
  
  ctx.clearRect(0, 0, 64, 64)
  
  // Circular clip
  ctx.beginPath()
  ctx.arc(32, 32, 32, 0, 2 * Math.PI)
  ctx.clip()
  
  const sx = (crop.x - crop.imageOffsetX) / crop.scale
  const sy = (crop.y - crop.imageOffsetY) / crop.scale
  const sw = crop.width / crop.scale
  const sh = crop.height / crop.scale
  
  ctx.drawImage(img, sx, sy, sw, sh, 0, 0, 64, 64)
}

const startCrop = (event) => {
  event.preventDefault()
  isDragging.value = true
  const rect = cropCanvas.value.getBoundingClientRect()
  const x = (event.clientX || event.touches?.[0]?.clientX) - rect.left
  const y = (event.clientY || event.touches?.[0]?.clientY) - rect.top
  dragStart.value = { x: x - cropData.value.x, y: y - cropData.value.y }
}

const updateCrop = (event) => {
  if (!isDragging.value) return
  event.preventDefault()
  
  const rect = cropCanvas.value.getBoundingClientRect()
  const x = (event.clientX || event.touches?.[0]?.clientX) - rect.left
  const y = (event.clientY || event.touches?.[0]?.clientY) - rect.top
  
  cropData.value.x = Math.max(cropData.value.imageOffsetX, 
    Math.min(x - dragStart.value.x, cropData.value.imageOffsetX + cropData.value.imageWidth - cropData.value.width))
  cropData.value.y = Math.max(cropData.value.imageOffsetY,
    Math.min(y - dragStart.value.y, cropData.value.imageOffsetY + cropData.value.imageHeight - cropData.value.height))
  
  drawCropOverlay()
  updatePreview()
}

const endCrop = () => {
  isDragging.value = false
}

const resetCrop = () => {
  cropSettings.value = {
    aspectRatio: '1:1',
    zoom: 1,
    rotation: 0,
    quality: 0.9,
    showGrid: true
  }
  initializeCrop()
}

const applyCrop = () => {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  const crop = cropData.value
  
  canvas.width = 400
  canvas.height = 400
  
  const sx = (crop.x - crop.imageOffsetX) / crop.scale
  const sy = (crop.y - crop.imageOffsetY) / crop.scale
  const sw = crop.width / crop.scale
  const sh = crop.height / crop.scale
  
  ctx.drawImage(originalImage.value, sx, sy, sw, sh, 0, 0, 400, 400)
  
  canvas.toBlob(async (blob) => {
    const file = new File([blob], 'profile.jpg', { type: 'image/jpeg' })
    showCropModal.value = false
    await uploadImage(file)
  }, 'image/jpeg', cropSettings.value.quality)
}

const cancelCrop = () => {
  showCropModal.value = false
  selectedImageFile.value = null
  originalImage.value = null
}

const initializeProfile = async () => {
  try {
    loading.value = true
    await refreshData()
    await loadDevices()
    
    // Initialize form data
    editedDisplayName.value = user.value.displayName
    
    // Load usage statistics (mock data for now)
    totalDataUsed.value = Math.floor(Math.random() * 10000000000) // 10GB max
    dailyUsage.value = Math.floor(Math.random() * 500000000) // 500MB max
    weeklyUsage.value = dailyUsage.value * 7
    monthlyUsage.value = weeklyUsage.value * 4
  } catch (error) {
    showError('Failed to load profile data')
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  initializeProfile()
})
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-in-left {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slide-in-right {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out;
}

.animate-slide-in-left {
  animation: slide-in-left 0.8s ease-out;
}

.animate-slide-in-right {
  animation: slide-in-right 0.8s ease-out;
}

.animate-fade-in-up {
  animation: fade-in-up 0.6s ease-out;
  animation-fill-mode: both;
}
</style>