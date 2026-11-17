const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface Filter {
  id: string
  user_id: string
  name: string
  skills: string[]
  project_type: 'fixed' | 'hourly' | 'any'
  min_budget?: number | null
  min_hourly_rate?: number | null
  created_at: string
}

export type CreateFilterInput = {
  name: string
  skills?: string[]
  project_type?: 'fixed' | 'hourly' | 'any'
  min_budget?: number | null
  min_hourly_rate?: number | null
}

export type UpdateFilterInput = Partial<CreateFilterInput>

const getHeaders = (token?: string | null): HeadersInit => ({
  'Content-Type': 'application/json',
  ...(token ? { Authorization: `Bearer ${token}` } : {}),
})

// shortcut: generic Error thrown with detail/statusText, upgrade to custom ApiError if UI needs status codes
const checkOk = async (res: Response) => {
  if (!res.ok) {
    const data = await res.json().catch(() => null)
    throw new Error(data?.detail || `Request failed with status ${res.status}`)
  }
  return res
}

export const getFilter = async (token?: string | null): Promise<Filter | null> => {
  const res = await fetch(`${API_URL}/filter/`, { headers: getHeaders(token) })
  if (res.status === 404) return null
  await checkOk(res)
  return res.json()
}

export const createFilter = async (data: CreateFilterInput, token?: string | null): Promise<Filter> => {
  const res = await fetch(`${API_URL}/filter/`, {
    method: 'POST',
    headers: getHeaders(token),
    body: JSON.stringify(data),
  })
  await checkOk(res)
  return res.json()
}

export const updateFilter = async (data: UpdateFilterInput, token?: string | null): Promise<Filter> => {
  const res = await fetch(`${API_URL}/filter/`, {
    method: 'PATCH',
    headers: getHeaders(token),
    body: JSON.stringify(data),
  })
  await checkOk(res)
  return res.json()
}

export const deleteFilter = async (token?: string | null): Promise<void> => {
  const res = await fetch(`${API_URL}/filter/`, {
    method: 'DELETE',
    headers: getHeaders(token),
  })
  await checkOk(res)
}
