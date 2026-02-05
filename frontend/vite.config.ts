import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import VueRouter from 'unplugin-vue-router/vite'
import path from 'node:path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    VueRouter({
      routesFolder: './src/pages',
      extensions: ['.page.vue'],
      importMode: 'async',
      dts: './types/auto-routes.d.ts',
      routeBlockLang: 'yaml',
    }),
    vue(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/layouts': path.resolve(__dirname, './src/layouts'),
      '@/pages': path.resolve(__dirname, './src/pages'),
      '@/stores': path.resolve(__dirname, './src/stores'),
      '@/composables': path.resolve(__dirname, './src/composables'),
      '@/utils': path.resolve(__dirname, './src/utils'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/design-tokens': path.resolve(__dirname, './src/design-tokens'),
      '@/content': path.resolve(__dirname, './src/content'),
      '@/locales': path.resolve(__dirname, './src/locales'),
      '@/tailwind.config': path.resolve(__dirname, './config/tailwind.config.js'),
    },
  },
  server: {
    port: 5173,
    strictPort: false,
    host: true,
    watch: {
      usePolling: true,
    },
  },
  css: {
    postcss: './config/postcss.config.js',
  },
})
