import { test, expect } from '@playwright/test';

const LIVE_URL = 'https://app.laurayoga.co.uk';

test.describe('Production Final Verification', () => {
  test('Complete flow: Register → Dashboard → Poses', async ({ page }) => {
    const timestamp = Date.now();
    const testEmail = `finaltest${timestamp}@test.com`;
    const testPassword = 'FinalTest123!';

    console.log('\n' + '='.repeat(70));
    console.log('PRODUCTION FINAL VERIFICATION TEST');
    console.log('='.repeat(70));

    // 1. REGISTRATION
    console.log('\n1. Testing Registration...');
    await page.goto(`${LIVE_URL}/register`);
    await page.waitForLoadState('networkidle');

    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[name="name"]', 'Final Test User');
    await page.fill('input[type="password"]', testPassword);
    await page.selectOption('select[name="experience_level"]', 'beginner');

    console.log(`   Email: ${testEmail}`);
    console.log(`   Submitting registration...`);

    await page.click('button[type="submit"]');

    // Should redirect to dashboard or poses
    try {
      await page.waitForURL(/\/(dashboard|poses)/, { timeout: 10000 });
      const redirectUrl = page.url();
      console.log(`   ✅ Registration successful, redirected to: ${redirectUrl}`);
    } catch (e) {
      console.log(`   ❌ Registration failed or didn't redirect`);
      const errorText = await page.textContent('body').catch(() => 'Could not read page');
      console.log(`   Page content: ${errorText.substring(0, 200)}...`);
      await page.screenshot({ path: '/tmp/prod-registration-failed.png' });
      throw new Error('Registration failed');
    }

    // 2. DASHBOARD TEST
    console.log('\n2. Testing Dashboard...');
    await page.goto(`${LIVE_URL}/dashboard`);

    // Wait for page to load but don't hang
    const loadPromise = page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {
      console.log('   ⚠️  Network idle timeout (may still be loading)');
    });

    const contentPromise = page.waitForSelector('body', { timeout: 5000 });

    await Promise.race([loadPromise, contentPromise]);

    // Check if dashboard loaded (not stuck in infinite loading)
    const bodyText = await page.textContent('body');

    // Look for dashboard-specific content
    const hasDashboardContent = bodyText.includes('Dashboard') ||
                                 bodyText.includes('Practice') ||
                                 bodyText.includes('Stats') ||
                                 bodyText.includes('History');

    if (hasDashboardContent) {
      console.log(`   ✅ Dashboard loaded with content`);
    } else {
      console.log(`   ⚠️  Dashboard loaded but content unclear`);
      console.log(`   First 300 chars: ${bodyText.substring(0, 300)}`);
    }

    // Check for infinite loading spinner
    const spinners = await page.locator('[data-testid="loading"], .spinner, .loading').count();
    if (spinners > 0) {
      const spinnerVisible = await page.locator('[data-testid="loading"], .spinner, .loading').first().isVisible();
      if (spinnerVisible) {
        console.log(`   ❌ Dashboard stuck in loading state`);
        await page.screenshot({ path: '/tmp/prod-dashboard-loading.png' });
        throw new Error('Dashboard stuck loading');
      }
    } else {
      console.log(`   ✅ No loading spinner (page rendered)`);
    }

    await page.screenshot({ path: '/tmp/prod-dashboard-success.png', fullPage: true });
    console.log(`   📸 Dashboard screenshot: /tmp/prod-dashboard-success.png`);

    // 3. POSES PAGE TEST
    console.log('\n3. Testing Poses Page...');
    await page.goto(`${LIVE_URL}/poses`);
    await page.waitForSelector('text=/Showing .* poses/', { timeout: 10000 });

    const posesText = await page.textContent('text=/Showing .* poses/');
    console.log(`   ✅ Poses page: ${posesText}`);

    // Count pose cards
    const poseCards = await page.locator('button:has-text("View Details")').count();
    console.log(`   ✅ Found ${poseCards} pose cards`);

    expect(poseCards).toBeGreaterThan(0);

    // 4. NAVIGATION TEST
    console.log('\n4. Testing Navigation...');

    // Click Dashboard link
    await page.click('a:has-text("Dashboard"), nav a:has-text("Dashboard")');
    await page.waitForURL(/\/dashboard/, { timeout: 5000 });
    console.log(`   ✅ Dashboard navigation works`);

    // Final verification
    console.log('\n' + '='.repeat(70));
    console.log('✅ ALL TESTS PASSED - PRODUCTION SITE WORKING');
    console.log('='.repeat(70));
    console.log('\nSummary:');
    console.log('  ✅ Registration: Success');
    console.log('  ✅ Dashboard: Loads without hanging');
    console.log('  ✅ Poses Page: Displays ' + poseCards + ' poses');
    console.log('  ✅ Navigation: Working');
    console.log('\n' + '='.repeat(70) + '\n');
  });
});
