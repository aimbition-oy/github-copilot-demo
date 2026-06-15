import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../lib/auth-context'
import { Login } from './Login'
import type { ReactNode } from 'react'

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <MemoryRouter initialEntries={['/login']}>{children}</MemoryRouter>
    </AuthProvider>
  )
}

describe('Login page (integration)', () => {
  it('renders the login form', () => {
    render(<Login />, { wrapper: Wrapper })
    expect(screen.getByLabelText('Username')).toBeInTheDocument()
    expect(screen.getByLabelText('Password')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /start game/i })).toBeInTheDocument()
  })

  it('submitting valid credentials calls login API', async () => {
    render(<Login />, { wrapper: Wrapper })
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'player1' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'secret' } })
    fireEvent.click(screen.getByRole('button', { name: /start game/i }))
    await waitFor(() => {
      // After successful login, loading disappears
      expect(screen.queryByText('Loading…')).not.toBeInTheDocument()
    })
  })

  it('failed login shows error message', async () => {
    // Override handler to return error
    const { server } = await import('../test/handlers')
    const { http, HttpResponse } = await import('msw')
    server.use(
      http.post('http://localhost:8001/login', () =>
        HttpResponse.json({ detail: 'Invalid credentials' }, { status: 401 })
      )
    )

    render(<Login />, { wrapper: Wrapper })
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'bad' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'wrong' } })
    fireEvent.click(screen.getByRole('button', { name: /start game/i }))

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
    })
  })
})
