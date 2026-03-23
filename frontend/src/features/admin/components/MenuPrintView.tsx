import { useEffect } from 'react'
import { X, Printer } from 'lucide-react'
import type { MenuItemResponse } from '../types/menu'

interface Props { items: MenuItemResponse[]; onClose: () => void }

type VpArr = { vendor_slug: string; price_paise: number }[] | undefined
const getOnline = (vps: VpArr) =>
  vps?.find(v => v.vendor_slug === 'swiggy' || v.vendor_slug === 'zomato')?.price_paise

const S = { font: 'Courier New, monospace', size: '8pt', line: '13pt', col: '52px' as const }

function PriceRow({ name, paise, indent, vps }: { name: string; paise: number; indent?: boolean; vps: VpArr }) {
  const online = getOnline(vps)
  const cell = { fontFamily: S.font, fontSize: S.size, lineHeight: S.line }
  return (
    <tr>
      <td style={{ ...cell, paddingLeft: indent ? '10pt' : 0, overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>{name}</td>
      <td style={{ ...cell, textAlign: 'right', width: S.col, whiteSpace: 'nowrap' }}>₹{paise / 100}</td>
      <td style={{ ...cell, textAlign: 'right', width: S.col, whiteSpace: 'nowrap' }}>{online != null ? `₹${online / 100}` : '–'}</td>
    </tr>
  )
}

function buildContent(byCategory: Record<string, MenuItemResponse[]>) {
  const th = { fontFamily: S.font, fontSize: '7pt', textAlign: 'right' as const, width: S.col, paddingBottom: '2pt' }
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', tableLayout: 'fixed' }}>
      <thead>
        <tr style={{ borderBottom: '2px solid black' }}>
          <th style={{ ...th, textAlign: 'left', fontFamily: S.font, fontSize: '7pt' }}>ITEM</th>
          <th style={th}>OFFLINE</th>
          <th style={th}>ONLINE</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(byCategory).map(([cat, catItems]) => (
          <>
            <tr key={`h-${cat}`}><td colSpan={3} style={{ fontFamily: S.font, fontSize: '7pt', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid black', paddingTop: '5pt', paddingBottom: '1pt' }}>{cat}</td></tr>
            {catItems.map(item =>
              item.variants?.length
                ? [
                    <tr key={`p-${item.id}`}><td colSpan={3} style={{ fontFamily: S.font, fontSize: S.size, lineHeight: S.line, fontWeight: '600' }}>{item.name}</td></tr>,
                    ...item.variants.map(v => <PriceRow key={v.id ?? v.name} name={v.name} paise={v.price_paise} indent vps={v.vendor_prices} />)
                  ]
                : <PriceRow key={item.id} name={item.name} paise={item.price_paise} vps={item.vendor_prices} />
            )}
          </>
        ))}
      </tbody>
    </table>
  )
}

export function MenuPrintView({ items, onClose }: Props) {
  useEffect(() => {
    const s = document.createElement('style')
    s.textContent = `@media print { @page { size: 80mm auto; margin: 3mm 2mm; } body > *:not(#menu-rate-print) { display: none !important; } }`
    document.head.appendChild(s)
    return () => s.remove()
  }, [])

  const byCategory = items.reduce<Record<string, MenuItemResponse[]>>((acc, item) => {
    ;(acc[item.category] ??= []).push(item)
    return acc
  }, {})

  const title = <div style={{ textAlign: 'center', fontFamily: S.font, fontSize: '9pt', fontWeight: 'bold', marginBottom: '4pt' }}>MENU RATE LIST</div>

  return (
    <>
      <div id="menu-rate-print" className="hidden print:block fixed inset-0 bg-white z-[9999] p-1 overflow-auto">{title}{buildContent(byCategory)}</div>
      <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center print:hidden">
        <div className="bg-white dark:bg-bg-surface w-[460px] max-h-[90vh] flex flex-col rounded-xl shadow-2xl">
          <div className="flex items-center justify-between px-4 py-3 border-b border-sphotel-border shrink-0">
            <span className="font-semibold text-sm text-text-primary">Menu Rate List</span>
            <div className="flex gap-2">
              <button onClick={() => window.print()} className="flex items-center gap-1 text-xs border border-sphotel-border rounded px-2 py-1 text-text-secondary hover:text-text-primary"><Printer size={12} /> Print</button>
              <button onClick={onClose} className="text-text-muted hover:text-text-primary"><X size={16} /></button>
            </div>
          </div>
          <div className="overflow-auto p-4">{title}{buildContent(byCategory)}</div>
        </div>
      </div>
    </>
  )
}
