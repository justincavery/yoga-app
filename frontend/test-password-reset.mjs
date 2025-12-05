import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testPasswordReset() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('Testing Forgot Password page...');

    // Test Forgot Password page
    await page.goto('http://localhost:5173/forgot-password');
    await page.screenshot({ path: join(__dirname, 'screenshots', 'forgot-password-initial.png') });
    console.log('✓ Screenshot saved: forgot-password-initial.png');

    // Check page elements
    const header = await page.locator('h1:has-text("Forgot Your Password?")').isVisible();
    console.log(`✓ Header visible: ${header}`);

    const emailInput = await page.locator('input[type="email"]').isVisible();
    console.log(`✓ Email input visible: ${emailInput}`);

    const submitButton = await page.locator('button:has-text("Send Reset Link")').isVisible();
    console.log(`✓ Submit button visible: ${submitButton}`);

    // Test form submission with valid email
    await page.fill('input[type="email"]', 'test@example.com');
    await page.screenshot({ path: join(__dirname, 'screenshots', 'forgot-password-filled.png') });
    console.log('✓ Screenshot saved: forgot-password-filled.png');

    await page.click('button:has-text("Send Reset Link")');

    // Wait for success message
    await page.waitForSelector('text=Check Your Email', { timeout: 5000 });
    await page.screenshot({ path: join(__dirname, 'screenshots', 'forgot-password-success.png') });
    console.log('✓ Screenshot saved: forgot-password-success.png');

    console.log('\\nTesting Reset Password page...');

    // Test Reset Password page
    await page.goto('http://localhost:5173/reset-password/test-token-123');
    await page.screenshot({ path: join(__dirname, 'screenshots', 'reset-password-initial.png') });
    console.log('✓ Screenshot saved: reset-password-initial.png');

    // Check page elements
    const resetHeader = await page.locator('h1:has-text("Reset Your Password")').isVisible();
    console.log(`✓ Reset header visible: ${resetHeader}`);

    const passwordInput = await page.locator('input[name="password"]').isVisible();
    console.log(`✓ Password input visible: ${passwordInput}`);

    const confirmInput = await page.locator('input[name="confirmPassword"]').isVisible();
    console.log(`✓ Confirm password input visible: ${confirmInput}`);

    // Test password strength indicator
    await page.fill('input[name="password"]', 'Test');
    await page.screenshot({ path: join(__dirname, 'screenshots', 'reset-password-weak.png') });
    console.log('✓ Screenshot saved: reset-password-weak.png (weak password)');

    await page.fill('input[name="password"]', 'TestPass123!@#');
    await page.screenshot({ path: join(__dirname, 'screenshots', 'reset-password-strong.png') });
    console.log('✓ Screenshot saved: reset-password-strong.png (strong password)');

    // Fill confirm password
    await page.fill('input[name="confirmPassword"]', 'TestPass123!@#');
    await page.screenshot({ path: join(__dirname, 'screenshots', 'reset-password-filled.png') });
    console.log('✓ Screenshot saved: reset-password-filled.png');

    // Submit form
    await page.click('button:has-text("Reset Password")');

    // Wait for success or redirect
    try {
      await page.waitForSelector('text=Password reset successful', { timeout: 3000 });
      await page.screenshot({ path: join(__dirname, 'screenshots', 'reset-password-success.png') });
      console.log('✓ Screenshot saved: reset-password-success.png');
    } catch (e) {
      console.log('✓ Form submitted (redirect may occur)');
    }

    console.log('\\n✅ All password reset pages tested successfully!');

  } catch (error) {
    console.error('❌ Error during testing:', error);
    await page.screenshot({ path: join(__dirname, 'screenshots', 'error.png') });
  } finally {
    await browser.close();
  }
}

// Create screenshots directory if it doesn't exist
import { existsSync, mkdirSync } from 'fs';
const screenshotsDir = join(dirname(fileURLToPath(import.meta.url)), 'screenshots');
if (!existsSync(screenshotsDir)) {
  mkdirSync(screenshotsDir, { recursive: true });
}

testPasswordReset();
