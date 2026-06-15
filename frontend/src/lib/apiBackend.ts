const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000'

export interface Game {
  id: number; slug: string; title: string; year: number;
  publisher: string; cover_art_path: string
}

export interface LeaderboardEntry {
  rank: number; username: string; score: number; achieved_at: string
}

export interface ScoreResponse {
  id: number; user_id: number; username_cached: string;
  game_id: number; score: number; achieved_at: string
}

function extractDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => (typeof d === 'object' && d !== null && 'msg' in d ? String(d.msg) : String(d))).join('; ')
  }
  return 'Request failed'
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw Object.assign(new Error(extractDetail(err.detail)), { status: res.status })
  }
  return res.json() as Promise<T>
}

export const apiBackend = {
  games: () => request<Game[]>(`${BACKEND_URL}/games`),
  game: (slug: string) => request<Game>(`${BACKEND_URL}/games/${slug}`),
  leaderboard: (slug: string, limit = 10) =>
    request<LeaderboardEntry[]>(`${BACKEND_URL}/games/${slug}/leaderboard?limit=${limit}`),
  submitScore: (token: string, gameSlug: string, score: number) =>
    request<ScoreResponse>(`${BACKEND_URL}/scores`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ game_slug: gameSlug, score }),
    }),
}
