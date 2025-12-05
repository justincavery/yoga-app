import { test, expect } from '@playwright/test';

test.describe('Poses Page - With Mock Auth', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');

    // Set mock auth in localStorage to bypass login
    await page.evaluate(() => {
      const mockAuthState = {
        user: {
          user_id: 1,
          email: 'test@playwright.com',
          name: 'Test User',
          experience_level: 'beginner'
        },
        token: 'mock-token-for-testing',
        isAuthenticated: true
      };

      // Store in localStorage (assuming this is how Zustand persists)
      localStorage.setItem('auth-storage', JSON.stringify({ state: mockAuthState }));
    });

    // Navigate to poses page
    await page.goto('/poses');
    await page.waitForLoadState('networkidle');
  });

  test('should display poses page with mock auth', async ({ page }) => {
    // Wait a bit for React to render
    await page.waitForTimeout(2000);

    // Take screenshot
    await page.screenshot({
      path: '/Users/justinavery/claude/yoga-app/frontend/screenshots/poses-with-mock-auth.png',
      fullPage: true
    });

    // Check current URL
    const url = page.url();
    console.log('Current URL:', url);

    // Check if on poses page or redirected to login
    const isOnPosesPage = url.includes('/poses');
    const isOnLoginPage = url.includes('/login');

    console.log('On poses page:', isOnPosesPage);
    console.log('On login page:', isOnLoginPage);

    // Get body text
    const bodyText = await page.textContent('body');
    console.log('Page content preview:', bodyText.substring(0, 500));
  });

  test('should wait for and display pose cards', async ({ page }) => {
    // Capture console logs
    const consoleLogs = [];
    const errors = [];

    page.on('console', msg => {
      const text = msg.text();
      consoleLogs.push(text);
      if (msg.type() === 'error') {
        errors.push(text);
      }
    });

    // Capture network responses
    let posesAPIResponse = null;
    page.on('response', async (response) => {
      if (response.url().includes('/poses')) {
        console.log('Response URL:', response.url());
        console.log('Response status:', response.status());

        if (response.status() === 200) {
          try {
            posesAPIResponse = await response.json();
            console.log('API Response keys:', Object.keys(posesAPIResponse));
            console.log('Poses count from API:', posesAPIResponse.poses?.length || 0);
          } catch (error) {
            console.log('Error parsing response:', error.message);
          }
        }
      }
    });

    // Wait for network to settle
    await page.waitForTimeout(3000);

    // Take screenshot after wait
    await page.screenshot({
      path: '/Users/justinavery/claude/yoga-app/frontend/screenshots/poses-after-wait.png',
      fullPage: true
    });

    // Log console messages
    console.log('\n=== Console Logs ===');
    consoleLogs.forEach(log => console.log(log));

    console.log('\n=== Console Errors ===');
    if (errors.length > 0) {
      errors.forEach(err => console.error(err));
    } else {
      console.log('No console errors');
    }

    // Check if API was called
    if (posesAPIResponse) {
      console.log('\n=== API Response Summary ===');
      console.log('Total poses:', posesAPIResponse.total || posesAPIResponse.poses?.length || 0);
      if (posesAPIResponse.poses && posesAPIResponse.poses.length > 0) {
        const firstPose = posesAPIResponse.poses[0];
        console.log('First pose data:', JSON.stringify(firstPose, null, 2).substring(0, 300));
      }
    } else {
      console.log('\n=== No API Response ===');
      console.log('API may not have been called - checking page state...');
    }

    // Check for pose elements on the page
    const poseCards = await page.locator('[class*="grid"] > div').count();
    console.log('Pose card elements found:', poseCards);

    // Check for any text containing pose names
    const pageHasContent = await page.locator('text=/pose|asana/i').count();
    console.log('Elements with "pose" or "asana":', pageHasContent);

    // Check for loading state
    const hasSpinner = await page.locator('[class*="spin"], [class*="loading"]').count();
    console.log('Loading indicators found:', hasSpinner);

    // Check for error messages
    const hasError = await page.locator('[class*="error"]').count();
    console.log('Error elements found:', hasError);

    // Take final screenshot
    await page.screenshot({
      path: '/Users/justinavery/claude/yoga-app/frontend/screenshots/poses-final-state.png',
      fullPage: true
    });
  });
});
