import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function takeScreenshots() {
  console.log('Launching browser...');
  const browser = await chromium.launch();

  try {
    // Desktop screenshots
    console.log('\n📸 Taking Desktop Screenshots...');
    const desktopPage = await browser.newPage({
      viewport: { width: 1280, height: 800 },
    });

    // Login page
    console.log('  - Login page');
    await desktopPage.goto('http://localhost:5173/login');
    await desktopPage.waitForTimeout(1000);
    await desktopPage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-login-desktop.png'),
      fullPage: true,
    });

    // Register page
    console.log('  - Register page');
    await desktopPage.goto('http://localhost:5173/register');
    await desktopPage.waitForTimeout(1000);
    await desktopPage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-register-desktop.png'),
      fullPage: true,
    });

    // Fill registration form (to show validation)
    console.log('  - Register page with partial form');
    await desktopPage.fill('input[name="email"]', 'test@example.com');
    await desktopPage.fill('input[name="name"]', 'Test User');
    await desktopPage.fill('input[name="password"]', 'Test');
    await desktopPage.waitForTimeout(500);
    await desktopPage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-register-form-desktop.png'),
      fullPage: true,
    });

    // Login with demo credentials
    console.log('  - Logging in with demo credentials');
    await desktopPage.goto('http://localhost:5173/login');
    await desktopPage.fill('input[name="email"]', 'test@example.com');
    await desktopPage.fill('input[name="password"]', 'TestPass123');
    await desktopPage.check('input[name="remember_me"]');
    await desktopPage.waitForTimeout(500);
    await desktopPage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-login-filled-desktop.png'),
      fullPage: true,
    });

    // Submit login
    await desktopPage.click('button[type="submit"]');
    await desktopPage.waitForURL('**/dashboard', { timeout: 5000 });
    await desktopPage.waitForTimeout(1000);

    // Dashboard
    console.log('  - Dashboard');
    await desktopPage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-dashboard-desktop.png'),
      fullPage: true,
    });

    // Navigate to Poses
    console.log('  - Poses library');
    await desktopPage.click('a[href="/poses"]');
    await desktopPage.waitForURL('**/poses', { timeout: 5000 });
    await desktopPage.waitForTimeout(2000); // Wait for poses to load
    await desktopPage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-poses-desktop.png'),
      fullPage: true,
    });

    // Search poses
    console.log('  - Poses search');
    await desktopPage.fill('input[placeholder*="Search poses"]', 'warrior');
    await desktopPage.waitForTimeout(1000);
    await desktopPage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-poses-search-desktop.png'),
      fullPage: true,
    });

    // Filter poses
    console.log('  - Poses filter');
    await desktopPage.fill('input[placeholder*="Search poses"]', '');
    await desktopPage.selectOption('select[name="difficulty"]', 'beginner');
    await desktopPage.selectOption('select[name="category"]', 'standing');
    await desktopPage.waitForTimeout(1000);
    await desktopPage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-poses-filter-desktop.png'),
      fullPage: true,
    });

    await desktopPage.close();

    // Mobile screenshots
    console.log('\n📱 Taking Mobile Screenshots...');
    const mobilePage = await browser.newPage({
      viewport: { width: 375, height: 667 },
      isMobile: true,
    });

    // Login page mobile
    console.log('  - Login page');
    await mobilePage.goto('http://localhost:5173/login');
    await mobilePage.waitForTimeout(1000);
    await mobilePage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-login-mobile.png'),
      fullPage: true,
    });

    // Register page mobile
    console.log('  - Register page');
    await mobilePage.goto('http://localhost:5173/register');
    await mobilePage.waitForTimeout(1000);
    await mobilePage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-register-mobile.png'),
      fullPage: true,
    });

    // Login and go to dashboard
    console.log('  - Dashboard');
    await mobilePage.goto('http://localhost:5173/login');
    await mobilePage.fill('input[name="email"]', 'test@example.com');
    await mobilePage.fill('input[name="password"]', 'TestPass123');
    await mobilePage.click('button[type="submit"]');
    await mobilePage.waitForURL('**/dashboard', { timeout: 5000 });
    await mobilePage.waitForTimeout(1000);
    await mobilePage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-dashboard-mobile.png'),
      fullPage: true,
    });

    // Poses page mobile (navigate directly)
    console.log('  - Poses library');
    await mobilePage.goto('http://localhost:5173/poses');
    await mobilePage.waitForTimeout(2000);
    await mobilePage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-poses-mobile.png'),
      fullPage: true,
    });

    await mobilePage.close();

    // Tablet screenshots
    console.log('\n📊 Taking Tablet Screenshots...');
    const tabletPage = await browser.newPage({
      viewport: { width: 768, height: 1024 },
    });

    // Login page tablet
    console.log('  - Login page');
    await tabletPage.goto('http://localhost:5173/login');
    await tabletPage.waitForTimeout(1000);
    await tabletPage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-login-tablet.png'),
      fullPage: true,
    });

    // Poses page tablet
    console.log('  - Poses library');
    await tabletPage.goto('http://localhost:5173/login');
    await tabletPage.fill('input[name="email"]', 'test@example.com');
    await tabletPage.fill('input[name="password"]', 'TestPass123');
    await tabletPage.click('button[type="submit"]');
    await tabletPage.waitForURL('**/dashboard', { timeout: 5000 });
    await tabletPage.click('a[href="/poses"]');
    await tabletPage.waitForURL('**/poses', { timeout: 5000 });
    await tabletPage.waitForTimeout(2000);
    await tabletPage.screenshot({
      path: join(__dirname, 'screenshots', 'batch1-poses-tablet.png'),
      fullPage: true,
    });

    await tabletPage.close();

    console.log('\n✅ All screenshots captured successfully!');
    console.log('   Screenshots saved to: frontend/screenshots/batch1-*.png');
  } catch (error) {
    console.error('\n❌ Error taking screenshots:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

takeScreenshots().catch((error) => {
  console.error(error);
  process.exit(1);
});
