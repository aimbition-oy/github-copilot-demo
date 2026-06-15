import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ScoreRow } from './ScoreRow'
import type { LeaderboardEntry } from '../lib/apiBackend'

function makeEntry(rank: number): LeaderboardEntry {
  return { rank, username: `player${rank}`, score: 10000 - rank * 100, achieved_at: '2024-01-01T00:00:00' }
}

describe('ScoreRow', () => {
  it('renders 🥇 for rank 1', () => {
    render(<table><tbody><ScoreRow entry={makeEntry(1)} /></tbody></table>)
    expect(screen.getByText('🥇')).toBeInTheDocument()
  })

  it('renders 🥈 for rank 2', () => {
    render(<table><tbody><ScoreRow entry={makeEntry(2)} /></tbody></table>)
    expect(screen.getByText('🥈')).toBeInTheDocument()
  })

  it('renders 🥉 for rank 3', () => {
    render(<table><tbody><ScoreRow entry={makeEntry(3)} /></tbody></table>)
    expect(screen.getByText('🥉')).toBeInTheDocument()
  })

  it('renders #N for rank > 3', () => {
    render(<table><tbody><ScoreRow entry={makeEntry(4)} /></tbody></table>)
    expect(screen.getByText('#4')).toBeInTheDocument()
  })

  it('renders username and score', () => {
    render(<table><tbody><ScoreRow entry={makeEntry(1)} /></tbody></table>)
    expect(screen.getByText('player1')).toBeInTheDocument()
    // score is 9900, toLocaleString may vary, just check it's present
    expect(screen.getByText(/9[,.]?900/)).toBeInTheDocument()
  })
})
