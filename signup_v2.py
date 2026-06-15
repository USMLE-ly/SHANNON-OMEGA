#!/usr/bin/env python3
"""
SHANNON-Ω Instagram Signup v2 — handles full flow with birthday + verification code
"""
import sys, os, json, time, random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

def rd(min_s=0.5, max_s=2.0):
    time.sleep(random.uniform(min_s, max_s))

def main():
    email = 'vehokij438@afterdo.com'
    password = 'Hesoyam2001'
    fullname = 'Vaulex Watches'
    username = 'vaulex_watches_off'
    
    print('=' * 50)
    print('SHANNON-Ω Instagram Signup v2')
    print(f'Email: {email}')
    print(f'Username: {username}')
    print('=' * 50)
    
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            viewport={'width': 1366, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='en-US',
        )
        page = context.new_page()
        page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        window.chrome = { runtime: {} };
        """)
        
        try:
            # STEP 1: Load signup
            print('\n[1] Loading signup page...')
            page.goto('https://www.instagram.com/accounts/emailsignup/', wait_until='domcontentloaded', timeout=30000)
            rd(3, 4)
            page.screenshot(path=str(PROJECT_ROOT / 's01_loaded.png'))
            
            # STEP 2: Fill form
            print('[2] Filling form...')
            inputs = page.locator('input').all()
            for i, (val, label) in enumerate(zip(
                [email, password, fullname, username],
                ['email', 'password', 'name', 'username']
            )):
                if i < len(inputs):
                    inputs[i].fill(val)
                    rd(0.4, 0.8)
                    print(f'  ✓ {label}')
            
            # STEP 3: Click "Sign up" to reveal birthday
            print('[3] Clicking Sign up...')
            page.evaluate("""
                const divs = document.querySelectorAll('div');
                for (const d of divs) {
                    if (d.innerText === 'Sign up' && d.offsetParent !== null) {
                        d.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
                        break;
                    }
                }
            """)
            rd(3, 5)
            page.screenshot(path=str(PROJECT_ROOT / 's02_after_signup_click.png'))
            
            # STEP 4: Fill birthday using comboboxes
            print('[4] Filling birthday (combobox dropdowns)...')
            
            birthday_data = [('Month', 'January'), ('Day', '1'), ('Year', '1995')]
            
            for label, value in birthday_data:
                try:
                    # Find the combobox div with this label
                    combo = page.locator(f'div[role="combobox"]:has-text("{label}")').first
                    if combo.is_visible(timeout=3000):
                        print(f'  Opening {label} combobox...')
                        combo.click()
                        rd(0.5, 1)
                        
                        # Wait for the dropdown/listbox to appear
                        rd(0.5, 1)
                        
                        # Find and click the option
                        option = page.locator(f'div[role="option"]:has-text("{value}"), div[role="option"]:has-text("{value}")').first
                        if option.is_visible(timeout=3000):
                            option.click()
                            print(f'  ✓ Selected {label}: {value}')
                            rd(0.3, 0.7)
                        else:
                            # Try scrolling the list
                            print(f'  Option not visible, pressing arrow keys...')
                            page.keyboard.press('ArrowDown')
                            rd(0.2, 0.5)
                            page.keyboard.press('Enter')
                            rd(0.3, 0.7)
                    else:
                        print(f'  ⚠ {label} combobox not visible')
                except Exception as e:
                    print(f'  ⚠ {label} error: {e}')
            
            page.screenshot(path=str(PROJECT_ROOT / 's03_birthday_filled.png'))
            
            # STEP 5: Click Submit
            print('[5] Clicking Submit...')
            page.evaluate("""
                const divs = document.querySelectorAll('div');
                for (const d of divs) {
                    if (d.innerText === 'Submit' && d.offsetParent !== null) {
                        d.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
                        break;
                    }
                }
            """)
            rd(4, 6)
            page.screenshot(path=str(PROJECT_ROOT / 's04_after_submit.png'))
            print(f'  URL: {page.url}')
            
            # Check what page we're on
            body = page.inner_text('body')[:800]
            print(f'  Body: {body[:200]}')
            
            # Check for verification code inputs
            numeric_inputs = page.locator('input[inputmode="numeric"]').all()
            if len(numeric_inputs) > 0:
                print(f'\n✅ VERIFICATION CODE PAGE! Found {len(numeric_inputs)} digit inputs')
                
                # Save state and wait for code
                state = {
                    'email': email, 'password': password, 'username': username, 'fullname': fullname,
                    'step': 'waiting_for_code', 'url': page.url
                }
                with open(PROJECT_ROOT / '.ig_state.json', 'w') as f:
                    json.dump(state, f)
                
                context.storage_state(path=str(PROJECT_ROOT / '.ig_browser_state.json'))
                
                print('\n' + '=' * 55)
                print('  ✅ SIGNUP SUBMITTED SUCCESSFULLY!')
                print(f'  📧 Code sent to: {email}')
                print()
                print('  🔑 Send me the verification code and I\'ll enter it!')
                print('  💡 Or run: python3 enter_code_v2.py <CODE>')
                print('=' * 55)
                
                # Wait for code from user
                code = None
                state_path = PROJECT_ROOT / '.ig_state.json'
                
                while True:
                    rd(5, 8)
                    try:
                        with open(state_path) as f:
                            s = json.load(f)
                        if s.get('step') == 'code_received':
                            code = s.get('code')
                            print(f'\n✅ Received code: {code}')
                            break
                    except:
                        pass
                
                # Enter the code
                if code:
                    print(f'\n[6] Entering code: {code}...')
                    for i, digit in enumerate(code):
                        if i < len(numeric_inputs):
                            numeric_inputs.nth(i).fill(digit)
                            rd(0.1, 0.25)
                    print('  ✓ Code entered')
                    rd(2, 4)
                    
                    # Click Next/Verify
                    for text in ['Next', 'Verify', 'Submit', 'Confirm']:
                        try:
                            btn = page.locator(f'button:has-text("{text}")').first
                            if btn.is_visible(timeout=2000):
                                btn.click()
                                print(f'  ✓ Clicked {text}')
                                break
                        except:
                            continue
                    
                    rd(4, 6)
                    page.screenshot(path=str(PROJECT_ROOT / 's05_verified.png'))
                    print(f'  URL: {page.url}')
                    
                    if 'challenge' in page.url.lower():
                        print('\n⚠ Challenge page - may need device verification')
                    elif 'login' not in page.url:
                        print('\n✅ ACCOUNT CREATED!')
                    else:
                        print(f'\n  Status: {page.url}')
                    
                    # Save final state
                    with open(state_path, 'w') as f:
                        json.dump({**state, 'step': 'completed', 'final_url': page.url}, f)
            
            else:
                # Check for reCAPTCHA or challenge
                print('\n⚠ No code inputs found')
                if 'challenge' in page.url.lower():
                    print('Challenge page detected')
                else:
                    print(f'Unexpected page: {page.url}')
                page.screenshot(path=str(PROJECT_ROOT / 's04_unexpected.png'))
                
                # Save state for debugging
                with open(PROJECT_ROOT / '.ig_state.json', 'w') as f:
                    json.dump({
                        'step': 'debug', 'url': page.url,
                        'body': body[:500]
                    }, f)
        
        except Exception as e:
            print(f'\n❌ Error: {e}')
            import traceback
            traceback.print_exc()
            page.screenshot(path=str(PROJECT_ROOT / 's_error.png'))
        
        finally:
            try:
                browser.close()
            except:
                pass

if __name__ == '__main__':
    main()
