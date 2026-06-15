import { describe, it, expect } from 'vitest'
import { apiBackend } from './apiBackend'
import { MOCK_TOKEN } from '../test/handlers'

describe('apiBackend', () => {
  it('games() fetches GET /games and returns game list', async () => {
    const games = await apiBackend.games()
    expect(games).toHaveLength(2)
    expect(games[0].slug).toBe('super-mario-bros')
  })

  it('game(slug) fetches GET /games/:slug and returns game', async () => {
    const game = await apiBackend.game('super-mario-bros')
    expect(game.title).toBe('Super Mario Bros.')
  })

  it('leaderboard(slug) fetches GET /games/:slug/leaderboard', async () => {
    const entries = await apiBackend.leaderboard('super-mario-bros')
    expect(entries).toHaveLength(2)
    expect(entries[0].rank).toBe(1)
  })

  it('submitScore sends POST /scores with Authorization header', async () => {
    const result = await apiBackend.submitScore(MOCK_TOKEN, 'super-mario-bros', 9999)
    expect(result.score).toBe(9999)
  })

  it('error response throws an Error with detail message', async () => {
    await expect(apiBackend.game('nonexistent-game')).rejects.toThrow('Not found')
  })
})
