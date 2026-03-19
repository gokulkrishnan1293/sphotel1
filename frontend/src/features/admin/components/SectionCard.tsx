import { useState } from 'react'
import { Check, Pencil, Plus, Trash2, ChevronRight } from 'lucide-react'
import type { SectionResponse } from '../types/tables'
import { TableRow } from './TableRow'

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#f43f5e', '#06b6d4']
const INPUT = 'bg-bg-elevated border border-sphotel-border rounded-lg px-2 py-1 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-sphotel-accent'

interface Props {
  section: SectionResponse
  onDeleteSection: () => void
  onUpdateSection: (name: string, color: string) => void
  onAddTable: (name: string, capacity: number) => void
  onUpdateTable: (id: string, name: string, capacity: number) => void
  onDeleteTable: (id: string) => void
  onToggleTable: (id: string, is_active: boolean) => void
}

export function SectionCard({ section, onDeleteSection, onUpdateSection, onAddTable, onUpdateTable, onDeleteTable, onToggleTable }: Props) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const [editName, setEditName] = useState(section.name)
  const [editColor, setEditColor] = useState(section.color)
  const [adding, setAdding] = useState(false)
  const [newName, setNewName] = useState('')
  const [newCap, setNewCap] = useState('4')

  function saveSection() {
    if (editName.trim()) onUpdateSection(editName.trim(), editColor)
    setEditing(false)
  }

  function addTable() {
    if (!newName.trim()) return
    onAddTable(newName.trim(), Number(newCap) || 4)
    setNewName(''); setNewCap('4'); setAdding(false)
  }

  return (
    <div className="bg-bg-surface border border-sphotel-border rounded-xl overflow-hidden">
      <div className="flex items-center gap-3 px-4 py-3">
        {editing ? (
          <>
            <div className="flex gap-1 items-center">
              {COLORS.map((c) => (
                <button key={c} onClick={() => setEditColor(c)} style={{ backgroundColor: c }}
                  className={`w-4 h-4 rounded-full hover:scale-110 transition-transform ${editColor === c ? 'ring-2 ring-white ring-offset-1 scale-110' : ''}`} />
              ))}
            </div>
            <input className={`${INPUT} flex-1`} value={editName}
              onChange={(e) => setEditName(e.target.value)} autoFocus
              onKeyDown={(e) => { if (e.key === 'Enter') saveSection(); if (e.key === 'Escape') setEditing(false) }} />
            <button onClick={saveSection} className="p-1 text-sphotel-accent rounded hover:bg-sphotel-accent-subtle">
              <Check size={14} />
            </button>
          </>
        ) : (
          <>
            <button onClick={() => setExpanded((e) => !e)} className="flex items-center gap-3 flex-1 text-left hover:opacity-80 transition-opacity">
              <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: section.color }} />
              <span className="font-medium text-text-primary flex-1">{section.name}</span>
              <span className="text-xs text-text-muted">{section.tables.length} tables</span>
              <ChevronRight size={14} className={`text-text-muted transition-transform ${expanded ? 'rotate-90' : ''}`} />
            </button>
            <button onClick={() => { setEditName(section.name); setEditColor(section.color); setEditing(true) }}
              className="p-1 text-text-muted hover:text-text-primary rounded"><Pencil size={13} /></button>
            <button onClick={onDeleteSection} className="p-1 text-text-muted hover:text-status-error rounded"><Trash2 size={13} /></button>
          </>
        )}
      </div>

      {expanded && (
        <div className="border-t border-sphotel-border px-4 py-3 flex flex-col gap-2">
          {section.tables.map((t) => (
            <TableRow key={t.id} table={t}
              onDelete={() => onDeleteTable(t.id)}
              onToggle={(v) => onToggleTable(t.id, v)}
              onUpdate={(name, cap) => onUpdateTable(t.id, name, cap)} />
          ))}
          {adding ? (
            <div className="flex gap-2 mt-1">
              <input className={`${INPUT} flex-1`} placeholder="Table name" value={newName}
                onChange={(e) => setNewName(e.target.value)} autoFocus
                onKeyDown={(e) => { if (e.key === 'Enter') addTable(); if (e.key === 'Escape') setAdding(false) }} />
              <input className={`${INPUT} w-16`} placeholder="Cap" value={newCap}
                onChange={(e) => setNewCap(e.target.value)} inputMode="numeric" />
              <button onClick={addTable} disabled={!newName.trim()}
                className="px-3 py-1 bg-sphotel-accent text-sphotel-accent-fg rounded-lg text-sm disabled:opacity-50">Add</button>
              <button onClick={() => setAdding(false)} className="px-2 py-1 border border-sphotel-border rounded-lg text-sm text-text-secondary">✕</button>
            </div>
          ) : (
            <button onClick={() => setAdding(true)} className="flex items-center gap-1.5 text-sm text-sphotel-accent hover:text-sphotel-accent-hover py-1">
              <Plus size={14} /> Add table
            </button>
          )}
        </div>
      )}
    </div>
  )
}
