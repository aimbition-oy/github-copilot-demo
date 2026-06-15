import { Link } from 'react-router-dom'
import type { Game } from '../lib/apiBackend'

interface Props {
  game: Game
}

export function GameCard({ game }: Props) {
  return (
    <div className="nes-container with-title" style={{ cursor: 'pointer' }}>
      <p className="title">{game.title}</p>
      <div style={{ textAlign: 'center' }}>
        <p className="nes-text is-disabled">{game.publisher} • {game.year}</p>
        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', marginTop: '0.5rem' }}>
          <Link to={`/leaderboard/${game.slug}`} className="nes-btn is-primary">Leaderboard</Link>
          <Link to={`/submit/${game.slug}`} className="nes-btn is-success">Submit Score</Link>
        </div>
      </div>
    </div>
  )
}
