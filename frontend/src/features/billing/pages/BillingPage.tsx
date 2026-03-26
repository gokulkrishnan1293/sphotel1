import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronLeft, Printer } from 'lucide-react'
import { useTenantName } from '@/shared/hooks/useTenantName'
import { useBillingStore } from '../stores/billingStore'
import { useAutoSave } from '../hooks/useAutoSave'
import { useOfflineSync } from '../hooks/useOfflineSync'
import { ActiveBillsPanel } from '../components/ActiveBillsPanel'
import { BillCanvas } from '../components/BillCanvas'
import { PrinterOfflineBanner } from '../components/PrinterOfflineBanner'
import { printApi } from '../../settings/api/printSettings'
import { cachePrintTemplate } from '@/lib/localPrint'
import { useIsLocalMachine } from '@/lib/db/localAgentStatus'
import { shortcutsApi } from '../../settings/api/shortcuts'
import { useShortcutStore } from '@/lib/shortcutStore'
import { useNetworkStore } from '@/lib/networkStatus'
import { Toast } from '@/shared/components/Toast'

export function BillingPage() {
  const activeBillId = useBillingStore((s) => s.activeBillId)
  useAutoSave(activeBillId)
  useOfflineSync()
  const setShortcuts = useShortcutStore((s) => s.setShortcuts)
  useEffect(() => { shortcutsApi.get().then(setShortcuts).catch(() => {}) }, [setShortcuts])
  const isOnline = useNetworkStore((s) => s.isOnline)
  const isLocalMachine = useIsLocalMachine()
  const { data: agents = [], isLoading: agentsLoading } = useQuery({ queryKey: ['print-agents'], queryFn: printApi.listAgents, refetchInterval: 30_000, staleTime: 20_000 })
  const { data: printTemplate } = useQuery({ queryKey: ['print-template'], queryFn: printApi.getTemplate, staleTime: 300_000 })
  useEffect(() => { if (printTemplate) cachePrintTemplate(printTemplate) }, [printTemplate])
  const printerOnline = agents.some((a) => a.status === 'online')
  const canOpenNewBill = agentsLoading || isLocalMachine || (isOnline && printerOnline)

  const [mobileView, setMobileView] = useState<'panel' | 'canvas'>('panel')
  useEffect(() => { if (activeBillId) setMobileView('canvas') }, [activeBillId])

  const tenantName = useTenantName()

  const [fontSizeIdx, setFontSizeIdx] = useState<number>(() => {
    const saved = localStorage.getItem('billFontSize')
    return saved ? Math.max(0, Math.min(8, parseInt(saved, 10))) : 2
  })
  const changeFontSize = (delta: number) => {
    setFontSizeIdx((prev) => {
      const next = Math.max(0, Math.min(8, prev + delta))
      localStorage.setItem('billFontSize', String(next))
      return next
    })
  }

  return (
    <>
    <div className="flex flex-col h-full">
      <header className="px-4 md:px-6 py-3 md:py-4 border-b border-sphotel-border bg-bg-surface shrink-0 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold text-text-primary">Billing</h1>
          {tenantName && (
            <div className="hidden md:flex items-center gap-2">
              <span className="w-px h-4 bg-sphotel-border" />
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sphotel-accent opacity-60" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-sphotel-accent" />
              </span>
              <span className="text-sm font-semibold text-sphotel-accent tracking-wide">{tenantName}</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <div className="hidden md:flex items-center gap-0.5 mr-1">
            <button onClick={() => changeFontSize(-1)} disabled={fontSizeIdx === 0} title="Smaller text"
              className="w-6 h-6 flex items-center justify-center rounded text-text-muted hover:text-text-primary hover:bg-bg-base disabled:opacity-30 font-bold" style={{ fontSize: '10px' }}>A−</button>
            <button onClick={() => changeFontSize(1)} disabled={fontSizeIdx === 8} title="Larger text"
              className="w-6 h-6 flex items-center justify-center rounded text-text-muted hover:text-text-primary hover:bg-bg-base disabled:opacity-30 font-bold" style={{ fontSize: '13px' }}>A+</button>
          </div>
          <span className="hidden md:inline w-px h-3 bg-sphotel-border" />
          <span className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-status-success' : 'bg-status-error'}`} />
          <span className={isOnline ? '' : 'text-status-error'}>{isOnline ? 'Online' : 'Offline'}</span>
          <span className="hidden sm:inline w-px h-3 bg-sphotel-border mx-1" />
          <Printer size={11} className={`hidden sm:block ${printerOnline ? 'text-status-success' : 'text-status-error'}`} />
          <span className={`hidden sm:inline ${printerOnline ? 'text-status-success' : 'text-status-error'}`}>
            {printerOnline ? 'Printer ready' : 'No printer'}
          </span>
        </div>
      </header>
      <PrinterOfflineBanner printerOnline={printerOnline} isLocalMachine={isLocalMachine} />

      <div className="flex flex-1 min-h-0 min-w-0">
        <div className={`${mobileView === 'canvas' ? 'hidden md:flex' : 'flex'} w-full md:w-auto md:flex-none flex-col min-h-0 min-w-0`}>
          <ActiveBillsPanel onSelect={() => setMobileView('canvas')} canOpenNewBill={canOpenNewBill} />
        </div>
        <div className={`${mobileView === 'panel' ? 'hidden md:flex' : 'flex'} flex-1 flex-col min-h-0 min-w-0`}>
          <button onClick={() => setMobileView('panel')}
            className="md:hidden shrink-0 flex items-center gap-1 px-4 py-2.5 text-sm text-text-secondary border-b border-sphotel-border bg-bg-surface">
            <ChevronLeft size={16} /> Back to Bills
          </button>
          <BillCanvas fontSizeIdx={fontSizeIdx} canOpenNewBill={canOpenNewBill} />
        </div>
      </div>
    </div>
    <Toast />
    </>
  )
}
