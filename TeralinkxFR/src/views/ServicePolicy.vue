<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-800 pt-16">
    <NavBar @toggleMenu="$emit('toggleMenu')" @logout="$emit('logout')" />
    
    <div class="sm:max-w-md md:max-w-lg lg:max-w-4xl mx-auto px-4 mt-4 mb-8">
      <!-- Page Header -->
      <header class="mb-8 transform transition-all duration-500 animate-fade-in">
        <div class="flex items-center space-x-3 mb-2">
          <div class="p-2 bg-red-500 rounded-lg transition-all duration-300 hover:bg-red-600 hover:scale-110 hover:rotate-3">
            <svg class="w-6 h-6 text-white transition-transform duration-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
            </svg>
          </div>
          <div class="transition-all duration-300 hover:translate-x-1">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Service Policy</h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 transition-colors duration-300">Terms of service, privacy policy, and usage guidelines</p>
          </div>
        </div>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Navigation Sidebar -->
        <div class="lg:col-span-1">
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 sticky top-20">
            <nav class="space-y-2">
              <button
                v-for="section in policySections"
                :key="section.id"
                @click="activeSection = section.id"
                :class="[
                  'w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-all duration-200 text-sm',
                  activeSection === section.id
                    ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                ]"
              >
                <component :is="section.icon" class="w-4 h-4" />
                <span class="font-medium">{{ section.name }}</span>
              </button>
            </nav>
          </div>
        </div>

        <!-- Content Area -->
        <div class="lg:col-span-3">
          <!-- Terms of Service -->
          <div v-if="activeSection === 'terms'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Terms of Service</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">Last updated: {{ new Date().toLocaleDateString() }}</p>
            
            <div class="space-y-6 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">1. Acceptance of Terms</h3>
                <p>By accessing and using TeralinkX services, you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by the above, please do not use this service.</p>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">2. Service Description</h3>
                <p>TeralinkX provides internet connectivity services through wireless networks. Our services include data packages, device management, and customer support. Service availability may vary by location and network conditions.</p>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">3. Account Registration</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li>You must provide accurate and complete information during registration</li>
                  <li>You are responsible for maintaining the confidentiality of your account credentials</li>
                  <li>You must notify us immediately of any unauthorized use of your account</li>
                  <li>One account per phone number is permitted</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">4. Acceptable Use Policy</h3>
                <p class="mb-3">You agree not to use our services for:</p>
                <ul class="list-disc list-inside space-y-2">
                  <li>Illegal activities or violation of any laws</li>
                  <li>Transmitting harmful, offensive, or inappropriate content</li>
                  <li>Attempting to gain unauthorized access to our systems</li>
                  <li>Interfering with or disrupting our network services</li>
                  <li>Reselling or redistributing our services without permission</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">5. Payment and Billing</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li>All payments must be made in advance for data packages</li>
                  <li>Prices are subject to change with 30 days notice</li>
                  <li>No refunds for unused data after package expiration</li>
                  <li>Payment disputes must be reported within 30 days</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">6. Service Limitations</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li>Data speeds may be throttled after reaching package limits</li>
                  <li>Service availability is not guaranteed 100% of the time</li>
                  <li>Device connection limits apply based on package type</li>
                  <li>We reserve the right to suspend service for policy violations</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">7. Termination</h3>
                <p>We may terminate or suspend your account immediately, without prior notice, for conduct that we believe violates these Terms of Service or is harmful to other users, us, or third parties.</p>
              </div>
            </div>
          </div>

          <!-- Privacy Policy -->
          <div v-if="activeSection === 'privacy'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Privacy Policy</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">Last updated: {{ new Date().toLocaleDateString() }}</p>
            
            <div class="space-y-6 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Information We Collect</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li><strong>Personal Information:</strong> Phone number, name, email address (if provided)</li>
                  <li><strong>Usage Data:</strong> Data consumption, connection times, device information</li>
                  <li><strong>Technical Data:</strong> IP addresses, browser type, device identifiers</li>
                  <li><strong>Payment Information:</strong> Transaction records (payment details are processed by third parties)</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">How We Use Your Information</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li>Provide and maintain our internet services</li>
                  <li>Process payments and manage your account</li>
                  <li>Send service notifications and updates</li>
                  <li>Improve our services and customer experience</li>
                  <li>Comply with legal obligations</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Information Sharing</h3>
                <p class="mb-3">We do not sell your personal information. We may share information in these situations:</p>
                <ul class="list-disc list-inside space-y-2">
                  <li>With service providers who help us operate our business</li>
                  <li>When required by law or legal process</li>
                  <li>To protect our rights and prevent fraud</li>
                  <li>With your explicit consent</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Data Security</h3>
                <p>We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. However, no method of transmission over the internet is 100% secure.</p>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Your Rights</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li>Access and update your personal information</li>
                  <li>Request deletion of your data (subject to legal requirements)</li>
                  <li>Opt-out of marketing communications</li>
                  <li>Request a copy of your data</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Data Retention</h3>
                <p>We retain your information for as long as necessary to provide services and comply with legal obligations. Usage data is typically retained for 12 months for billing and support purposes.</p>
              </div>
            </div>
          </div>

          <!-- Usage Guidelines -->
          <div v-if="activeSection === 'usage'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Usage Guidelines</h2>
            
            <div class="space-y-6 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Fair Usage Policy</h3>
                <p class="mb-3">To ensure optimal service for all users, we implement fair usage policies:</p>
                <ul class="list-disc list-inside space-y-2">
                  <li>Unlimited packages may have speed restrictions after 100GB daily usage</li>
                  <li>Peer-to-peer traffic may be deprioritized during peak hours</li>
                  <li>Excessive usage that affects network performance may be limited</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Network Etiquette</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li>Avoid running servers or hosting services on residential connections</li>
                  <li>Do not attempt to bypass security measures or access restrictions</li>
                  <li>Report network issues or suspicious activity to support</li>
                  <li>Respect other users' bandwidth and connection quality</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Device Management</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li>Keep your devices secure with updated software and antivirus</li>
                  <li>Do not share your voucher codes with unauthorized users</li>
                  <li>Regularly review and manage connected devices</li>
                  <li>Report lost or stolen devices immediately</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Content Guidelines</h3>
                <p class="mb-3">While using our services, please ensure that:</p>
                <ul class="list-disc list-inside space-y-2">
                  <li>You comply with all applicable laws and regulations</li>
                  <li>You do not access or distribute illegal content</li>
                  <li>You respect intellectual property rights</li>
                  <li>You do not engage in cyberbullying or harassment</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Support Policy -->
          <div v-if="activeSection === 'support'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Support Policy</h2>
            
            <div class="space-y-6 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Support Channels</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li><strong>Live Chat:</strong> Available 24/7 for immediate assistance</li>
                  <li><strong>Email Support:</strong> Response within 24 hours</li>
                  <li><strong>Phone Support:</strong> Available during business hours</li>
                  <li><strong>WhatsApp:</strong> Quick support for common issues</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Response Times</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li><strong>Critical Issues:</strong> Within 1 hour</li>
                  <li><strong>Service Disruptions:</strong> Within 2 hours</li>
                  <li><strong>General Inquiries:</strong> Within 24 hours</li>
                  <li><strong>Billing Questions:</strong> Within 48 hours</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">What We Support</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li>Account and billing issues</li>
                  <li>Technical connectivity problems</li>
                  <li>Device connection assistance</li>
                  <li>Package and voucher questions</li>
                  <li>Security and privacy concerns</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Escalation Process</h3>
                <p class="mb-3">If your issue is not resolved to your satisfaction:</p>
                <ol class="list-decimal list-inside space-y-2">
                  <li>Request to speak with a supervisor</li>
                  <li>Submit a formal complaint via email</li>
                  <li>Contact our customer relations manager</li>
                  <li>Escalate to regulatory authorities if necessary</li>
                </ol>
              </div>
            </div>
          </div>

          <!-- Refund Policy -->
          <div v-if="activeSection === 'refunds'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Refund Policy</h2>
            
            <div class="space-y-6 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">General Policy</h3>
                <p>We understand that sometimes plans change. While digital services are typically non-refundable once activated, we strive to provide fair and flexible refund options for our customers.</p>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Eligible Refund Scenarios</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li>Service unavailability for more than 12 consecutive hours</li>
                  <li>Billing errors or duplicate charges</li>
                  <li>Technical issues preventing service usage for over 6 hours</li>
                  <li>Unauthorized purchases (reported within 48 hours)</li>
                  <li>Accidental purchases (reported within 24 hours)</li>
                  <li>Package not working as described</li>
                  <li>Network coverage issues in your area</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Partial Refunds</h3>
                <p class="mb-3">We offer partial refunds in certain situations:</p>
                <ul class="list-disc list-inside space-y-2">
                  <li>Unused data packages (minimum 80% data remaining)</li>
                  <li>Service downtime exceeding 6 hours (prorated refund)</li>
                  <li>Speed issues significantly below advertised rates</li>
                  <li>Early termination due to relocation outside coverage area</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Refund Process</h3>
                <ol class="list-decimal list-inside space-y-2">
                  <li>Contact our support team within 14 days of the issue</li>
                  <li>Provide detailed information about the problem</li>
                  <li>Allow our technical team to investigate and attempt resolution</li>
                  <li>Refunds are processed within 3-7 business days if approved</li>
                  <li>Refunds are issued to the original payment method</li>
                </ol>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Non-Refundable Items</h3>
                <ul class="list-disc list-inside space-y-2">
                  <li>Expired data packages (beyond validity period)</li>
                  <li>Packages with more than 20% data usage</li>
                  <li>Service fees and government taxes</li>
                  <li>Packages purchased more than 60 days ago</li>
                  <li>Promotional or discounted packages (unless technical issues)</li>
                </ul>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Alternative Solutions</h3>
                <p class="mb-3">Before requesting a refund, we may offer:</p>
                <ul class="list-disc list-inside space-y-2">
                  <li>Service credits for future purchases</li>
                  <li>Package upgrades or extensions</li>
                  <li>Technical support to resolve issues</li>
                  <li>Temporary speed boosts or additional data</li>
                </ul>
              </div>

              <div class="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <h4 class="font-medium text-green-800 dark:text-green-200 mb-2">Customer Satisfaction Guarantee</h4>
                <p class="text-sm text-green-700 dark:text-green-300">We're committed to your satisfaction. If you're not happy with our service, let us know within the first 7 days and we'll work with you to find a solution, including potential refunds for legitimate concerns.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Contact Information -->
      <div class="mt-8 bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 rounded-xl p-6 border border-red-200 dark:border-red-800">
        <div class="flex items-center space-x-3 mb-3">
          <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4C22,2.89 21.1,2 20,2Z"/>
          </svg>
          <h3 class="text-lg font-semibold text-red-900 dark:text-red-200">Questions About Our Policies?</h3>
        </div>
        <p class="text-red-800 dark:text-red-300 mb-4">If you have any questions about these policies, please don't hesitate to contact us.</p>
        <div class="flex flex-wrap gap-3">
          <button class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-all duration-300 hover:scale-105">
            Contact Support
          </button>
          <button class="px-4 py-2 border border-red-600 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg font-medium transition-all duration-300">
            Email Us
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import NavBar from '@/components/NavBar.vue'

const activeSection = ref('terms')

const policySections = [
  { id: 'terms', name: 'Terms of Service', icon: 'svg' },
  { id: 'privacy', name: 'Privacy Policy', icon: 'svg' },
  { id: 'usage', name: 'Usage Guidelines', icon: 'svg' },
  { id: 'support', name: 'Support Policy', icon: 'svg' },
  { id: 'refunds', name: 'Refund Policy', icon: 'svg' }
]
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