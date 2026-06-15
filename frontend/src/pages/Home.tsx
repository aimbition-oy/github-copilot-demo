import { useEffect, useState } from 'react'
import { GameCard } from '../components/GameCard'
import { apiBackend, type Game } from '../lib/apiBackend'

export function Home() {
  const [games, setGames] = useState<Game[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiBackend.games()
      .then(setGames)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="nes-text">Loading games…</p>
  if (error) return <p className="nes-text is-error">Error: {error}</p>

  return (
    <div>
      <h1 className="nes-text is-primary">🕹️ NES High-Score Arcade</h1>
      <p className="nes-text is-disabled">Select a game to view its leaderboard or submit your high score.</p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
        {games.map(g => <GameCard key={g.id} game={g} />)}
      </div>
    </div>
  )
}
