import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3002';

test.describe('UX Fixes Verification', () => {
  let testEmail;

  test.beforeEach(() => {
    // Generate unique email for each test
    testEmail = `uxtest${Date.now()}@test.com`;
  });

  test('Complete UX fixes verification flow', async ({ page }) => {
    // Set mobile viewport to test mobile nav
    await page.setViewportSize({ width: 375, height: 667 });

    // 1. Register a new user
    await page.goto(`${BASE_URL}/register`);
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[name="name"]', 'UX Test User');
    await page.fill('input[type="password"]', 'Test123!');
    await page.selectOption('select[name="experience_level"]', 'beginner');
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL(/\/dashboard/, { timeout: 10000 });

    // 2. Test Dashboard - should show welcome message for new users, not error
    await expect(page.locator('text=/Welcome back/')).toBeVisible({ timeout: 5000 });

    // Should show welcome message instead of error for empty stats
    const welcomeMessage = page.locator('text=/Welcome to YogaFlow/');
    const errorMessage = page.locator('text=/Unable to load/');

    // Check that we have either stats or a welcome message (not an error)
    const hasStats = await page.locator('text=/Total Sessions/').isVisible().catch(() => false);
    const hasWelcome = await welcomeMessage.isVisible().catch(() => false);
    const hasError = await errorMessage.isVisible().catch(() => false);

    expect(hasStats || hasWelcome).toBeTruthy();
    expect(hasError).toBeFalsy();

    // 3. Test Mobile Navigation - hamburger menu should be visible on mobile
    const mobileMenuButton = page.locator('button[aria-label="Open navigation menu"]');
    await expect(mobileMenuButton).toBeVisible();

    // Click mobile menu to open
    await mobileMenuButton.click();

    // Verify menu items are visible
    await expect(page.locator('text=Dashboard').nth(1)).toBeVisible();
    await expect(page.locator('text=Poses').nth(1)).toBeVisible();
    await expect(page.locator('text=Sequences').nth(1)).toBeVisible();
    await expect(page.locator('text=History').nth(1)).toBeVisible();

    // Close mobile menu
    await page.locator('button[aria-label="Close navigation menu"]').click();

    // 4. Test Sequences page - should show helpful empty state
    await page.goto(`${BASE_URL}/sequences`);

    // Should show "No Sequences Available Yet" message
    await expect(page.locator('text=/No Sequences Available Yet/')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=/While we prepare our sequence library/')).toBeVisible();

    // Should have "Browse Poses" button
    const browsePosesButton = page.locator('button:has-text("Browse Poses")');
    await expect(browsePosesButton).toBeVisible();

    // Click Browse Poses button
    await browsePosesButton.click();
    await page.waitForURL(/\/poses/);

    // 5. Test Poses page loads correctly
    await expect(page.locator('h2:has-text("Pose Library")')).toBeVisible({ timeout: 5000 });

    // Should have pose cards
    const poseCards = page.locator('button:has-text("View Details")');
    const poseCount = await poseCards.count();
    expect(poseCount).toBeGreaterThan(0);

    // 6. Test individual pose page loads without error
    await poseCards.first().click();

    // Should NOT show error message
    await expect(page.locator('text=/something went wrong/i')).not.toBeVisible();

    // Should show pose details
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('text=/Description|Benefits|Target Areas/i')).toBeVisible();

    // 7. Test navigation to History page (has header now)
    await page.goto(`${BASE_URL}/history`);

    // Should have YogaFlow header
    await expect(page.locator('h1:has-text("YogaFlow")')).toBeVisible();
    await expect(page.locator('h2:has-text("Practice History")')).toBeVisible();

    // Mobile menu should be available
    await expect(mobileMenuButton).toBeVisible();

    // 8. Test navigation to Profile page (has header now)
    await page.goto(`${BASE_URL}/profile`);

    // Should have YogaFlow header
    await expect(page.locator('h1:has-text("YogaFlow")')).toBeVisible();
    await expect(page.locator('h2:has-text("Profile")')).toBeVisible();

    // Mobile menu should be available
    await expect(mobileMenuButton).toBeVisible();

    // 9. Switch to desktop viewport and verify desktop nav works
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto(`${BASE_URL}/dashboard`);

    // Mobile menu button should NOT be visible on desktop
    await expect(mobileMenuButton).not.toBeVisible();

    // Desktop nav should be visible
    await expect(page.locator('nav a:has-text("Dashboard")')).toBeVisible();
    await expect(page.locator('nav a:has-text("Poses")')).toBeVisible();

    // Desktop logout button should be visible
    await expect(page.locator('button:has-text("Logout")')).toBeVisible();

    console.log('✅ All UX fixes verified successfully!');
  });

  test('Verify pose detail pages work for multiple poses', async ({ page }) => {
    // Register and login first
    await page.goto(`${BASE_URL}/register`);
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[name="name"]', 'Pose Test User');
    await page.fill('input[type="password"]', 'Test123!');
    await page.selectOption('select[name="experience_level"]', 'beginner');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/dashboard/);

    // Go to poses page
    await page.goto(`${BASE_URL}/poses`);
    await page.waitForSelector('button:has-text("View Details")', { timeout: 10000 });

    // Test first 3 poses
    const poseCards = page.locator('button:has-text("View Details")');
    const count = Math.min(await poseCards.count(), 3);

    for (let i = 0; i < count; i++) {
      // Go back to poses page
      await page.goto(`${BASE_URL}/poses`);
      await page.waitForSelector('button:has-text("View Details")');

      // Click on a pose
      const cards = page.locator('button:has-text("View Details")');
      await cards.nth(i).click();

      // Wait for page to load
      await page.waitForURL(/\/poses\/\d+/);

      // Should NOT show error
      await expect(page.locator('text=/something went wrong/i')).not.toBeVisible();

      // Should show pose name
      await expect(page.locator('h1')).toBeVisible();

      console.log(`✅ Pose ${i + 1} details loaded successfully`);
    }
  });
});
