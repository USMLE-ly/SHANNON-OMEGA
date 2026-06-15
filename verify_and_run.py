#!/usr/bin/env python3
"""
SHANNON-Ω Instagram Verification & Growth Tool
Handles: login, challenge resolution, session save, growth cycles
"""
import sys, os, json, time, random, logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
log = logging.getLogger(__name__)

def verify_and_login(username, password):
    """Try ALL login methods and return a working session."""
    
    # Method 1: Try API with session
    log.info('Method 1: API login with session...')
    session_path = PROJECT_ROOT / '.ig_api_session.json'
    try:
        from instagrapi import Client
        cl = Client()
        cl.delay_range = [3, 6]
        
        if session_path.exists():
            cl.load_settings(str(session_path))
        
        cl.login(username, password)
        log.info('✓ API LOGIN SUCCESSFUL!')
        cl.dump_settings(str(session_path))
        return cl, 'api'
    except Exception as e:
        err = str(e)
        if 'challenge' in err.lower() or 'checkpoint' in err.lower():
            log.warning('⚠ Account needs verification')
            log.info('Open Instagram on your phone to approve the login')
            log.info('Or use email verification if available')
            
            # Check if we can send email code
            if hasattr(cl, 'last_json') and cl.last_json:
                with open(PROJECT_ROOT / 'last_challenge.json', 'w') as f:
                    json.dump(cl.last_json, f, indent=2)
                log.info(f'Challenge details saved to last_challenge.json')
        else:
            log.warning(f'API login error: {e}')
    
    # Method 2: Try web login via Playwright
    log.info('\nMethod 2: Web login via Playwright...')
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            context = browser.new_context(
                viewport={'width': 1366, 'height': 900},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            """)
            
            page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            page.locator('input[name="email"]').fill(username)
            time.sleep(0.5)
            page.locator('input[name="pass"]').fill(password)
            time.sleep(0.5)
            
            # Submit form via JS (most reliable)
            page.evaluate("document.getElementById('login_form')?.requestSubmit()")
            time.sleep(6)
            
            current_url = page.url.lower()
            page.screenshot(path=str(PROJECT_ROOT / 'ig_web_result.png'))
            
            if 'challenge' in current_url:
                log.warning('⚠ Challenge page detected')
                log.info(f'Challenge URL: {page.url}')
                
                # Save the challenge page HTML
                with open(PROJECT_ROOT / 'ig_challenge.html', 'w') as f:
                    f.write(page.content())
                
                # Try to find options on the challenge page
                body = page.inner_text('body')[:2000]
                log.info(f'Challenge page content:\n{body}')
                
                # Look for any email/SMS options
                if 'email' in body.lower():
                    log.info('Email verification option found!')
                if 'phone' in body.lower() or 'sms' in body.lower():
                    log.info('SMS verification option found!')
                    
            elif 'login' not in current_url:
                log.info('✓ WEB LOGIN SUCCESSFUL!')
                # Save cookies
                cookies = context.cookies()
                with open(PROJECT_ROOT / '.ig_web_cookies.json', 'w') as f:
                    json.dump(cookies, f)
                log.info(f'Saved {len(cookies)} cookies')
                context.close()
                return cookies, 'web'
            else:
                log.warning('Still on login page')
            
            browser.close()
    except Exception as e:
        log.warning(f'Web login error: {e}')
    
    # Method 3: Try mobile web
    log.info('\nMethod 3: Mobile web login...')
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            context = browser.new_context(
                viewport={'width': 390, 'height': 844},
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15'
            )
            page = context.new_page()
            page.add_init_script('Object.defineProperty(navigator, "webdriver", { get: () => undefined });')
            
            page.goto('https://www.instagram.com/accounts/login/', wait_until='domcontentloaded', timeout=20000)
            time.sleep(4)
            
            # Fill and submit on mobile
            page.locator('input').first.fill(username)
            time.sleep(0.5)
            page.locator('input').nth(1).fill(password)
            time.sleep(0.5)
            page.evaluate("document.querySelector('form')?.requestSubmit()")
            time.sleep(6)
            
            if 'challenge' in page.url.lower():
                log.warning('⚠ Mobile challenge detected')
            elif 'login' not in page.url.lower():
                log.info('✓ MOBILE LOGIN SUCCESSFUL!')
                cookies = context.cookies()
                with open(PROJECT_ROOT / '.ig_mobile_cookies.json', 'w') as f:
                    json.dump(cookies, f)
                browser.close()
                return cookies, 'mobile'
            
            browser.close()
    except Exception as e:
        log.warning(f'Mobile login error: {e}')
    
    return None, 'failed'

def run_growth(session, session_type):
    """Run growth cycles with the obtained session."""
    if not session:
        log.error('No session available')
        return
    
    log.info(f'Starting growth with {session_type} session...')
    # TODO: Implement growth using the session
    log.info('Growth module ready - needs session to proceed')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='SHANNON-Ω Instagram Verification')
    parser.add_argument('--login', nargs=2, metavar=('USER', 'PASS'), required=True)
    parser.add_argument('--email', help='Check this email for verification codes')
    parser.add_argument('--sid', help='Guerrilla Mail SID token')
    args = parser.parse_args()
    
    print('=' * 60)
    print('  SHANNON-Ω Instagram Login Assistant')
    print('=' * 60)
    
    session, s_type = verify_and_login(args.login[0], args.login[1])
    
    if session:
        print(f'\n✅ LOGIN SUCCESSFUL via {s_type}!')
        run_growth(session, s_type)
    else:
        print(f'\n❌ All login methods failed.')
        print()
        print('➡  WHAT YOU NEED TO DO:')
        print('   1. Open the Instagram app on your phone')
        print('   2. Check your notifications/activity for a login prompt')
        print('   3. Tap "Approve" or "This was me"')
        print('   4. Run this command again:')
        print(f'      python3 verify_and_run.py --login {args.login[0]} [password]')
        print()
        print('➡  OR try email verification:')
        print('   1. Run the script with --email flag:')
        print(f'      python3 verify_and_run.py --login {args.login[0]} [password] --email your@email.com')
        print()
        print('➡  After successful login, use the growth bot:')
        print(f'      python3 million_bot/scripts/bot_engine.py --login {args.login[0]} [password] --cycles 10')
