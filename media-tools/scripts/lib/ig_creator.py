#!/usr/bin/env python3
"""
IG Creator Pro — Instagram account creation bot (ZORG-Ω)
Uses Playwright (Chromium) + Guerrilla Mail API
Full pipeline: email → signup → verify → bot ready
"""
import os, sys, json, re, time, random, requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LAST_EMAIL = PROJECT_ROOT / '.last_email.json'
CREDENTIALS = PROJECT_ROOT / '.ig_credentials.json'
GUERRILLA_API = 'https://api.guerrillamail.com/ajax.php'

def random_delay(min_s=0.5, max_s=2.0):
    time.sleep(random.uniform(min_s, max_s))

def api_call(params):
    r = requests.get(GUERRILLA_API, params=params, timeout=15)
    return r.json()

def generate_email():
    print('[IG] Generating temporary email...')
    data = api_call({'f': 'get_email_address', 'ip': '127.0.0.1', 'agent': 'ZORG-Ω'})
    with open(LAST_EMAIL, 'w') as f:
        json.dump(data, f)
    print(f'[IG] ✓ Email: {data["email_addr"]}')
    return data

def wait_for_ig_email(sid, timeout=180):
    print('[IG] Waiting for Instagram verification email...', end='', flush=True)
    start = time.time()
    while time.time() - start < timeout:
        inbox = api_call({'f': 'get_email_list', 'sid_token': sid, 'offset': '0', 'limit': '10'})
        for email in inbox.get('list', []):
            fr = (email.get('mail_from') or '').lower()
            subj = (email.get('mail_subject') or '').lower()
            if 'instagram' in fr or 'instagram' in subj or 'confirmation' in subj:
                print()
                print(f'[IG] ✓ Instagram email received: "{email["mail_subject"]}"')
                full = api_call({'f': 'fetch_email', 'sid_token': sid, 'email_id': email['mail_id']})
                return full
        print('.', end='', flush=True)
        time.sleep(5)
    print('\n[IG] ✗ Timeout waiting for Instagram email')
    return None

def extract_code(text):
    if not text:
        return None
    m = re.search(r'(\d{6})', text)
    return m.group(1) if m else None

