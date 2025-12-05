import { test, expect } from '@playwright/test';

test.describe('Diagnose API Issues', () => {
  test('should capture all network requests', async ({ page }) => {
    const requests = [];
    const responses = [];

    // Capture all requests
    page.on('request', request => {
      requests.push({
        url: request.url(),
        method: request.method(),
        headers: request.headers(),
      });
    });

    // Capture all responses
    page.on('response', async response => {
      const entry = {
        url: response.url(),
        status: response.status(),
        statusText: response.statusText(),
        headers: response.headers(),
      };

      // Try to get response body if it's JSON
      if (response.url().includes('/poses') || response.url().includes('/api/')) {
        try {
          entry.body = await response.json();
        } catch (error) {
          try {
            entry.bodyText = await response.text();
          } catch (e) {
            entry.bodyText = 'Could not read body';
          }
        }
      }

      responses.push(entry);
    });

    // Set mock auth
    await page.goto('/');
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
      localStorage.setItem('auth-storage', JSON.stringify({ state: mockAuthState }));
    });

    // Navigate to poses page
    await page.goto('/poses');
    await page.waitForTimeout(3000);

    // Take screenshot
    await page.screenshot({
      path: '/Users/justinavery/claude/yoga-app/frontend/screenshots/diagnose-api.png',
      fullPage: true
    });

    // Log all API-related requests
    console.log('\n=== API Requests ===');
    const apiRequests = requests.filter(r => r.url.includes('/api/') || r.url.includes('/poses'));
    apiRequests.forEach(req => {
      console.log(`${req.method} ${req.url}`);
    });

    // Log all API-related responses
    console.log('\n=== API Responses ===');
    const apiResponses = responses.filter(r => r.url.includes('/api/') || r.url.includes('/poses'));
    apiResponses.forEach(res => {
      console.log(`${res.status} ${res.url}`);
      if (res.body) {
        console.log('Body:', JSON.stringify(res.body).substring(0, 200));
      }
      if (res.bodyText && res.status !== 200) {
        console.log('Error body:', res.bodyText.substring(0, 200));
      }
    });

    // Check console errors
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    console.log('\n=== Console Errors ===');
    if (consoleErrors.length > 0) {
      consoleErrors.forEach(err => console.error(err));
    } else {
      console.log('No console errors captured');
    }

    // Check page text for errors
    const hasFailedToFetch = await page.locator('text="Failed to fetch"').count();
    console.log('\n"Failed to fetch" error present:', hasFailedToFetch > 0);

    if (hasFailedToFetch > 0) {
      console.log('\nDEBUG: Found "Failed to fetch" error on page');
      console.log('This suggests a network error or CORS issue');
      console.log('Check if the API URL is correct and the backend is running');
    }
  });
});
