import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../../../lib/api'
import { TenantBadge } from '@/shared/components/layout/TenantBadge'

const INPUT = 'bg-bg-elevated border border-sphotel-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-sphotel-accent w-full'

async function fetchSettings() { return apiClient.get('/api/v1/telegram/settings').then((r) => r.data) }
async function saveSettings(d: { bot_token: string; chat_id: string }) { return apiClient.patch('/api/v1/telegram/settings', d).then((r) => r.data) }
async function sendTest() { return apiClient.post('/api/v1/telegram/test').then((r) => r.data) }
async function sendEod() { return apiClient.post('/api/v1/telegram/eod').then((r) => r.data) }

export function TelegramPage() {
  const qc = useQueryClient()
  const { data } = useQuery({ queryKey: ['telegram-settings'], queryFn: fetchSettings })
  const [token, setToken] = useState('')
  const [chatId, setChatId] = useState('')
  const [msg, setMsg] = useState('')

  const save = useMutation({ mutationFn: saveSettings, onSuccess: () => { qc.invalidateQueries({ queryKey: ['telegram-settings'] }); setMsg('Saved!') } })
  const test = useMutation({ mutationFn: sendTest, onSuccess: () => setMsg('Test message sent!'), onError: () => setMsg('Test failed — check settings.') })
  const eod = useMutation({ mutationFn: sendEod, onSuccess: () => setMsg('EOD report sent!'), onError: () => setMsg('Send failed.') })

  const currentToken = token || data?.bot_token || ''
  const currentChat = chatId || data?.chat_id || ''

  return (
    <div className="flex flex-col h-full">
      <header className="px-6 py-4 border-b border-sphotel-border bg-bg-surface shrink-0 flex items-center gap-3">
        <h1 className="text-lg font-semibold text-text-primary">Telegram Integration</h1>
        <TenantBadge />
      </header>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-lg flex flex-col gap-6">
          <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-5 flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-text-secondary">Bot Token</label>
              <input className={INPUT} type="password" placeholder="1234567890:ABC..." value={currentToken} onChange={(e) => setToken(e.target.value)} />
              <p className="text-xs text-text-muted">Create a bot via @BotFather on Telegram</p>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-text-secondary">Chat ID</label>
              <input className={INPUT} placeholder="-1001234567890 or @channelname" value={currentChat} onChange={(e) => setChatId(e.target.value)} />
              <p className="text-xs text-text-muted">Your personal chat ID or a group/channel ID</p>
            </div>
            <button onClick={() => save.mutate({ bot_token: currentToken, chat_id: currentChat })}
              disabled={save.isPending}
              className="bg-sphotel-accent text-sphotel-accent-fg rounded-lg py-2 text-sm font-medium disabled:opacity-50">
              {save.isPending ? 'Saving…' : 'Save Settings'}
            </button>
          </div>

          <div className="bg-bg-elevated border border-sphotel-border rounded-xl p-5 flex flex-col gap-3">
            <h2 className="text-sm font-medium text-text-primary">Actions</h2>
            <div className="flex gap-2">
              <button onClick={() => test.mutate()} disabled={test.isPending}
                className="flex-1 border border-sphotel-border rounded-lg py-2 text-sm text-text-secondary hover:border-sphotel-accent disabled:opacity-50">
                {test.isPending ? 'Sending…' : 'Send Test Message'}
              </button>
              <button onClick={() => eod.mutate()} disabled={eod.isPending}
                className="flex-1 border border-sphotel-border rounded-lg py-2 text-sm text-text-secondary hover:border-sphotel-accent disabled:opacity-50">
                {eod.isPending ? 'Sending…' : 'Send EOD Report Now'}
              </button>
            </div>
            {msg && <p className="text-xs text-sphotel-accent">{msg}</p>}
          </div>
        </div>
      </div>
    </div>
  )
}
