import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const pkg = JSON.parse(readFileSync(fileURLToPath(new URL('./package.json', import.meta.url)), 'utf-8'))

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version),
  },
  server: {
    // 실 백엔드로 프록시 — 프론트/백엔드가 브라우저 입장에서 같은 오리진이 되어
    // refreshToken(HttpOnly 쿠키) 왕복에 CORS 설정이 필요 없다. 운영에서도 nginx가
    // 같은 방식(reverse proxy)으로 묶을 예정이라 로컬 개발 환경과 구조가 동일하다.
    proxy: {
      '/api/v1': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
