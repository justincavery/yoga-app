import { test, expect } from '@playwright/test';

test('Local: Dashboard loads after registration', async ({ page }) => {
  const timestamp = Date.now();
  const testEmail = `localtest${timestamp}@test.com`;
  const testPassword = 'TestPass123!';

  console.log('\n' + '='.repeat(60));
  console.log('LOCAL DASHBOARD TEST');
  console.log('='.repeat(60));

  // Register
  console.log(`\n1. Registering: ${testEmail}`);
  await page.goto('http://localhost:3001/register');
  await page.waitForLoadState('networkidle');

  await page.fill('input[type="email"]', testEmail);
  await page.fill('input[name="name"]', 'Local Test');
  await page.fill('input[type="password"]', testPassword);
  await page.selectOption('select[name="experience_level"]', 'beginner');

  await page.click('button[type="submit"]');

  await page.waitForURL(/\/(dashboard|poses)/, { timeout: 10000 });
  console.log(`   ✅ Registered, redirected to: ${page.url()}`);

  // Navigate to dashboard
  console.log(`\n2. Testing Dashboard...`);
  await page.goto('http://localhost:3001/dashboard');

  // Wait for dashboard to load (max 10 seconds)
  try {
    await page.waitForSelector('text=/Welcome back/', { timeout: 10000 });
    console.log(`   ✅ Dashboard loaded successfully!`);
  } catch (e) {
    console.log(`   ❌ Dashboard did not load`);
    const body = await page.textContent('body');
    console.log(`   Body: ${body.substring(0, 300)}`);
    throw e;
  }

  // Verify dashboard content
  const bodyText = await page.textContent('body');

  expect(bodyText).toContain('Welcome back');
  expect(bodyText).toContain('Total Sessions');
  expect(bodyText).toContain('Start your practice streak today');

  console.log(`   ✅ Dashboard shows correct content`);

  // Take screenshot
  await page.screenshot({ path: '/tmp/local-dashboard-fixed.png', fullPage: true });
  console.log(`   📸 Screenshot: /tmp/local-dashboard-fixed.png`);

  console.log('\n' + '='.repeat(60));
  console.log('✅ LOCAL TEST PASSED');
  console.log('='.repeat(60) + '\n');
});
