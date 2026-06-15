import { test, expect } from '@playwright/test'
import { createFreshUser, submitScoreViaApi, resetScores } from '../fixtures/api'

test.beforeEach(async () => {
  await resetScores()
})

test('leaderboard shows scores in descending order', async ({ page }) => {
  // Seed 3 scores via API (fast, deterministic)
  const user1 = await createFreshUser(`lbtest1_${Date.now()}`)
  const user2 = await createFreshUser(`lbtest2_${Date.now()}`)
  const user3 = await createFreshUser(`lbtest3_${Date.now()}`)

  await submitScoreViaApi(user1.token, 'super-mario-bros', 50000)
  await submitScoreViaApi(user2.token, 'super-mario-bros', 99999)
  await submitScoreViaApi(user3.token, 'super-mario-bros', 25000)

  await page.goto('/leaderboard/super-mario-bros')

  // Scores should be in descending order
  const scores = page.locator('tbody tr')
  await expect(scores).toHaveCount(3)

  // First row should be the highest score (99999 → "99,999")
  await expect(scores.nth(0).getByText('99,999')).toBeVisible()
  await expect(scores.nth(1).getByText('50,000')).toBeVisible()
  await expect(scores.nth(2).getByText('25,000')).toBeVisible()

  // Gold medal for rank 1
  await expect(scores.nth(0).getByText('🥇')).toBeVisible()
})

test('leaderboard shows no-scores message when empty', async ({ page }) => {
  await page.goto('/leaderboard/tetris')
  await expect(page.getByText(/no scores yet/i)).toBeVisible()
})
