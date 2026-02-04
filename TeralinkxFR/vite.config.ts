import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const isDev = mode === 'development'
  
  return {
    plugins: [
      vue(),
      vueJsx(),
      // Only include dev tools in development
      ...(isDev ? [import('vite-plugin-vue-devtools').then(m => m.default())] : [])
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    server: {
      host: '0.0.0.0', 
      port: 5173, 
      hmr: {
        host: 'localhost',
        port: 5173, 
      },
      proxy: {
        '/api': {
          target: 'http://192.168.88.16:8009',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '/api'),
        },
      }
    },
    build: {
      // Production optimizations
      minify: 'terser',
      sourcemap: false,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['vue', 'vue-router', 'pinia'],
            ui: ['@headlessui/vue']
          }
        }
      }
    }
  }
})
