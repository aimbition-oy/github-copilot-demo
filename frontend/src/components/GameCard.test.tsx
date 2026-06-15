import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { GameCard } from './GameCard'
import type { Game } from '../lib/apiBackend'

const MOCK_GAME: Game = {
  id: 1,
  slug: 'super-mario-bros',
  title: 'Super Mario Bros.',
  year: 1985,
  publisher: 'Nintendo',
  cover_art_path: 'covers/super-mario-bros.png',
}

describe('GameCard', () => {
  it('renders game title', () => {
    render(
      <BrowserRouter>
        <GameCard game={MOCK_GAME} />
      </BrowserRouter>
    )
    expect(screen.getByText('Super Mario Bros.')).toBeInTheDocument()
  })

  it('renders correct leaderboard link', () => {
    render(
      <BrowserRouter>
        <GameCard game={MOCK_GAME} />
      </BrowserRouter>
    )
    const link = screen.getByText('Leaderboard').closest('a')
    expect(link).toHaveAttribute('href', '/leaderboard/super-mario-bros')
  })

  it('renders correct submit score link', () => {
    render(
      <BrowserRouter>
        <GameCard game={MOCK_GAME} />
      </BrowserRouter>
    )
    const link = screen.getByText('Submit Score').closest('a')
    expect(link).toHaveAttribute('href', '/submit/super-mario-bros')
  })
})
