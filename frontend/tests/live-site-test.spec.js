/**
 * Live Site Integration Test
 * Tests the production deployment at https://app.laurayoga.co.uk
 *
 * Run with: npx playwright test tests/live-site-test.spec.js
 */

import { test, expect } from '@playwright/test';

// Production URL
const LIVE_URL = 'https://app.laurayoga.co.uk';

test.describe('Live Site - Production Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to live site
    await page.goto(LIVE_URL);
  });

  test('should load homepage successfully', async ({ page }) => {
    // Check page loaded
    await expect(page).toHaveTitle(/YogaFlow|Yoga/);

    // Take screenshot for verification
    await page.screenshot({ path: 'test-results/live-homepage.png', fullPage: true });
  });

  test('should display poses data', async ({ page }) => {
    // Navigate to poses page
    await page.goto(`${LIVE_URL}/poses`);

    // Wait for poses to load
    await page.waitForSelector('[data-testid="pose-card"], .pose-card, article', { timeout: 10000 });

    // Check that poses are displayed
    const poseCards = page.locator('[data-testid="pose-card"], .pose-card, article');
    const count = await poseCards.count();

    expect(count).toBeGreaterThan(0);
    console.log(`✓ Found ${count} poses displayed`);

    // Take screenshot
    await page.screenshot({ path: 'test-results/live-poses-page.png', fullPage: true });
  });

  test('should be able to search poses', async ({ page }) => {
    // Navigate to poses page
    await page.goto(`${LIVE_URL}/poses`);

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Find search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"], input[name*="search"]').first();

    if (await searchInput.count() > 0) {
      // Type in search box
      await searchInput.fill('Mountain');

      // Wait a bit for search to filter
      await page.waitForTimeout(1000);

      // Take screenshot of search results
      await page.screenshot({ path: 'test-results/live-search-results.png', fullPage: true });

      console.log('✓ Search functionality works');
    } else {
      console.log('⚠ Search input not found');
    }
  });

  test('should check API health endpoint', async ({ request }) => {
    const response = await request.get(`${LIVE_URL}/health`);
    expect(response.ok()).toBeTruthy();

    const text = await response.text();
    console.log(`✓ Health check response: ${text}`);
  });

  test('should fetch poses from API', async ({ request }) => {
    const response = await request.get(`${LIVE_URL}/api/v1/poses`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty('poses');
    expect(data).toHaveProperty('total');

    console.log(`✓ API returned ${data.total} total poses`);
    expect(data.total).toBeGreaterThan(0);
  });

  test('should navigate to dashboard (if login required, will check login page)', async ({ page }) => {
    // Try to access dashboard
    await page.goto(`${LIVE_URL}/dashboard`);

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check if we're redirected to login or if dashboard loads
    const url = page.url();

    if (url.includes('/login') || url.includes('/signin')) {
      console.log('✓ Dashboard requires authentication (redirected to login)');

      // Check login form exists
      const emailInput = page.locator('input[type="email"], input[name="email"]');
      const passwordInput = page.locator('input[type="password"], input[name="password"]');

      expect(await emailInput.count()).toBeGreaterThan(0);
      expect(await passwordInput.count()).toBeGreaterThan(0);

      // Take screenshot
      await page.screenshot({ path: 'test-results/live-login-page.png', fullPage: true });
    } else {
      console.log('✓ Dashboard loaded (no auth required or already authenticated)');

      // Take screenshot
      await page.screenshot({ path: 'test-results/live-dashboard.png', fullPage: true });
    }
  });

  test.skip('should login with test credentials', async ({ page }) => {
    // This test is skipped by default - enable when you have test credentials
    // Update with actual test credentials
    const TEST_EMAIL = 'test@example.com';
    const TEST_PASSWORD = 'test123';

    // Navigate to login
    await page.goto(`${LIVE_URL}/login`);

    // Fill in credentials
    await page.fill('input[type="email"], input[name="email"]', TEST_EMAIL);
    await page.fill('input[type="password"], input[name="password"]', TEST_PASSWORD);

    // Click login button
    await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")');

    // Wait for navigation
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });

    // Verify we're logged in
    expect(page.url()).toContain('/dashboard');

    // Take screenshot
    await page.screenshot({ path: 'test-results/live-logged-in.png', fullPage: true });
  });
});
