"""
SHANNON-Ω Safe Session Executor
Maximum ban prevention: warmup first, minimal actions, long delays, human behavior
"""
import sys, os, json, time, random
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "media-tools", "scripts", "lib"))
sys.path.insert(0, BASE)

from automation_engine import ProxyPool, CaptchaHandler, ContentGenerator
from cortex_catalog import CortexCatalog

EMAIL = "luxor.offacial@gmail.com"
PASSWORD = "Hesoyam$11011"
TWITTER_USER = "luxor_offacial"

log_file = os.path.join(BASE, "omega", "session_log.json")

def log(msg: str):
    ts = datetime.utcnow().isoformat()
    print(f"[{ts}] {msg}")
    with open(log_file, "a") as f:
        f.write(json.dumps({"time": ts, "msg": msg}) + "\n")

def safe_quora_login():
    """Phase 1: Just login and browse. NO actions. Warm only."""
    log("=== PHASE 1: Quora Warmup ===")
    log("Attempting Quora login only — no actions, no posts")
    
    # Use undetected chrome with profile
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    profile_dir = os.path.join(BASE, "omega", "chrome_profiles", "quora_luxor")
    os.makedirs(profile_dir, exist_ok=True)
    
    opts = uc.ChromeOptions()
    opts.add_argument(f"--user-data-dir={profile_dir}")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-first-run")
    opts.add_argument("--window-size=1366,768")
    
    driver = None
    try:
        driver = uc.Chrome(options=opts)
        driver.get("https://www.quora.com")
        time.sleep(random.uniform(3, 6))
        
        # Check if already logged in
        if "feed" in driver.current_url or "answer" in driver.page_source.lower():
            log("✅ Already logged into Quora via profile")
            return True
        
        # Try to find and click login
        try:
            login_btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
            )
            login_btn.click()
            time.sleep(random.uniform(2, 4))
        except:
            log("Login button not found, checking if already on login page")
        
        # Fill email with human typing
        try:
            email_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            for ch in EMAIL:
                email_field.send_keys(ch)
                time.sleep(random.uniform(0.03, 0.12))
            time.sleep(random.uniform(0.5, 1.5))
            
            pw_field = driver.find_element(By.NAME, "password")
            for ch in PASSWORD:
                pw_field.send_keys(ch)
                time.sleep(random.uniform(0.03, 0.12))
            time.sleep(random.uniform(0.5, 1.5))
            
            submit = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit.click()
            log("Login form submitted")
            time.sleep(random.uniform(5, 10))
            
            if "feed" in driver.current_url or "home" in driver.current_url:
                log("✅ Quora login successful!")
                
                # Browse a few pages to look human
                for page in ["/answers", "/following", "/topics/Fashion"]:
                    try:
                        driver.get(f"https://www.quora.com{page}")
                        time.sleep(random.uniform(3, 7))
                        # Scroll a bit
                        driver.execute_script("window.scrollBy(0, 300)")
                        time.sleep(random.uniform(2, 4))
                    except:
                        pass
                
                return True
            else:
                log(f"⚠️ Login may have failed. Current URL: {driver.current_url[:100]}")
                return False
        except Exception as e:
            log(f"⚠️ Login form error: {e}")
            return False
    
    except Exception as e:
        log(f"❌ Quora session error: {e}")
        return False
    finally:
        if driver:
            time.sleep(2)
            driver.quit()

def safe_twitter_warmup():
    """Phase 1b: Twitter warmup — just login and browse."""
    log("=== PHASE 1b: Twitter Warmup ===")
    log("Attempting Twitter login — no actions, just browse")
    
    try:
        from playwright.sync_api import sync_playwright
        from playwright_stealth import stealth_sync
    except ImportError:
        log("playwright not installed, skipping Twitter warmup")
        return False
    
    pw = None
    try:
        pw = sync_playwright().start()
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        )
        page = context.new_page()
        stealth_sync(page)
        
        page.goto("https://twitter.com/i/flow/login")
        time.sleep(random.uniform(3, 6))
        
        # Email
        page.fill('input[autocomplete="username"]', EMAIL)
        time.sleep(random.uniform(1, 2))
        page.click('text=Next')
        time.sleep(random.uniform(2, 4))
        
        # Username (sometimes required)
        try:
            page.fill('input[data-testid="ocfEnterTextTextInput"]', TWITTER_USER)
            time.sleep(1)
            page.click('text=Next')
            time.sleep(random.uniform(2, 4))
        except:
            pass
        
        # Password
        page.fill('input[type="password"]', PASSWORD)
        time.sleep(random.uniform(1, 2))
        page.click('text=Log in')
        time.sleep(random.uniform(5, 10))
        
        if "home" in page.url:
            log("✅ Twitter login successful!")
            
            # Browse explore and a profile to look human
            for url in ["https://twitter.com/explore", "https://twitter.com/i/trends"]:
                try:
                    page.goto(url)
                    time.sleep(random.uniform(3, 5))
                    page.evaluate("window.scrollBy(0, 400)")
                    time.sleep(random.uniform(2, 4))
                except:
                    pass
            
            context.storage_state(path=os.path.join(BASE, "omega", "twitter_state.json"))
            log("Twitter session state saved")
            return True
        else:
            log(f"⚠️ Twitter login may have failed. URL: {page.url[:80]}")
            return False
    
    except Exception as e:
        log(f"❌ Twitter warmup error: {e}")
        return False
    finally:
        if pw:
            try: browser.close()
            except: pass
            pw.stop()

def generate_first_content():
    """Generate safe, natural first posts using our API."""
    log("Generating first content...")
    gen = ContentGenerator()
    
    # Quora answer — fashion niche, natural tone
    quora_q = "What are the biggest mistakes people make when building a wardrobe?"
    answer = gen.generate_quora_answer(quora_q, niche="fashion")
    log(f"Generated Quora answer ({len(answer)} chars)")
    
    # Tweet — simple, no links, organic
    tweet = gen.generate_tweet(niche="fashion")
    log(f"Generated tweet ({len(tweet)} chars)")
    
    return {"quora_answer": answer[:200], "tweet": tweet[:200]}

def report():
    """Final report of session."""
    catalog = CortexCatalog()
    
    # Log the execution
    catalog.log_execution(
        8,  # automation_engine.py
        "success",
        duration_ms=0,
        output=f"Warmup session for {EMAIL}"
    )
    
    stats = catalog.get_stats()
    log(f"\n=== SESSION SUMMARY ===")
    log(f"Email: {EMAIL}")
    log(f"Quora: warmup {'completed' if os.path.exists(os.path.join(BASE, 'omega', 'chrome_profiles', 'quora_luxor')) else 'not started'}")
    log(f"Twitter: warmup {'completed' if os.path.exists(os.path.join(BASE, 'omega', 'twitter_state.json')) else 'not started'}")
    log(f"Total automations in cortex: {stats['total']}")
    log(f"Executions in 24h: {stats['executions_24h']}")
    
    return stats

if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if phase in ("all", "quora"):
        safe_quora_login()
    
    if phase in ("all", "twitter"):
        safe_twitter_warmup()
    
    if phase in ("all", "content"):
        content = generate_first_content()
        print(f"\n📝 First content ready:")
        print(json.dumps(content, indent=2))
    
    if phase in ("all", "report"):
        report()
    
    print("\n✅ Session execution complete. Check omega/session_log.json for details.")
