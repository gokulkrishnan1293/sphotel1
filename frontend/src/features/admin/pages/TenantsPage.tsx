import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus, Search } from 'lucide-react'
import { tenantsApi, type TenantSummary } from '../api/tenants'
import { CreateTenantPanel } from '../components/CreateTenantPanel'
import { EditTenantPanel } from '../components/EditTenantPanel'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/components/ui/table'
import { TenantBadge } from '@/shared/components/layout/TenantBadge'

export function TenantsPage() {
  const [panel, setPanel] = useState<'create' | TenantSummary | null>(null)
  const [search, setSearch] = useState('')
  const { data: tenants = [], isLoading } = useQuery({ queryKey: ['tenants'], queryFn: tenantsApi.list })
  const filtered = tenants.filter((t) => t.name.toLowerCase().includes(search.toLowerCase()) || t.slug.includes(search.toLowerCase()))

  return (
    <div className="flex flex-col h-full">
      <header className="px-6 py-4 border-b border-sphotel-border bg-bg-surface shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold text-text-primary">Tenants</h1>
          <TenantBadge />
        </div>
        <div className="flex items-center gap-3 mt-3">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" />
            <input placeholder="Search by name or slug…"
              className="pl-8 pr-3 py-1.5 w-64 bg-bg-elevated border border-sphotel-border rounded-lg text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent"
              value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
          <button onClick={() => setPanel('create')}
            className="ml-auto flex items-center gap-1.5 bg-sphotel-accent text-sphotel-accent-fg rounded-lg px-3 py-1.5 text-sm font-medium">
            <Plus size={16} /> New Tenant
          </button>
        </div>
      </header>

      <div className="flex flex-1 min-h-0">
        <div className="flex-1 overflow-auto p-6">
          {isLoading ? <p className="text-sm text-text-muted">Loading…</p> : (
            <div className="border border-sphotel-border rounded-xl overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="border-sphotel-border bg-bg-elevated hover:bg-bg-elevated">
                    {['Name', 'Slug', 'Status', 'Onboarding'].map((h) => (
                      <TableHead key={h} className="text-text-muted text-xs uppercase tracking-wide font-medium">{h}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filtered.map((t) => (
                    <TableRow key={t.slug} onClick={() => setPanel(t)} className="cursor-pointer border-sphotel-border hover:bg-bg-elevated transition-colors">
                      <TableCell className="font-medium text-text-primary">{t.name}</TableCell>
                      <TableCell className="font-mono text-text-muted">{t.slug}</TableCell>
                      <TableCell>
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${t.is_active ? 'bg-status-success/15 text-status-success' : 'bg-status-offline/15 text-status-offline'}`}>{t.is_active ? 'Active' : 'Inactive'}</span>
                      </TableCell>
                      <TableCell>
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${t.onboarding_completed ? 'bg-sphotel-accent-subtle text-sphotel-accent' : 'bg-status-warning/15 text-status-warning'}`}>{t.onboarding_completed ? 'Done' : 'Pending'}</span>
                      </TableCell>
                    </TableRow>
                  ))}
                  {filtered.length === 0 && (
                    <TableRow className="border-0"><TableCell colSpan={4} className="text-center text-text-muted py-8">No tenants found.</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </div>

        {panel && (
          <>
            <div className="fixed inset-0 z-10" onClick={() => setPanel(null)} />
            <aside className="relative z-20 w-80 border-l border-sphotel-border bg-bg-surface p-5 overflow-auto">
              {panel === 'create'
                ? <CreateTenantPanel onClose={() => setPanel(null)} />
                : <EditTenantPanel tenant={panel} onClose={() => setPanel(null)} onDeleted={() => setPanel(null)} />}
            </aside>
          </>
        )}
      </div>
    </div>
  )
}
