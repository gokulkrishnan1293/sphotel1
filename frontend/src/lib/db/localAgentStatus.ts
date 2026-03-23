import { useQuery } from '@tanstack/react-query'

async function checkLocalAgent(): Promise<boolean> {
  try {
    const res = await fetch('http://127.0.0.1:8766/health', {
      signal: AbortSignal.timeout(500),
    })
    return res.ok
  } catch {
    return false
  }
}

/**
 * Returns true if the print agent's local HTTP server responds on this machine.
 * Used to distinguish the restaurant machine from remote devices.
 */
export function useIsLocalMachine(): boolean {
  const { data } = useQuery({
    queryKey: ['local-agent-health'],
    queryFn: checkLocalAgent,
    retry: false,
    staleTime: 60_000,
    refetchInterval: 60_000,
  })
  return data ?? false
}
