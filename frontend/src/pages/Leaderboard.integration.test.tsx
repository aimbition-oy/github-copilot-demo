import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '../lib/auth-context'
import { Leaderboard } from './Leaderboard'
import { server } from '../test/handlers'
import { http, HttpResponse } from 'msw'
import type { ReactNode } from 'react'

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <MemoryRouter initialEntries={['/leaderboard/super-mario-bros']}>
        <Routes>
          <Route path="/leaderboard/:slug" element={children} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>
  )
}

describe('Leaderboard page (integration)', () => {
  it('shows loading state initially', () => {
    render(<Leaderboard />, { wrapper: Wrapper })
    expect(screen.getByText('Loading…')).toBeInTheDocument()
  })

  it('renders leaderboard entries from mocked API', async () => {
    render(<Leaderboard />, { wrapper: Wrapper })
    await waitFor(() => {
      expect(screen.getByText('player1')).toBeInTheDocument()
      expect(screen.getByText('player2')).toBeInTheDocument()
    })
  })

  it('shows "No scores yet" when leaderboard is empty', async () => {
    server.use(
      http.get('http://localhost:8000/games/:slug/leaderboard', () =>
        HttpResponse.json([])
      )
    )
    render(<Leaderboard />, { wrapper: Wrapper })
    await waitFor(() => {
      expect(screen.getByText(/No scores yet/)).toBeInTheDocument()
    })
  })
})
