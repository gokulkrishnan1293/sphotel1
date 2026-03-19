import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, ShieldPlus } from 'lucide-react'
import { staffApi } from '../api/staff'
import { StaffForm } from '../components/StaffForm'
import { StaffRow } from '../components/StaffRow'
import { CreateAdminPanel } from '../components/CreateAdminPanel'
import { useAuthStore } from '@/features/auth/stores/authStore'
import type { AdminCreatedResponse, CreateAdminRequest, CreateStaffRequest, StaffResponse } from '../types/staff'

export function StaffPage() {
  const qc = useQueryClient()
  const isSuperAdmin = useAuthStore((s) => s.currentUser?.role === 'super_admin')
  const [showForm, setShowForm] = useState(false)
  const [showAdminForm, setShowAdminForm] = useState(false)
  const [adminResult, setAdminResult] = useState<AdminCreatedResponse | null>(null)
  const [editTarget, setEditTarget] = useState<StaffResponse | null>(null)

  const { data: staff = [], isLoading } = useQuery({ queryKey: ['staff'], queryFn: staffApi.list })
  const inv = () => qc.invalidateQueries({ queryKey: ['staff'] })

  const createMutation = useMutation({ mutationFn: (d: CreateStaffRequest) => staffApi.create(d), onSuccess: () => { inv(); setShowForm(false) } })
  const createAdminMutation = useMutation({
    mutationFn: (d: CreateAdminRequest) => staffApi.createAdmin(d),
    onSuccess: (data) => { inv(); setAdminResult(data) },
  })
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: CreateStaffRequest }) =>
      staffApi.update(id, { name: data.name, role: data.role, short_code: data.short_code }),
    onSuccess: () => { inv(); setEditTarget(null) },
  })
  const deleteMutation = useMutation({ mutationFn: (id: string) => staffApi.delete(id), onSuccess: inv })
  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) => staffApi.update(id, { is_active }),
    onSuccess: inv,
  })
  const resetPinMutation = useMutation({
    mutationFn: ({ id, pin }: { id: string; pin: string }) => staffApi.resetPin(id, { pin }),
    onSuccess: inv,
  })

  return (
    <div className="flex flex-col h-full">
      <header className="px-6 py-4 border-b border-sphotel-border bg-bg-surface shrink-0 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-text-primary">Staff</h1>
        <div className="flex items-center gap-2">
          {isSuperAdmin && (
            <button onClick={() => { setAdminResult(null); setShowAdminForm(true) }}
              className="flex items-center gap-1.5 px-3 py-2 border border-sphotel-border text-text-secondary rounded-lg text-sm font-medium hover:bg-bg-elevated transition-colors">
              <ShieldPlus size={14} /> Add Admin
            </button>
          )}
          <button onClick={() => setShowForm(true)}
            className="flex items-center gap-1.5 px-3 py-2 bg-sphotel-accent text-sphotel-accent-fg rounded-lg text-sm font-medium">
            <Plus size={14} /> Add Staff
          </button>
        </div>
      </header>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-3xl flex flex-col gap-6">
          {isLoading ? (
            <p className="text-sm text-text-muted">Loading…</p>
          ) : staff.filter((s) => s.role !== 'super_admin').length === 0 ? (
            <p className="text-sm text-text-muted">No staff yet.</p>
          ) : (
            <div className="flex flex-col gap-2">
              {staff.filter((s) => s.role !== 'super_admin').map((s) => (
                <StaffRow key={s.id} staff={s}
                  onEdit={() => setEditTarget(s)}
                  onToggle={() => toggleMutation.mutate({ id: s.id, is_active: !s.is_active })}
                  onDelete={() => { if (confirm(`Delete ${s.name}?`)) deleteMutation.mutate(s.id) }}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {showForm && <StaffForm onSubmit={(d) => createMutation.mutate(d)} onCancel={() => setShowForm(false)} isPending={createMutation.isPending} />}
      {editTarget && (
        <StaffForm editTarget={editTarget}
          onSubmit={(d) => { updateMutation.mutate({ id: editTarget.id, data: d }); if (d.pin.length >= 4) resetPinMutation.mutate({ id: editTarget.id, pin: d.pin }) }}
          onCancel={() => setEditTarget(null)} isPending={updateMutation.isPending}
        />
      )}
      {showAdminForm && (
        <CreateAdminPanel
          onSubmit={(d) => createAdminMutation.mutate(d)}
          onCancel={() => { setShowAdminForm(false); setAdminResult(null) }}
          isPending={createAdminMutation.isPending}
          result={adminResult}
        />
      )}
    </div>
  )
}
