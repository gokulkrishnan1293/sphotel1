import { apiClient } from '../../../lib/api'

export interface ChecklistItem {
  key: string
  label: string
  completed: boolean
  route: string
}

export interface OnboardingStatus {
  completed: boolean
  items: ChecklistItem[]
}

export const onboardingApi = {
  getStatus: (): Promise<OnboardingStatus> =>
    apiClient
      .get<OnboardingStatus>('/api/v1/tenants/me/onboarding')
      .then((r) => r.data),

  complete: (): Promise<unknown> =>
    apiClient
      .post<unknown>('/api/v1/tenants/me/onboarding/complete')
      .then((r) => r.data),
}
