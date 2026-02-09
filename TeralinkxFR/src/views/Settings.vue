<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-800 pt-16">
    <NavBar @toggleMenu="$emit('toggleMenu')" @logout="$emit('logout')" />
    
    <div class="sm:max-w-md md:max-w-lg lg:max-w-4xl mx-auto px-4 mt-4 mb-8">
      <!-- Page Header -->
      <header class="mb-8 transform transition-all duration-500 animate-fade-in">
        <div class="flex items-center space-x-3 mb-2">
          <div class="p-2 bg-purple-500 rounded-lg transition-all duration-300 hover:bg-purple-600 hover:scale-110 hover:rotate-3">
            <svg class="w-6 h-6 text-white transition-transform duration-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11.03L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.22,8.95 2.27,9.22 2.46,9.37L4.57,11.03C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.22,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.68 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"/>
            </svg>
          </div>
          <div class="transition-all duration-300 hover:translate-x-1">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Account Settings</h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 transition-colors duration-300">Customize your account preferences and security</p>
          </div>
        </div>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Settings Navigation -->
        <div class="lg:col-span-1">
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 sticky top-20">
            <nav class="space-y-2">
              <button
                v-for="section in settingSections"
                :key="section.id"
                @click="activeSection = section.id"
                :disabled="section.id === 'account'"
                :class="[
                  'w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-all duration-200',
                  section.id === 'account'
                    ? 'opacity-50 cursor-not-allowed text-gray-400 dark:text-gray-500'
                    : activeSection === section.id
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                ]"
              >
                <component :is="section.icon" class="w-5 h-5" />
                <span class="font-medium">{{ section.name }}</span>
              </button>
            </nav>
          </div>
        </div>

        <!-- Settings Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Appearance Settings -->
          <div v-if="activeSection === 'appearance'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <div class="flex items-center space-x-3 mb-6">
              <div class="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 18.5A6.5 6.5 0 1 1 18.5 12A6.51 6.51 0 0 1 12 18.5zM12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2z"/>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Appearance</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">Customize your visual experience</p>
              </div>
            </div>
            
            <div class="space-y-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Theme</label>
                <div class="grid grid-cols-3 gap-3">
                  <button
                    v-for="theme in themes"
                    :key="theme.value"
                    @click="setTheme(theme.value)"
                    :class="[
                      'p-4 rounded-lg border-2 transition-all duration-200 hover:scale-105',
                      currentTheme === theme.value
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                    ]"
                  >
                    <div class="flex flex-col items-center space-y-2">
                      <component :is="theme.icon" class="w-6 h-6" :class="theme.color" />
                      <span class="text-sm font-medium text-gray-900 dark:text-white">{{ theme.name }}</span>
                    </div>
                  </button>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Language</label>
                <select v-model="selectedLanguage" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="en">English</option>
                  <option value="sw">Swahili</option>
                  <option value="fr">French</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Notifications Settings -->
          <div v-if="activeSection === 'notifications'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <div class="flex items-center space-x-3 mb-6">
              <div class="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
                <svg class="w-5 h-5 text-yellow-600 dark:text-yellow-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,18.5C9.5,18.5 7.5,16.5 7.5,14H16.5C16.5,16.5 14.5,18.5 12,18.5M12,2A2,2 0 0,1 14,4V5.5A6,6 0 0,1 18,11.5V16H6V11.5A6,6 0 0,1 10,5.5V4A2,2 0 0,1 12,2Z"/>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Notifications</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">Manage your notification preferences</p>
              </div>
            </div>
            
            <div class="space-y-4">
              <div v-for="notification in notificationSettings" :key="notification.id" class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <h4 class="font-medium text-gray-900 dark:text-white">{{ notification.title }}</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">{{ notification.description }}</p>
                </div>
                <button
                  @click="toggleNotification(notification.id)"
                  :class="[
                    'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                    notification.enabled ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
                  ]"
                >
                  <span
                    :class="[
                      'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                      notification.enabled ? 'translate-x-6' : 'translate-x-1'
                    ]"
                  />
                </button>
              </div>
            </div>
          </div>

          <!-- Privacy & Security Settings -->
          <div v-if="activeSection === 'privacy'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <div class="flex items-center space-x-3 mb-6">
              <div class="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M10,17L6,13L7.41,11.59L10,14.17L16.59,7.58L18,9L10,17Z"/>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Privacy & Security</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">Control your privacy and security settings</p>
              </div>
            </div>
            
            <div class="space-y-6">
              <div class="space-y-4">
                <div v-for="privacy in privacySettings" :key="privacy.id" class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <div class="flex items-center space-x-3">
                    <component :is="privacy.icon" class="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    <div>
                      <h4 class="font-medium text-gray-900 dark:text-white">{{ privacy.title }}</h4>
                      <p class="text-sm text-gray-600 dark:text-gray-400">{{ privacy.description }}</p>
                    </div>
                  </div>
                  <button
                    @click="togglePrivacy(privacy.id)"
                    :class="[
                      'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                      privacy.enabled ? 'bg-green-600' : 'bg-gray-200 dark:bg-gray-700'
                    ]"
                  >
                    <span
                      :class="[
                        'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                        privacy.enabled ? 'translate-x-6' : 'translate-x-1'
                      ]"
                    />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Data & Usage Settings -->
          <div v-if="activeSection === 'data'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <div class="flex items-center space-x-3 mb-6">
              <div class="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M16,11V3H8V9H2V21H22V11H16M10,5H14V9H10V5M4,11H6V19H4V11M8,11H10V19H8V11M12,11H14V19H12V11M16,11H18V19H16V11M20,11V19H20V11Z"/>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Data & Usage</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">Manage your data usage preferences</p>
              </div>
            </div>
            
            <div class="space-y-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Data Usage Alerts</label>
                <div class="space-y-3">
                  <div class="flex items-center justify-between">
                    <span class="text-sm text-gray-600 dark:text-gray-400">Alert at 80% usage</span>
                    <input type="checkbox" v-model="dataAlerts.eightyPercent" class="rounded" />
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-sm text-gray-600 dark:text-gray-400">Alert at 90% usage</span>
                    <input type="checkbox" v-model="dataAlerts.ninetyPercent" class="rounded" />
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-sm text-gray-600 dark:text-gray-400">Daily usage summary</span>
                    <input type="checkbox" v-model="dataAlerts.dailySummary" class="rounded" />
                  </div>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Auto-renewal</label>
                <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <div class="flex items-center justify-between mb-2">
                    <span class="font-medium text-gray-900 dark:text-white">Enable Auto-renewal</span>
                    <button
                      @click="autoRenewal = !autoRenewal"
                      :class="[
                        'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                        autoRenewal ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
                      ]"
                    >
                      <span
                        :class="[
                          'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                          autoRenewal ? 'translate-x-6' : 'translate-x-1'
                        ]"
                      />
                    </button>
                  </div>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Automatically renew your package when it expires</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Support & Help Settings -->
          <div v-if="activeSection === 'support'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <div class="flex items-center space-x-3 mb-6">
              <div class="p-2 bg-indigo-100 dark:bg-indigo-900/20 rounded-lg">
                <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,17A1.5,1.5 0 0,1 10.5,15.5A1.5,1.5 0 0,1 12,14A1.5,1.5 0 0,1 13.5,15.5A1.5,1.5 0 0,1 12,17M12,10.5C12.8,10.5 13.5,9.8 13.5,9C13.5,8.2 12.8,7.5 12,7.5C11.2,7.5 10.5,8.2 10.5,9C10.5,9.8 11.2,10.5 12,10.5Z"/>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Support & Help</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">Get help and contact support</p>
              </div>
            </div>
            
            <div class="space-y-4">
              <router-link to="/user-guide" class="w-full flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                  </svg>
                  <div class="text-left">
                    <h4 class="font-medium text-gray-900 dark:text-white">User Guide & Tutorials</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Complete guide to using TeralinkX</p>
                  </div>
                </div>
                <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"/>
                </svg>
              </router-link>
              
              <router-link to="/faq" class="w-full flex items-center justify-between p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-orange-600 dark:text-orange-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,17A1.5,1.5 0 0,1 10.5,15.5A1.5,1.5 0 0,1 12,14A1.5,1.5 0 0,1 13.5,15.5A1.5,1.5 0 0,1 12,17M12,10.5C12.8,10.5 13.5,9.8 13.5,9C13.5,8.2 12.8,7.5 12,7.5C11.2,7.5 10.5,8.2 10.5,9C10.5,9.8 11.2,10.5 12,10.5Z"/>
                  </svg>
                  <div class="text-left">
                    <h4 class="font-medium text-gray-900 dark:text-white">FAQ & Common Questions</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Find answers to frequently asked questions</p>
                  </div>
                </div>
                <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"/>
                </svg>
              </router-link>
              
              <router-link to="/service-policy" class="w-full flex items-center justify-between p-4 bg-red-50 dark:bg-red-900/20 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                  </svg>
                  <div class="text-left">
                    <h4 class="font-medium text-gray-900 dark:text-white">Service Policy & Terms</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Terms of service and privacy policy</p>
                  </div>
                </div>
                <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"/>
                </svg>
              </router-link>
              
              <button class="w-full flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4C22,2.89 21.1,2 20,2Z"/>
                  </svg>
                  <div class="text-left">
                    <h4 class="font-medium text-gray-900 dark:text-white">Live Chat Support</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Chat with our support team</p>
                  </div>
                </div>
                <span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">Online</span>
              </button>
              
              <button class="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12,15C12.81,15 13.5,14.7 14.11,14.11C14.7,13.5 15,12.81 15,12C15,11.19 14.7,10.5 14.11,9.89C13.5,9.3 12.81,9 12,9C11.19,9 10.5,9.3 9.89,9.89C9.3,10.5 9,11.19 9,12C9,12.81 9.3,13.5 9.89,14.11C10.5,14.7 11.19,15 12,15M12,2C14.21,2 16.21,2.81 17.78,4.39C19.36,5.96 20.17,7.96 20.17,10.17C20.17,12.38 19.36,14.38 17.78,15.95L12,21.5L6.22,15.95C4.64,14.38 3.83,12.38 3.83,10.17C3.83,7.96 4.64,5.96 6.22,4.39C7.79,2.81 9.79,2 12,2Z"/>
                  </svg>
                  <div class="text-left">
                    <h4 class="font-medium text-gray-900 dark:text-white">Find Service Centers</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Locate nearby service centers</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- Account Management -->
          <div v-if="activeSection === 'account'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in opacity-50">
            <div class="flex items-center space-x-3 mb-6">
              <div class="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-500">Account Management</h3>
                <p class="text-sm text-gray-400">Contact support for account changes</p>
              </div>
            </div>
            
            <div class="space-y-4">
              <div class="p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg border border-gray-200 dark:border-gray-600">
                <div class="flex items-center space-x-2 mb-2">
                  <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M13,14H11V10H13M13,18H11V16H13M1,21H23L12,2L1,21Z"/>
                  </svg>
                  <h4 class="font-medium text-gray-500">Restricted Access</h4>
                </div>
                <p class="text-sm text-gray-400 mb-3">Account management features are restricted for security purposes. Please contact our support team for assistance with account changes.</p>
              </div>
              
              <button disabled class="w-full flex items-center justify-between p-4 bg-gray-100 dark:bg-gray-700/30 rounded-lg cursor-not-allowed opacity-60">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                  </svg>
                  <div class="text-left">
                    <h4 class="font-medium text-gray-500">Export Account Data</h4>
                    <p class="text-sm text-gray-400">Contact support to request data export</p>
                  </div>
                </div>
              </button>
              
              <button disabled class="w-full flex items-center justify-between p-4 bg-gray-100 dark:bg-gray-700/30 rounded-lg cursor-not-allowed opacity-60">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9Z"/>
                  </svg>
                  <div class="text-left">
                    <h4 class="font-medium text-gray-500">Deactivate Account</h4>
                    <p class="text-sm text-gray-400">Contact support for account deactivation</p>
                  </div>
                </div>
              </button>
              
              <button disabled class="w-full flex items-center justify-between p-4 bg-gray-100 dark:bg-gray-700/30 rounded-lg cursor-not-allowed opacity-60">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"/>
                  </svg>
                  <div class="text-left">
                    <h4 class="font-medium text-gray-500">Delete Account</h4>
                    <p class="text-sm text-gray-400">Contact support for account deletion</p>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <div class="mt-8 flex justify-end">
        <button
          @click="saveSettings"
          :disabled="saving"
          class="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg transform flex items-center space-x-2"
        >
          <svg v-if="saving" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ saving ? 'Saving...' : 'Save Changes' }}</span>
        </button>
      </div>
    </div>

    <fooTr />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import NavBar from '@/components/NavBar.vue'
