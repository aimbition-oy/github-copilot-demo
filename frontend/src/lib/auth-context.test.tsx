import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { AuthProvider, useAuth } from './auth-context'
import type { ReactNode } from 'react'

const wrapper = ({ children }: { children: ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
)

const MOCK_USER = { id: 1, username: 'player1', created_at: '2024-01-01T00:00:00' }
const MOCK_TOKEN = 'test-token'

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('useAuth', () => {
  it('initial state has null token and null user', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    expect(result.current.token).toBeNull()
    expect(result.current.user).toBeNull()
  })

  it('LOGIN action sets token and user', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    act(() => {
      result.current.login(MOCK_TOKEN, MOCK_USER)
    })
    expect(result.current.token).toBe(MOCK_TOKEN)
    expect(result.current.user).toEqual(MOCK_USER)
  })

  it('LOGOUT action clears token and user', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    act(() => {
      result.current.login(MOCK_TOKEN, MOCK_USER)
    })
    act(() => {
      result.current.logout()
    })
    expect(result.current.token).toBeNull()
    expect(result.current.user).toBeNull()
  })

  it('HYDRATE: restores state from localStorage on mount', () => {
    window.localStorage.setItem('arcade_token', JSON.stringify({ token: MOCK_TOKEN, user: MOCK_USER }))
    const { result } = renderHook(() => useAuth(), { wrapper })
    // State is hydrated synchronously from localStorage
    expect(result.current.token).toBe(MOCK_TOKEN)
    expect(result.current.user).toEqual(MOCK_USER)
  })

  it('AuthProvider renders children', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    expect(result.current).toBeDefined()
  })

  it('useAuth outside provider throws error', () => {
    // Suppress console.error for this test
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
    expect(() => renderHook(() => useAuth())).toThrow('useAuth must be used within AuthProvider')
    consoleError.mockRestore()
  })
})
