import axios, { type AxiosError, type AxiosInstance, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '../features/auth/stores/authStore'

interface ApiSuccessResponse<T> {
  data: T
  error: null
}

interface ApiErrorBody {
  code: string
  message: string
  details: Record<string, unknown>
}

interface ApiErrorResponse {
  data: null
  error: ApiErrorBody
}

type ApiEnvelope<T> = ApiSuccessResponse<T> | ApiErrorResponse

export const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL as string,
  headers: { 'Content-Type': 'application/json' },
  // httpOnly cookies for auth — no tokens in localStorage (Story 2.x)
  withCredentials: true,
})

// Attach X-Tenant-Override when super_admin has selected a tenant
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const { currentUser, selectedTenantSlug } = useAuthStore.getState()
  if (currentUser?.role === 'super_admin' && selectedTenantSlug) {
    config.headers['X-Tenant-Override'] = selectedTenantSlug
  }
  return config
})

// Unwrap { data, error } envelope — throw on API-level errors
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiEnvelope<unknown>>) => {
    const body = response.data
    if (typeof body !== 'object' || body === null) return response
    if (body.error != null) {
      throw new Error(body.error.message)
    }
    return { ...response, data: (body as ApiSuccessResponse<unknown>).data }
  },
  (error: AxiosError<ApiErrorResponse>) => {
    const apiMessage = error.response?.data?.error?.message
    if (apiMessage) {
      return Promise.reject(new Error(apiMessage))
    }
    return Promise.reject(error)
  },
)