import fooTr from '@/components/Footer.vue'

const { showSuccess, showError } = useToast()

// State
const activeSection = ref('appearance')
const saving = ref(false)
const currentTheme = ref(localStorage.getItem('theme') || 'light')
const selectedLanguage = ref('en')
const autoRenewal = ref(false)

// Setting sections
const settingSections = [
  {
    id: 'appearance',
    name: 'Appearance',
    icon: 'svg'
  },
  {
    id: 'notifications',
    name: 'Notifications',
    icon: 'svg'
  },
  {
    id: 'privacy',
    name: 'Privacy & Security',
    icon: 'svg'
  },
  {
    id: 'data',
    name: 'Data & Usage',
    icon: 'svg'
  },
  {
    id: 'support',
    name: 'Support & Help',
    icon: 'svg'
  },
  {
    id: 'account',
    name: 'Account',
    icon: 'svg'
  }
]

// Theme options
const themes = [
  {
    value: 'light',
    name: 'Light',
    icon: 'svg',
    color: 'text-yellow-500'
  },
  {
    value: 'dark',
    name: 'Dark',
    icon: 'svg',
    color: 'text-gray-700'
  },
  {
    value: 'auto',
    name: 'Auto',
    icon: 'svg',
    color: 'text-blue-500'
  }
]

