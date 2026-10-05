import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
// Proxy /api/* ke backend. Default UAT: 8001 / WEB_PORT — jangan jatuh ke live 8000/5173.
export default defineConfig(({ mode }) => {
  const env = { ...loadEnv(mode, process.cwd(), ''), ...process.env }
  const proxyTarget = env.VITE_API_PROXY || 'http://127.0.0.1:8002'
  const hmrHost = (env.VITE_HMR_HOST || '').trim() || undefined
  const hmrProtocol = env.VITE_HMR_PROTOCOL || 'ws'
  const listenPort = Number(env.WEB_PORT || env.VITE_DEV_PORT || 8082)
  const hmrPort = Number(env.VITE_HMR_PORT || env.WEB_PORT || listenPort)
  const hmrClientPort = Number(env.VITE_HMR_CLIENT_PORT || env.WEB_PORT || listenPort)
  const devPublicOrigin = (env.VITE_DEV_PUBLIC_ORIGIN || '').trim() || undefined
  return {
    plugins: [vue()],
    server: {
      host: '0.0.0.0',
      allowedHosts: true,
      /** https://vite.dev/config/server-options.html#server-origin */
      origin: devPublicOrigin,
      port: listenPort,
      strictPort: true,
      watch: {
        usePolling: true,
        interval: 300,
      },
      hmr: {
        protocol: hmrProtocol,
        port: hmrPort,
        clientPort: hmrClientPort,
        ...(hmrHost ? { host: hmrHost } : {}),
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
