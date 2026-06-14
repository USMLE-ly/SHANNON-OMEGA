#!/usr/bin/env node
/**
 * IG Creator — Instagram account creation + verification bot
 * Full pipeline: generate email → sign up → verify code → start bot
 */
import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(__dirname, '../../..');
const ELECTRON_PATH = path.join(PROJECT_ROOT, 'instatakker', 'node_modules', 'electron', 'dist', 'electron');
const LAST_EMAIL = path.join(PROJECT_ROOT, '.last_email.json');

const GUERRILLA_API = 'https://api.guerrillamail.com/ajax.php';

const CONFIG = {
  headless: false,  // Set to true for fully automated
  executablePath: ELECTRON_PATH,
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
};

function randomDelay(min, max) {
  return new Promise(r => setTimeout(r, Math.floor(Math.random() * (max - min + 1) + min)));
}

async function apiCall(params) {
  const url = `${GUERRILLA_API}?${new URLSearchParams(params)}`;
  const res = await fetch(url);
  return res.json();
}

async function generateEmail() {
  console.log('[IG] Generating temporary email...');
  const data = await apiCall({ f: 'get_email_address', ip: '127.0.0.1', agent: 'ZORG-Ω' });
  fs.writeFileSync(LAST_EMAIL, JSON.stringify(data, null, 2));
  console.log(`[IG] Email: ${data.email_addr}`);
  return data;
}

async function waitForEmail(sidToken, timeoutMs = 180000) {
  console.log('[IG] Waiting for verification email...');
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const inbox = await apiCall({ f: 'get_email_list', sid_token: sidToken, offset: '0', limit: '10' });
    const emails = inbox.list || [];
    for (const email of emails) {
      if (email.mail_from && email.mail_from.toLowerCase().includes('instagram')) {
        console.log(`[IG] Instagram email received: "${email.mail_subject}"`);
        const full = await apiCall({ f: 'fetch_email', sid_token: sidToken, email_id: email.mail_id });
        return full;
      }
    }
    process.stdout.write('.');
    await new Promise(r => setTimeout(r, 5000));
  }
  console.log('\n[IG] Timeout waiting for Instagram email');
  return null;
}

function extractCode(emailBody) {
  if (!emailBody) return null;
  // Instagram codes are typically 6 digits
  const match = emailBody.match(/(\d{6})/);
  return match ? match[0] : null;
}

async function createAccount(email, password, fullname, username) {
  console.log(`[IG] Launching browser for signup...`);
  const browser = await puppeteer.launch(CONFIG);
  const page = await browser.newPage();
  
  await page.setUserAgent(
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
    '(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
  );
  
  try {
    // Step 1: Go to Instagram signup
    console.log('[IG] Step 1: Loading Instagram signup...');
    await page.goto('https://www.instagram.com/accounts/signup/', {
      waitUntil: 'networkidle2', timeout: 30000
    });
    await randomDelay(2000, 3000);
    
    // Step 2: Fill email
    console.log(`[IG] Step 2: Entering email: ${email}`);
    const emailInput = await page.waitForSelector('input[name="emailOrPhone"]', { timeout: 10000 });
    await emailInput.click();
    await randomDelay(500, 1000);
    await page.type('input[name="emailOrPhone"]', email, { delay: 30 + Math.random() * 50 });
    await randomDelay(800, 1500);
    
    // Step 3: Fill full name
    console.log(`[IG] Step 3: Entering name: ${fullname}`);
    await page.type('input[name="fullName"]', fullname, { delay: 30 + Math.random() * 50 });
    await randomDelay(800, 1500);
    
    // Step 4: Fill username
    console.log(`[IG] Step 4: Entering username: ${username}`);
    await page.type('input[name="username"]', username, { delay: 30 + Math.random() * 50 });
    await randomDelay(800, 1500);
    
    // Step 5: Fill password
    console.log(`[IG] Step 5: Entering password`);
    await page.type('input[name="password"]', password, { delay: 20 + Math.random() * 40 });
    await randomDelay(1000, 2000);
    
    // Step 6: Click sign up
    console.log('[IG] Step 6: Submitting signup...');
    const submitBtn = await page.$('button[type="submit"]');
    if (submitBtn) {
      await submitBtn.click();
    }
    
    // Wait for next page (may ask for birthday or confirmation)
    console.log('[IG] Waiting for post-signup page...');
    await randomDelay(5000, 8000);
    
    // Take screenshot to see current state
    const screenshot = path.join(PROJECT_ROOT, 'ig_signup.png');
    await page.screenshot({ path: screenshot, fullPage: false });
    console.log(`[IG] Screenshot: ${screenshot}`);
    
    // Check current URL
    const currentUrl = page.url();
    console.log(`[IG] Current URL: ${currentUrl}`);
    
    return { browser, page, success: true };
    
  } catch (e) {
    console.error(`[IG] Error: ${e.message}`);
    const screenshot = path.join(PROJECT_ROOT, 'ig_error.png');
    await page.screenshot({ path: screenshot, fullPage: false });
    console.log(`[IG] Error screenshot: ${screenshot}`);
    await browser.close();
    return { browser: null, page: null, success: false, error: e.message };
  }
}

