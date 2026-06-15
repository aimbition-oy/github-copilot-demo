const AUTH_URL = import.meta.env.VITE_AUTH_URL ?? 'http://localhost:8001'

export interface RegisterData { username: string; password: string }
export interface LoginData { username: string; password: string }
export interface TokenResponse { access_token: string; token_type: string }
export interface UserResponse { id: number; username: string; created_at: string }

function extractDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail
  // FastAPI 422 validation errors: detail is an array of {msg, loc, ...}
  if (Array.isArray(detail)) {
    return detail.map((d) => (typeof d === 'object' && d !== null && 'msg' in d ? String(d.msg) : String(d))).join('; ')
  }
  return 'Request failed'
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw Object.assign(new Error(extractDetail(err.detail)), { status: res.status })
  }
  return res.json() as Promise<T>
}

export const apiAuth = {
  register: (data: RegisterData) =>
    request<UserResponse>(`${AUTH_URL}/register`, { method: 'POST', body: JSON.stringify(data) }),

  login: (data: LoginData) =>
    request<TokenResponse>(`${AUTH_URL}/login`, { method: 'POST', body: JSON.stringify(data) }),

  me: (token: string) =>
    request<UserResponse>(`${AUTH_URL}/me`, { headers: { Authorization: `Bearer ${token}` } }),
}
