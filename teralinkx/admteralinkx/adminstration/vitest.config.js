import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig, configDefaults } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      exclude: [...configDefaults.exclude, 'e2e/**'],
      root: fileURLToPath(new URL('./', import.meta.url)),
    },
    // server: {
    //   proxy: {
    //     '/suapi': {
    //       target: 'https://service.teralinkxwaves.uk',
    //       changeOrigin: true,
    //       secure: false,
    //       rewrite: (path) => path.replace(/^\/suapi/, '/suapi'),
    //     }
    //   }
    // }
  })
)
