import { describe, it, expect } from 'vitest'
import { apiClient } from './api'

describe('apiClient', () => {
  it('is an axios instance with correct base config', () => {
    expect(apiClient.defaults.headers['Content-Type']).toBe('application/json')
    expect(apiClient.defaults.withCredentials).toBe(true)
  })
})
