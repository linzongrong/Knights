import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import viteCompression from 'vite-plugin-compression'

// https://vite.dev/config/
export default defineConfig({
  base: './',
  plugins: [
    vue(),
    viteCompression({
      verbose: true,
      disable: false,
      threshold: 10240,
      algorithm: 'gzip',
      ext: '.gz',
    })
  ],
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('echarts')) {
              return 'echarts';
            }
            if (id.includes('@amap')) {
              return 'amap';
            }
            if (id.includes('leaflet')) {
              return 'leaflet';
            }
            if (id.includes('vue') || id.includes('vuedraggable')) {
              return 'vue-vendor';
            }
            return 'vendor'; // functional/utility libs
          }
        },
      },
    },
  },
})
