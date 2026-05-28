import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  // Proxy API calls to FastAPI during development
  // so we don't have to type localhost:8000 everywhere
  server: {
    proxy: {
  '/chat': 'http://localhost:8000',
  '/history': 'http://localhost:8000',
  '/clear': 'http://localhost:8000',
  '/upload': 'http://localhost:8000',
  }
  }
})