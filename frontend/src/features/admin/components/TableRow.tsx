import { useState } from 'react'
import { Check, Pencil, Trash2 } from 'lucide-react'
import type { TableResponse } from '../types/tables'

interface Props {
  table: TableResponse
  onDelete: () => void
  onToggle: (v: boolean) => void
  onUpdate: (name: string, cap: number) => void
}

export function TableRow({ table, onDelete, onToggle, onUpdate }: Props) {
  const [editing, setEditing] = useState(false)
  const [name, setName] = useState(table.name)
  const [cap, setCap] = useState(String(table.capacity))

  function save() {
    onUpdate(name.trim() || table.name, Number(cap) || table.capacity)
    setEditing(false)
  }

  if (editing) {
    return (
      <div className="flex items-center gap-2 py-1">
        <input
          className="bg-bg-elevated border border-sphotel-border rounded px-2 py-1 text-sm text-text-primary flex-1 focus:outline-none focus:ring-1 focus:ring-sphotel-accent"
          value={name} onChange={(e) => setName(e.target.value)} autoFocus
          onKeyDown={(e) => { if (e.key === 'Enter') save(); if (e.key === 'Escape') setEditing(false) }} />
        <input
          className="bg-bg-elevated border border-sphotel-border rounded px-2 py-1 text-sm text-text-primary w-14 focus:outline-none"
          value={cap} onChange={(e) => setCap(e.target.value)} inputMode="numeric" />
        <button onClick={save} className="p-1 text-sphotel-accent rounded hover:bg-sphotel-accent-subtle">
          <Check size={13} />
        </button>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 py-1.5 px-2 rounded-lg hover:bg-bg-base group">
      <span className="font-medium text-text-primary text-sm flex-1">{table.name}</span>
      <span className="text-xs text-text-muted">{table.capacity} seats</span>
      <button onClick={() => onToggle(!table.is_active)}
        className={`text-xs px-2 py-0.5 rounded-full font-medium transition-colors ${table.is_active ? 'bg-sphotel-accent-subtle text-sphotel-accent' : 'bg-bg-elevated text-text-muted'}`}>
        {table.is_active ? 'Active' : 'Inactive'}
      </button>
      <button onClick={() => setEditing(true)}
        className="opacity-0 group-hover:opacity-100 p-1 text-text-muted hover:text-text-primary rounded">
        <Pencil size={13} />
      </button>
      <button onClick={onDelete}
        className="opacity-0 group-hover:opacity-100 p-1 text-text-muted hover:text-status-error rounded">
        <Trash2 size={13} />
      </button>
    </div>
  )
}
