import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import dayjs from 'dayjs'
import 'dayjs/locale/ko'
import './index.css'

dayjs.locale('ko')
import App from './App.tsx'
import { theme } from './theme/theme'
import { AuthProvider } from './auth/AuthContext'
import { LoginGateProvider } from './auth/LoginGateContext'
import { AdminAuthProvider } from './admin/AdminAuthContext'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
})

async function enableMocking() {
  if (import.meta.env.PROD) return
  const { worker } = await import('./mocks/browser')
  return worker.start({ onUnhandledRequest: 'bypass' })
}

enableMocking().then(() => {
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <AuthProvider>
              <LoginGateProvider>
                <AdminAuthProvider>
                  <App />
                </AdminAuthProvider>
              </LoginGateProvider>
            </AuthProvider>
          </BrowserRouter>
        </QueryClientProvider>
      </ThemeProvider>
    </StrictMode>,
  )
})
