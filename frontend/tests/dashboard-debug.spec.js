import { test, expect } from '@playwright/test';

const LIVE_URL = 'https://app.laurayoga.co.uk';

test('Debug dashboard loading issue', async ({ page }) => {
  const timestamp = Date.now();
  const testEmail = `debugtest${timestamp}@test.com`;
  const testPassword = 'DebugTest123!';

  console.log('\n' + '='.repeat(70));
  console.log('DASHBOARD DEBUG TEST');
  console.log('='.repeat(70));

  // Capture console logs
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    console.log(`[BROWSER ${type.toUpperCase()}] ${text}`);
  });

  // Capture failed requests
  page.on('requestfailed', request => {
    console.log(`[REQUEST FAILED] ${request.method()} ${request.url()}`);
    console.log(`   Failure: ${request.failure()?.errorText || 'Unknown'}`);
  });

  // Capture all API responses
  page.on('response', response => {
    const url = response.url();
    if (url.includes('/api/v1/')) {
      const status = response.status();
      console.log(`[API RESPONSE] ${status} ${url}`);
    }
  });

  // Register
  console.log(`\n1. Registering: ${testEmail}`);
  await page.goto(`${LIVE_URL}/register`);
  await page.waitForLoadState('networkidle');

  await page.fill('input[type="email"]', testEmail);
  await page.fill('input[name="name"]', 'Debug User');
  await page.fill('input[type="password"]', testPassword);
  await page.selectOption('select[name="experience_level"]', 'beginner');

  await page.click('button[type="submit"]');

  try {
    await page.waitForURL(/\/(dashboard|poses)/, { timeout: 10000 });
    console.log(`✅ Registered and redirected to: ${page.url()}`);
  } catch (e) {
    console.log(`❌ Registration failed`);
    throw e;
  }

  // Navigate to dashboard and monitor
  console.log(`\n2. Navigating to dashboard...`);
  await page.goto(`${LIVE_URL}/dashboard`);

  // Wait a bit to capture any console errors
  await page.waitForTimeout(5000);

  // Check what's on the page
  const bodyText = await page.textContent('body');
  console.log(`\n3. Dashboard page content (first 500 chars):`);
  console.log(bodyText.substring(0, 500));

  // Check for loading indicator
  const hasLoadingText = bodyText.includes('Loading');
  const hasLoadingSpinner = await page.locator('[data-testid="loading"], .animate-spin').count() > 0;

  console.log(`\n4. Loading state check:`);
  console.log(`   Has "Loading" text: ${hasLoadingText}`);
  console.log(`   Has spinner element: ${hasLoadingSpinner}`);

  // Take screenshot
  await page.screenshot({ path: '/tmp/dashboard-debug.png', fullPage: true });
  console.log(`   📸 Screenshot: /tmp/dashboard-debug.png`);

  // Check if dashboard actually rendered
  const hasDashboardContent = bodyText.includes('Welcome back') ||
                               bodyText.includes('Total Sessions') ||
                               bodyText.includes('YogaFlow');

  console.log(`   Has dashboard content: ${hasDashboardContent}`);

  console.log('\n' + '='.repeat(70) + '\n');

  // Fail the test if still loading
  if (hasLoadingText && !hasDashboardContent) {
    throw new Error('Dashboard stuck in loading state');
  }
});
