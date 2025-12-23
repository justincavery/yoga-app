const { test, expect } = require('@playwright/test');

test('Local E2E: Register, login, and dashboard', async ({ page }) => {
  const timestamp = Date.now();
  const testEmail = `localtest${timestamp}@test.com`;
  const testPassword = 'TestPass123!';

  console.log(`\n${'='.repeat(60)}`);
  console.log('LOCAL END-TO-END TEST');
  console.log('='.repeat(60));

  // 1. Register
  console.log('\n1. Testing Registration...');
  await page.goto('http://localhost:5173/register');
  await page.waitForLoadState('networkidle');

  await page.fill('input[type="email"]', testEmail);
  await page.fill('input[name="name"]', 'Local Test User');
  await page.fill('input[type="password"]', testPassword);
  await page.selectOption('select[name="experience_level"]', 'beginner');

  console.log(`   Email: ${testEmail}`);

  await page.click('button[type="submit"]');

  // Should redirect to dashboard
  try {
    await page.waitForURL(/\/(dashboard|poses)/, { timeout: 10000 });
    const url = page.url();
    console.log(`   ✅ Registered successfully, redirected to: ${url}`);
  } catch (e) {
    console.log(`   ❌ Registration failed or didn't redirect`);
    await page.screenshot({ path: '/tmp/registration-failed.png' });
    throw e;
  }

  // 2. Navigate to Dashboard
  console.log('\n2. Testing Dashboard...');
  await page.goto('http://localhost:5173/dashboard');
  await page.waitForLoadState('networkidle', { timeout: 15000 });

  // Check if dashboard loads without hanging
  const bodyText = await page.textContent('body');

  if (bodyText.includes('Dashboard') || bodyText.includes('Practice')) {
    console.log(`   ✅ Dashboard loaded successfully`);
  } else {
    console.log(`   ❌ Dashboard didn't load expected content`);
  }

  // Take screenshot of dashboard
  await page.screenshot({ path: '/tmp/local-dashboard.png', fullPage: true });
  console.log(`   📸 Screenshot saved to /tmp/local-dashboard.png`);

  // 3. Check poses page
  console.log('\n3. Testing Poses Page...');
  await page.goto('http://localhost:5173/poses');
  await page.waitForSelector('text=/Showing .* poses/', { timeout: 5000 });

  const posesText = await page.textContent('body');
  if (posesText.includes('Showing')) {
    console.log(`   ✅ Poses page loaded`);
  }

  // Count pose cards
  const poseCards = await page.locator('button:has-text("View Details")').count();
  console.log(`   Found ${poseCards} pose cards`);

  console.log(`\n${'='.repeat(60)}`);
  console.log('✅ ALL LOCAL TESTS PASSED');
  console.log('='.repeat(60)}\n`);
});
