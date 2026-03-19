const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function pad(n: number) { return String(n).padStart(2, '0') }

function timeStr(hour: string, min: string): string | null {
  const h = parseInt(hour, 10)
  const m = parseInt(min, 10)
  if (isNaN(h)) return null
  return `${h}:${pad(isNaN(m) ? 0 : m)}`
}

export function describeCron(cron: string): string {
  if (!cron?.trim()) return ''
  const parts = cron.trim().split(/\s+/)
  if (parts.length !== 5) return cron
  const [min, hour, dom, , dow] = parts
  const t = timeStr(hour, min)

  if (dom !== '*' && dow === '*') {
    const suffix = dom === '1' ? 'st' : dom === '2' ? 'nd' : dom === '3' ? 'rd' : 'th'
    return `Monthly on the ${dom}${suffix}${t ? ` at ${t}` : ''}`
  }
  if (dow !== '*') {
    const names = dow.split(',').map((d) => DAYS[parseInt(d, 10)] ?? d).join(', ')
    return `Every ${names}${t ? ` at ${t}` : ''}`
  }
  if (t) return `Daily at ${t}`
  if (hour === '*' && min === '0') return 'Every hour'
  return cron
}
