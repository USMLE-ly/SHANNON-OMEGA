#!/usr/bin/env python3
"""Quora DOM Poster — uses Playwright + Chromium to post answers via UI automation.
Works in this container by using Chromium (not Firefox/Camoufox) via xvfb."""
import asyncio, json, os, sys, time
from playwright.async_api import async_playwright

PROJECT = os.path.dirname(os.path.abspath(__file__))

async def post_answer(qid_or_url: str, content: str, headless: bool = False):
    """Post an answer to Quora via DOM automation."""
    os.environ['DISPLAY'] = ':99'
    
    # Load cookies
    cookies_path = os.path.join(PROJECT, "cookies_quora_working.json")
    with open(cookies_path) as f:
        raw_cookies = json.load(f)
    
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-gpu", "--disable-software-rasterizer",
                  "--disable-dev-shm-usage", "--single-process",
                  "--disable-blink-features=AutomationControlled"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        
        # Inject cookies
        success = 0
        for c in raw_cookies:
            try:
                ss = c.get('sameSite', 'Lax').lower()
                ss_map = {'lax':'Lax','strict':'Strict','none':'None','no_restriction':'None','unspecified':'None'}
                ss = ss_map.get(ss, 'Lax')
                url = c.get('url', 'https://www.quora.com/')
                if 'www.www.' in url: url = 'https://www.quora.com/'
                await context.add_cookies([{
                    'name': c['name'], 'value': c.get('value', ''),
                    'url': url, 'sameSite': ss,
                }])
                success += 1
            except:
                pass
        print(f"[+] Injected {success}/{len(raw_cookies)} cookies")
        
        page = await context.new_page()
        page.set_default_timeout(60000)
        
        # Build the URL
        if qid_or_url.startswith("http"):
            url = qid_or_url
        else:
            # Try to find the question URL
            url = f"https://www.quora.com/question/{qid_or_url}"
        
        print(f"[*] Navigating to: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        # Wait for Cloudflare to clear
        for i in range(30):
            title = await page.title()
            if "Just a moment" not in title:
                break
            await page.wait_for_timeout(2000)
        else:
            print("[-] Cloudflare still blocking after 60s")
            await page.screenshot(path="/tmp/quora_cf_blocked_final.png")
            await browser.close()
            return False
        
        print(f"[+] Page loaded: {await page.title()}")
        await page.wait_for_timeout(3000)
        
        # Scroll to find content
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight/3)")
        await page.wait_for_timeout(2000)
        
        # Click "Answer" button
        answer_selectors = [
            'a:has-text("Answer")',
            'button:has-text("Answer")',
            '[data-testid="answer_button"]',
            'a[href*="/answer"]',
            '.q-box a:has-text("Answer")',
        ]
        
        answer_btn = None
        for sel in answer_selectors:
            answer_btn = await page.query_selector(sel)
            if answer_btn and await answer_btn.is_visible():
                print(f"[+] Found Answer button: {sel}")
                break
        
        if not answer_btn:
            # Try JS click on any element with "Answer" text
            clicked = await page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('a, button, span, div');
                    for (const el of elements) {
                        if (el.textContent.trim() === 'Answer' || el.textContent.trim() === 'Write answer') {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
            if clicked:
                print("[+] Clicked 'Answer' via JS")
            else:
                print("[-] No Answer button found on page")
                await page.screenshot(path="/tmp/quora_no_answer_btn2.png")
                await browser.close()
                return False
        else:
            await answer_btn.click()
            print("[+] Clicked Answer button")
        
        # Wait for editor to appear
        await page.wait_for_timeout(5000)
        
        # Find the editor
        editor = await page.query_selector('[contenteditable="true"]')
        if not editor:
            # Maybe the editor is in a popup/modal
            await page.wait_for_timeout(3000)
            editor = await page.query_selector('[contenteditable="true"]')
        
        if not editor:
            print("[-] Editor not found after clicking Answer")
            await page.screenshot(path="/tmp/quora_no_editor3.png")
            await browser.close()
            return False
        
        print(f"[+] Editor found! Typing answer ({len(content)} chars)...")
        
        # Click the editor and type
        await editor.click()
        await page.wait_for_timeout(500)
        
        # Type in chunks to avoid issues
        chunk_size = 500
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            await page.keyboard.type(chunk, delay=0)
            await page.wait_for_timeout(100)
        
        await page.wait_for_timeout(2000)
        
        # Find and click submit button
        submit_selectors = [
            'button:has-text("Submit")',
            'button:has-text("Post")',
            'button:has-text("Done")',
            'button:has-text("Add Answer")',
            'button:has-text("Save")',
            '[data-testid="submit_button"]',
            '.q-submit button',
        ]
        
        submit_btn = None
        for sel in submit_selectors:
            submit_btn = await page.query_selector(sel)
            if submit_btn and await submit_btn.is_visible():
                print(f"[+] Found Submit button: {sel}")
                break
        
        if submit_btn:
            await submit_btn.click()
            await page.wait_for_timeout(5000)
            print("[+] ✅ Answer submitted successfully!")
            
            # Take a final screenshot
            await page.screenshot(path="/tmp/quora_submitted.png", full_page=True)
            print("[+] Screenshot: /tmp/quora_submitted.png")
            await browser.close()
            return True
        else:
            print("[?] Submit button not found - content may be in editor")
            await page.screenshot(path="/tmp/quora_after_typing.png", full_page=True)
            
            # Try keyboard shortcut (Ctrl+Enter on Windows/Linux)
            await page.keyboard.press("Control+Enter")
            await page.wait_for_timeout(5000)
            
            # Check if we're still on the same page
            current_url = page.url
            if "/answer/" in current_url or "answer" in current_url.lower():
                print("[+] ✅ Answer submitted via Ctrl+Enter!")
                await browser.close()
                return True
            
            print("[-] Could not submit answer")
            await browser.close()
            return False


if __name__ == "__main__":
    # Load from content queue
    queue_path = os.path.join(PROJECT, "content_queue.json")
    with open(queue_path) as f:
        queue = json.load(f)
    
    if len(sys.argv) > 1:
        qid = sys.argv[1]
    else:
        qid = "28794363"  # Default QID
    
    if len(sys.argv) > 2:
        idx = int(sys.argv[2])
        content = queue[idx]["content"] if idx < len(queue) else queue[0]["content"]
    else:
        content = queue[0]["content"]
    
    print("=" * 60)
    print("QUORA DOM POSTER v1.0 — Chromium + Playwright")
    print("=" * 60)
    print(f"QID: {qid}")
    print(f"Content: {content[:50]}...")
    print()
    
    result = asyncio.run(post_answer(qid, content))
    print(f"\n{'✅ SUCCESS' if result else '❌ FAILED'}")
