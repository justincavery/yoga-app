import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });
  const page = await context.newPage();

  console.log('Navigating to http://localhost:5173');
  await page.goto('http://localhost:5173');
  await page.waitForLoadState('networkidle');

  console.log('Taking desktop screenshot...');
  await page.screenshot({ path: 'screenshots/desktop-full.png', fullPage: true });

  console.log('Taking mobile screenshot...');
  await page.setViewportSize({ width: 375, height: 667 });
  await page.screenshot({ path: 'screenshots/mobile-full.png', fullPage: true });

  console.log('Taking tablet screenshot...');
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.screenshot({ path: 'screenshots/tablet-full.png', fullPage: true });

  await browser.close();
  console.log('Screenshots saved to screenshots/ directory');
})();
