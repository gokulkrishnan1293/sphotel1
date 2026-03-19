import './index.css'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { applyAccent, getStoredAccent } from './lib/accent'
import { getStoredTheme, getSystemTheme } from './lib/theme'

// Apply saved accent color on boot (theme mode is handled by index.html inline script)
const savedAccent = getStoredAccent()
if (savedAccent) {
  const isDark = (getStoredTheme() ?? getSystemTheme()) !== 'light'
  applyAccent(savedAccent, isDark)
}
import * as Sentry from '@sentry/react'
import { App } from './app/App'
import { Providers } from './app/providers'

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.MODE,
    integrations: [Sentry.browserTracingIntegration()],
    tracesSampleRate: 0.1,
    sendDefaultPii: false,
  })
}

const rootElement = document.getElementById('root')
if (!rootElement) throw new Error('Root element #root not found in index.html')

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <Providers>
      <App />
    </Providers>
  </React.StrictMode>
)
