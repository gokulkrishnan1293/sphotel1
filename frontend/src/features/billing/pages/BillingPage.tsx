import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronLeft, Printer } from 'lucide-react'
import { useBillingStore } from '../stores/billingStore'
import { useAutoSave } from '../hooks/useAutoSave'
import { ActiveBillsPanel } from '../components/ActiveBillsPanel'
import { BillCanvas } from '../components/BillCanvas'
import { printApi } from '../../settings/api/printSettings'
import { shortcutsApi } from '../../settings/api/shortcuts'
import { useShortcutStore } from '@/lib/shortcutStore'
import { useNetworkStore } from '@/lib/networkStatus'
import { Toast } from '@/shared/components/Toast'

export function BillingPage() {
  const activeBillId = useBillingStore((s) => s.activeBillId)
  useAutoSave(activeBillId)
  const setShortcuts = useShortcutStore((s) => s.setShortcuts)
  useEffect(() => { shortcutsApi.get().then(setShortcuts).catch(() => {}) }, [setShortcuts])
  const isOnline = useNetworkStore((s) => s.isOnline)
  const { data: agents = [] } = useQuery({ queryKey: ['print-agents'], queryFn: printApi.listAgents, refetchInterval: 30_000, staleTime: 20_000 })
  const printerOnline = agents.some((a) => a.status === 'online')

  const [mobileView, setMobileView] = useState<'panel' | 'canvas'>('panel')
  useEffect(() => { if (activeBillId) setMobileView('canvas') }, [activeBillId])

  return (
    <>
    <div className="flex flex-col h-full">
      <header className="px-4 md:px-6 py-3 md:py-4 border-b border-sphotel-border bg-bg-surface shrink-0 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-text-primary">Billing</h1>
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <span className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-status-success' : 'bg-status-error'}`} />
          <span className={isOnline ? '' : 'text-status-error'}>{isOnline ? 'Online' : 'Offline'}</span>
          <span className="hidden sm:inline w-px h-3 bg-sphotel-border mx-1" />
          <Printer size={11} className={`hidden sm:block ${printerOnline ? 'text-status-success' : 'text-status-error'}`} />
          <span className={`hidden sm:inline ${printerOnline ? 'text-status-success' : 'text-status-error'}`}>
            {printerOnline ? 'Printer ready' : 'No printer'}
          </span>
        </div>
      </header>

      <div className="flex flex-1 min-h-0">
        <div className={`${mobileView === 'canvas' ? 'hidden md:flex' : 'flex'} flex-1 md:flex-none flex-col`}>
          <ActiveBillsPanel onSelect={() => setMobileView('canvas')} />
        </div>
        <div className={`${mobileView === 'panel' ? 'hidden md:flex' : 'flex'} flex-1 flex-col min-h-0`}>
          <button onClick={() => setMobileView('panel')}
            className="md:hidden shrink-0 flex items-center gap-1 px-4 py-2.5 text-sm text-text-secondary border-b border-sphotel-border bg-bg-surface">
            <ChevronLeft size={16} /> Back to Bills
          </button>
          <BillCanvas />
        </div>
      </div>
    </div>
    <Toast />
    </>
  )
}
