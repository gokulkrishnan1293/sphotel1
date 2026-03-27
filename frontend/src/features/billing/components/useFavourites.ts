const KEY = 'sphotel_item_freq'

function getFreq(): Record<string, number> {
  try { return JSON.parse(localStorage.getItem(KEY) ?? '{}') } catch { return {} }
}

export function recordItemOrder(itemId: string) {
  const freq = getFreq()
  freq[itemId] = (freq[itemId] ?? 0) + 1
  localStorage.setItem(KEY, JSON.stringify(freq))
}

export function getFavouriteIds(n = 16): string[] {
  return Object.entries(getFreq())
    .sort(([, a], [, b]) => b - a)
    .slice(0, n)
    .map(([id]) => id)
}
