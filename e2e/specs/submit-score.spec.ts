import { test, expect } from '@playwright/test'
import { createFreshUser, resetScores } from '../fixtures/api'

test.beforeEach(async () => {
  await resetScores()
})

test('logged-in user submits a score and sees it on the leaderboard', async ({ page }) => {
  const user = await createFreshUser(`scorer_${Date.now()}`)

  // Inject token into localStorage so the app treats us as logged-in
  await page.goto('/')
  await page.evaluate(
    ({ token, userObj }) => {
      localStorage.setItem('arcade_token', JSON.stringify({ token, user: userObj }))
    },
    { token: user.token, userObj: { id: user.userId, username: user.username, created_at: new Date().toISOString() } }
  )
  await page.reload()

  // Navigate to submit score for Super Mario Bros.
  await page.goto('/submit/super-mario-bros')
  await expect(page.getByText('super-mario-bros')).toBeVisible()

  await page.getByLabel('Your Score').fill('12345')
  await page.getByRole('button', { name: /submit/i }).click()

  // Should redirect to leaderboard
  await expect(page).toHaveURL('/leaderboard/super-mario-bros')
  await expect(page.getByText('12,345')).toBeVisible()
  await expect(page.getByText(user.username)).toBeVisible()
})
