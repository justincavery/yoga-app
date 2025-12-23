import { test, expect } from '@playwright/test';

test('Debug: Check auth store after registration', async ({ page }) => {
  const timestamp = Date.now();
  const testEmail = `debugauth${timestamp}@test.com`;

  // Capture all console logs
  page.on('console', msg => {
    console.log(`[BROWSER] ${msg.text()}`);
  });

  // Register
  await page.goto('https://app.laurayoga.co.uk/register');
  await page.waitForLoadState('networkidle');

  await page.fill('input[type="email"]', testEmail);
  await page.fill('input[name="name"]', 'Debug Test');
  await page.fill('input[type="password"]', 'Test123!');
  await page.selectOption('select[name="experience_level"]', 'beginner');
  await page.click('button[type="submit"]');

  await page.waitForURL(/\/dashboard/, { timeout: 10000 });

  // Check localStorage
  const authStorage = await page.evaluate(() => {
    const storage = localStorage.getItem('auth-storage');
    return storage;
  });

  console.log('\n=== AUTH STORAGE CHECK ===');
  console.log('Raw storage:', authStorage);

  if (authStorage) {
    const parsed = JSON.parse(authStorage);
    console.log('Parsed storage:', JSON.stringify(parsed, null, 2));
    console.log('Has accessToken:', !!parsed.state?.accessToken);
    console.log('Token value:', parsed.state?.accessToken?.substring(0, 50) + '...');
  } else {
    console.log('❌ NO AUTH STORAGE FOUND!');
  }

  await page.waitForTimeout(3000);
  const bodyText = await page.textContent('body');
  console.log('\nDashboard content:', bodyText.substring(0, 200));
});
