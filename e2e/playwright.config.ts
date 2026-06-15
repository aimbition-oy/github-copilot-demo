import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './specs',
  fullyParallel: false,  // specs share state (DB), run serially
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  // Assumes the compose stack is already running when tests are run.
  // To auto-start: uncomment webServer block below.
  // webServer: {
  //   command: 'docker compose up --build -d',
  //   url: 'http://localhost:5173',
  //   reuseExistingServer: true,
  //   timeout: 120000,
  // },
})
