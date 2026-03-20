import { apiClient } from '../../../lib/api'

export interface PrintTemplateConfig {
  restaurant_name: string
  address_line_1: string
  address_line_2: string
  phone: string
  gst_number: string
  fssai_number: string
  footer_message: string
  show_name_field: boolean
  show_cashier: boolean
  show_token_no: boolean
  show_bill_no: boolean
  receipt_width: number
  kot_width: number
  receipt_font_size: number
  kot_font_size: number
  top_padding: number
  bottom_padding: number
}

export interface PrintAgent {
  id: string
  name: string
  status: string
  printer_role: string   // main | kot
  last_seen_at: string | null
  printer_config: any
}

export const printApi = {
  getTemplate: (): Promise<PrintTemplateConfig> =>
    apiClient.get('/api/v1/tenants/me/print-template').then((r) => r.data),

  updateTemplate: (body: Partial<PrintTemplateConfig>): Promise<PrintTemplateConfig> =>
    apiClient.patch('/api/v1/tenants/me/print-template', body).then((r) => r.data),

  listAgents: (): Promise<PrintAgent[]> =>
    apiClient.get('/api/v1/print/agents').then((r) => r.data),

  registerAgentToken: (): Promise<{ token: string; expires_in_seconds: number }> =>
    apiClient.post('/api/v1/print/agents/register-token').then((r) => r.data),

  revokeAgent: (id: string): Promise<void> =>
    apiClient.delete(`/api/v1/print/agents/${id}`).then(() => undefined),

  setAgentRole: (id: string, printer_role: 'main' | 'kot'): Promise<PrintAgent> =>
    apiClient.patch(`/api/v1/print/agents/${id}/role`, { printer_role }).then((r) => r.data),
}
