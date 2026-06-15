import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '../lib/auth-context'
import { NavBar } from './NavBar'
import type { ReactNode } from 'react'

const MOCK_USER = { id: 1, username: 'player1', created_at: '2024-01-01T00:00:00' }
const MOCK_TOKEN = 'test-token'

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <BrowserRouter>{children}</BrowserRouter>
    </AuthProvider>
  )
}

describe('NavBar', () => {
  it('renders login and register links when not logged in', () => {
    render(<NavBar />, { wrapper: Wrapper })
    expect(screen.getByText('Login')).toBeInTheDocument()
    expect(screen.getByText('Register')).toBeInTheDocument()
  })

  it('renders username and logout button when logged in', async () => {
    window.localStorage.setItem('arcade_token', JSON.stringify({ token: MOCK_TOKEN, user: MOCK_USER }))
    render(<NavBar />, { wrapper: Wrapper })
    await waitFor(() => {
      expect(screen.getByText(/player1/)).toBeInTheDocument()
    })
    expect(screen.getByText('Logout')).toBeInTheDocument()
  })

  it('clicking logout clears auth state', async () => {
    window.localStorage.setItem('arcade_token', JSON.stringify({ token: MOCK_TOKEN, user: MOCK_USER }))
    render(<NavBar />, { wrapper: Wrapper })
    await waitFor(() => {
      expect(screen.getByText('Logout')).toBeInTheDocument()
    })
    fireEvent.click(screen.getByText('Logout'))
    expect(window.localStorage.getItem('arcade_token')).toBeNull()
  })
})
