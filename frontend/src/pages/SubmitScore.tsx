import { useState, type FormEvent } from 'react'
import { useNavigate, useParams, Navigate } from 'react-router-dom'
import { apiBackend } from '../lib/apiBackend'
import { useAuth } from '../lib/auth-context'
import { PixelButton } from '../components/PixelButton'

export function SubmitScore() {
  const { slug } = useParams<{ slug: string }>()
  const { token } = useAuth()
  const navigate = useNavigate()
  const [score, setScore] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  if (!token) return <Navigate to="/login" replace />

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!slug || !token) return
    setLoading(true)
    setError(null)
    try {
      await apiBackend.submitScore(token, slug, parseInt(score, 10))
      navigate(`/leaderboard/${slug}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Submission failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto' }}>
      <h2 className="nes-text is-primary">Submit Score</h2>
      <div className="nes-container with-title">
        <p className="title">{slug}</p>
        <form onSubmit={handleSubmit}>
          <div className="nes-field" style={{ marginBottom: '1rem' }}>
            <label htmlFor="score">Your Score</label>
            <input
              id="score"
              type="number"
              min="0"
              className="nes-input"
              value={score}
              onChange={e => setScore(e.target.value)}
              required
              placeholder="e.g. 99999"
            />
          </div>
          {error && <p className="nes-text is-error">{error}</p>}
          <PixelButton type="submit" disabled={loading}>
            {loading ? 'Saving…' : '🚀 Submit'}
          </PixelButton>
        </form>
      </div>
    </div>
  )
}
