import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Helper to prevent proxy crashes
const proxyErrorHandler = (proxy) => {
  proxy.on('error', (err) => {
    console.warn('[Vite Proxy Error]', err.message);
  });
};

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        configure: proxyErrorHandler,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true,
        configure: proxyErrorHandler,
      },
      '/graphics': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        configure: proxyErrorHandler,
      },
      '/data': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        configure: proxyErrorHandler,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
