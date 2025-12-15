import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Enable code splitting
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks for better caching
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['lucide-react', 'react-hot-toast'],
          'state-vendor': ['zustand', '@tanstack/react-query'],
        },
      },
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 600,
    // Enable source maps for production debugging (can be disabled for smaller builds)
    sourcemap: false,
  },
  // Performance optimizations
  server: {
    port: 3000,
    proxy: {
      // Proxy image requests to backend
      '/images': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
