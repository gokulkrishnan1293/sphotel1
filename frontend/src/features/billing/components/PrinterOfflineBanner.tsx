interface Props {
  printerOnline: boolean
  isLocalMachine: boolean
}

/**
 * Shown when the print agent is offline.
 * - Restaurant machine (isLocalMachine): warns but allows full billing.
 * - Other devices: warns that new bills are blocked until the printer agent reconnects.
 */
export function PrinterOfflineBanner({ printerOnline, isLocalMachine }: Props) {
  if (printerOnline) return null

  return (
    <div className="px-4 py-2 bg-amber-500/10 border-b border-amber-500/20 text-xs text-amber-500 flex items-center gap-2">
      <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse shrink-0" />
      {isLocalMachine
        ? 'Printer agent offline — receipts will print locally. Bills will sync when reconnected.'
        : 'Printer agent offline — new bills cannot be opened from this device until the printer reconnects.'}
    </div>
  )
}
