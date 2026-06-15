#!/usr/bin/env python3
"""
omega_sloth.py — Phase 1: Instagram automation via Playwright Chromium
Extreme delays, headless operation, captcha-avoidance pacing.
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
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
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
        log.info(f"Logging in as @{self.cfg['username']}")
        self.page.goto('https://www.instagram.com/accounts/login/')
        self.page.wait_for_timeout(3000)
        
        # Accept cookies if present
        try:
            if self.page.locator('button:has-text("Allow all")').is_visible(timeout=3000):
                self.page.locator('button:has-text("Allow all")').click()
                self.page.wait_for_timeout(1000)
        except:
            pass
        
        # Enter username
        username_input = self.page.locator('input[name="username"]')
        username_input.fill(self.cfg['username'])
        self.page.wait_for_timeout(random.uniform(500, 1500))
        
        # Enter password
        password_input = self.page.locator('input[name="password"]')
        password_input.fill(self.cfg['password'])
        self.page.wait_for_timeout(random.uniform(500, 1500))
        
        # Click login
        self.page.locator('button[type="submit"]').click()
        self.page.wait_for_timeout(5000)
        
        # Check for "Save info" dialog
        try:
            if self.page.locator('button:has-text("Not Now")').is_visible(timeout=5000):
                self.page.locator('button:has-text("Not Now")').click()
                self.page.wait_for_timeout(2000)
        except:
            pass
            
        # Check for notifications dialog
        try:
            if self.page.locator('button:has-text("Not Now")').is_visible(timeout=5000):
                self.page.locator('button:has-text("Not Now")').click()
                self.page.wait_for_timeout(2000)
        except:
            pass
        
        # Verify login
        if self.page.locator('svg[aria-label="Home"]').is_visible(timeout=10000):
            log.info("✓ Login successful")
            return True
        else:
            log.warning("⚠ Login may have failed (check manually)")
            return False
    
    def like_recent_posts(self, username, count=5):
        log.info(f"Liking recent posts from @{username}")
        self.page.goto(f'https://www.instagram.com/{username}/')
        self.page.wait_for_timeout(3000)
        
        liked = 0
        for i in range(min(count, 6)):  # first row max
            try:
                posts = self.page.locator('article a[href*="/p/"]')
                post_count = posts.count()
                if i >= post_count:
                    break
                
                posts.nth(i).click()
                self.page.wait_for_timeout(random.uniform(2000, 4000))
                
                # Click like button
                like_btn = self.page.locator('svg[aria-label="Like"]').first
                if like_btn.is_visible(timeout=3000):
                    like_btn.click()
                    liked += 1
                    log.info(f"  ❤ Liked post #{i+1}")
                    self.page.wait_for_timeout(random.uniform(1500, 3000))
                
                # Close
                self.page.locator('svg[aria-label="Close"]').click()
                self.page.wait_for_timeout(random.uniform(1500, 3000))
            except Exception as e:
                log.debug(f"Like error: {e}")
                continue
        
        log.info(f"Liked {liked}/{count} posts")
        return liked
    
    def follow_followers(self, username, count=5):
        log.info(f"Following followers of @{username}")
        self.page.goto(f'https://www.instagram.com/{username}/')
        self.page.wait_for_timeout(3000)
        
        # Click followers link
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
            except Exception as e:
                log.debug(f"Follow error: {e}")
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
            
            # Phase A: Like target's posts
            self.like_recent_posts(self.cfg['target'], self.cfg['like_per_session'])
            
            delay = random.uniform(self.cfg['action_delay_min'], self.cfg['action_delay_max'])
            log.info(f"Inter-phase delay: {delay:.0f}s")
            self.page.wait_for_timeout(delay * 1000)
            
            # Phase B: Follow target's followers
            self.follow_followers(self.cfg['target'], self.cfg['follow_per_session'])
            
            log.info("═══ SESSION COMPLETE ═══")
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
    
    # Save timestamp
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
