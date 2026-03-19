import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  type CreateStaffPayload,
  type ResetPinPayload,
  staffApi,
} from '../api/staff'

const STAFF_KEY = ['staff'] as const

export function useStaffList() {
  return useQuery({
    queryKey: STAFF_KEY,
    queryFn: staffApi.list,
  })
}

export function useCreateStaff() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: CreateStaffPayload) => staffApi.create(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: STAFF_KEY })
    },
  })
}

export function useResetPin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: ResetPinPayload }) =>
      staffApi.resetPin(id, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: STAFF_KEY })
    },
  })
}

export function useDeactivateStaff() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => staffApi.deactivate(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: STAFF_KEY })
    },
  })
}

export function useRevokeSessions() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => staffApi.revokeSessions(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: STAFF_KEY })
    },
  })
}
