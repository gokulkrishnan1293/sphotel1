import { PrintTemplateConfig } from '../api/printSettings'

export function ReceiptPreview({ template, type }: { template: PrintTemplateConfig, type: 'receipt' | 'kot' | 'eod' }) {
  const W = type === 'receipt' ? template.receipt_width : type === 'eod' ? 42 : template.kot_width
  const fontSize = type === 'receipt' ? (template.receipt_font_size ?? 1) : type === 'eod' ? (template.eod_font_size ?? 1) : (template.kot_font_size ?? 1)
  const previewPx = 8 + (fontSize - 1) * 2

  const center = (text: string) => {
    if (!text) return ''
    const padding = Math.max(0, W - text.length)
    const left = Math.floor(padding / 2)
    return ' '.repeat(left) + text + ' '.repeat(padding - left)
  }
  const divider = (char: string) => char.repeat(W)
  const leftRight = (left: string, right: string) => {
    if (!left) return right
    if (!right) return left
    return left + ' '.repeat(Math.max(1, W - left.length - right.length)) + right
  }

  const items = [{ name: 'Parotta [1 Pc]', note: '--', qty: 4, price: '25.00', amount: '100.00' }]

  const lines: string[] = []
  const boldLines = new Set<number>()
  const push = (line: string) => lines.push(line)
  const pb = (line: string) => { boldLines.add(lines.length); lines.push(line) }

  if (type === 'kot') {
    push('28/02/26 14:44')
    if (template.show_token_no !== false) {
      const kotLine = leftRight('KOT - 46', 'Bill No.: 66')
      template.bold_kot_number ? pb(kotLine) : push(kotLine)
    }
    push('Pick Up')
    push(divider('.'))
    const iw = W - 20
    push(`Item${' '.repeat(Math.max(0, iw - 4))}Special Note  Qty.`)
    for (const item of items) {
      const itemLine = `${item.name.substring(0, iw).padEnd(iw)}${item.note.substring(0, 10).padEnd(12)}${item.qty.toString().padStart(4)}`
      template.bold_kot_items ? pb(itemLine) : push(itemLine)
    }
    push(divider('.'))
  } else if (type === 'eod') {
    push(center('*** EOD REPORT ***'))
    push(leftRight(template.restaurant_name || 'Hotel Name', '28 Feb 2026'))
    push(divider('='))
    if (template.eod_show_payment !== false) {
      template.bold_eod_headers ? pb(center('PAYMENT SUMMARY')) : push(center('PAYMENT SUMMARY'))
      push(divider('-'))
      push(leftRight('Cash', '12,540.00'))
      push(leftRight('UPI', '8,200.00'))
      push(leftRight('Online', '3,500.00'))
      push(divider('~'))
      push(leftRight('Total (48 bills)', '24,240.00'))
      push(divider('='))
    }
    if (template.eod_show_items !== false) {
      template.bold_eod_headers ? pb(center('ITEMS SOLD')) : push(center('ITEMS SOLD'))
      push(divider('-'))
      push(leftRight('Butter Chicken', 'x32'))
      push(leftRight('Parotta [1 Pc]', 'x24'))
      push(divider('='))
    }
    if (template.eod_show_waiters !== false) {
      template.bold_eod_headers ? pb(center('WAITER PERFORMANCE')) : push(center('WAITER PERFORMANCE'))
      push(divider('-'))
      push('Ravi         18 bills      9,800.00')
      push('Suresh       15 bills      8,100.00')
      push(divider('='))
    }
  } else {
    // Receipt
    const hpush = (line: string) => template.bold_header ? pb(line) : push(line)
    if (template.restaurant_name) hpush(center(template.restaurant_name))
    if (template.address_line_1) hpush(center(template.address_line_1))
    if (template.address_line_2) hpush(center(template.address_line_2))
    if (template.phone) hpush(center(`PH : ${template.phone}`))
    if (template.gst_number) hpush(center(`GST NO : ${template.gst_number}`))
    if (template.fssai_number) hpush(center(`FSSAI : ${template.fssai_number}`))
    if (template.show_name_field) push('Name: ___________________')
    push('')
    push(leftRight('Date: 28/02/26 19:04', 'Pick Up'))
    if (template.show_cashier) push('Cashier: Ravi')
    push('Waiter: Ravi')
    const tok = template.show_token_no ? 'Token No.: 85' : ''
    const bil = template.show_bill_no ? 'Bill No.: 66' : ''
    const tb = tok && bil ? leftRight(tok, bil) : tok || bil
    if (tb) push(tb)
    push(divider('-'))
    const iw = W - 22
    push(`Item${' '.repeat(Math.max(0, iw - 4))}  Qty.  Price   Amount`)
    push(divider('-'))
    for (const item of items) {
      push(`${item.name.substring(0, iw).padEnd(iw)}${item.qty.toString().padStart(4)}${item.price.padStart(7)}${item.amount.padStart(8)}`)
    }
    push(divider('-'))
    push(leftRight('Total Qty: 4', 'Sub Total 100.00'))
    push(divider('-'))
    const grandTotal = center('Grand Total   100.00')
    template.bold_total ? pb(grandTotal) : push(grandTotal)
    push(divider('-'))
    if (template.footer_message) push(center(template.footer_message))
  }

  return (
    <div className="bg-white p-4 sm:p-6 shadow-sm border border-sphotel-border w-auto inline-block min-w-full overflow-x-auto flex justify-center">
      <pre className="font-mono leading-tight text-black whitespace-pre break-normal" style={{ fontSize: `${previewPx}px` }}>
        {lines.map((line, i) => (
          <span key={i} style={boldLines.has(i) ? { fontWeight: 700 } : undefined}>{line}{'\n'}</span>
        ))}
      </pre>
    </div>
  )
}


