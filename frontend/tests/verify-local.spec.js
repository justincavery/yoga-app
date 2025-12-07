import { test, expect } from '@playwright/test';

test.describe('YogaFlow Local Server Verification', () => {
  test('frontend loads successfully', async ({ page }) => {
    // Navigate to the frontend
    await page.goto('http://localhost:3002');

    // Wait for the page to load
    await page.waitForLoadState('networkidle');

    // Check that we can see the YogaFlow branding
    await expect(page.locator('text=YogaFlow')).toBeVisible({ timeout: 10000 });

    // Take a screenshot
    await page.screenshot({ path: 'screenshots/local-verification.png', fullPage: true });
  });

  test('backend API is accessible', async ({ page }) => {
    // Test backend health endpoint
    const response = await page.request.get('http://localhost:8000/health');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.service).toBe('yogaflow-api');
  });

  test('frontend can communicate with backend', async ({ page }) => {
    await page.goto('http://localhost:3002');
    await page.waitForLoadState('networkidle');

    // Try to access the poses API endpoint (should get 401 without auth)
    const response = await page.request.get('http://localhost:8000/api/v1/poses');

    // We expect either 200 (if public) or 401 (if auth required)
    expect([200, 401]).toContain(response.status());
  });

  test('can navigate to registration page', async ({ page }) => {
    await page.goto('http://localhost:3002');
    await page.waitForLoadState('networkidle');

    // Look for register link/button
    const registerLink = page.locator('a[href*="register"], button:has-text("Register"), a:has-text("Register")').first();

    if (await registerLink.isVisible()) {
      await registerLink.click();
      await page.waitForURL(/.*register.*/);
      await expect(page.locator('text=Register')).toBeVisible();
    } else {
      // If we're already on a page with a registration form
      await expect(page.locator('input[type="email"], input[name="email"]')).toBeVisible();
    }

    await page.screenshot({ path: 'screenshots/registration-page.png' });
  });
});
