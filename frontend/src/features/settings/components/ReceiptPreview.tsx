import { PrintTemplateConfig } from '../api/printSettings'

export function ReceiptPreview({ template, type }: { template: PrintTemplateConfig, type: 'receipt' | 'kot' }) {
  const W = type === 'receipt' ? template.receipt_width : template.kot_width

  // helper functions
  const center = (text: string) => {
    if (!text) return ''
    const padding = Math.max(0, W - text.length)
    const left = Math.floor(padding / 2)
    const right = padding - left
    return ' '.repeat(left) + text + ' '.repeat(right)
  }

  const divider = (char: string) => char.repeat(W)

  const leftRight = (left: string, right: string) => {
    if (!left) return right
    if (!right) return left
    const space = Math.max(1, W - left.length - right.length)
    return left + ' '.repeat(space) + right
  }

  const items = [
    { name: 'Parotta [1 Pc]', note: '--', qty: 4, price: '25.00', amount: '100.00' }
  ]

  let lines: string[] = []

  if (type === 'kot') {
    lines.push('28/02/26 14:44')
    if (template.show_token_no !== false) lines.push('KOT - 46') // Using token_no logic for kot no as it's not separated
    lines.push('Pick Up')
    lines.push(divider('.'))
    
    const iw = W - 20
    lines.push(`Item${' '.repeat(Math.max(0, iw - 4))}Special Note  Qty.`)
    for (const item of items) {
      const n = item.name.substring(0, iw).padEnd(iw, ' ')
      const nt = item.note.substring(0, 10).padEnd(12, ' ')
      const q = item.qty.toString().padStart(4, ' ')
      lines.push(`${n}${nt}${q}`)
    }
    lines.push(divider('.'))
  } else {
    // Receipt Header
    if (template.restaurant_name) lines.push(center(template.restaurant_name))
    if (template.address_line_1) lines.push(center(template.address_line_1))
    if (template.address_line_2) lines.push(center(template.address_line_2))
    if (template.phone) lines.push(center(`PH : ${template.phone}`))
    if (template.gst_number) lines.push(center(`GST NO : ${template.gst_number}`))
    if (template.fssai_number) lines.push(center(`FSSAI : ${template.fssai_number}`))
    
    if (template.show_name_field) lines.push('Name: ___________________')
    lines.push('')
    
    // Receipt Info
    lines.push(leftRight('Date: 28/02/26 19:04', 'Pick Up'))
    if (template.show_cashier) lines.push('Cashier: biller')
    
    let tb = ''
    if (template.show_token_no) tb += 'Token No.: 85'
    if (template.show_bill_no) {
       const b = 'Bill No.: 60626'
       tb = tb ? leftRight(tb, b) : b
    }
    if (tb) lines.push(tb)
    
    lines.push(divider('-'))
    
    // Columns
    const iw = W - 22
    lines.push(`Item${' '.repeat(Math.max(0, iw - 4))}  Qty.  Price   Amount`)
    lines.push(divider('-'))
    for (const item of items) {
      const n = item.name.substring(0, iw).padEnd(iw, ' ')
      const q = item.qty.toString().padStart(4, ' ')
      const p = item.price.padStart(7, ' ')
      const a = item.amount.padStart(8, ' ')
      lines.push(`${n}${q}${p}${a}`)
    }
    lines.push(divider('-'))
    
    // Totals
    lines.push(leftRight('Total Qty: 4', 'Sub Total 100.00'))
    lines.push(divider('-'))
    lines.push(center('Grand Total   100.00'))
    lines.push(divider('-'))
    
    if (template.footer_message) lines.push(center(template.footer_message))
  }

  return (
    <div className="bg-white p-4 sm:p-6 shadow-sm border border-sphotel-border w-auto inline-block min-w-full overflow-x-auto flex justify-center">
      <pre className="font-mono text-[13px] leading-tight text-black whitespace-pre break-normal">
        {lines.join('\n')}
      </pre>
    </div>
  )
}
