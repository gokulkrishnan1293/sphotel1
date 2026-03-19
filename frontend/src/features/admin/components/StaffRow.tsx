import { Pencil, Trash2 } from 'lucide-react'
import type { StaffResponse } from '../types/staff'

const ROLE_LABELS: Record<string, string> = {
  waiter: 'Waiter', biller: 'Biller', kitchen_staff: 'Kitchen',
  manager: 'Manager', admin: 'Admin', super_admin: 'Super Admin',
}

interface Props {
  staff: StaffResponse
  onEdit: () => void
  onToggle: () => void
  onDelete: () => void
}

export function StaffRow({ staff, onEdit, onToggle, onDelete }: Props) {
  return (
    <div className="bg-bg-surface border border-sphotel-border rounded-xl flex items-center gap-3 px-4 py-3 group">
      <div className="w-8 h-8 rounded-full bg-sphotel-accent-subtle text-sphotel-accent flex items-center justify-center text-sm font-bold uppercase shrink-0">
        {staff.name[0]}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="font-medium text-text-primary text-sm truncate">{staff.name}</p>
          {staff.short_code != null && (
            <span className="text-[10px] font-mono bg-bg-elevated border border-sphotel-border text-text-muted px-1.5 py-0.5 rounded shrink-0">
              #{staff.short_code}
            </span>
          )}
        </div>
        <p className="text-xs text-text-muted">{ROLE_LABELS[staff.role] ?? staff.role}</p>
      </div>

      <button onClick={onToggle}
        className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 transition-colors ${staff.is_active ? 'bg-sphotel-accent-subtle text-sphotel-accent' : 'bg-bg-elevated text-text-muted'}`}>
        {staff.is_active ? 'Active' : 'Inactive'}
      </button>

      <button onClick={onEdit}
        className="opacity-0 group-hover:opacity-100 p-1.5 text-text-muted hover:text-text-primary rounded transition-opacity">
        <Pencil size={13} />
      </button>

      <button onClick={onDelete}
        className="opacity-0 group-hover:opacity-100 p-1.5 text-text-muted hover:text-status-error rounded transition-opacity">
        <Trash2 size={13} />
      </button>
    </div>
  )
}
