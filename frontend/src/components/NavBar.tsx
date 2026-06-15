import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth-context'
import { PixelButton } from './PixelButton'

export function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="nes-container" style={{ marginBottom: '1rem', padding: '0.5rem 1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Link to="/" className="nes-text is-primary" style={{ textDecoration: 'none', fontSize: '1.2rem' }}>
          🕹️ Arcade
        </Link>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          {user ? (
            <>
              <span className="nes-text">👤 {user.username}</span>
              <PixelButton variant="error" onClick={handleLogout}>Logout</PixelButton>
            </>
          ) : (
            <>
              <Link to="/login" className="nes-btn is-primary" style={{ textDecoration: 'none' }}>Login</Link>
              <Link to="/register" className="nes-btn" style={{ textDecoration: 'none' }}>Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
