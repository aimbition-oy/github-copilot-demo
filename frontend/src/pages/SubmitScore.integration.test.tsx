import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '../lib/auth-context'
import { SubmitScore } from './SubmitScore'
import type { ReactNode } from 'react'

function UnauthWrapper({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <MemoryRouter initialEntries={['/submit/super-mario-bros']}>
        <Routes>
          <Route path="/submit/:slug" element={children} />
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>
  )
}

describe('SubmitScore page (integration)', () => {
  it('redirects to /login when no token (unauthenticated)', () => {
    render(<SubmitScore />, { wrapper: UnauthWrapper })
    expect(screen.getByText('Login Page')).toBeInTheDocument()
  })

  it('shows the submit form when authenticated', async () => {
    window.localStorage.setItem(
      'arcade_token',
      JSON.stringify({ token: 'test-token', user: { id: 1, username: 'player1', created_at: '2024-01-01T00:00:00' } })
    )
    render(<SubmitScore />, { wrapper: UnauthWrapper })
    await waitFor(() => {
      expect(screen.getByLabelText('Your Score')).toBeInTheDocument()
    })
  })

  it('submitting navigates to leaderboard', async () => {
    window.localStorage.setItem(
      'arcade_token',
      JSON.stringify({ token: 'test-token', user: { id: 1, username: 'player1', created_at: '2024-01-01T00:00:00' } })
    )

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/submit/super-mario-bros']}>
          <Routes>
            <Route path="/submit/:slug" element={<SubmitScore />} />
            <Route path="/leaderboard/:slug" element={<div>Leaderboard Page</div>} />
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByLabelText('Your Score')).toBeInTheDocument()
    })

    fireEvent.change(screen.getByLabelText('Your Score'), { target: { value: '9999' } })
    fireEvent.click(screen.getByRole('button', { name: /submit/i }))
    await waitFor(() => {
      expect(screen.getByText('Leaderboard Page')).toBeInTheDocument()
    })
  })
})
