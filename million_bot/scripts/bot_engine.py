#!/usr/bin/env python3
"""
SHANNON-Ω Million Bot — Instagram Growth Engine
Uses InstaTakker core logic wrapped in Playwright for 
human-like automation at scale.
"""
import sys, os, json, time, random, logging, argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / 'million_bot' / 'config' / 'bot_config.json'
LOGS_DIR = PROJECT_ROOT / 'million_bot' / 'logs'

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler(LOGS_DIR / f'bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=2)

def random_delay(min_s=1.0, max_s=3.0):
    """Human-like random delay with InstaTakker anti-ban patterns"""
    if random.random() < 0.08:
        time.sleep(random.uniform(5.0, 12.0))
    else:
        time.sleep(random.uniform(min_s, max_s))

def human_scroll(page, distance=500):
    """Scroll like a human — small steps with random delays"""
    steps = max(1, min(distance // 200, 8))
    for _ in range(steps):
        page.evaluate(f'window.scrollBy(0, {random.randint(150, 350)})')
        time.sleep(random.uniform(0.2, 0.6))

def human_type(page, locator, text):
    """Type like a human — character by character with random delays"""
    locator.click()
    time.sleep(random.uniform(0.3, 0.8))
    for char in text:
        locator.type(char, delay=random.randint(30, 120))
    time.sleep(random.uniform(0.3, 0.8))

class IGrowthBot:
    """Instagram growth automation bot."""
    
    def __init__(self, config):
        self.config = config
        self.stats = {'followed': 0, 'unfollowed': 0, 'liked': 0, 'commented': 0}
        self.browser = None
        self.page = None
        self.context = None
    
    def login(self, username, password):
        """Login to Instagram - tries web first, then API fallback."""
        from playwright.sync_api import sync_playwright
        
        log.info(f'Logging in as @{username}...')
        
        # Try API login first (no browser needed)
        if self._login_api(username, password):
            return True
        
        # Fall back to web login
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            context = browser.new_context(
                viewport={'width': 1366, 'height': 900},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # Stealth patches
            page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
            """)
            
            if self._login_web(page, context, browser, username, password):
                self.browser = browser
                self.page = page
                self.context = context
                return True
            
            browser.close()
            return False
    
    def _login_api(self, username, password):
        """Login via Instagram private API (bypasses web/reCAPTCHA entirely)."""
        try:
            from instagrapi import Client
            cl = Client()
            cl.delay_range = [3, 6]
            
            session_path = PROJECT_ROOT / '.ig_api_session.json'
            if session_path.exists():
                try:
                    cl.load_settings(str(session_path))
                    cl.login(username, password)
                    log.info('✓ API login successful (loaded session)!')
                    return True
                except Exception as e:
                    log.warning(f'Session expired: {e}')
            
            cl.login(username, password)
            cl.dump_settings(str(session_path))
            log.info('✓ API login successful (fresh)!')
            
            # Store client for later use
            self._api_client = cl
            return True
            
        except ImportError:
            log.warning('instagrapi not available - install: pip install instagrapi')
            return False
        except Exception as e:
            err = str(e).lower()
            if 'challenge' in err or 'checkpoint' in err or 'bloks' in err:
                log.warning('Account needs manual verification via Instagram app/website')
                log.warning('➡ Open Instagram on phone, check notifications, verify login')
            elif 'password' in err:
                log.warning('Wrong password for @%s', username)
            else:
                log.warning(f'API login failed: {e}')
            return False
    
    def _login_web(self, page, context, browser, username, password):
        """Web login via Instagram's login form."""
        log.info('Attempting web login...')
        
        try:
            page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle', timeout=30000)
        except:
            pass
        
        # Wait for page to stabilize
        time.sleep(3)
        
        # Check if already logged in
        if 'login' not in page.url.lower():
            log.info('✓ Already logged in!')
            return True
        
        # Find input fields - Instagram uses 'email' and 'pass' as names
        try:
            page.wait_for_selector('input[name="email"]', timeout=10000)
        except:
            log.warning('Login form not found')
            page.screenshot(path=str(PROJECT_ROOT / 'ig_login_page.png'))
            return False
        
        random_delay(2, 4)
        page.locator('input[name="email"]').fill(username)
        random_delay(1, 2)
        page.locator('input[name="pass"]').fill(password)
        random_delay(1, 2)
        
        page.screenshot(path=str(PROJECT_ROOT / 'ig_login_filled.png'))
        
        # Click login using multiple strategies
        clicked = False
        strategies = [
            # 1: Click the "Log in" div directly
            lambda: page.locator('div:has-text("Log in")').first.click(),
            # 2: Use JS to click
            lambda: page.evaluate("document.querySelector('div:has-text(\"Log in\")')?.click()"),
            # 3: Submit the form via JS
            lambda: page.evaluate("document.getElementById('login_form')?.requestSubmit()"),
            # 4: Click submit button
            lambda: page.locator('button[type="submit"]').first.click(timeout=3000),
            # 5: Dispatch mouse events
            lambda: page.evaluate("""
                const d = [...document.querySelectorAll('div')].find(d => d.innerText === 'Log in');
                if(d) { d.dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
                d.dispatchEvent(new MouseEvent('mouseup', {bubbles:true}));
                d.dispatchEvent(new MouseEvent('click', {bubbles:true})); }
            """),
        ]
        
        for strategy in strategies:
            try:
                strategy()
                clicked = True
                break
            except Exception:
                continue
        
        if not clicked:
            log.error('Could not click login button')
            return False
        
        # Wait for login result
        random_delay(5, 8)
        
        current_url = page.url.lower()
        page.screenshot(path=str(PROJECT_ROOT / 'ig_login_result.png'))
        
        if '/challenge/' in current_url:
            log.warning('⚠ Challenge page - Instagram needs human verification')
            log.warning('Open instagram.com on your phone to approve this login')
            page.screenshot(path=str(PROJECT_ROOT / 'ig_challenge.png'))
            return False
        elif 'login' not in current_url or 'onetap' in current_url:
            log.info('✓ Web login successful!')
            
            # Handle dialogs
            for text in ['Save Info', 'Not Now', 'Turn On']:
                try:
                    btn = page.locator(f'button:has-text("{text}")').first
                    if btn.is_visible(timeout=3000):
                        btn.click()
                        random_delay(1, 2)
                except:
                    pass
            
            return True
        
        log.warning(f'Login incomplete - URL: {page.url}')
        return False
    
    def navigate_to_profile(self, username):
        """Navigate to a user's profile."""
        log.info(f'Navigating to @{username}...')
        self.page.goto(f'https://www.instagram.com/{username}/', wait_until='networkidle', timeout=30000)
        random_delay(2, 4)
        return True
    
    def follow_user(self):
        """Follow the current profile."""
        try:
            follow_btn = self.page.locator('button:has-text("Follow")').first
            if follow_btn.is_visible(timeout=5000):
                follow_btn.click()
                random_delay(2, 4)
                self.stats['followed'] += 1
                log.info('✓ Followed!')
                return True
            else:
                log.info('Already following or button not found')
                return False
        except Exception as e:
            log.warning(f'Follow error: {e}')
            return False
    
    def like_recent_posts(self, count=5):
        """Like recent posts on the current page/profile."""
        liked = 0
        try:
            like_buttons = self.page.locator('span[aria-label="Like"], svg[aria-label="Like"]').all()
            log.info(f'Found {len(like_buttons)} like buttons')
            
            for btn in like_buttons[:count]:
                try:
                    if btn.is_visible(timeout=3000):
                        btn.click()
                        self.stats['liked'] += 1
                        liked += 1
                        random_delay(3, 6)
                        log.info(f'  Liked #{liked}')
                except:
                    continue
        except Exception as e:
            log.warning(f'Like error: {e}')
        
        return liked
    
    def follow_followers_of(self, target_username, max_follows=30):
        """Follow followers of a target account."""
        log.info(f'Following followers of @{target_username}...')
        
        try:
            self.navigate_to_profile(target_username)
            random_delay(2, 4)
            
            followers_link = self.page.locator('a[href$="/followers/"]').first
            if followers_link.is_visible(timeout=5000):
                followers_link.click()
                random_delay(3, 5)
                
                # Scroll follower list
                followed_count = 0
                for i in range(50):
                    if followed_count >= max_follows:
                        break
                    
                    # Get visible follow buttons
                    follow_btns = self.page.locator('button:has-text("Follow")').all()
                    
                    for btn in follow_btns:
                        if followed_count >= max_follows:
                            break
                        try:
                            if btn.is_visible(timeout=2000):
                                btn.click()
                                self.stats['followed'] += 1
                                followed_count += 1
                                log.info(f'  ✓ Followed #{self.stats["followed"]}')
                                random_delay(8, 14)
                        except:
                            continue
                    
                    # Scroll more
                    self.page.evaluate('document.querySelector("div[role=dialog] div")?.scrollBy(0, 300)')
                    random_delay(1, 2)
                
                # Close dialog
                try:
                    self.page.locator('[aria-label="Close"]').first.click()
                except:
                    self.page.keyboard.press('Escape')
        
        except Exception as e:
            log.warning(f'Follower fetch error: {e}')
    
    def run_growth_cycle(self, cycles=3):
        """Run the main growth cycle loop."""
        cfg = self.config
        
        log.info(f'Starting {cycles} growth cycles')
        
        for cycle in range(1, cycles + 1):
            log.info(f'\n{"="*50}')
            log.info(f'Cycle {cycle}/{cycles}')
            log.info(f'{"="*50}')
            
            # Skip if hourly limits reached
            ab = cfg.get('anti_ban', {})
            
            # Follow from competitor accounts
            for competitor in cfg.get('competitor_accounts', []):
                if self.stats['followed'] >= ab.get('daily_follow_limit', 100):
                    log.info('Daily follow limit reached')
                    break
                if self.stats['followed'] >= ab.get('hourly_follow_limit', 30):
                    log.info('Hourly follow limit, pausing...')
                    time.sleep(random.uniform(300, 600))
                
                max_follow = min(
                    ab.get('hourly_follow_limit', 30) // len(cfg.get('competitor_accounts', [1])),
                    ab.get('daily_follow_limit', 100) // (cycles * len(cfg.get('competitor_accounts', [1])))
                )
                self.follow_followers_of(competitor, max_follow=5)
                random_delay(5, 10)
            
            # Like hashtag posts
            for ht in cfg.get('hashtags', [])[:3]:
                try:
                    self.page.goto(f'https://www.instagram.com/explore/tags/{ht}/', wait_until='networkidle', timeout=30000)
                    random_delay(3, 5)
                    liked = self.like_recent_posts(3)
                    if liked > 0:
                        log.info(f'  Liked {liked} posts from #{ht}')
                except Exception as e:
                    log.warning(f'Hashtag error: {e}')
                random_delay(3, 6)
        
        log.info(f'\n{"="*50}')
        log.info('Growth cycles complete!')
        log.info(f'Stats: {json.dumps(self.stats)}')
    
    def close(self):
        """Clean up browser resources."""
        try:
            self.browser.close()
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description='SHANNON-Ω Instagram Growth Bot')
    parser.add_argument('--login', nargs=2, metavar=('USERNAME', 'PASSWORD'), help='Instagram login')
    parser.add_argument('--cycles', type=int, default=3, help='Number of growth cycles')
    parser.add_argument('--target', help='Follow specific user\'s followers')
    parser.add_argument('--like', type=int, default=10, help='Like recent posts')
    
    args = parser.parse_args()
    
    cfg = load_config()
    
    # Use command line credentials or config
    username = args.login[0] if args.login else cfg['instagram']['username']
    password = args.login[1] if args.login else cfg['instagram']['password']
    
    if not username or not password:
        print("❌ No Instagram credentials provided!")
        print("   Use: python3 bot_engine.py --login user pass --cycles 5")
        print("   Or set credentials in config/bot_config.json")
        sys.exit(1)
    
    bot = IGrowthBot(cfg)
    
    if bot.login(username, password):
        if args.target:
            bot.navigate_to_profile(args.target)
        if args.like and bot.page:
            bot.like_recent_posts(args.like)
        bot.run_growth_cycle(cycles=args.cycles)
    else:
        print("\n❌ Login failed. Reasons:")
        print("   1. Account needs verification — open Instagram on your phone")
        print("   2. Wrong credentials")
        print("   3. Instagram is blocking automated logins")
        print("\n💡 Once verified, the session will be saved and next time will work.")
    
    bot.close()
    
    print(f"\n{'='*50}")
    print(f"✅ Session complete!")
    print(f"   Followed: {bot.stats['followed']}")
    print(f"   Liked: {bot.stats['liked']}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
