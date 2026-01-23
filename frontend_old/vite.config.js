import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'


// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      '/news-chat': {
        target: 'http://backend:8001',
        changeOrigin: true,
      },
      '/chat': {
        target: 'http://backend:8001',
        changeOrigin: true,
      },
      '/rss': {
        target: 'http://backend:8001',
        changeOrigin: true,
      }
    }
  }
})
