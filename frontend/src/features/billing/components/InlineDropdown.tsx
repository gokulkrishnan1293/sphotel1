interface Item { key: string; label: React.ReactNode }
interface Props { items: Item[]; activeIdx: number; onSelect: (key: string) => void }

export function InlineDropdown({ items, activeIdx, onSelect }: Props) {
  return (
    <div className="absolute top-full mt-1 left-0 right-0 bg-bg-elevated border border-sphotel-border rounded-lg shadow-xl z-20 overflow-hidden max-h-52 overflow-y-auto">
      {items.map((item, i) => (
        <button key={item.key} type="button" onMouseDown={() => onSelect(item.key)}
          className={`w-full text-left px-3 py-2 text-sm transition-colors ${i === activeIdx ? 'bg-sphotel-accent-subtle text-sphotel-accent' : 'hover:bg-bg-base text-text-primary'}`}>
          {item.label}
        </button>
      ))}
    </div>
  )
}