def create_account(email, password, fullname, username, headless=True):
    """Create Instagram account using Playwright Chromium"""
    from playwright.sync_api import sync_playwright
    
    print(f'[IG] Launching Chromium (headless={headless})...')
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = browser.new_context(
            viewport={'width': 1366, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        try:
            # Step 1: Go to signup
            print('[IG] Step 1: Loading Instagram signup...')
            page.goto('https://www.instagram.com/accounts/emailsignup/?next=', wait_until='networkidle', timeout=30000)
            page.wait_for_selector('input', timeout=15000)
            random_delay(2, 3)
            
            page.screenshot(path=str(PROJECT_ROOT / 'ig_01_signup.png'))
            
            # Step 2: Fill form fields
            all_inputs = page.locator('input')
            input_count = all_inputs.count()
            print(f'[IG] Found {input_count} input fields')
            
            if input_count < 4:
                print(f'[IG] Expected at least 4 inputs, found {input_count}')
                page.screenshot(path=str(PROJECT_ROOT / 'ig_error_inputs.png'))
                browser.close()
                return None, None, False
            
            # Instagram signup order: [0]=email, [1]=password, [2]=fullname, [3]=username
            form_fields = [
                (0, 'email', email),
                (1, 'password', password),
                (2, 'full name', fullname),
            ]
            for idx, field_name, value in form_fields:
                print(f'[IG] Entering {field_name}...')
                inp = all_inputs.nth(idx)
                inp.click()
                random_delay()
                inp.fill(value)
                random_delay()
            
            # Step 3: Fill birthday (custom comboboxes)
            # Step 3: Fill birthday (custom comboboxes)
            print('[IG] Filling birthday...')
            
            # Helper to select from combobox using JS
            def _select_bday(combo_aria, value):
                combo = page.locator(f'div[role="combobox"][aria-label="{combo_aria}"]')
                if combo.count() == 0:
                    return False
                combo.click(force=True)
                time.sleep(1.5)
                result = page.evaluate(
                    f'() => {{'
                    f'  const opts = document.querySelectorAll("div[role=\\"option\\"]");'
                    f'  for (let o of opts) {{'
                    f'    if (o.textContent.trim() === "{value}" && o.offsetParent !== null) {{'
                    f'      o.click(); return true;'
                    f'    }}'
                    f'  }}'
                    f'  return false;'
                    f'}}'
                )
                if result:
                    print(f'[IG]   {combo_aria}: {value} selected')
                page.keyboard.press('Escape')
                time.sleep(0.8)
                return result
            
            # Select birthday fields
            _select_bday('Select Month', 'January')
            _select_bday('Select Day', '15')
            _select_bday('Select Year', '1995')
            
            # Step 4: Fill username (last field before submit)
            print(f'[IG] Entering username...')
            user_input = all_inputs.nth(3)
            user_input.click()
            random_delay()
            user_input.fill(username)
            random_delay()
            
            # Step 5: Scroll and click Submit
            print('[IG] Scrolling to Submit button...')
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            random_delay(1, 2)
            
            print('[IG] Clicking Submit...')
            submit_btn = page.locator('div[role="button"]:has-text("Submit")').first
            if submit_btn.count() > 0:
                submit_btn.scroll_into_view_if_needed()
                random_delay()
                submit_btn.click()
            else:
                page.keyboard.press('Enter')
            
            random_delay(5, 8)
            page.screenshot(path=str(PROJECT_ROOT / 'ig_02_after_submit.png'))
            print(f'[IG] URL: {page.url}')
            
            return browser, page, True
            
        except Exception as e:
            print(f'[IG] Error: {e}')
            import traceback
            traceback.print_exc()
            page.screenshot(path=str(PROJECT_ROOT / 'ig_error.png'))
            browser.close()
            return None, None, False

def verify_account(page, code):
    """Enter verification code"""
    if not page:
        return False
    try:
        print(f'[IG] Entering verification code: {code}')
        # Try numeric input fields
        code_inputs = page.locator('input[inputmode="numeric"]')
        count = code_inputs.count()
        if count > 0:
            for i, digit in enumerate(code):
                if i < count:
                    code_inputs.nth(i).fill(digit)
                    random_delay(0.1, 0.3)
            print('[IG] ✓ Code entered')
            random_delay(3, 5)
            page.screenshot(path=str(PROJECT_ROOT / 'ig_03_verified.png'))
            return True
        else:
            # Try single input
            single = page.locator('input[type="tel"]')
            if single.is_visible(timeout=3000):
                single.fill(code)
                print('[IG] ✓ Code entered (single field)')
                random_delay(3, 5)
                return True
            print(f'[IG] No code inputs found. URL: {page.url}')
            return False
    except Exception as e:
        print(f'[IG] ✗ Verification error: {e}')
        return False

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else 'help'
    
    if cmd == 'email':
        data = generate_email()
        print(f'Email: {data["email_addr"]}')
        print(f'SID:   {data["sid_token"]}')
        
    elif cmd in ('signup', 'full'):
        email_data = generate_email()
        email = email_data['email_addr']
        sid = email_data['sid_token']
        password = f'ZORG{random.randbytes(4).hex()}!{random.randint(100,999)}'
        fullname = args[1] if len(args) > 1 else 'Vaulex Watches'
        username = args[2] if len(args) > 2 else f'vaulex_{random.randint(10000, 99999)}'
        
        print(f'\n[IG] === Account Details ===')
        print(f'[IG] Email:    {email}')
        print(f'[IG] Password: {password}')
        print(f'[IG] Name:     {fullname}')
        print(f'[IG] Username: {username}')
        
        headless = cmd == 'full'
        browser, page, success = create_account(email, password, fullname, username, headless=headless)
        
        if success and headless:
            print('\n[IG] Waiting for verification email...')
            verif = wait_for_ig_email(sid)
            if verif:
                body = verif.get('mail_body', '') or ''
                code = extract_code(body)
                if code:
                    print(f'[IG] ✓ Code: {code}')
                    verify_account(page, code)
                    print('[IG] ✓ Account creation complete!')
                    creds = {'email': email, 'password': password, 'username': username, 'fullname': fullname}
                    with open(CREDENTIALS, 'w') as f:
                        json.dump(creds, f)
                    print(f'[IG] Credentials saved to {CREDENTIALS}')
                else:
                    print(f'[IG] No code found in email')
                    print(f'Body: {body[:300]}')
            random_delay(3, 5)
            browser.close()
        elif success and not headless:
            print('\n[IG] Browser open. Press Ctrl+C when done.')
            input('[IG] Press Enter to close browser...')
            browser.close()
        
    elif cmd == 'verify':
        sid = args[1] if len(args) > 1 else None
        if not sid:
            with open(LAST_EMAIL) as f:
                sid = json.load(f)['sid_token']
        verif = wait_for_ig_email(sid)
        if verif:
            body = verif.get('mail_body', '') or ''
            code = extract_code(body)
            if code:
                print(f'[IG] Verification code: {code}')
            else:
                print(f'[IG] No code found')
                print(f'Body: {body[:500]}')
    
    else:
        print('IG Creator Pro — Instagram Account Automation')
        print()
        print('Commands:')
        print('  email                         Generate temp email')
        print('  signup [name] [user]          Signup (opens browser)')
        print('  full [name] [user]            Full auto pipeline (headless)')
        print('  verify [sid]                  Wait for verification code')

if __name__ == '__main__':
    main()
