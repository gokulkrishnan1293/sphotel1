import { render, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MenuItemsPage } from './MenuItemsPage'
import type { MenuItemResponse } from '../types/menu'

// Mock the API module so no real HTTP calls are made
vi.mock('../api/menu', () => ({
  menuApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}))

import { menuApi } from '../api/menu'

const MOCK_ITEMS: MenuItemResponse[] = [
  {
    id: 'item-uuid-1',
    tenant_id: 'testrestaurant',
    name: 'Chicken Biryani',
    category: 'Biryani Varities',
    short_code: 97,
    price_paise: 18000,
    food_type: 'non_veg',
    description: null,
    is_available: true,
    display_order: 1,
  },
  {
    id: 'item-uuid-2',
    tenant_id: 'testrestaurant',
    name: 'Idly [2 Nos]',
    category: 'Idli Varities',
    short_code: 1,
    price_paise: 2500,
    food_type: 'veg',
    description: null,
    is_available: false,
    display_order: 2,
  },
]

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('MenuItemsPage', () => {
  it('shows empty state when no items', async () => {
    vi.mocked(menuApi.list).mockResolvedValue([])
    const { getByText } = render(<MenuItemsPage />, { wrapper })
    await waitFor(() => {
      expect(getByText(/No menu items yet/i)).toBeTruthy()
    })
  })

  it('renders a list of menu items', async () => {
    vi.mocked(menuApi.list).mockResolvedValue(MOCK_ITEMS)
    const { getByText } = render(<MenuItemsPage />, { wrapper })
    await waitFor(() => {
      expect(getByText('Chicken Biryani')).toBeTruthy()
      expect(getByText('Idly [2 Nos]')).toBeTruthy()
    })
  })

  it('displays price in rupees', async () => {
    vi.mocked(menuApi.list).mockResolvedValue(MOCK_ITEMS)
    const { getByText } = render(<MenuItemsPage />, { wrapper })
    await waitFor(() => {
      expect(getByText('₹180')).toBeTruthy() // 18000 paise = ₹180
      expect(getByText('₹25')).toBeTruthy()  // 2500 paise = ₹25
    })
  })

  it('opens add form when Add Item button clicked', async () => {
    vi.mocked(menuApi.list).mockResolvedValue([])
    const { getByText } = render(<MenuItemsPage />, { wrapper })
    await waitFor(() => getByText('+ Add Item'))
    fireEvent.click(getByText('+ Add Item'))
    expect(getByText('Add Menu Item')).toBeTruthy()
  })

  it('opens edit form when row is clicked', async () => {
    vi.mocked(menuApi.list).mockResolvedValue(MOCK_ITEMS)
    const { getByText } = render(<MenuItemsPage />, { wrapper })
    await waitFor(() => getByText('Chicken Biryani'))
    fireEvent.click(getByText('Chicken Biryani'))
    expect(getByText('Edit Menu Item')).toBeTruthy()
  })

  it('shows delete confirmation dialog', async () => {
    vi.mocked(menuApi.list).mockResolvedValue(MOCK_ITEMS)
    const { getAllByText, getByText } = render(<MenuItemsPage />, { wrapper })
    await waitFor(() => getByText('Chicken Biryani'))
    const deleteButtons = getAllByText('Delete')
    fireEvent.click(deleteButtons[0])
    expect(
      getByText(/Are you sure you want to delete this menu item/i)
    ).toBeTruthy()
  })

  it('calls delete mutation on confirmation', async () => {
    vi.mocked(menuApi.list).mockResolvedValue(MOCK_ITEMS)
    vi.mocked(menuApi.delete).mockResolvedValue(undefined)
    const { getAllByText, getByText } = render(<MenuItemsPage />, { wrapper })
    await waitFor(() => getByText('Chicken Biryani'))
    const deleteButtons = getAllByText('Delete')
    fireEvent.click(deleteButtons[0])
    // Click confirm button in dialog
    const confirmBtn = getAllByText('Delete').find(
      (el) => el.closest('button') && el.closest('.fixed')
    )
    if (confirmBtn) fireEvent.click(confirmBtn)
    await waitFor(() => {
      expect(menuApi.delete).toHaveBeenCalledWith('item-uuid-1')
    })
  })
})
