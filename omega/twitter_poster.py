#!/usr/bin/env python3
"""
LEXOR Twitter Poster — robust posting with cookie auth + API content generation
Uses SHANNON-Ω / ZORG-Ω for content.
"""
import json, time, sys, os
from playwright.sync_api import sync_playwright

# Ensure working dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def generate_tweet(persona="zorg"):
    """Generate a tweet about fashion using the API."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from api_interact import chat
    
    prompt = "Generate one short tweet about minimalist fashion for @Luxor_Offical. Make it stylish, under 220 chars. No hashtags except #LUXOR at end. Just the tweet text, nothing else."
    result = chat(prompt, mode="shannon", persona=persona, max_tokens=300, temperature=0.85)
    
    if "error" in result:
        print(f"API Error: {result['error']}")
        return None
    
    content = result["choices"][0]["message"]["content"].strip()
    # Clean up - remove reasoning if present
    if "<｜end▁of▁thinking｜>" in content:
        parts = content.split("<｜end▁of▁thinking｜>")
        content = parts[-1].strip() if len(parts) > 1 else content
    # Remove quotes
    content = content.strip('"').strip("'")
    # Ensure hashtag
    if "#LUXOR" not in content.upper():
        content = content.rstrip('.') + " #LUXOR"
    return content[:280]

def post_tweet(tweet_text, use_queue=False):
    """Post a tweet using Playwright with saved cookies."""
    print(f"\n=== LEXOR Twitter Poster ===")
    print(f"Tweet: {tweet_text[:120]}...")
    
    # If queue mode, read from queue
    if use_queue:
        try:
            with open('omega/tweet_queue.txt') as f:
                content = f.read().strip()
            tweets = [t.strip() for t in content.split('\n\n') if t.strip() and not t.startswith('===') and not t.startswith('LEXOR')]
            for t in tweets:
                lines = t.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        tweet_text = line.strip()
                        break
                break
        except Exception as e:
            print(f"Queue error: {e}")
    
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    
    # Use stored state
    context = browser.new_context(
        storage_state='omega/twitter_authenticated_state.json',
        viewport={'width': 1366, 'height': 768}
    )
    page = context.new_page()
    
    try:
        page.goto('https://x.com/home', wait_until='domcontentloaded', timeout=30000)
        time.sleep(5)
        
        # Check login
        compose = page.query_selector('[data-testid="SideNav_NewTweet_Button"]')
        if not compose:
            print("❌ NOT LOGGED IN")
            page.screenshot(path='omega/twitter_poster_not_logged.png')
            browser.close()
            pw.stop()
            return False
        
        print("✅ Logged in. Clicking compose via JS...")
        page.evaluate('document.querySelector("[data-testid=SideNav_NewTweet_Button]").click()')
        time.sleep(3)
        
        # Type tweet
        page.keyboard.type(tweet_text, delay=10)
        time.sleep(1)
        
        # Click Post via JS (bypasses overlay)
        posted = page.evaluate("""() => {
            const btn = document.querySelector('[data-testid="tweetButton"]') || 
                       document.querySelector('[data-testid="tweetButtonInline"]');
            if (btn) { btn.click(); return true; }
            return false;
        }""")
        
        if posted:
            print("✅ Post button clicked!")
            time.sleep(4)
            page.screenshot(path='omega/twitter_poster_result.png')
            
            # Remove from queue if queue mode
            if use_queue:
                try:
                    with open('omega/tweet_queue.txt') as f:
                        data = f.read()
                    lines = data.split('\n\n', 1)
                    if len(lines) > 1:
                        with open('omega/tweet_queue.txt', 'w') as f:
                            f.write(lines[1])
                        print("Removed posted tweet from queue")
                except:
                    pass
            
            browser.close()
            pw.stop()
            return True
        else:
            print("❌ Could not find post button")
            page.screenshot(path='omega/twitter_poster_no_btn.png')
            browser.close()
            pw.stop()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        try: page.screenshot(path='omega/twitter_poster_error.png')
        except: pass
        browser.close()
        pw.stop()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--queue":
        post_tweet("", use_queue=True)
    elif len(sys.argv) > 1:
        post_tweet(" ".join(sys.argv[1:]))
    else:
        # Generate and post
        tweet = generate_tweet()
        if tweet:
            print(f"Generated: {tweet}")
            post_tweet(tweet)
        else:
            print("Failed to generate tweet")
