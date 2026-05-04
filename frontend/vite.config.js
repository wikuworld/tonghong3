import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
// Proxy /api/* ke backend (dev lokal: localhost:8000, Docker dev: VITE_API_PROXY=http://backend:8000)
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget = env.VITE_API_PROXY || 'http://127.0.0.1:8000'
  const hmrHost = env.VITE_HMR_HOST || 'localhost'
  const hmrProtocol = env.VITE_HMR_PROTOCOL || 'ws'
  const hmrPort = Number(env.VITE_HMR_PORT || 5173)
  const hmrClientPort = Number(env.VITE_HMR_CLIENT_PORT || hmrPort)
  return {
    plugins: [vue()],
    server: {
      host: '0.0.0.0',
      allowedHosts: true,
      port: 5173,
      strictPort: true,
      watch: {
        usePolling: true,
        interval: 300,
      },
      hmr: {
        host: hmrHost,
        protocol: hmrProtocol,
        port: hmrPort,
        clientPort: hmrClientPort,
      },
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
