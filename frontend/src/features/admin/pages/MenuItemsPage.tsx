import { useRef, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus, Search, X, Download, Upload, Printer } from 'lucide-react'
import { TenantBadge } from '@/shared/components/layout/TenantBadge'
import { MenuItemForm } from '../components/MenuItemForm'
import { MenuItemTable } from '../components/MenuItemTable'
import { CategoriesTab } from '../components/CategoriesTab'
import { OnlineVendorsCard } from '../../settings/components/OnlineVendorsCard'
import { useCreateMenuItem, useDeleteMenuItem, useMenuItems, useUpdateMenuItem } from '../hooks/useMenuItems'
import { menuApi } from '../api/menu'
import { vendorsApi } from '../../settings/api/onlineVendors'
import { MenuPrintView } from '../components/MenuPrintView'
import type { MenuItemCreate, MenuItemResponse, MenuItemUpdate } from '../types/menu'
type Tab = 'items' | 'categories' | 'vendors'
export function MenuItemsPage() {
  const { data: items = [], isLoading, isError } = useMenuItems()
  const { data: vendors = [] } = useQuery({ queryKey: ['online-vendors'], queryFn: vendorsApi.list })
  const createMutation = useCreateMenuItem()
  const updateMutation = useUpdateMenuItem()
  const deleteMutation = useDeleteMenuItem()
  const [tab, setTab] = useState<Tab>('items')
  const [panel, setPanel] = useState<'create' | MenuItemResponse | null>(null)
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [importing, setImporting] = useState(false); const [showPrint, setShowPrint] = useState(false); const fileRef = useRef<HTMLInputElement>(null)
  const existingCategories = useMemo(() => [...new Set(items.map((i) => i.category))].sort(), [items])
  const isMutating = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending
  function handleSubmit(data: MenuItemCreate | MenuItemUpdate) {
    if (panel && panel !== 'create') updateMutation.mutate({ id: panel.id, data: data as MenuItemUpdate }, { onSuccess: () => setPanel(null) })
    else createMutation.mutate(data as MenuItemCreate, { onSuccess: () => setPanel(null) })
  }
  async function handleExport() { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([await menuApi.exportCsv()], { type: 'text/csv' })); a.download = 'menu.csv'; a.click() }
  async function handleImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]; if (!file) return
    setImporting(true)
    try { const res = await menuApi.importCsv(file); alert(`${res.created} items imported${res.errors.length ? '\n' + res.errors.join('\n') : ''}`) }
    finally { setImporting(false); if (fileRef.current) fileRef.current.value = '' }
  }
  if (isLoading) return <div className="p-6 text-sm text-text-muted">Loading…</div>
  if (isError) return <div className="p-6 text-sm text-status-error">Failed to load. Please refresh.</div>
  return (
    <div className="flex flex-col h-full">
      <header className="px-6 py-4 border-b border-sphotel-border bg-bg-surface shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold text-text-primary">Menu Items</h1>
          <TenantBadge />
        </div>
        <div className="flex flex-col md:flex-row md:items-center gap-3 mt-3">
          <div className="flex overflow-x-auto whitespace-nowrap gap-1 bg-bg-elevated border border-sphotel-border rounded-lg p-0.5 shrink-0">
            {(['items', 'categories', 'vendors'] as Tab[]).map((t) => (
              <button key={t} onClick={() => setTab(t)} className={`px-3 py-1 rounded text-sm font-medium transition-colors capitalize ${tab === t ? 'bg-sphotel-accent text-sphotel-accent-fg' : 'text-text-secondary hover:text-text-primary'}`}>{t}</button>
            ))}
          </div>
          {tab === 'items' && <>
            <div className="relative w-full md:w-auto shrink-0">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" />
              <input placeholder="Search name, category, code…" className="w-full md:w-56 bg-bg-elevated border border-sphotel-border rounded-lg pl-8 pr-3 py-1.5 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent" value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
            <div className="md:ml-auto flex flex-wrap items-center gap-2 shrink-0">
              <input ref={fileRef} type="file" accept=".csv" className="hidden" onChange={handleImport} />
              <button onClick={() => fileRef.current?.click()} disabled={importing} className="flex items-center gap-1.5 border border-sphotel-border rounded-lg px-3 py-1.5 text-sm text-text-secondary hover:text-text-primary disabled:opacity-50"><Upload size={14} />{importing ? 'Importing…' : 'Import'}</button>
              <button onClick={handleExport} className="flex items-center gap-1.5 border border-sphotel-border rounded-lg px-3 py-1.5 text-sm text-text-secondary hover:text-text-primary"><Download size={14} />Export</button>
              <button onClick={() => setShowPrint(true)} className="flex items-center gap-1.5 border border-sphotel-border rounded-lg px-3 py-1.5 text-sm text-text-secondary hover:text-text-primary"><Printer size={14} />Print</button>
              <button onClick={() => setPanel('create')} className="flex items-center gap-1.5 bg-sphotel-accent text-sphotel-accent-fg rounded-lg px-3 py-1.5 text-sm font-medium"><Plus size={16} />Add Item</button>
            </div>
          </>}
        </div>
      </header>
      <div className="flex flex-1 min-h-0">
        <div className="flex-1 overflow-auto p-6 min-w-0">
          {tab === 'items' && (items.length === 0
            ? <p className="text-sm text-text-muted">No menu items yet. <button onClick={() => setPanel('create')} className="text-sphotel-accent underline">Add the first one.</button></p>
            : <MenuItemTable items={items} search={search} onEdit={setPanel} onToggle={(item) => updateMutation.mutate({ id: item.id, data: { is_available: !item.is_available } })} onDelete={setDeleteConfirmId} isUpdating={updateMutation.isPending} />)}
          {tab === 'categories' && <CategoriesTab />}
          {tab === 'vendors' && <OnlineVendorsCard />}
        </div>
        {panel && <>
          <div className="fixed inset-0 z-10" onClick={() => setPanel(null)} />
          <aside className="relative z-20 w-80 border-l border-sphotel-border bg-bg-surface p-5 overflow-auto">
            <button onClick={() => setPanel(null)} className="absolute top-4 right-4 text-text-muted hover:text-text-primary"><X size={18} /></button>
            <MenuItemForm item={panel !== 'create' ? panel : undefined} existingCategories={existingCategories} vendors={vendors} onSubmit={handleSubmit} onCancel={() => setPanel(null)} isLoading={isMutating} />
          </aside>
        </>}
      </div>
      {showPrint && <MenuPrintView items={items} onClose={() => setShowPrint(false)} />}
      {deleteConfirmId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-bg-surface border border-sphotel-border rounded-xl shadow-xl p-6 w-80 flex flex-col gap-4">
            <div><p className="text-sm font-medium text-text-primary">Delete menu item?</p><p className="text-xs text-text-muted mt-0.5">This action cannot be undone.</p></div>
            <div className="flex gap-2">
              <button onClick={() => setDeleteConfirmId(null)} className="flex-1 border border-sphotel-border rounded-lg py-2 text-sm text-text-secondary">Cancel</button>
              <button onClick={() => deleteMutation.mutate(deleteConfirmId, { onSuccess: () => setDeleteConfirmId(null) })} disabled={deleteMutation.isPending} className="flex-1 bg-status-error text-white rounded-lg py-2 text-sm font-medium disabled:opacity-50">{deleteMutation.isPending ? 'Deleting…' : 'Delete'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
