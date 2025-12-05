const { chromium } = require('playwright');

async function testPoseDetail() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('Navigating to login page...');
    await page.goto('http://localhost:5174/login');
    await page.waitForLoadState('networkidle');

    // Login
    console.log('Logging in...');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'TestPass123');
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard');
    console.log('Logged in successfully');

    // Navigate to poses
    console.log('Navigating to poses...');
    await page.click('a[href="/poses"]');
    await page.waitForURL('**/poses');
    await page.waitForTimeout(1000);
    console.log('On poses page');

    // Click on first pose
    console.log('Clicking on first pose...');
    await page.click('button:has-text("View Details")');
    await page.waitForURL('**/poses/*');
    await page.waitForTimeout(1000);
    console.log('On pose detail page');

    // Take screenshots
    console.log('Taking desktop screenshot...');
    await page.setViewportSize({ width: 1280, height: 1024 });
    await page.screenshot({ path: 'screenshots/pose-detail-desktop.png', fullPage: true });

    console.log('Taking tablet screenshot...');
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.screenshot({ path: 'screenshots/pose-detail-tablet.png', fullPage: true });

    console.log('Taking mobile screenshot...');
    await page.setViewportSize({ width: 375, height: 812 });
    await page.screenshot({ path: 'screenshots/pose-detail-mobile.png', fullPage: true });

    console.log('Screenshots saved successfully!');
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
}

testPoseDetail();
