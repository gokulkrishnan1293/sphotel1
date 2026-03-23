/**
 * Sends the menu rate list directly to the local print agent (127.0.0.1:8766).
 * Formats as 48-char monospace text: name(28) + offline(10) + online(10).
 */
import type { MenuItemResponse } from '../features/admin/types/menu'

const LOCAL_PRINT_URL = 'http://127.0.0.1:8766/print'
const W = 48, NW = 28, PW = 10

type VpArr = { vendor_slug: string; price_paise: number }[] | undefined

function mp(s: string, w: number, right = false): string {
  const t = s.length > w ? s.slice(0, w) : s
  return right ? t.padStart(w) : t.padEnd(w)
}
function rp(paise: number | undefined): string {
  return paise != null ? `Rs.${paise / 100}` : '-'
}
function getOl(vps: VpArr): number | undefined {
  return vps?.find(v => v.vendor_slug === 'swiggy' || v.vendor_slug === 'zomato')?.price_paise
}

function buildText(items: MenuItemResponse[]): string {
  const L: string[] = []
  const title = 'MENU RATE LIST'
  L.push(title.padStart(Math.floor((W + title.length) / 2)).padEnd(W))
  L.push('='.repeat(W))
  L.push(mp('ITEM', NW) + mp('OFFLINE', PW, true) + mp('ONLINE', PW, true))
  L.push('-'.repeat(W))

  const byCategory: Record<string, MenuItemResponse[]> = {}
  for (const item of items) { ;(byCategory[item.category] ??= []).push(item) }

  for (const [cat, catItems] of Object.entries(byCategory)) {
    L.push('')
    L.push(mp(`«B»${cat.toUpperCase()}«/B»`, W))
    for (const item of catItems) {
      if (item.variants?.length) {
        L.push(mp(`«B»${item.name}«/B»`, W))
        for (const v of item.variants)
          L.push('  ' + mp(v.name, NW - 2) + mp(rp(v.price_paise), PW, true) + mp(rp(getOl(v.vendor_prices)), PW, true))
      } else {
        L.push(mp(item.name, NW) + mp(rp(item.price_paise), PW, true) + mp(rp(getOl(item.vendor_prices)), PW, true))
      }
    }
  }
  L.push('\n\n')
  return L.join('\n')
}

export async function localPrintMenu(items: MenuItemResponse[]): Promise<void> {
  const res = await fetch(LOCAL_PRINT_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ print_text: buildText(items), font_size: 1 }),
  })
  if (!res.ok) throw new Error('Print agent unavailable')
}
