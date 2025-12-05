import { test, expect } from '@playwright/test';

test.describe('Poses Page - Direct Access (No Auth)', () => {
  test('should directly navigate to poses page and check API', async ({ page }) => {
    // Navigate directly to poses page
    await page.goto('/poses');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Take screenshot
    await page.screenshot({
      path: '/Users/justinavery/claude/yoga-app/frontend/screenshots/poses-direct-access.png',
      fullPage: true
    });

    // Check if we're redirected to login or if poses load
    const currentURL = page.url();
    console.log('Current URL:', currentURL);

    // Get page text
    const bodyText = await page.textContent('body');
    console.log('Page content:', bodyText.substring(0, 500));

    // Check for errors
    const errorElements = await page.locator('[class*="error"], [role="alert"]').count();
    console.log('Error elements found:', errorElements);
  });

  test('should verify API client configuration', async ({ page }) => {
    // Navigate to any page to access the API client
    await page.goto('/');

    // Check environment variables in browser context
    const envConfig = await page.evaluate(() => {
      return {
        apiUrl: import.meta.env.VITE_API_URL,
        useMock: import.meta.env.VITE_USE_MOCK_API,
      };
    });

    console.log('Frontend env config:', envConfig);
  });

  test('should test poses API directly', async ({ page }) => {
    let apiResponse;

    // Set up response listener
    page.on('response', async (response) => {
      if (response.url().includes('/api/v1/poses') && response.status() === 200) {
        try {
          apiResponse = await response.json();
          console.log('API Response received:', JSON.stringify(apiResponse).substring(0, 300));
        } catch (error) {
          console.log('Error parsing API response:', error);
        }
      }
    });

    // Navigate to poses page (may redirect to login)
    await page.goto('/poses');
    await page.waitForTimeout(3000);

    // Take screenshot
    await page.screenshot({
      path: '/Users/justinavery/claude/yoga-app/frontend/screenshots/poses-api-test.png',
      fullPage: true
    });

    if (apiResponse) {
      console.log('API returned data!');
      console.log('Poses count:', apiResponse.poses?.length || 0);
      if (apiResponse.poses && apiResponse.poses.length > 0) {
        console.log('First pose:', JSON.stringify(apiResponse.poses[0], null, 2));
      }
    } else {
      console.log('No API response captured - may be redirected to login');
    }
  });
});
