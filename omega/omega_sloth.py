#!/usr/bin/env python3
"""
omega_sloth.py — SHANNON-Ω Phase 1: Instagram automation via Playwright Chromium
Multi-strategy login with cookie injection, mobile endpoint, keyboard submit,
challenge handling, and slow safe action pacing.
"""
import os, sys, json, time, random, logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

CONFIG = {
    "username": os.environ.get("IG_USERNAME", "chip.munk.19"),
    "password": os.environ.get("IG_PASSWORD", "Hesoyam$18043"),
    "target": "vaulex_watches",
    "follow_per_session": 5,
    "like_per_session": 15,
    "action_delay_min": 90,
    "action_delay_max": 180,
    "session_delay_hours": 6,
}

class OmegaSloth:
    def __init__(self, cfg=None):
        self.cfg = cfg or CONFIG
        self.browser = None
        self.page = None
    
    def start_browser(self):
        from playwright.sync_api import sync_playwright
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--single-process',
            ]
        )
        context = self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        )
        self.page = context.new_page()
        log.info("Browser started")
    
    def close(self):
        if self.browser:
            self.browser.close()
        if hasattr(self, 'pw') and self.pw:
            self.pw.stop()
        log.info("Browser closed")
    
    def login(self):
        """Multi-strategy login: cookie injection, web, mobile"""
        log.info(f"Logging in as @{self.cfg['username']}")
        
        if self._try_cookie_login():
            return True
        if self._try_web_login():
            return True
        if self._try_mobile_login():
            return True
        
        log.error("All login strategies failed")
        return False
    
    def _try_cookie_login(self):
        """Inject saved cookies + attempt login"""
        log.debug("Strategy A: Cookie-based login")
        self.page.goto('https://www.instagram.com/', wait_until='domcontentloaded')
        self.page.wait_for_timeout(3000)
        
        cookie_files = [
            Path(__file__).parent.parent / '.ig_web_cookies.json',
            Path(__file__).parent.parent / '.ig_code_state.json',
        ]
        saved_cookies = []
        for cf in cookie_files:
            if cf.exists():
                try:
                    data = json.loads(cf.read_text())
                    if isinstance(data, list):
                        saved_cookies = data
                        break
                    elif isinstance(data, dict) and 'cookies' in data:
                        saved_cookies = data['cookies']
                        break
                except:
                    pass
        
        if saved_cookies:
            for c in saved_cookies:
                try:
                    self.page.context.add_cookies([{
                        'name': c['name'],
                        'value': c['value'],
                        'domain': c.get('domain', '.instagram.com'),
                        'path': c.get('path', '/'),
                    }])
                except:
                    pass
            log.debug(f"Injected {len(saved_cookies)} cookies")
            self.page.wait_for_timeout(2000)
        
        self.page.goto('https://www.instagram.com/accounts/login/')
        self.page.wait_for_timeout(3000)
        return self._fill_and_submit()
    
    def _try_web_login(self):
        """Standard web login flow"""
        log.debug("Strategy B: Web login")
        self.page.goto('https://www.instagram.com/accounts/login/')
        self.page.wait_for_timeout(5000)
        return self._fill_and_submit()
    
    def _try_mobile_login(self):
        """Mobile login endpoint — less CAPTCHA triggering"""
        log.debug("Strategy C: Mobile login")
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.page.wait_for_timeout(1000)
        self.page.goto('https://www.instagram.com/accounts/login/')
        self.page.wait_for_timeout(5000)
        result = self._fill_and_submit()
        self.page.set_viewport_size({'width': 1280, 'height': 800})
        return result
    
    def _fill_and_submit(self):
        """Fill credentials and submit, then verify"""
        for btn_text in ["Allow all", "Allow essential", "Accept", "Accept All"]:
            try:
                btn = self.page.get_by_role("button", name=btn_text)
                if btn.is_visible(timeout=2000):
                    btn.click()
                    self.page.wait_for_timeout(1000)
                    break
            except:
                pass
        self.page.wait_for_timeout(2000)
        
        # Fill username/email
        username_filled = False
        for selector in ['input[name="email"]', 'input[name="username"]', 'input[type="text"]']:
            try:
                inp = self.page.locator(selector).first
                if inp.is_visible(timeout=5000):
                    inp.fill(self.cfg['username'])
                    username_filled = True
                    log.debug(f"Username filled via: {selector}")
                    break
            except:
                continue
        if not username_filled:
            log.error("Could not find username field")
            return False
        self.page.wait_for_timeout(random.uniform(500, 1500))
        
        # Fill password
        password_filled = False
        for selector in ['input[name="pass"]', 'input[type="password"]', 'input[name="password"]']:
            try:
                inp = self.page.locator(selector).first
                if inp.is_visible(timeout=5000):
                    inp.fill(self.cfg['password'])
                    password_filled = True
                    log.debug(f"Password filled via: {selector}")
                    break
            except:
                continue
        if not password_filled:
            log.error("Could not find password field")
            return False
        self.page.wait_for_timeout(random.uniform(500, 1500))
        
        # Submit via keyboard Enter then JS fallback
        try:
            self.page.keyboard.press("Enter")
            log.debug("Submitted via keyboard Enter")
        except:
            try:
                self.page.evaluate("""() => {
                    const b = document.querySelector('button[type="submit"], input[type="submit"]');
                    if (b) { b.click(); return true; }
                    const f = document.querySelector('form');
                    if (f) { f.submit(); return true; }
                    return false;
                }""")
                log.debug("Submitted via JS evaluate")
            except:
                return False
        
        self.page.wait_for_timeout(8000)
        
        # Handle post-login dialogs
        for dt in ["Not Now", "Not now", "Save Info", "Save info", "Save Your Login Info", "Turn On"]:
            try:
                db = self.page.get_by_role("button", name=dt)
                if db.is_visible(timeout=3000):
                    db.click()
                    log.debug(f"Dismissed: {dt}")
                    self.page.wait_for_timeout(1000)
            except:
                pass
        
        # Check result
        current_url = self.page.url
        log.debug(f"Post-login URL: {current_url[:100]}")
        
        if '/challenge/' in current_url or '/recaptcha/' in current_url or '/codeentry/' in current_url:
            log.warning(f"Challenge page: {current_url[:80]}")
            return self.handle_challenge()
        
        if self._is_logged_in():
            return True
        
        log.warning(f"Login uncertain. URL: {current_url[:80]}")
        return False
    
    def handle_challenge(self):
        """Handle Instagram challenge page — save state for manual code entry"""
        url = self.page.url
        log.info(f"Challenge page detected: {url[:80]}")
        
        # Save screenshot
        try:
            self.page.screenshot(path='omega/challenge_page.png')
            log.info("Screenshot saved to omega/challenge_page.png")
        except:
            pass
        
        # Save challenge state
        import json
        from pathlib import Path
        state_data = {
            "step": "challenge",
            "url": url,
            "username": self.cfg["username"],
            "cookies": self.page.context.cookies(),
            "message": "Instagram requires verification code. Check email/SMS linked to account.",
        }
        Path('omega/challenge_state.json').write_text(json.dumps(state_data, indent=2))
        log.info("Challenge state saved to omega/challenge_state.json")
        
        # Try to resolve challenge via in-challenge email code
        # First check if there's a way to request email code
        try:
            # Instagram challenge pages have different layouts:
            # Option 1: "Get help logging in" or "Send code via email"
            options = self.page.locator('button, a[role="button"]').all()
            for opt in options:
                text = opt.text_content().lower() if opt.text_content() else ""
                if "email" in text or "text" in text or "sms" in text:
                    log.info(f"Clicking option: {opt.text_content()[:50]}")
                    opt.click(timeout=3000)
                    self.page.wait_for_timeout(3000)
                    break
        except:
            pass
        
        # Look for code input
        try:
            selector = 'input[inputmode="numeric"], input[name="code"], input[type="text"]'
            inp = self.page.locator(selector).first
            if inp.is_visible(timeout=3000):
                log.info("Code input field found!")
                
                # Save updated state
                state_data["step"] = "awaiting_code"
                Path('omega/challenge_state.json').write_text(json.dumps(state_data, indent=2))
                log.info("--- CHALLENGE CODE REQUIRED ---")
                log.info(f"Check email/phone for @{self.cfg['username']}")
                log.info("Provide code by writing to .ig_state.json:")
                log.info("  echo '{\"step\":\"code_received\",\"code\":\"123456\"}' > .ig_state.json")
                
                # Poll for code
                state_file = Path(__file__).parent.parent / '.ig_state.json'
                for i in range(60):
                    self.page.wait_for_timeout(10000)
                    if state_file.exists():
                        try:
                            data = json.loads(state_file.read_text())
                            if data.get('step') == 'code_received' and data.get('code'):
                                code = str(data['code'])
                                inp.fill(code)
                                self.page.wait_for_timeout(500)
                                self.page.keyboard.press('Enter')
                                self.page.wait_for_timeout(8000)
                                log.info(f"Code {code} submitted")
                                
                                if self._is_logged_in():
                                    log.info("Challenge resolved! Logged in.")
                                    return True
                                
                                # Try submitting via JS
                                self.page.evaluate("""() => {
                                    const btn = document.querySelector('button[type="submit"]');
                                    if (btn) btn.click();
                                }""")
                                self.page.wait_for_timeout(5000)
                                
                                if self._is_logged_in():
                                    log.info("Challenge resolved! Logged in.")
                                    return True
                                
                                log.info("Code submitted but still on challenge page")
                                break
                        except:
                            pass
                
                log.warning("Code not provided within timeout")
                return False
        except:
            pass
        
        log.warning("Could not find code input on challenge page (anti-bot)")
        log.info("Try alternative: use Tampermonkey script in real browser")
        log.info("  omega_tampermonkey.sh for setup instructions")
        return False
    
    def _is_logged_in(self):
        """Check login status by URL and page elements"""
        url = self.page.url
        if '/challenge/' in url or '/recaptcha/' in url or '/codeentry/' in url:
            return False
        for indicator in ['svg[aria-label="Home"]', 'svg[aria-label="Search"]',
                          'a[href="/direct/inbox/"]', 'span:has-text("Home")']:
            try:
                if self.page.locator(indicator).is_visible(timeout=3000):
                    return True
            except:
                continue
        if '/accounts/login' not in url:
            try:
                self.page.locator('header').is_visible(timeout=2000)
                return True
            except:
                pass
        return False
    
    def like_recent_posts(self, username, count=5):
        log.info(f"Liking recent posts from @{username}")
        self.page.goto(f'https://www.instagram.com/{username}/')
        self.page.wait_for_timeout(3000)
        liked = 0
        for i in range(min(count, 6)):
            try:
                posts = self.page.locator('article a[href*="/p/"]')
                post_count = posts.count()
                if i >= post_count:
                    break
                posts.nth(i).click()
                self.page.wait_for_timeout(random.uniform(2000, 4000))
                like_btn = self.page.locator('svg[aria-label="Like"]').first
                if like_btn.is_visible(timeout=3000):
                    like_btn.click()
                    liked += 1
                    log.info(f"  ❤ Liked post #{i+1}")
                    self.page.wait_for_timeout(random.uniform(1500, 3000))
                self.page.locator('svg[aria-label="Close"]').click()
                self.page.wait_for_timeout(random.uniform(1500, 3000))
            except:
                continue
        log.info(f"Liked {liked}/{count} posts")
        return liked
    
    def follow_followers(self, username, count=5):
        log.info(f"Following followers of @{username}")
        self.page.goto(f'https://www.instagram.com/{username}/')
        self.page.wait_for_timeout(3000)
        try:
            self.page.locator(f'a[href="/{username}/followers/"]').click()
            self.page.wait_for_timeout(3000)
        except:
            log.warning("Could not find followers link")
            return 0
        followed = 0
        for i in range(count):
            try:
                follow_btns = self.page.locator('button:has-text("Follow")')
                if follow_btns.count() <= i:
                    break
                follow_btns.nth(i).click()
                followed += 1
                log.info(f"  ➕ Followed user #{i+1}")
                delay = random.uniform(self.cfg['action_delay_min'], self.cfg['action_delay_max'])
                log.info(f"  Waiting {delay:.0f}s...")
                self.page.wait_for_timeout(delay * 1000)
            except:
                continue
        log.info(f"Followed {followed}/{count} users")
        return followed
    
    def run_session(self):
        log.info("═══ OMEGA SLOTH SESSION ═══")
        log.info(f"Target: @{self.cfg['target']}")
        try:
            self.start_browser()
            if not self.login():
                log.error("Login failed, aborting")
                return False
            self.like_recent_posts(self.cfg['target'], self.cfg['like_per_session'])
            delay = random.uniform(self.cfg['action_delay_min'], self.cfg['action_delay_max'])
            log.info(f"Inter-phase delay: {delay:.0f}s")
            self.page.wait_for_timeout(delay * 1000)
            self.follow_followers(self.cfg['target'], self.cfg['follow_per_session'])
            log.info("═══ SESSION COMPLETE ═══")
            
            # Save session cookies for future use
            try:
                cookies = self.page.context.cookies()
                Path('omega/session_cookies.json').write_text(json.dumps(cookies, indent=2))
                log.info("Session cookies saved")
            except:
                pass
            
            return True
        except Exception as e:
            log.error(f"Session error: {e}")
            return False
        finally:
            self.close()

def main():
    cfg_file = Path(__file__).parent / "omega_config.json"
    if cfg_file.exists():
        with open(cfg_file) as f:
            CONFIG.update(json.load(f))
    
    sloth = OmegaSloth(CONFIG)
    success = sloth.run_session()
    
    status = {
        "last_run": datetime.utcnow().isoformat(),
        "success": success,
        "target": CONFIG["target"],
        "username": CONFIG["username"],
    }
    status_file = Path(__file__).parent / "omega_status.json"
    with open(status_file, "w") as f:
        json.dump(status, f, indent=2)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
