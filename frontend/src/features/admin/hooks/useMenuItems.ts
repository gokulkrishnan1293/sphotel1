import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { menuApi } from '../api/menu'
import type { MenuItemCreate, MenuItemUpdate } from '../types/menu'

export const MENU_ITEMS_KEY = ['menu-items'] as const

export function useMenuItems() {
  return useQuery({
    queryKey: MENU_ITEMS_KEY,
    queryFn: menuApi.list,
  })
}

export function useCreateMenuItem() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: MenuItemCreate) => menuApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: MENU_ITEMS_KEY }),
  })
}

export function useUpdateMenuItem() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: MenuItemUpdate }) =>
      menuApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: MENU_ITEMS_KEY }),
  })
}

export function useDeleteMenuItem() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => menuApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: MENU_ITEMS_KEY }),
  })
}
