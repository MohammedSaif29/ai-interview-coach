import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // PROXY: when the page asks for /api/..., Vite forwards it to the backend.
    // The browser thinks everything comes from one place (localhost:5173),
    // so login cookies work smoothly and we avoid cross-origin problems.
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
