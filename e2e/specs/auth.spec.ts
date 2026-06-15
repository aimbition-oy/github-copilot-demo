import { test, expect } from '@playwright/test'
import { resetScores } from '../fixtures/api'

test.beforeEach(async () => {
  await resetScores()
})

test('register a new user via UI, see username in NavBar, log out', async ({ page }) => {
  const username = `player_${Date.now()}`

  // Navigate to register
  await page.goto('/')
  await page.getByRole('link', { name: 'Register' }).click()
  await expect(page).toHaveURL('/register')

  // Fill and submit registration form
  await page.getByLabel('Username').fill(username)
  await page.getByLabel('Password').fill('password123')
  await page.getByRole('button', { name: /register/i }).click()

  // After registration and auto-login, should be on home page
  await expect(page).toHaveURL('/')
  await expect(page.getByText(username)).toBeVisible()

  // Log out
  await page.getByRole('button', { name: /logout/i }).click()
  await expect(page.getByRole('link', { name: 'Login' })).toBeVisible()
  await expect(page.getByText(username)).not.toBeVisible()
})

test('login via UI shows username in NavBar', async ({ page }) => {
  const username = `logintest_${Date.now()}`

  // Register via UI first
  await page.goto('/register')
  await page.getByLabel('Username').fill(username)
  await page.getByLabel('Password').fill('mypassword')
  await page.getByRole('button', { name: /register/i }).click()
  await page.getByRole('button', { name: /logout/i }).click()

  // Now login
  await page.goto('/login')
  await page.getByLabel('Username').fill(username)
  await page.getByLabel('Password').fill('mypassword')
  await page.getByRole('button', { name: /start game/i }).click()

  await expect(page).toHaveURL('/')
  await expect(page.getByText(username)).toBeVisible()
})
