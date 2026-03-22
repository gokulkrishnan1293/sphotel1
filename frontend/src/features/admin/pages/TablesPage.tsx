import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { tablesApi } from '../api/tables'
import { SectionCard } from '../components/SectionCard'
import { TenantBadge } from '@/shared/components/layout/TenantBadge'

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#f43f5e', '#06b6d4']
const INPUT = 'bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent'

export function TablesPage() {
  const qc = useQueryClient()
  const [sectionName, setSectionName] = useState('')
  const [sectionColor, setSectionColor] = useState(COLORS[0])

  const { data: sections = [], isLoading } = useQuery({ queryKey: ['sections'], queryFn: tablesApi.listSections })
  const inv = () => qc.invalidateQueries({ queryKey: ['sections'] })
  const createSection = useMutation({
    mutationFn: () => tablesApi.createSection({ name: sectionName.trim(), color: sectionColor }),
    onSuccess: () => { inv(); setSectionName('') },
  })
  const deleteSection = useMutation({ mutationFn: (id: string) => tablesApi.deleteSection(id), onSuccess: inv })
  const updateSection = useMutation({
    mutationFn: ({ id, name, color }: { id: string; name: string; color: string }) => tablesApi.updateSection(id, { name, color }),
    onSuccess: inv,
  })
  const createTable = useMutation({ mutationFn: tablesApi.createTable, onSuccess: inv })
  const updateTable = useMutation({
    mutationFn: ({ id, ...data }: { id: string; name?: string; capacity?: number; is_active?: boolean }) => tablesApi.updateTable(id, data),
    onSuccess: inv,
  })
  const deleteTable = useMutation({ mutationFn: (id: string) => tablesApi.deleteTable(id), onSuccess: inv })

  return (
    <div className="flex flex-col h-full">
      <header className="px-6 py-4 border-b border-sphotel-border bg-bg-surface shrink-0 flex items-center gap-3">
        <h1 className="text-lg font-semibold text-text-primary">Tables & Sections</h1>
        <TenantBadge />
      </header>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-3xl flex flex-col gap-6">
          <div className="bg-bg-surface border border-sphotel-border rounded-xl p-4 flex flex-col gap-3">
            <p className="text-xs font-medium text-text-muted uppercase tracking-wide">New Section</p>
            <div className="flex gap-2">
              <input className={`${INPUT} flex-1`} placeholder="Section name" value={sectionName}
                onChange={(e) => setSectionName(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && sectionName.trim()) createSection.mutate() }} />
              <div className="flex gap-1 items-center">
                {COLORS.map((c) => (
                  <button key={c} onClick={() => setSectionColor(c)} style={{ backgroundColor: c }}
                    className={`w-6 h-6 rounded-full hover:scale-110 transition-transform ${sectionColor === c ? 'ring-2 ring-white ring-offset-1 ring-offset-bg-surface scale-110' : ''}`}
                  />
                ))}
              </div>
              <button onClick={() => { if (sectionName.trim()) createSection.mutate() }}
                disabled={!sectionName.trim() || createSection.isPending}
                className="shrink-0 px-4 py-2 bg-sphotel-accent text-sphotel-accent-fg rounded-lg text-sm font-medium disabled:opacity-50 flex items-center gap-1">
                <Plus size={14} /> Add
              </button>
            </div>
          </div>

          {isLoading ? (
            <p className="text-sm text-text-muted">Loading…</p>
          ) : sections.length === 0 ? (
            <p className="text-sm text-text-muted">No sections yet.</p>
          ) : (
            <div className="flex flex-col gap-3">
              {sections.map((s) => (
                <SectionCard key={s.id} section={s}
                  onDeleteSection={() => { if (confirm(`Delete "${s.name}" and all its tables?`)) deleteSection.mutate(s.id) }}
                  onUpdateSection={(name, color) => updateSection.mutate({ id: s.id, name, color })}
                  onAddTable={(name, capacity) => createTable.mutate({ section_id: s.id, name, capacity })}
                  onUpdateTable={(id, name, capacity) => updateTable.mutate({ id, name, capacity })}
                  onDeleteTable={(id) => deleteTable.mutate(id)}
                  onToggleTable={(id, is_active) => updateTable.mutate({ id, is_active })}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
