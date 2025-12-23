import { test, expect } from '@playwright/test';

const LIVE_URL = 'https://app.laurayoga.co.uk';

test.describe('Production Login Test', () => {

  test('Register and login with new user', async ({ page }) => {
    console.log('Starting registration and login test...');

    // Capture console logs
    page.on('console', msg => {
      console.log(`[BROWSER ${msg.type()}]:`, msg.text());
    });

    // Capture page errors
    page.on('pageerror', error => {
      console.log(`[PAGE ERROR]:`, error.message);
    });

    // Create unique test user
    const timestamp = Date.now();
    const testEmail = `logintest${timestamp}@example.com`;
    const testPassword = 'TestPass123!';
    const testName = 'Login Test User';

    console.log(`Test user: ${testEmail}`);

    // Step 1: Register
    console.log('\n=== REGISTRATION ===');
    await page.goto(`${LIVE_URL}/register`);
    await page.waitForLoadState('networkidle');

    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[placeholder*="Jane Doe"], input[placeholder*="name"]', testName);
    await page.fill('input[type="password"]', testPassword);
    await page.selectOption('select', 'beginner');

    console.log('Submitting registration form...');
    await page.click('button:has-text("Create Account")');

    // Wait for response
    await page.waitForTimeout(2000);

    const currentUrl = page.url();
    console.log(`After registration, URL: ${currentUrl}`);

    // Take screenshot
    await page.screenshot({ path: 'test-results/after-registration.png', fullPage: true });

    // Check for any error messages
    const errorText = await page.textContent('body');
    if (errorText.includes('error') || errorText.includes('Error')) {
      console.log('⚠️  Possible error on page');
      console.log(errorText.substring(0, 500));
    }

    // Step 2: Navigate to login page
    console.log('\n=== LOGIN ===');
    await page.goto(`${LIVE_URL}/login`);
    await page.waitForLoadState('networkidle');

    console.log('Login page loaded');

    // Fill login form
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);

    console.log('Submitting login form...');

    // Listen for network responses
    page.on('response', response => {
      if (response.url().includes('/auth/login')) {
        console.log(`Login API response: ${response.status()}`);
        response.json().then(data => {
          console.log('Response body:', JSON.stringify(data, null, 2));
        }).catch(() => {
          console.log('Could not parse response as JSON');
        });
      }
    });

    await page.click('button:has-text("Sign In"), button:has-text("Log In")');

    // Wait for response
    await page.waitForTimeout(3000);

    const afterLoginUrl = page.url();
    console.log(`After login, URL: ${afterLoginUrl}`);

    // Take screenshot
    await page.screenshot({ path: 'test-results/after-login.png', fullPage: true });

    // Check page content
    const pageContent = await page.textContent('body');

    if (pageContent.includes('error') || pageContent.includes('Error') || pageContent.includes('Invalid')) {
      console.log('\n⚠️  ERROR DETECTED:');
      console.log(pageContent.substring(0, 1000));
    }

    if (afterLoginUrl.includes('dashboard') || afterLoginUrl.includes('poses')) {
      console.log('\n✅ LOGIN SUCCESSFUL - Redirected to authenticated page');
    } else {
      console.log('\n❌ LOGIN FAILED - Still on login page or unexpected location');
    }

    // Verify we're authenticated by checking for user-specific content
    const isAuthenticated = afterLoginUrl.includes('dashboard') ||
                           afterLoginUrl.includes('poses') ||
                           await page.locator('text=Logout, text=Sign Out').count() > 0;

    if (isAuthenticated) {
      console.log('✅ User appears to be authenticated');
    } else {
      console.log('❌ User does NOT appear to be authenticated');
    }

    expect(isAuthenticated).toBeTruthy();
  });

  test('Test login API directly', async ({ request }) => {
    console.log('\n=== DIRECT API TEST ===');

    // Create unique test user
    const timestamp = Date.now();
    const testEmail = `apitest${timestamp}@example.com`;
    const testPassword = 'TestPass123!';

    // Register via API
    console.log('Registering user via API...');
    const registerResponse = await request.post(`${LIVE_URL}/api/v1/auth/register`, {
      data: {
        email: testEmail,
        password: testPassword,
        name: 'API Test User',
        experience_level: 'beginner'
      }
    });

    console.log(`Registration status: ${registerResponse.status()}`);
    const registerData = await registerResponse.json();
    console.log('Registration response:', JSON.stringify(registerData, null, 2));

    expect(registerResponse.ok()).toBeTruthy();

    // Login via API
    console.log('\nLogging in via API...');
    const loginResponse = await request.post(`${LIVE_URL}/api/v1/auth/login`, {
      data: {
        email: testEmail,
        password: testPassword,
        remember_me: false
      }
    });

    console.log(`Login status: ${loginResponse.status()}`);

    if (loginResponse.ok()) {
      const loginData = await loginResponse.json();
      console.log('Login response:', JSON.stringify(loginData, null, 2));
      console.log('\n✅ LOGIN API SUCCESSFUL');

      expect(loginData.access_token).toBeDefined();
      expect(loginData.user).toBeDefined();
    } else {
      const errorData = await loginResponse.text();
      console.log('Login error response:', errorData);
      console.log('\n❌ LOGIN API FAILED');
    }

    expect(loginResponse.ok()).toBeTruthy();
  });
});
