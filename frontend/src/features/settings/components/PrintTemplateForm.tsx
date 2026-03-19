import { type PrintTemplateConfig } from '../api/printSettings'
import { ReceiptPreview } from './ReceiptPreview'
import { useState } from 'react'

const L = 'block text-sm font-medium text-text-muted mb-1'
const I = 'w-full bg-bg-base border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-sphotel-accent'

interface Props { formData: PrintTemplateConfig; onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void }

export function PrintTemplateForm({ formData, onChange }: Props) {
  const [tab, setTab] = useState<'receipt' | 'kot'>('receipt')
  const tabCls = (t: 'receipt' | 'kot') =>
    `px-4 py-2 text-sm font-medium border-b-2 transition-colors ${tab === t ? 'border-sphotel-accent text-sphotel-accent' : 'border-transparent text-text-muted hover:text-text-primary'}`

  return (
    <div className="bg-bg-elevated border border-sphotel-border rounded-xl overflow-hidden">
      <div className="flex border-b border-sphotel-border px-2 pt-2">
        <button onClick={() => setTab('receipt')} className={tabCls('receipt')}>Full Receipt</button>
        <button onClick={() => setTab('kot')} className={tabCls('kot')}>KOT Slip</button>
      </div>
      <div className="p-6 flex flex-col lg:flex-row gap-10">
        <div className="flex-1 flex flex-col gap-5">
          {tab === 'receipt' ? (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div><label className={L}>Restaurant Name</label><input name="restaurant_name" value={formData.restaurant_name} onChange={onChange} className={I} /></div>
                <div><label className={L}>Paper Width</label>
                  <select name="receipt_width" value={formData.receipt_width} onChange={onChange} className={I}>
                    <option value={32}>58mm (32 chars)</option><option value={42}>80mm (42 chars)</option>
                  </select>
                </div>
                <div><label className={L}>Address Line 1</label><input name="address_line_1" value={formData.address_line_1} onChange={onChange} className={I} /></div>
                <div><label className={L}>Address Line 2</label><input name="address_line_2" value={formData.address_line_2} onChange={onChange} className={I} /></div>
                <div><label className={L}>Phone Number</label><input name="phone" value={formData.phone} onChange={onChange} className={I} /></div>
                <div><label className={L}>GST Number</label><input name="gst_number" value={formData.gst_number} onChange={onChange} className={I} /></div>
                <div><label className={L}>FSSAI Number</label><input name="fssai_number" value={formData.fssai_number} onChange={onChange} className={I} /></div>
                <div><label className={L}>Footer Message</label><input name="footer_message" value={formData.footer_message} onChange={onChange} className={I} /></div>
              </div>
              <div className="pt-4 border-t border-sphotel-border">
                <h3 className="text-sm font-medium text-text-primary mb-3">Visible Fields</h3>
                <div className="grid grid-cols-2 gap-3">
                  {([['show_name_field','Customer Name Blank'],['show_cashier','Cashier Name'],['show_token_no','Token Number'],['show_bill_no','Bill Number']] as const).map(([name, label]) => (
                    <label key={name} className="flex items-center gap-2 text-sm text-text-primary cursor-pointer">
                      <input type="checkbox" name={name} checked={formData[name as keyof PrintTemplateConfig] as boolean} onChange={onChange} className="accent-sphotel-accent" />{label}
                    </label>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div><label className={L}>KOT Paper Width</label>
                <select name="kot_width" value={formData.kot_width} onChange={onChange} className={I}>
                  <option value={32}>58mm (32 chars)</option><option value={42}>80mm (42 chars)</option>
                </select>
              </div>
              <div><label className={L}>Visible Fields</label>
                <div className="mt-2"><label className="flex items-center gap-2 text-sm text-text-primary cursor-pointer">
                  <input type="checkbox" name="show_token_no" checked={formData.show_token_no} onChange={onChange} className="accent-sphotel-accent" />Show KOT Number
                </label></div>
              </div>
            </div>
          )}
        </div>
        <div className="w-full lg:w-80 shrink-0 bg-bg-base p-4 rounded-xl border border-sphotel-border">
          <div className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">Live Preview</div>
          <ReceiptPreview template={formData} type={tab} />
        </div>
      </div>
    </div>
  )
}
