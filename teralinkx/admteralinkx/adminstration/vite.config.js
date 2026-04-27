import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig(({ mode }) => ({
  base: '/su/',
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('ion-')
        }
      }
    }),
    vueJsx(),
    mode === 'development' && vueDevTools(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      base: '/su/',
      scope: '/su/',
      manifest: {
        name: 'TeralinkX Admin',
        short_name: 'TeralinkX',
        description: 'TeralinkX ISP Management Platform',
        start_url: '/su/',
        scope: '/su/',
        display: 'standalone',
        background_color: '#0f172a',
        theme_color: '#3b82f6',
        icons: [
          { src: '/su/favicon.ico', sizes: '64x64', type: 'image/x-icon' }
        ]
      },
      workbox: {
        maximumFileSizeToCacheInBytes: 4 * 1024 * 1024,
        // Cache static assets permanently (hashed = safe forever)
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        // Don't cache API calls in service worker — useApi.js handles that
        navigateFallback: '/su/index.html',
        navigateFallbackDenylist: [/^\/api\//, /^\/suapi\//, /^\/service\//],
        runtimeCaching: [
          {
            // Cache GET API responses for 5 minutes (stale-while-revalidate)
            urlPattern: /^https:\/\/(srv|accounts)\.teralinkxwaves\.uk\/api\//,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'api-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 300 },
              cacheableResponse: { statuses: [200] }
            }
          },
          {
            // Cache suapi responses for 2 minutes
            urlPattern: /^https:\/\/(srv|accounts)\.teralinkxwaves\.uk\/suapi\//,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'suapi-cache',
              expiration: { maxEntries: 50, maxAgeSeconds: 120 },
              cacheableResponse: { statuses: [200] }
            }
          }
        ]
      },
      devOptions: { enabled: false }
    })
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    target: 'es2020',
    minify: false,   // rolldown bundler conflicts with esbuild minifier
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) return 'vue-vendor'
            if (id.includes('apexcharts') || id.includes('chart')) return 'charts'
            if (id.includes('axios') || id.includes('pusher')) return 'utils'
            if (id.includes('workbox') || id.includes('vite-plugin-pwa')) return 'pwa'
          }
        },
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    chunkSizeWarningLimit: 1000,
    cssCodeSplit: true,
    sourcemap: false
  },
  server: {
    port: 5173,
    strictPort: false,
    hmr: { overlay: true }
  },
  preview: { port: 4173 },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'axios'],
    exclude: ['vite-plugin-vue-devtools']
  }
}))
