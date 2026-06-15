import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ScoreRow } from '../components/ScoreRow'
import { apiBackend, type LeaderboardEntry } from '../lib/apiBackend'

export function Leaderboard() {
  const { slug } = useParams<{ slug: string }>()
  const [entries, setEntries] = useState<LeaderboardEntry[]>([])
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!slug) return
    Promise.all([apiBackend.game(slug), apiBackend.leaderboard(slug)])
      .then(([game, board]) => { setTitle(game.title); setEntries(board) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) return <p className="nes-text">Loading…</p>
  if (error) return <p className="nes-text is-error">Error: {error}</p>

  return (
    <div>
      <h2 className="nes-text is-primary">{title} — Top Scores</h2>
      {entries.length === 0 ? (
        <p className="nes-text is-disabled">No scores yet. Be the first!</p>
      ) : (
        <div className="nes-table-responsive">
          <table className="nes-table is-bordered is-centered" style={{ width: '100%' }}>
            <thead>
              <tr>
                <th>Rank</th><th>Player</th><th>Score</th><th>Date</th>
              </tr>
            </thead>
            <tbody>
              {entries.map(e => <ScoreRow key={e.rank} entry={e} />)}
            </tbody>
          </table>
        </div>
      )}
      <Link to={`/submit/${slug}`} className="nes-btn is-success" style={{ marginTop: '1rem', display: 'inline-block' }}>
        Submit Your Score
      </Link>
    </div>
  )
}
