import * as Sentry from '@sentry/react'
import { createBrowserRouter, Navigate } from 'react-router'

const sentryCreateBrowserRouter = Sentry.wrapCreateBrowserRouterV7(createBrowserRouter)
import { LoginPage } from '../features/auth/pages/LoginPage'
import { TenantCodePage } from '../features/auth/pages/TenantCodePage'
import { TenantRolePage } from '../features/auth/pages/TenantRolePage'
import { TenantAdminLoginPage } from '../features/auth/pages/TenantAdminLoginPage'
import { TenantBillerLoginPage } from '../features/auth/pages/TenantBillerLoginPage'
import { TenantStaffLoginPage } from '../features/auth/pages/TenantStaffLoginPage'
import { ProtectedRoute } from '../features/auth/components/ProtectedRoute'
import { AppShell } from '../shared/components/layout/AppShell'
import { MenuItemsPage } from '../features/admin/pages/MenuItemsPage'
import { TenantsPage } from '../features/admin/pages/TenantsPage'
import { TablesPage } from '../features/admin/pages/TablesPage'
import { StaffPage } from '../features/admin/pages/StaffPage'
import { BillingPage } from '../features/billing/pages/BillingPage'
import { KitchenPage } from '../features/kitchen/pages/KitchenPage'
import { PrintSettingsPage } from '../features/settings/routes/PrintSettingsPage'
import { TelegramPage } from '../features/settings/routes/TelegramPage'
import { ShortcutsPage } from '../features/settings/routes/ShortcutsPage'
import { ReportsPage } from '../features/reports/pages/ReportsPage'
import { BrandingPage } from '../features/settings/routes/BrandingPage'

const isAdminDomain = window.location.hostname.includes('managehotels') || import.meta.env.VITE_APP_TYPE === 'admin'

export const router = sentryCreateBrowserRouter([
  { path: '/login', element: isAdminDomain ? <LoginPage /> : <TenantCodePage /> },
  { path: '/t', element: <Navigate to="/login" replace /> },
  { path: '/t/:code', element: <TenantRolePage /> },
  { path: '/t/:code/admin', element: <TenantAdminLoginPage /> },
  { path: '/t/:code/biller', element: <TenantBillerLoginPage /> },
  { path: '/t/:code/staff', element: <TenantStaffLoginPage /> },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Navigate to="/billing" replace /> },
      { path: 'billing', element: <BillingPage /> },
      { path: 'admin/menu', element: <MenuItemsPage /> },
      { path: 'admin/tables', element: <TablesPage /> },
      { path: 'admin/staff', element: <StaffPage /> },
      { path: 'admin/tenants', element: <TenantsPage /> },
      { path: 'admin/print-settings', element: <PrintSettingsPage /> },
      { path: 'admin/telegram', element: <TelegramPage /> },
      { path: 'admin/shortcuts', element: <ShortcutsPage /> },
      { path: 'admin/branding', element: <BrandingPage /> },
      { path: 'reports', element: <ReportsPage /> },
      { path: 'kitchen', element: <KitchenPage /> },
    ],
  },
  { path: '*', element: <Navigate to="/t" replace /> },
])
