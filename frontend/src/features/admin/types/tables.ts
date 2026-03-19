export interface SectionResponse {
  id: string
  name: string
  color: string
  position: number
  tables: TableResponse[]
}

export interface TableResponse {
  id: string
  section_id: string
  name: string
  capacity: number
  is_active: boolean
  position: number
}

export interface SectionCreate {
  name: string
  color?: string
  position?: number
}

export interface TableCreate {
  section_id: string
  name: string
  capacity?: number
  is_active?: boolean
  position?: number
}

export interface TableUpdate {
  name?: string
  capacity?: number
  is_active?: boolean
  position?: number
  section_id?: string
}
