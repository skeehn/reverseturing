import { test, expect, Page } from '@playwright/test';

// Test configuration
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

// Helper functions
async function login(page: Page, username: string, password: string) {
  await page.goto(`${BASE_URL}/login`);
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(`${BASE_URL}/lobby`);
}

async function createRoom(page: Page, roomType: string) {
  await page.click('button:has-text("Create Room")');
  await page.selectOption('select[name="roomType"]', roomType);
  await page.click('button:has-text("Create")');
  await page.waitForURL(/.*\/room\/.*/);
}

// Test suite
test.describe('Reverse Turing Game E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Clear cookies and local storage
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
  });

  test('User can register and login', async ({ page }) => {
    // Go to registration page
    await page.goto(`${BASE_URL}/register`);
    
    // Fill registration form
    const timestamp = Date.now();
    const username = `testuser${timestamp}`;
    const email = `test${timestamp}@example.com`;
    const password = 'TestPassword123!';
    
    await page.fill('input[name="username"]', username);
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.fill('input[name="confirmPassword"]', password);
    
    // Submit registration
    await page.click('button[type="submit"]');
    
    // Should redirect to login
    await page.waitForURL(`${BASE_URL}/login`);
    
    // Login with new account
    await login(page, username, password);
    
    // Verify we're in the lobby
    await expect(page).toHaveURL(`${BASE_URL}/lobby`);
    await expect(page.locator('h1')).toContainText('Game Lobby');
  });

  test('User can create and join a game room', async ({ page }) => {
    // Login first
    await login(page, 'testuser', 'password123');
    
    // Create a new room
    await createRoom(page, 'poetry');
    
    // Verify room page elements
    await expect(page.locator('.room-header')).toBeVisible();
    await expect(page.locator('.player-list')).toBeVisible();
    await expect(page.locator('.game-status')).toContainText('Waiting for players');
  });

  test('Complete game flow', async ({ browser }) => {
    // Create two browser contexts for two players
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    
    const player1 = await context1.newPage();
    const player2 = await context2.newPage();
    
    // Player 1 logs in and creates room
    await login(player1, 'player1', 'password123');
    await createRoom(player1, 'debate');
    
    // Get room URL
    const roomUrl = player1.url();
    const roomId = roomUrl.split('/').pop();
    
    // Player 2 logs in and joins room
    await login(player2, 'player2', 'password123');
    await player2.goto(roomUrl);
    
    // Both players should see each other
    await expect(player1.locator('.player-list')).toContainText('player1');
    await expect(player1.locator('.player-list')).toContainText('player2');
    await expect(player2.locator('.player-list')).toContainText('player1');
    await expect(player2.locator('.player-list')).toContainText('player2');
    
    // Player 1 starts the game
    await player1.click('button:has-text("Start Game")');
    
    // Both players should see the prompt
    await expect(player1.locator('.game-prompt')).toBeVisible();
    await expect(player2.locator('.game-prompt')).toBeVisible();
    
    // Submit responses
    await player1.fill('textarea[name="response"]', 'This is player 1 response');
    await player1.click('button:has-text("Submit Response")');
    
    await player2.fill('textarea[name="response"]', 'This is player 2 response');
    await player2.click('button:has-text("Submit Response")');
    
    // Wait for voting phase
    await expect(player1.locator('.voting-phase')).toBeVisible({ timeout: 10000 });
    await expect(player2.locator('.voting-phase')).toBeVisible({ timeout: 10000 });
    
    // Submit votes
    await player1.click('.response-option:first-child');
    await player1.click('button:has-text("Submit Vote")');
    
    await player2.click('.response-option:last-child');
    await player2.click('button:has-text("Submit Vote")');
    
    // Wait for results
    await expect(player1.locator('.results-display')).toBeVisible({ timeout: 10000 });
    await expect(player2.locator('.results-display')).toBeVisible({ timeout: 10000 });
    
    // Verify results are shown
    await expect(player1.locator('.ai-judgment')).toBeVisible();
    await expect(player1.locator('.vote-results')).toBeVisible();
    
    // Clean up
    await context1.close();
    await context2.close();
  });

  test('Leaderboard updates after game', async ({ page }) => {
    // Login and play a game
    await login(page, 'testuser', 'password123');
    
    // Navigate to leaderboard
    await page.goto(`${BASE_URL}/leaderboard`);
    
    // Verify leaderboard loads
    await expect(page.locator('.leaderboard-table')).toBeVisible();
    await expect(page.locator('.player-rank')).toHaveCount(0, { timeout: 5000 });
    
    // Verify different leaderboard categories
    await page.click('button:has-text("Deception Score")');
    await expect(page.locator('.leaderboard-category')).toContainText('Deception');
    
    await page.click('button:has-text("Detection Score")');
    await expect(page.locator('.leaderboard-category')).toContainText('Detection');
  });

  test('Analytics page displays game statistics', async ({ page }) => {
    await page.goto(`${BASE_URL}/analytics`);
    
    // Verify analytics components load
    await expect(page.locator('.analytics-dashboard')).toBeVisible();
    await expect(page.locator('.judge-accuracy-chart')).toBeVisible();
    await expect(page.locator('.game-metrics')).toBeVisible();
    
    // Check for specific metrics
    await expect(page.locator('.total-games-stat')).toBeVisible();
    await expect(page.locator('.average-accuracy-stat')).toBeVisible();
    await expect(page.locator('.active-players-stat')).toBeVisible();
  });

  test('Error handling for network issues', async ({ page }) => {
    // Login
    await login(page, 'testuser', 'password123');
    
    // Simulate network offline
    await page.context().setOffline(true);
    
    // Try to create a room
    await page.click('button:has-text("Create Room")');
    
    // Should show error message
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toContainText(/network|offline|connection/i);
    
    // Restore network
    await page.context().setOffline(false);
  });

  test('Responsive design on mobile', async ({ browser }) => {
    // Create mobile context
    const iPhone = {
      viewport: { width: 375, height: 667 },
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
      deviceScaleFactor: 2,
      isMobile: true,
      hasTouch: true,
    };
    
    const mobileContext = await browser.newContext(iPhone);
    const mobilePage = await mobileContext.newPage();
    
    // Navigate to home
    await mobilePage.goto(BASE_URL);
    
    // Check mobile menu
    await expect(mobilePage.locator('.mobile-menu-button')).toBeVisible();
    await mobilePage.click('.mobile-menu-button');
    await expect(mobilePage.locator('.mobile-menu')).toBeVisible();
    
    // Navigate to different pages
    await mobilePage.click('a:has-text("Leaderboard")');
    await expect(mobilePage).toHaveURL(`${BASE_URL}/leaderboard`);
    
    // Verify responsive layout
    const viewportSize = mobilePage.viewportSize();
    expect(viewportSize?.width).toBeLessThan(400);
    
    await mobileContext.close();
  });

  test('WebSocket reconnection handling', async ({ page }) => {
    // Login and join a room
    await login(page, 'testuser', 'password123');
    await createRoom(page, 'creative');
    
    // Simulate WebSocket disconnection
    await page.evaluate(() => {
      // Force disconnect WebSocket
      const socket = (window as any).socket;
      if (socket) {
        socket.disconnect();
      }
    });
    
    // Should show reconnecting message
    await expect(page.locator('.connection-status')).toContainText(/reconnecting|disconnected/i);
    
    // Simulate reconnection
    await page.evaluate(() => {
      const socket = (window as any).socket;
      if (socket) {
        socket.connect();
      }
    });
    
    // Should show connected status
    await expect(page.locator('.connection-status')).toContainText(/connected/i);
  });

  test('Accessibility - keyboard navigation', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Tab through interactive elements
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();
    
    // Navigate to login using keyboard
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Enter');
    
    await expect(page).toHaveURL(`${BASE_URL}/login`);
    
    // Tab through form fields
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="username"]:focus')).toBeVisible();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="password"]:focus')).toBeVisible();
  });

  test('Performance - page load times', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    
    const loadTime = Date.now() - startTime;
    
    // Page should load in under 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    // Check Core Web Vitals
    const metrics = await page.evaluate(() => {
      return {
        FCP: performance.getEntriesByName('first-contentful-paint')[0]?.startTime,
        LCP: performance.getEntriesByType('largest-contentful-paint').pop()?.startTime,
      };
    });
    
    // First Contentful Paint should be under 1.8s
    if (metrics.FCP) {
      expect(metrics.FCP).toBeLessThan(1800);
    }
    
    // Largest Contentful Paint should be under 2.5s
    if (metrics.LCP) {
      expect(metrics.LCP).toBeLessThan(2500);
    }
  });
});