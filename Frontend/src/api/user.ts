const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface UserProfile {
  id: string
  clerk_id: string
  email: string
  telegram_id: number | null
  created_at: string
  is_active: boolean
}

const getHeaders = (token?: string | null): HeadersInit => ({
  'Content-Type': 'application/json',
  ...(token ? { Authorization: `Bearer ${token}` } : {}),
})

export const getUserMe = async (token?: string | null): Promise<UserProfile | null> => {
  try {
    const res = await fetch(`${API_URL}/user/me`, { headers: getHeaders(token) })
    if (!res.ok) {
      console.warn(`[getUserMe] HTTP ${res.status}: ${res.statusText}`)
      return null
    }
    const data = await res.json()
    console.log('[getUserMe] User loaded:', data.email, 'TG ID:', data.telegram_id)
    return data
  } catch (err) {
    console.error('[getUserMe] Network error:', err)
    return null
  }
}
