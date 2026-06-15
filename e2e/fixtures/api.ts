/**
 * API fixtures for E2E test setup.
 * Uses the real APIs (no UI) to create test users, submit scores, and reset DB.
 * This keeps spec setup deterministic and fast.
 */

const AUTH_URL = process.env.AUTH_URL ?? 'http://localhost:8001'
const BACKEND_URL = process.env.BACKEND_URL ?? 'http://localhost:8000'

export interface TestUser {
  username: string
  password: string
  token: string
  userId: number
}

/** Register a fresh user and return their credentials + JWT. */
export async function createFreshUser(
  username = `testuser_${Date.now()}`,
  password = 'testpassword'
): Promise<TestUser> {
  const regRes = await fetch(`${AUTH_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!regRes.ok) {
    const err = await regRes.json()
    throw new Error(`Register failed: ${JSON.stringify(err)}`)
  }
  const user = await regRes.json()

  const loginRes = await fetch(`${AUTH_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  const { access_token } = await loginRes.json()

  return { username, password, token: access_token, userId: user.id }
}

/** Submit a score via API (no UI). */
export async function submitScoreViaApi(
  token: string,
  gameSlug: string,
  score: number
): Promise<void> {
  const res = await fetch(`${BACKEND_URL}/scores`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ game_slug: gameSlug, score }),
  })
  if (!res.ok) throw new Error(`Submit score failed: ${res.status}`)
}

/**
 * Reset the scores table via the test-only endpoint.
 * Only works when ENABLE_TEST_ENDPOINTS=1 (set in docker-compose.yml).
 */
export async function resetScores(): Promise<void> {
  const res = await fetch(`${BACKEND_URL}/test/scores`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`Reset scores failed: ${res.status}. Is ENABLE_TEST_ENDPOINTS=1?`)
}
