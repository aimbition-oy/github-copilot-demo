import { createContext, useContext, useReducer, type ReactNode } from 'react'
import type { UserResponse } from './apiAuth'

interface AuthState {
  token: string | null
  user: UserResponse | null
}

type AuthAction =
  | { type: 'LOGIN'; token: string; user: UserResponse }
  | { type: 'LOGOUT' }
  | { type: 'HYDRATE'; token: string; user: UserResponse }

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN':
    case 'HYDRATE':
      return { token: action.token, user: action.user }
    case 'LOGOUT':
      return { token: null, user: null }
  }
}

interface AuthContextValue extends AuthState {
  login: (token: string, user: UserResponse) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

const STORAGE_KEY = 'arcade_token'

function safeStorage() {
  try {
    return typeof window !== 'undefined' ? window.localStorage : null
  } catch {
    return null
  }
}

function getInitialState(): AuthState {
  try {
    const stored = safeStorage()?.getItem(STORAGE_KEY)
    if (stored) {
      return JSON.parse(stored) as { token: string; user: UserResponse }
    }
  } catch {
    safeStorage()?.removeItem(STORAGE_KEY)
  }
  return { token: null, user: null }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, undefined, getInitialState)

  const login = (token: string, user: UserResponse) => {
    safeStorage()?.setItem(STORAGE_KEY, JSON.stringify({ token, user }))
    dispatch({ type: 'LOGIN', token, user })
  }

  const logout = () => {
    safeStorage()?.removeItem(STORAGE_KEY)
    dispatch({ type: 'LOGOUT' })
  }

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
