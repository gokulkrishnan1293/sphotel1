import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Plus, Trash, Wifi, WifiOff, Copy } from 'lucide-react'
import { printApi } from '../api/printSettings'

const inv = (qc: ReturnType<typeof useQueryClient>) => qc.invalidateQueries({ queryKey: ['print-agents'] })

export function PrintAgentCard() {
  const qc = useQueryClient()
  const { data: agents = [], isLoading } = useQuery({ queryKey: ['print-agents'], queryFn: printApi.listAgents })
  const register = useMutation({ mutationFn: printApi.registerAgentToken, onSuccess: () => inv(qc) })
  const revoke = useMutation({ mutationFn: printApi.revokeAgent, onSuccess: () => inv(qc) })
  const setRole = useMutation({ mutationFn: ({ id, role }: { id: string; role: 'main' | 'kot' }) => printApi.setAgentRole(id, role), onSuccess: () => inv(qc) })
  const [copiedToken, setCopiedToken] = useState<string | null>(null)

  function handleCopy(token: string) {
    navigator.clipboard.writeText(token)
    setCopiedToken(token)
    setTimeout(() => setCopiedToken(null), 2000)
  }

  return (
    <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">Print Agents</h2>
          <p className="text-sm text-text-muted mt-1">Manage printers. Set role to <strong>KOT</strong> for the kitchen printer.</p>
        </div>
        <button onClick={() => register.mutate()}
          className="flex items-center gap-2 bg-sphotel-accent text-bg-base px-4 py-2 rounded-lg text-sm font-medium hover:opacity-90">
          <Plus size={16} /><span>New Agent</span>
        </button>
      </div>

      {register.isError && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4 text-sm text-red-500">
          {(register.error as Error)?.message || 'Failed to generate token'}
        </div>
      )}

      {register.isSuccess && register.data && (
        <div className="bg-sphotel-accent-subtle border border-sphotel-accent rounded-lg p-4 mb-6">
          <h3 className="text-sphotel-accent font-semibold text-sm mb-2">Agent Registration Token</h3>
          <p className="text-sm text-text-muted mb-3">Copy this token and use it to register the print agent software. Valid for 24 hours, single use.</p>
          <div className="flex items-center gap-2 bg-bg-base border border-sphotel-border rounded p-2">
            <code className="text-sm font-mono flex-1 truncate text-text-primary">{register.data.token}</code>
            <button onClick={() => handleCopy(register.data.token)}
              className="p-1 sm:px-2 rounded bg-bg-elevated border border-sphotel-border text-xs text-text-primary flex items-center gap-1 hover:bg-bg-hover">
              <Copy size={14} /><span>{copiedToken === register.data.token ? 'Copied!' : 'Copy'}</span>
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <p className="text-sm text-text-muted">Loading agents...</p>
      ) : agents.length === 0 ? (
        <div className="text-center py-8 bg-bg-base border border-sphotel-border border-dashed rounded-lg">
          <p className="text-sm text-text-muted">No print agents registered.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {agents.map((agent) => (
            <div key={agent.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-bg-base border border-sphotel-border rounded-lg gap-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded bg-bg-elevated flex items-center justify-center">
                  {agent.status === 'online' ? <Wifi size={20} className="text-green-500" /> : <WifiOff size={20} className="text-text-muted" />}
                </div>
                <div>
                  <p className="font-medium text-text-primary">{agent.name}</p>
                  <p className="text-xs text-text-muted">
                    <span className={agent.status === 'online' ? 'text-green-500' : ''}>{agent.status}</span>
                    {agent.last_seen_at && ` · Last seen: ${new Date(agent.last_seen_at).toLocaleString()}`}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 sm:ml-auto">
                <div className="flex rounded-lg overflow-hidden border border-sphotel-border text-xs font-medium">
                  {(['main', 'kot'] as const).map((role) => (
                    <button key={role} onClick={() => setRole.mutate({ id: agent.id, role })}
                      className={`px-3 py-1.5 uppercase tracking-wide transition-colors ${agent.printer_role === role ? 'bg-sphotel-accent text-sphotel-accent-fg' : 'text-text-muted hover:text-text-primary'}`}>
                      {role}
                    </button>
                  ))}
                </div>
                <button onClick={() => confirm('Revoke this agent?') && revoke.mutate(agent.id)}
                  className="p-2 text-red-500/80 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors" title="Revoke Agent">
                  <Trash size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