// Notification settings
const notificationSettings = ref([
  {
    id: 'dataUsage',
    title: 'Data Usage Alerts',
    description: 'Get notified when you reach data limits',
    enabled: true
  },
  {
    id: 'packageExpiry',
    title: 'Package Expiry',
    description: 'Alerts before your package expires',
    enabled: true
  },
  {
    id: 'newDevices',
    title: 'New Device Login',
    description: 'Notify when a new device connects',
    enabled: false
  },
  {
    id: 'promotions',
    title: 'Promotions & Offers',
    description: 'Receive promotional notifications',
    enabled: false
  }
])

// Privacy settings
const privacySettings = ref([
  {
    id: 'analytics',
    title: 'Usage Analytics',
    description: 'Help improve our service with anonymous usage data',
    enabled: true,
    icon: 'svg'
  },
  {
    id: 'location',
    title: 'Location Services',
    description: 'Allow location-based features and services',
    enabled: false,
    icon: 'svg'
  },
  {
    id: 'marketing',
    title: 'Marketing Communications',
    description: 'Receive marketing emails and SMS',
    enabled: false,
    icon: 'svg'
  }
])

// Data alerts
const dataAlerts = ref({
  eightyPercent: true,
  ninetyPercent: true,
  dailySummary: false
})

// Methods
const setTheme = (mode) => {
  currentTheme.value = mode
  const root = document.documentElement
  
  if (mode === 'dark') {
    root.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else if (mode === 'light') {
    root.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  } else {
    // Auto mode - check system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem('theme', 'auto')
  }
}

const toggleNotification = (id) => {
  const notification = notificationSettings.value.find(n => n.id === id)
  if (notification) {
    notification.enabled = !notification.enabled
  }
}

const togglePrivacy = (id) => {
  const privacy = privacySettings.value.find(p => p.id === id)
  if (privacy) {
    privacy.enabled = !privacy.enabled
  }
}

const saveSettings = async () => {
  try {
    saving.value = true
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const settings = {
      theme: currentTheme.value,
      language: selectedLanguage.value,
      notifications: notificationSettings.value,
      privacy: privacySettings.value,
      dataAlerts: dataAlerts.value,
      autoRenewal: autoRenewal.value
    }
    
    // Here you would typically send to your API
    console.log('Saving settings:', settings)
    
    showSuccess('Settings saved successfully!')
  } catch (error) {
    showError('Failed to save settings. Please try again.')
  } finally {
    saving.value = false
  }
}

// Initialize theme on mount
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    setTheme(savedTheme)
  }
})
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>