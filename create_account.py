#!/usr/bin/env python3
"""
SHANNON-Ω Instagram Account Creator
You provide email + verification code. We handle the rest.
"""
import sys, os, json, time, random, re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

def random_delay(min_s=0.5, max_s=2.0):
    time.sleep(random.uniform(min_s, max_s))

def main():
    print('=' * 60)
    print('  SHANNON-Ω Instagram Account Creator')
    print('=' * 60)
    
    # Get user input
    email = input('\nEmail: ').strip()
    if not email:
        print('❌ Email is required')
        sys.exit(1)
    
    password = input('Password: ').strip()
    if not password:
        password = f'SHANNON{random.randint(1000,9999)}!'
        print(f'  Using generated password: {password}')
    
    fullname = input('Full name (e.g. "Vaulex Watches"): ').strip() or 'Vaulex Watches'
    username = input('Username: ').strip()
    if not username:
        username = f'vaulex_{random.randint(10000, 99999)}'
        print(f'  Using generated username: {username}')
    
    print(f'\n📋 Account Details:')
    print(f'  Email:    {email}')
    print(f'  Password: {password}')
    print(f'  Name:     {fullname}')
    print(f'  Username: {username}')
    
    # Save credentials
    creds = {'email': email, 'password': password, 'username': username, 'fullname': fullname}
    with open(PROJECT_ROOT / '.ig_new_creds.json', 'w') as f:
        json.dump(creds, f)
    
    print('\n🚀 Launching Instagram signup...')
    
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        # Launch with stealth
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
            ]
        )
        
        # Use a realistic profile
        context = browser.new_context(
            viewport={'width': 1366, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            permissions=['geolocation'],
        )
        
        page = context.new_page()
        
        # Maximum stealth
        page.add_init_script("""
        // Override webdriver
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        
        // Override plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // Override chrome object
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: 'denied' }) :
                originalQuery(parameters)
        );
        
        // Remove webdriver trace
        delete navigator.__proto__.webdriver;
        """)
        
        try:
            # Step 1: Go to signup page
            print('\n[1/5] Loading signup page...')
            page.goto('https://www.instagram.com/accounts/emailsignup/', wait_until='domcontentloaded', timeout=30000)
            random_delay(3, 5)
            print(f'  URL: {page.url}')
            
            page.screenshot(path=str(PROJECT_ROOT / 'ig_signup_01.png'))
            
            # Step 2: Fill the signup form
            print('\n[2/5] Filling signup form...')
            
            # Wait for inputs
            page.wait_for_selector('input', timeout=10000)
            random_delay(1, 2)
            
            # Find all input fields
            inputs = page.locator('input').all()
            print(f'  Found {len(inputs)} input fields')
            
            if len(inputs) >= 4:
                # Standard signup: [email, password, fullname, username]
                inputs[0].fill(email)
                random_delay(0.5, 1)
                inputs[1].fill(password)
                random_delay(0.5, 1)
                inputs[2].fill(fullname)
                random_delay(0.5, 1)
                inputs[3].fill(username)
                random_delay(0.5, 1)
                print('  ✓ Form filled')
            else:
                print(f'  ⚠ Only {len(inputs)} inputs found, trying anyway...')
                for i, inp in enumerate(inputs):
                    if i == 0: inp.fill(email)
                    elif i == 1: inp.fill(password)
                    elif i == 2: inp.fill(fullname)
                    elif i == 3: inp.fill(username)
                    random_delay(0.3, 0.7)
            
            page.screenshot(path=str(PROJECT_ROOT / 'ig_signup_02_filled.png'))
            
            # Step 3: Click submit
            print('\n[3/5] Submitting form...')
            
            # Look for submit button
            submitted = False
            for selector in [
                'button[type="submit"]',
                'div:has-text("Sign up")',
                'button:has-text("Sign up")',
                'button',
            ]:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        print(f'  Clicked: {selector}')
                        submitted = True
                        break
                except:
                    continue
            
            if not submitted:
                # Try pressing Enter
                page.keyboard.press('Enter')
                print('  Pressed Enter')
            
            random_delay(3, 5)
            
            # Check for birthday field
            page.screenshot(path=str(PROJECT_ROOT / 'ig_signup_03_birthday.png'))
            current_url = page.url
            print(f'  URL: {current_url}')
            
            # Check if birthday field appeared
            birthday_inputs = page.locator('select').all()
            if len(birthday_inputs) >= 3:
                print('\n[3b/5] Filling birthday...')
                # Select a birthday
                birthday_inputs[0].select_option('1')
                random_delay(0.3, 0.7)
                birthday_inputs[1].select_option('Jan')
                random_delay(0.3, 0.7)
                birthday_inputs[2].select_option('1990')
                random_delay(0.5, 1)
                
                # Click next/submit
                for selector in ['button[type="submit"]', 'button:has-text("Next")', 'button']:
                    try:
                        btn = page.locator(selector).first
                        if btn.is_visible(timeout=2000):
                            btn.click()
                            print('  Birthday submitted')
                            break
                    except:
                        continue
                
                random_delay(3, 5)
                page.screenshot(path=str(PROJECT_ROOT / 'ig_signup_04_birthday_done.png'))
                print(f'  URL: {page.url}')
            
            # Step 4: Wait for verification code from user
            print('\n' + '=' * 60)
            print('  ✅ SIGNUP SUBMITTED!')
            print('  📧 Instagram sent a verification code to:')
            print(f'     {email}')
            print()
            print('  🔑 Please check your email and send me the code.')
            print('=' * 60)
            
            # Save state
            state = {
                'email': email,
                'password': password,
                'username': username,
                'fullname': fullname,
                'browser_pid': os.getpid(),
                'step': 'waiting_for_code',
                'url': current_url,
            }
            with open(PROJECT_ROOT / '.ig_signup_state.json', 'w') as f:
                json.dump(state, f, indent=2)
            
            # Save context for later use
            context.storage_state(path=str(PROJECT_ROOT / '.ig_signup_context.json'))
            
            # Wait for code from user input
            code = None
            for attempt in range(60):  # Wait up to ~10 min
                print(f'\r  ⏳ Waiting for code... ({attempt+1}/60, check every 10s)', end='', flush=True)
                time.sleep(10)
                
                # Check if state file was updated
                try:
                    with open(PROJECT_ROOT / '.ig_signup_state.json') as f:
                        s = json.load(f)
                    if s.get('step') == 'code_received':
                        code = s.get('code')
                        print(f'\n  ✅ Code received: {code}')
                        break
                except:
                    pass
            
            if not code:
                print('\n\n  ⚠ No code received yet.')
                print('  The browser state is saved.')
                print('  Run: python3 enter_code.py <CODE>')
                print('\n  Keeping browser alive for you to send the code...')
                
                # Keep the script running for the user
                page.screenshot(path=str(PROJECT_ROOT / 'ig_signup_waiting.png'))
                
                while True:
                    try:
                        with open(PROJECT_ROOT / '.ig_signup_state.json') as f:
                            s = json.load(f)
                        if s.get('step') == 'code_received':
                            code = s.get('code')
                            print(f'\n✅ Code received: {code}')
                            break
                        if s.get('step') == 'cancelled':
                            print('\n❌ Cancelled')
                            browser.close()
                            return
                    except:
                        pass
                    time.sleep(5)
            
            # Step 5: Enter verification code
            if code:
                print(f'\n[4/5] Entering verification code: {code}...')
                
                # Look for code input fields
                code_entered = False
                
                # Try numeric input fields (one per digit)
                code_inputs = page.locator('input[inputmode="numeric"]').all()
                if len(code_inputs) >= 4:
                    for i, digit in enumerate(code):
                        if i < len(code_inputs):
                            code_inputs.nth(i).fill(digit)
                            random_delay(0.1, 0.3)
                    code_entered = True
                    print('  ✓ Code entered (digit fields)')
                else:
                    # Try single input field
                    try:
                        single_input = page.locator('input[type="tel"]').first
                        if single_input.is_visible(timeout=3000):
                            single_input.fill(code)
                            code_entered = True
                            print('  ✓ Code entered (tel field)')
                    except:
                        pass
                    
                    if not code_entered:
                        # Try any visible input
                        for inp in page.locator('input').all():
                            if inp.is_visible():
                                inp.fill(code)
                                code_entered = True
                                print('  ✓ Code entered')
                                break
                
                if code_entered:
                    random_delay(2, 4)
                    
                    # Click verify/submit
                    for selector in ['button[type="submit"]', 'button:has-text("Next")', 'button:has-text("Verify")', 'button']:
                        try:
                            btn = page.locator(selector).first
                            if btn.is_visible(timeout=2000):
                                btn.click()
                                print('  ✓ Verification submitted')
                                break
                        except:
                            continue
                    
                    random_delay(5, 8)
                    page.screenshot(path=str(PROJECT_ROOT / 'ig_signup_05_verified.png'))
                    print(f'  URL: {page.url}')
                    
                    # Check for success
                    if 'challenge' in page.url.lower():
                        print('\n⚠ Challenge page detected')
                        print('  Account created but needs device verification')
                    elif 'login' in page.url.lower():
                        print('\n⚠ Redirected to login - may need to sign in')
                    else:
                        print('\n✅ ACCOUNT CREATED SUCCESSFULLY!')
                    
                    # Save final state
                    state['step'] = 'completed'
                    state['final_url'] = page.url
                    with open(PROJECT_ROOT / '.ig_signup_state.json', 'w') as f:
                        json.dump(state, f, indent=2)
                    
                    # Try to save API session
                    try:
                        cl.dump_settings(str(PROJECT_ROOT / '.ig_api_session.json'))
                        print('  ✓ API session saved')
                    except:
                        pass
                else:
                    print('  ❌ Could not find code input field')
                    page.screenshot(path=str(PROJECT_ROOT / 'ig_signup_error_code.png'))
            
            # Save final state
            context.storage_state(path=str(PROJECT_ROOT / '.ig_signup_final.json'))
            
            print('\n' + '=' * 60)
            print('  Account creation complete!')
            print(f'  Username: {username}')
            print(f'  Password: {password}')
            print('=' * 60)
            
        except Exception as e:
            print(f'\n❌ Error: {e}')
            import traceback
            traceback.print_exc()
            page.screenshot(path=str(PROJECT_ROOT / 'ig_signup_error.png'))
        
        finally:
            try:
                browser.close()
            except:
                pass

if __name__ == '__main__':
    main()
