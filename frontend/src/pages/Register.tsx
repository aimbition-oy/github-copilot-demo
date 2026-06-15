import { useState, type FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { apiAuth } from '../lib/apiAuth'
import { useAuth } from '../lib/auth-context'
import { PixelButton } from '../components/PixelButton'

export function Register() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await apiAuth.register({ username, password })
      const { access_token } = await apiAuth.login({ username, password })
      const user = await apiAuth.me(access_token)
      login(access_token, user)
      navigate('/')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto' }}>
      <h2 className="nes-text is-primary">Register</h2>
      <div className="nes-container with-title">
        <p className="title">NEW PLAYER</p>
        <form onSubmit={handleSubmit}>
          <div className="nes-field" style={{ marginBottom: '1rem' }}>
            <label htmlFor="username">Username</label>
            <input
              id="username"
              className="nes-input"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
              autoComplete="username"
            />
          </div>
          <div className="nes-field" style={{ marginBottom: '1rem' }}>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="nes-input"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>
          {error && <p className="nes-text is-error">{error}</p>}
          <PixelButton type="submit" disabled={loading}>
            {loading ? 'Loading…' : 'Create Account'}
          </PixelButton>
        </form>
        <p style={{ marginTop: '1rem' }}>
          Already have an account? <Link to="/login">Login here</Link>
        </p>
      </div>
    </div>
  )
}
