import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ChefHat } from 'lucide-react'
import { kotApi } from '../api/kot'
import { KotCard } from '../components/KotCard'

export function KitchenPage() {
  const qc = useQueryClient()
  const { data: kots = [], isLoading } = useQuery({
    queryKey: ['kot', 'active'],
    queryFn: kotApi.listActive,
    refetchInterval: 10_000,
  })

  const markReady = useMutation({
    mutationFn: kotApi.markReady,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['kot', 'active'] }),
  })

  return (
    <div className="flex flex-col h-full">
      <header className="px-6 py-4 border-b border-sphotel-border bg-bg-surface shrink-0 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-text-primary">Kitchen Display</h1>
        <span className="text-xs px-2.5 py-1 rounded-full bg-status-warning/15 text-status-warning font-medium">{kots.length} pending</span>
      </header>

      <div className="flex-1 overflow-y-auto p-6 bg-bg-base">
        {isLoading ? (
          <p className="text-sm text-text-muted text-center py-12">Loading…</p>
        ) : kots.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 gap-3">
            <ChefHat size={40} className="text-text-muted opacity-40" />
            <p className="text-text-muted text-sm">No active orders — kitchen is clear</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {kots.map((kot) => (
              <KotCard key={kot.id} kot={kot}
                onMarkReady={(id) => markReady.mutate(id)}
                isMarking={markReady.isPending && markReady.variables === kot.id} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
