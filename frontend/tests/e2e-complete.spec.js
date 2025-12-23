import { test, expect } from '@playwright/test';

const LIVE_URL = 'https://app.laurayoga.co.uk';

test.describe('Complete E2E Flow - Live Site', () => {
  test('should register new user and see poses on dashboard', async ({ page }) => {
    console.log('Starting registration test...');

    // Navigate to registration page
    await page.goto(`${LIVE_URL}/register`);
    await page.waitForLoadState('networkidle');

    // Take screenshot of registration page
    await page.screenshot({ path: 'test-results/01-registration-page.png', fullPage: true });

    // Generate unique email for this test
    const timestamp = Date.now();
    const testEmail = `test${timestamp}@example.com`;
    const testPassword = 'TestPass123!';
    const testName = 'E2E Test User';

    console.log(`Registering with email: ${testEmail}`);

    // Fill registration form
    await page.fill('input[name="name"], input[placeholder*="name" i]', testName);
    await page.fill('input[name="email"], input[type="email"]', testEmail);
    await page.fill('input[name="password"], input[type="password"]', testPassword);

    // Select experience level if present
    const experienceSelect = page.locator('select[name="experience_level"], select[name="experienceLevel"]');
    if (await experienceSelect.count() > 0) {
      await experienceSelect.selectOption('beginner');
    }

    await page.screenshot({ path: 'test-results/02-registration-filled.png', fullPage: true });

    // Submit registration
    await page.click('button[type="submit"], button:has-text("Sign Up"), button:has-text("Register")');

    console.log('Registration submitted, waiting for redirect...');

    // Wait for redirect to dashboard or poses page
    await page.waitForURL(/\/(dashboard|poses)/, { timeout: 15000 });
    await page.waitForLoadState('networkidle');

    await page.screenshot({ path: 'test-results/03-after-registration.png', fullPage: true });

    // Check if we're on dashboard
    const currentUrl = page.url();
    console.log(`Current URL after registration: ${currentUrl}`);

    // Navigate to poses page if not already there
    if (!currentUrl.includes('/poses')) {
      console.log('Navigating to poses page...');
      await page.goto(`${LIVE_URL}/poses`);
      await page.waitForLoadState('networkidle');
    }

    await page.screenshot({ path: 'test-results/04-poses-page.png', fullPage: true });

    // Wait for poses to load - check multiple possible selectors
    console.log('Waiting for poses to load...');

    try {
      await page.waitForSelector('[data-testid="pose-card"], .pose-card, article, .card', {
        timeout: 15000,
        state: 'visible'
      });

      const poseCards = await page.locator('[data-testid="pose-card"], .pose-card, article, .card').count();
      console.log(`✓ Found ${poseCards} pose cards`);

      expect(poseCards).toBeGreaterThan(0);

      await page.screenshot({ path: 'test-results/05-poses-loaded.png', fullPage: true });

    } catch (error) {
      console.log('❌ Poses did not load. Checking page content...');

      // Get page content for debugging
      const bodyText = await page.locator('body').textContent();
      console.log('Page content:', bodyText.substring(0, 500));

      // Check if there's an error message
      const errorMsg = await page.locator('.error, [role="alert"], .alert').textContent().catch(() => 'No error message');
      console.log('Error message:', errorMsg);

      await page.screenshot({ path: 'test-results/05-poses-failed.png', fullPage: true });

      throw error;
    }
  });

  test('should login with existing test user and see poses', async ({ page }) => {
    console.log('Starting login test with existing user...');

    // Navigate to login page
    await page.goto(`${LIVE_URL}/login`);
    await page.waitForLoadState('networkidle');

    await page.screenshot({ path: 'test-results/10-login-page.png', fullPage: true });

    // Login with test credentials
    const testEmail = 'test@example.com';
    const testPassword = 'TestPass123';

    console.log(`Logging in with: ${testEmail}`);

    await page.fill('input[name="email"], input[type="email"]', testEmail);
    await page.fill('input[name="password"], input[type="password"]', testPassword);

    await page.screenshot({ path: 'test-results/11-login-filled.png', fullPage: true });

    // Submit login
    await page.click('button[type="submit"], button:has-text("Sign In"), button:has-text("Login")');

    console.log('Login submitted, waiting for redirect...');

    // Wait for redirect
    await page.waitForURL(/\/(dashboard|poses)/, { timeout: 15000 });
    await page.waitForLoadState('networkidle');

    await page.screenshot({ path: 'test-results/12-after-login.png', fullPage: true });

    const currentUrl = page.url();
    console.log(`Current URL after login: ${currentUrl}`);

    // Navigate to dashboard
    console.log('Navigating to dashboard...');
    await page.goto(`${LIVE_URL}/dashboard`);
    await page.waitForLoadState('networkidle');

    await page.screenshot({ path: 'test-results/13-dashboard.png', fullPage: true });

    // Wait a bit for any dynamic content
    await page.waitForTimeout(3000);

    await page.screenshot({ path: 'test-results/14-dashboard-loaded.png', fullPage: true });

    // Check dashboard content
    const bodyText = await page.locator('body').textContent();
    console.log('Dashboard content preview:', bodyText.substring(0, 300));

    // Navigate to poses page
    console.log('Navigating to poses page...');
    await page.goto(`${LIVE_URL}/poses`);
    await page.waitForLoadState('networkidle');

    await page.screenshot({ path: 'test-results/15-poses-page.png', fullPage: true });

    // Wait for poses to load
    console.log('Waiting for poses to load...');

    try {
      await page.waitForSelector('[data-testid="pose-card"], .pose-card, article, .card', {
        timeout: 15000,
        state: 'visible'
      });

      const poseCards = await page.locator('[data-testid="pose-card"], .pose-card, article, .card').count();
      console.log(`✓ Found ${poseCards} pose cards`);

      expect(poseCards).toBeGreaterThan(0);

      // Get first pose name
      const firstPose = await page.locator('[data-testid="pose-card"], .pose-card, article, .card').first();
      const poseName = await firstPose.textContent();
      console.log(`First pose: ${poseName}`);

      await page.screenshot({ path: 'test-results/16-poses-loaded.png', fullPage: true });

    } catch (error) {
      console.log('❌ Poses did not load. Checking page content...');

      const bodyText = await page.locator('body').textContent();
      console.log('Page content:', bodyText.substring(0, 500));

      await page.screenshot({ path: 'test-results/16-poses-failed.png', fullPage: true });

      throw error;
    }
  });

  test('should check API directly returns 80 poses', async ({ request }) => {
    console.log('Testing API directly...');

    const response = await request.get(`${LIVE_URL}/api/v1/poses`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    console.log(`API response: ${data.total} total poses`);
    console.log(`First few poses: ${data.poses.slice(0, 3).map(p => p.name_english).join(', ')}`);

    expect(data.total).toBe(80);
    expect(data.poses).toHaveLength(80);
  });
});
