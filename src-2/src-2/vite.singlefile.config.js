import { defineConfig } from 'vite'
import path from 'path'
import vue from '@vitejs/plugin-vue'
import { viteSingleFile } from 'vite-plugin-singlefile'

// 单文件构建配置：把 JS、CSS、图片全部内联进一个 index.html，可双击打开
export default defineConfig({
  plugins: [vue(), viteSingleFile()],
  base: './',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
      'vue': 'vue/dist/vue.esm-bundler.js'
    }
  },
  build: {
    outDir: 'dist-single',
    emptyOutDir: true,
    assetsInlineLimit: 100 * 1024 * 1024,
    cssCodeSplit: false,
    chunkSizeWarningLimit: 20000
  }
})
