import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './lib/auth-context'
import { NavBar } from './components/NavBar'
import { Home } from './pages/Home'
import { Leaderboard } from './pages/Leaderboard'
import { SubmitScore } from './pages/SubmitScore'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import 'nes.css/css/nes.min.css'
import './styles/nes-overrides.css'

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div style={{ maxWidth: '900px', margin: '0 auto', padding: '1rem', fontFamily: '"Press Start 2P", monospace' }}>
          <NavBar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/leaderboard/:slug" element={<Leaderboard />} />
            <Route path="/submit/:slug" element={<SubmitScore />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}
