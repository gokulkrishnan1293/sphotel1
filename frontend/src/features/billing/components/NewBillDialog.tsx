import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { tablesApi } from '../../admin/api/tables'
import { staffApi } from '../../admin/api/staff'
import type { BillType } from '../types/bills'

const INPUT = 'bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent w-full'
type OnOpen = (data: { bill_type: BillType; table_id?: string | null; covers?: number | null; reference_no?: string | null; platform?: string | null; waiter_id?: string | null }) => void

export function NewBillDialog({ onOpen, onCancel, isLoading }: { onOpen: OnOpen; onCancel: () => void; isLoading: boolean }) {
  const [type, setType] = useState<BillType>('table')
  const [tableId, setTableId] = useState('')
  const [covers, setCovers] = useState('2')
  const [refNo, setRefNo] = useState('')
  const [platform, setPlatform] = useState('swiggy')
  const [waiterId, setWaiterId] = useState('')

  const { data: sections = [] } = useQuery({ queryKey: ['sections'], queryFn: tablesApi.listSections, enabled: type === 'table' })
  const { data: waiters = [] } = useQuery({ queryKey: ['waiters'], queryFn: staffApi.listWaiters })

  function submit() {
    const wid = waiterId || null
    if (type === 'table') onOpen({ bill_type: 'table', table_id: tableId || null, covers: Number(covers) || null, waiter_id: wid })
    else if (type === 'parcel') onOpen({ bill_type: 'parcel', waiter_id: wid })
    else onOpen({ bill_type: 'online', reference_no: refNo || null, platform: platform || null, waiter_id: wid })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onCancel} />
      <div className="relative bg-bg-surface border border-sphotel-border rounded-2xl shadow-2xl p-6 w-80 flex flex-col gap-4">
        <h2 className="font-semibold text-text-primary">New Bill</h2>

        <div className="flex gap-1">
          {(['table', 'parcel', 'online'] as const).map((t) => (
            <button key={t} onClick={() => setType(t)}
              className={`flex-1 py-2 rounded-lg text-xs font-medium capitalize transition-colors ${type === t ? 'bg-sphotel-accent text-sphotel-accent-fg' : 'bg-bg-elevated text-text-secondary hover:text-text-primary'}`}>
              {t}
            </button>
          ))}
        </div>

        {type === 'table' && (
          <>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-text-secondary font-medium">Table</label>
              <select className={INPUT} value={tableId} onChange={(e) => setTableId(e.target.value)}>
                <option value="">No table (quick bill)</option>
                {sections.map((s) => s.tables.filter((t) => t.is_active).map((t) => (
                  <option key={t.id} value={t.id}>{s.name} — {t.name} ({t.capacity} seats)</option>
                )))}
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-text-secondary font-medium">Covers (guests)</label>
              <input className={INPUT} type="number" min={1} value={covers} onChange={(e) => setCovers(e.target.value)} />
            </div>
          </>
        )}

        {type === 'online' && (
          <>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-text-secondary font-medium">Platform</label>
              <select className={INPUT} value={platform} onChange={(e) => setPlatform(e.target.value)}>
                <option value="swiggy">Swiggy</option>
                <option value="zomato">Zomato</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-text-secondary font-medium">Order Reference</label>
              <input className={INPUT} placeholder="e.g. SW123456" value={refNo} onChange={(e) => setRefNo(e.target.value)} />
            </div>
          </>
        )}

        <div className="flex flex-col gap-1">
          <label className="text-xs text-text-secondary font-medium">Waiter (optional)</label>
          <select className={INPUT} value={waiterId} onChange={(e) => setWaiterId(e.target.value)}>
            <option value="">Unassigned</option>
            {waiters.map((w) => <option key={w.id} value={w.id}>{w.name}</option>)}
          </select>
        </div>

        <div className="flex gap-2 pt-1">
          <button onClick={onCancel} className="flex-1 border border-sphotel-border rounded-lg py-2 text-sm text-text-secondary">Cancel</button>
          <button onClick={submit} disabled={isLoading} className="flex-1 bg-sphotel-accent text-sphotel-accent-fg rounded-lg py-2 text-sm font-medium disabled:opacity-50">
            {isLoading ? 'Opening…' : 'Open Bill'}
          </button>
        </div>
      </div>
    </div>
  )
}
