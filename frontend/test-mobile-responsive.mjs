import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testMobileResponsive() {
  const browser = await chromium.launch({ headless: false });

  // Test mobile viewport (iPhone 12)
  const mobileContext = await browser.newContext({
    viewport: { width: 390, height: 844 },
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
  });
  const mobilePage = await mobileContext.newPage();

  try {
    console.log('Testing mobile responsiveness...');

    // Test Forgot Password on mobile
    await mobilePage.goto('http://localhost:5173/forgot-password');
    await mobilePage.screenshot({ path: join(__dirname, 'screenshots', 'forgot-password-mobile.png'), fullPage: true });
    console.log('✓ Screenshot saved: forgot-password-mobile.png');

    // Test Reset Password on mobile
    await mobilePage.goto('http://localhost:5173/reset-password/test-token');
    await mobilePage.screenshot({ path: join(__dirname, 'screenshots', 'reset-password-mobile.png'), fullPage: true });
    console.log('✓ Screenshot saved: reset-password-mobile.png');

    // Test with password strength indicator
    await mobilePage.fill('input[name="password"]', 'TestPass123!@#');
    await mobilePage.screenshot({ path: join(__dirname, 'screenshots', 'reset-password-mobile-strength.png'), fullPage: true });
    console.log('✓ Screenshot saved: reset-password-mobile-strength.png');

    console.log('\\n✅ Mobile responsive tests completed!');

  } catch (error) {
    console.error('❌ Error during testing:', error);
  } finally {
    await browser.close();
  }
}

testMobileResponsive();
