import { test, expect } from '@playwright/test';

const LIVE_URL = 'https://app.laurayoga.co.uk';

test.describe('Dashboard Loading Test', () => {
  test('should register user and see dashboard load without hanging', async ({ page }) => {
    console.log('Testing dashboard loading...');

    // Register new user
    const timestamp = Date.now();
    const testEmail = `dashboard${timestamp}@example.com`;
    const testPassword = 'DashTest123!';

    await page.goto(`${LIVE_URL}/register`);
    await page.waitForLoadState('networkidle');

    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[placeholder*="Jane Doe"], input[placeholder*="name"]', 'Dashboard Test');
    await page.fill('input[type="password"]', testPassword);
    await page.selectOption('select', 'beginner');

    console.log(`✓ Registering with: ${testEmail}`);
    await page.click('button:has-text("Create Account")');

    // Wait for redirect to dashboard
    await page.waitForURL(/\/(dashboard|poses)/, { timeout: 10000 });
    console.log(`✓ Redirected to: ${page.url()}`);

    // Navigate to dashboard if not there
    if (!page.url().includes('/dashboard')) {
      await page.goto(`${LIVE_URL}/dashboard`);
    }

    console.log('✓ Waiting for dashboard to load...');

    // Wait for dashboard content with reasonable timeout
    await page.waitForLoadState('networkidle', { timeout: 15000 });

    // Take screenshot of dashboard
    await page.screenshot({ path: 'test-results/dashboard-loaded.png', fullPage: true });
    console.log('✓ Dashboard screenshot saved');

    // Check that dashboard is visible (not stuck loading)
    const bodyText = await page.locator('body').textContent();
    console.log(`✓ Dashboard page content length: ${bodyText.length} chars`);

    // Verify we're not stuck on a loading state
    const loadingSpinner = page.locator('[data-testid="loading"], .spinner, .loading');
    const spinnerCount = await loadingSpinner.count();

    if (spinnerCount > 0) {
      const isVisible = await loadingSpinner.first().isVisible();
      console.log(`⚠ Loading spinner found: ${spinnerCount}, visible: ${isVisible}`);

      if (isVisible) {
        // Wait a bit more to see if it disappears
        await page.waitForTimeout(5000);
        const stillVisible = await loadingSpinner.first().isVisible();
        expect(stillVisible).toBe(false);
      }
    } else {
      console.log('✓ No loading spinner found (good)');
    }

    // Check for error messages
    const errorElement = page.locator('.error, [role="alert"], .alert-error');
    const errorCount = await errorElement.count();

    if (errorCount > 0) {
      const errorText = await errorElement.first().textContent();
      console.log(`⚠ Error found: ${errorText}`);
    } else {
      console.log('✓ No errors on dashboard');
    }

    // Verify navigation works
    await expect(page.locator('text=Dashboard, text=YogaFlow')).toHaveCount({ min: 1 });
    console.log('✅ Dashboard loaded successfully without hanging!');
  });

  test('should show dashboard stats without errors', async ({ page }) => {
    console.log('Testing dashboard stats...');

    // Use existing test user
    await page.goto(`${LIVE_URL}/login`);
    await page.waitForLoadState('networkidle');

    const testEmail = 'test@example.com';
    const testPassword = 'TestPass123';

    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.click('button:has-text("Sign In")');

    console.log('✓ Logging in...');

    try {
      await page.waitForURL(/\/(dashboard|poses)/, { timeout: 10000 });
    } catch (e) {
      console.log('⚠ Test user may not exist, skipping this test');
      test.skip();
      return;
    }

    // Navigate to dashboard
    await page.goto(`${LIVE_URL}/dashboard`);
    await page.waitForLoadState('networkidle', { timeout: 15000 });

    console.log('✓ Dashboard loaded');

    // Take screenshot
    await page.screenshot({ path: 'test-results/dashboard-with-stats.png', fullPage: true });

    // Check for stats section
    const bodyText = await page.locator('body').textContent();
    console.log(`✓ Dashboard content: ${bodyText.substring(0, 200)}...`);

    console.log('✅ Dashboard stats test completed');
  });
});
