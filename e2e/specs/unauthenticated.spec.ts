import { test, expect } from '@playwright/test'

test('visiting /submit while logged out redirects to /login', async ({ page }) => {
  // Clear any stored auth
  await page.goto('/')
  await page.evaluate(() => localStorage.removeItem('arcade_token'))

  await page.goto('/submit/super-mario-bros')
  await expect(page).toHaveURL('/login')
})

test('home page shows login and register links when logged out', async ({ page }) => {
  await page.goto('/')
  await page.evaluate(() => localStorage.removeItem('arcade_token'))
  await page.reload()

  await expect(page.getByRole('link', { name: 'Login' })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Register' })).toBeVisible()
})
