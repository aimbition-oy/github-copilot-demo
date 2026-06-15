import { describe, it, expect } from 'vitest'
import { apiAuth } from './apiAuth'
import { MOCK_TOKEN } from '../test/handlers'

describe('apiAuth', () => {
  it('login() calls POST /login and returns token response', async () => {
    const result = await apiAuth.login({ username: 'player1', password: 'secret' })
    expect(result.access_token).toBe(MOCK_TOKEN)
    expect(result.token_type).toBe('bearer')
  })

  it('me(token) calls GET /me with Authorization header and returns user', async () => {
    const user = await apiAuth.me(MOCK_TOKEN)
    expect(user.username).toBe('player1')
    expect(user.id).toBe(1)
  })

  it('register() calls POST /register and returns user', async () => {
    const user = await apiAuth.register({ username: 'player1', password: 'secret' })
    expect(user.username).toBe('player1')
  })
})
