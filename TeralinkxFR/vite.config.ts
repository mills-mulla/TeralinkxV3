import { fileURLToPath, URL } from 'node:url'
import { copyFileSync, mkdirSync } from 'node:fs'
import { dirname } from 'node:path'

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
      ...(isDev ? [import('vite-plugin-vue-devtools').then(m => m.default())] : []),
      {
        name: 'copy-mikrotik-pages',
        closeBundle() {
          const files = ['login.html', 'logout.html', 'status.html']
          files.forEach(file => {
            const src = fileURLToPath(new URL(`./src/assets/flash/hotspot/${file}`, import.meta.url))
            const dest = fileURLToPath(new URL(`./dist/src/assets/flash/hotspot/${file}`, import.meta.url))
            mkdirSync(dirname(dest), { recursive: true })
            copyFileSync(src, dest)
          })
          // Copy assets for MikroTik pages
          const assets = [
            { src: './src/assets/teralinkx2.png', dest: './dist/assets/teralinkx2.png' },
            { src: './src/assets/TeralinkxWavesic.jpeg', dest: './dist/assets/TeralinkxWavesic.jpeg' }
          ]
          assets.forEach(({ src, dest }) => {
            const srcPath = fileURLToPath(new URL(src, import.meta.url))
            const destPath = fileURLToPath(new URL(dest, import.meta.url))
            mkdirSync(dirname(destPath), { recursive: true })
            copyFileSync(srcPath, destPath)
          })
        }
      }
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
          manualChunks: (id) => {
            if (id.includes('node_modules')) {
              if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
                return 'vendor'
              }
              if (id.includes('@headlessui')) {
                return 'ui'
              }
            }
          }
        }
      }
    }
  }
})
