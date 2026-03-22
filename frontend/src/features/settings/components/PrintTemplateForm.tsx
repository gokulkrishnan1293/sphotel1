import { type PrintTemplateConfig } from '../api/printSettings'
import { ReceiptPreview } from './ReceiptPreview'
import { useState } from 'react'

const L = 'block text-sm font-medium text-text-muted mb-1'
const I = 'w-full bg-bg-base border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-sphotel-accent'

interface Props { formData: PrintTemplateConfig; onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void }

export function PrintTemplateForm({ formData, onChange }: Props) {
  const [tab, setTab] = useState<'receipt' | 'kot' | 'eod'>('receipt')
  const tabCls = (t: 'receipt' | 'kot' | 'eod') =>
    `px-4 py-2 text-sm font-medium border-b-2 transition-colors ${tab === t ? 'border-sphotel-accent text-sphotel-accent' : 'border-transparent text-text-muted hover:text-text-primary'}`

  return (
    <div className="bg-bg-elevated border border-sphotel-border rounded-xl overflow-hidden">
      <div className="flex border-b border-sphotel-border px-2 pt-2">
        <button onClick={() => setTab('receipt')} className={tabCls('receipt')}>Full Receipt</button>
        <button onClick={() => setTab('kot')} className={tabCls('kot')}>KOT Slip</button>
        <button onClick={() => setTab('eod')} className={tabCls('eod')}>EOD Report</button>
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
                <div><label className={L}>Font Size</label>
                  <div className="flex items-center gap-3 mt-1">
                    <input type="range" name="receipt_font_size" min={1} max={8} step={1} value={formData.receipt_font_size} onChange={onChange} className="flex-1 accent-sphotel-accent" />
                    <input type="number" name="receipt_font_size" min={1} max={8} value={formData.receipt_font_size} onChange={onChange} className={`${I} w-16 text-center`} />
                  </div>
                  <div className="flex justify-between text-xs text-text-muted mt-0.5"><span>1× Normal</span><span>8× Max</span></div>
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
              <div className="pt-4 border-t border-sphotel-border">
                <h3 className="text-sm font-medium text-text-primary mb-3">Bold Options</h3>
                <div className="grid grid-cols-2 gap-3">
                  {([['bold_header','Hotel Name'],['bold_total','Grand Total']] as const).map(([name, label]) => (
                    <label key={name} className="flex items-center gap-2 text-sm text-text-primary cursor-pointer">
                      <input type="checkbox" name={name} checked={!!formData[name as keyof PrintTemplateConfig]} onChange={onChange} className="accent-sphotel-accent" />{label}
                    </label>
                  ))}
                </div>
              </div>
            </>
          ) : tab === 'kot' ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div><label className={L}>KOT Paper Width</label>
                <select name="kot_width" value={formData.kot_width} onChange={onChange} className={I}>
                  <option value={32}>58mm (32 chars)</option><option value={42}>80mm (42 chars)</option>
                </select>
              </div>
              <div><label className={L}>Font Size</label>
                <div className="flex items-center gap-3 mt-1">
                  <input type="range" name="kot_font_size" min={1} max={8} step={1} value={formData.kot_font_size} onChange={onChange} className="flex-1 accent-sphotel-accent" />
                  <input type="number" name="kot_font_size" min={1} max={8} value={formData.kot_font_size} onChange={onChange} className={`${I} w-16 text-center`} />
                </div>
                <div className="flex justify-between text-xs text-text-muted mt-0.5"><span>1× Normal</span><span>8× Max</span></div>
              </div>
              <div><label className={L}>Visible Fields</label>
                <div className="mt-2"><label className="flex items-center gap-2 text-sm text-text-primary cursor-pointer">
                  <input type="checkbox" name="show_token_no" checked={formData.show_token_no} onChange={onChange} className="accent-sphotel-accent" />Show KOT Number
                </label></div>
              </div>
              <div><label className={L}>Bold Options</label>
                <div className="mt-2 flex flex-col gap-2">
                  {([['bold_kot_number','KOT Number Line'],['bold_kot_items','Item Names']] as const).map(([name, label]) => (
                    <label key={name} className="flex items-center gap-2 text-sm text-text-primary cursor-pointer">
                      <input type="checkbox" name={name} checked={!!formData[name as keyof PrintTemplateConfig]} onChange={onChange} className="accent-sphotel-accent" />{label}
                    </label>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="pt-4">
              <h3 className="text-sm font-medium text-text-primary mb-3">EOD Report Sections</h3>
              <p className="text-xs text-text-muted mb-4">Toggle which sections appear on the thermal printout and Telegram PDF for the end-of-day report.</p>
              <div className="flex flex-col gap-3">
                {[['eod_show_payment', 'Payment Mode Summary'], ['eod_show_items', 'All Items Sold Today'], ['eod_show_waiters', 'Waiter Performance']].map(([name, label]) => (
                  <label key={name} className="flex items-center gap-2 text-sm text-text-primary cursor-pointer w-fit">
                    <input type="checkbox" name={name} checked={formData[name as keyof PrintTemplateConfig] as boolean} onChange={onChange} className="accent-sphotel-accent shadow-sm" />{label}
                  </label>
                ))}
              </div>
              <div className="mt-4">
                <h3 className="text-sm font-medium text-text-primary mb-3">Bold Options</h3>
                <label className="flex items-center gap-2 text-sm text-text-primary cursor-pointer">
                  <input type="checkbox" name="bold_eod_headers" checked={!!formData.bold_eod_headers} onChange={onChange} className="accent-sphotel-accent" />Section Headers
                </label>
              </div>
              <div className="mt-5"><label className="block text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">Font Size</label>
                <div className="flex items-center gap-3 mt-1">
                  <input type="range" name="eod_font_size" min={1} max={8} step={1} value={formData.eod_font_size} onChange={onChange} className="flex-1 accent-sphotel-accent" />
                  <input type="number" name="eod_font_size" min={1} max={8} value={formData.eod_font_size} onChange={onChange} className="bg-bg-elevated border border-sphotel-border text-text-primary rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sphotel-accent focus:border-transparent transition-all w-16 text-center" />
                </div>
                <div className="flex justify-between text-xs text-text-muted mt-0.5"><span>1× Normal</span><span>8× Max</span></div>
              </div>
            </div>
          )}
          <div className="pt-4 border-t border-sphotel-border">
            <h3 className="text-sm font-medium text-text-primary mb-3">Paper Padding (blank lines)</h3>
            <div className="grid grid-cols-2 gap-5">
              <div><label className={L}>Top Padding</label><input type="number" name="top_padding" value={formData.top_padding} min={0} max={10} onChange={onChange} className={I} /></div>
              <div><label className={L}>Bottom Padding</label><input type="number" name="bottom_padding" value={formData.bottom_padding} min={0} max={15} onChange={onChange} className={I} /></div>
            </div>
          </div>
        </div>
        <div className="w-full lg:w-80 shrink-0 bg-bg-base p-4 rounded-xl border border-sphotel-border">
          <div className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">Live Preview</div>
          <ReceiptPreview template={formData} type={tab} />
        </div>
      </div>
    </div>
  )
}
