import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

const AUTH_URL = 'http://localhost:8001'
const BACKEND_URL = 'http://localhost:8000'

export const MOCK_TOKEN = 'mock-jwt-token'
export const MOCK_USER = { id: 1, username: 'player1', created_at: '2024-01-01T00:00:00' }
export const MOCK_GAMES = [
  { id: 1, slug: 'super-mario-bros', title: 'Super Mario Bros.', year: 1985, publisher: 'Nintendo', cover_art_path: 'covers/super-mario-bros.png' },
  { id: 2, slug: 'contra', title: 'Contra', year: 1987, publisher: 'Konami', cover_art_path: 'covers/contra.png' },
]
export const MOCK_LEADERBOARD = [
  { rank: 1, username: 'player1', score: 99999, achieved_at: '2024-01-01T00:00:00' },
  { rank: 2, username: 'player2', score: 50000, achieved_at: '2024-01-01T00:00:00' },
]

export const handlers = [
  http.post(`${AUTH_URL}/register`, () =>
    HttpResponse.json(MOCK_USER, { status: 201 })
  ),
  http.post(`${AUTH_URL}/login`, () =>
    HttpResponse.json({ access_token: MOCK_TOKEN, token_type: 'bearer' })
  ),
  http.get(`${AUTH_URL}/me`, () =>
    HttpResponse.json(MOCK_USER)
  ),
  http.get(`${BACKEND_URL}/games`, () =>
    HttpResponse.json(MOCK_GAMES)
  ),
  http.get(`${BACKEND_URL}/games/:slug`, ({ params }) => {
    const game = MOCK_GAMES.find(g => g.slug === params.slug)
    if (!game) return HttpResponse.json({ detail: 'Not found' }, { status: 404 })
    return HttpResponse.json(game)
  }),
  http.get(`${BACKEND_URL}/games/:slug/leaderboard`, () =>
    HttpResponse.json(MOCK_LEADERBOARD)
  ),
  http.post(`${BACKEND_URL}/scores`, () =>
    HttpResponse.json({ id: 1, user_id: 1, username_cached: 'player1', game_id: 1, score: 9999, achieved_at: '2024-01-01T00:00:00' }, { status: 201 })
  ),
]

export const server = setupServer(...handlers)