async function verifyCode(browser, page, code) {
  if (!page) return false;
  try {
    console.log(`[IG] Entering verification code: ${code}`);
    
    // Look for code input fields
    const codeInputs = await page.$$('input[inputmode="numeric"]');
    if (codeInputs.length > 0) {
      // Type code digit by digit
      for (let i = 0; i < code.length && i < codeInputs.length; i++) {
        await codeInputs[i].type(code[i], { delay: 100 + Math.random() * 200 });
        await randomDelay(200, 400);
      }
      console.log('[IG] Verification code entered');
      await randomDelay(3000, 5000);
      return true;
    }
    console.log('[IG] No code input fields found, checking URL...');
    console.log(`[IG] Current URL: ${page.url()}`);
    return false;
  } catch (e) {
    console.error(`[IG] Verification error: ${e.message}`);
    return false;
  }
}

const args = process.argv.slice(2);
const cmd = args[0] || 'help';

switch (cmd) {
  case 'full': {
    // Full automated pipeline
    const emailData = await generateEmail();
    const email = emailData.email_addr;
    const sid = emailData.sid_token;
    
    const password = `ZORG${Math.random().toString(36).slice(2, 10)}!${Math.floor(Math.random() * 999)}`;
    const fullname = args[1] || 'Vaulex Watches';
    const username = args[2] || `vaulex_${Date.now().toString(36)}`;
    
    console.log(`[IG] === Full Account Creation ===`);
    console.log(`[IG] Email:    ${email}`);
    console.log(`[IG] Password: ${password}`);
    console.log(`[IG] Name:     ${fullname}`);
    console.log(`[IG] Username: ${username}`);
    
    const { browser, page, success } = await createAccount(email, password, fullname, username);
    
    if (success && page) {
      console.log('[IG] Waiting for verification email...');
      const verifEmail = await waitForEmail(sid);
      
      if (verifEmail) {
        const body = verifEmail.mail_body || '';
        console.log(`[IG] Email body preview: ${body.substring(0, 300)}`);
        const code = extractCode(body);
        
        if (code) {
          console.log(`[IG] Verification code found: ${code}`);
          await verifyCode(browser, page, code);
          await randomDelay(5000, 8000);
          console.log('[IG] Account creation pipeline completed');
          
          // Save credentials
          const creds = { email, password, fullname, username, sid };
          const credPath = path.join(PROJECT_ROOT, '.ig_credentials.json');
          fs.writeFileSync(credPath, JSON.stringify(creds, null, 2));
          console.log(`[IG] Credentials saved to: ${credPath}`);
        } else {
          console.log('[IG] Could not extract verification code from email');
        }
      }
      
      await randomDelay(3000, 5000);
      await browser.close();
    }
    break;
  }
  
  case 'signup': {
    // Just do signup with existing email
    const email = args[1] || JSON.parse(fs.readFileSync(LAST_EMAIL, 'utf8')).email_addr;
    const password = args[2] || `ZORG${Math.random().toString(36).slice(2, 10)}!99`;
    const fullname = args[3] || 'Vaulex Official';
    const username = args[4] || `vaulex_${Date.now().toString(36)}`;
    
    const { browser, page } = await createAccount(email, password, fullname, username);
    if (browser) {
      console.log('[IG] Browser open. Complete verification manually or run verify command.');
      // Don't close browser - let user see it
    }
    break;
  }
  
  case 'verify': {
    // Check for verification email and extract code
    const sid = args[1] || JSON.parse(fs.readFileSync(LAST_EMAIL, 'utf8')).sid_token;
    const verifEmail = await waitForEmail(sid);
    if (verifEmail) {
      const body = verifEmail.mail_body || '';
      const code = extractCode(body);
      if (code) {
        console.log(`[IG] Verification code: ${code}`);
      } else {
        console.log('[IG] No code found in email');
        console.log(`Body: ${body.substring(0, 500)}`);
      }
    }
    break;
  }
  
  case 'email': {
    const data = await generateEmail();
    console.log(`Email: ${data.email_addr}`);
    console.log(`SID:   ${data.sid_token}`);
    break;
  }
  
  default:
    console.log('IG Creator — Instagram Account Automation');
    console.log('');
    console.log('Commands:');
    console.log('  full [name] [username]    Full pipeline: email → signup → verify');
    console.log('  signup [email] [pass]     Manual signup (opens browser)');
    console.log('  verify [sid]              Wait for verification code');
    console.log('  email                     Generate new temp email');
}
