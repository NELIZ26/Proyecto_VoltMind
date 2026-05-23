import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import legacy from '@vitejs/plugin-legacy' // <-- 1. Importamos el plugin
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    // 2. Configuramos el soporte para navegadores antiguos
    legacy({
      targets: ['Android >= 9', 'iOS >= 11'],
      renderLegacyChunks: true,
    })
  ],
  base: './',
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})