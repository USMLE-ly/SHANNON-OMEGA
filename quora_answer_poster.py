#!/usr/bin/env python3
"""Quora Answer Poster — Uses /answer page → Answer button → modal editor.
The most reliable Quora posting flow found.
"""
import json, sys, os, time, re
from playwright.sync_api import sync_playwright

PROJECT = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(PROJECT, "cookies_quora_working.json")
QUEUE_FILE = os.path.join(PROJECT, "content_queue.json")

def load_cookies(path=COOKIES_FILE):
    with open(path) as f:
        return json.load(f)

def load_queue(path=QUEUE_FILE):
    with open(path) as f:
        return json.load(f)

def click_answer_btn(page):
    """Click 'Answer' button on /answer page."""
    return page.evaluate("""
        () => {
            const btns = document.querySelectorAll('button');
            for (const b of btns) {
                const t = b.textContent.trim();
                if (t === 'Answer' && b.offsetParent !== null) {
                    b.scrollIntoView({block: 'center'});
                    b.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true, cancelable: true}));
                    b.dispatchEvent(new PointerEvent('pointerup', {bubbles: true, cancelable: true}));
                    b.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));
                    b.click();
                    b.focus();
                    return true;
                }
            }
            return false;
        }
    """)

def wait_for_editor(page, timeout=20):
    """Wait for contenteditable editor to appear (in modal or inline)."""
    for i in range(timeout):
        # Check main page
        editor = page.query_selector('[contenteditable="true"]')
        if editor:
            return editor, 'main'
        # Check all iframes
        for frame in page.frames:
            ed = frame.query_selector('[contenteditable="true"]')
            if ed:
                return ed, 'iframe'
        # Check for rich text
        rich = page.query_selector('[role="textbox"]')
        if rich:
            return rich, 'textbox'
        time.sleep(1)
    return None, None

def type_into_editor(editor, text, editor_type):
    """Type text into editor with human-like delays."""
    editor.click()
    time.sleep(0.5)
    if editor_type == 'textbox':
        editor.fill(text)
    else:
        page.keyboard.type(text, delay=3)
    time.sleep(1)

def click_submit_btn(page):
    """Find and click the Submit/Post button."""
    # Wait a moment for button to appear
    time.sleep(1)
    
    result = page.evaluate("""
        () => {
            const btns = document.querySelectorAll('button');
            const targets = ['submit', 'post', 'done', 'add answer', 'publish', 'share'];
            for (const b of btns) {
                const t = b.textContent.trim().toLowerCase();
                if (targets.includes(t) && b.offsetParent !== null) {
                    b.scrollIntoView({block: 'center'});
                    b.click();
                    return 'clicked: ' + t;
                }
            }
            return 'notfound';
        }
    """)
    
    if result == 'notfound':
        page.keyboard.press("Control+Enter")
        time.sleep(3)
        return 'ctrl+enter'
    return result

def post_via_answer_page(page, content, idx=0):
    """Full flow: /answer page → click Answer → type → submit."""
    print(f"[1] Loading /answer page...")
    page.goto("https://www.quora.com/answer", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(4000)
    
    title = page.title()
    print(f"  Title: {title[:60]}")
    if "Just a moment" in title:
        return False
    
    # Find and click Answer button
    print(f"[2] Looking for Answer button...")
    found = click_answer_btn(page)
    if not found:
        # Scroll and retry
        page.evaluate("window.scrollTo(0, 300)")
        page.wait_for_timeout(2000)
        found = click_answer_btn(page)
    
    if found:
        print(f"  ✅ Answer button clicked")
    else:
        print(f"  ❌ No Answer button found")
        page.screenshot(path=f"/tmp/quora_no_btn_{idx}.png")
        return False
    
    # Wait for editor
    print(f"[3] Waiting for editor...")
    editor, etype = wait_for_editor(page)
    if not editor:
        print(f"  ❌ No editor appeared")
        page.screenshot(path=f"/tmp/quora_no_editor_{idx}.png")
        return False
    
    print(f"  ✅ Editor found (type: {etype})")
    
    # Type content
    print(f"[4] Typing answer ({len(content)} chars)...")
    editor.click()
    page.wait_for_timeout(500)
    page.keyboard.type(content, delay=2)
    page.wait_for_timeout(1000)
    print(f"  ✅ Typed")
    
    # Remove overlays
    page.evaluate("""() => {
        for (const s of ['#onetrust-consent-sdk', '.consent-banner']) {
            const e = document.querySelector(s);
            if (e) e.remove();
        }
    }""")
    
    # Submit
    print(f"[5] Submitting...")
    result = click_submit_btn(page)
    print(f"  Submit: {result}")
    
    page.wait_for_timeout(5000)
    page.screenshot(path=f"/tmp/quora_post_result_{idx}.png")
    return 'notfound' not in result

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Quora Answer Poster")
    parser.add_argument("--queue", "-i", type=int, default=0, help="Queue index")
    parser.add_argument("--all", "-a", action="store_true", help="Post all")
    parser.add_argument("--text", "-t", help="Custom text")
    args = parser.parse_args()
    
    cookies = load_cookies()
    queue = load_queue()
    
    if args.text:
        contents = [{"topic": "custom", "content": args.text}]
    else:
        contents = queue if args.all else [queue[args.queue]]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-gpu', '--disable-software-rasterizer',
                  '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        )
        
        # Inject cookies
        valid = 0
        for c in cookies:
            try:
                ss_map = {'lax':'Lax','strict':'Strict','none':'None','no_restriction':'None','unspecified':'None'}
                ss = ss_map.get(c.get('sameSite','Lax').lower(), 'Lax')
                url = c.get('url', 'https://www.quora.com/')
                if 'www.www.' in url: url = 'https://www.quora.com/'
                context.add_cookies([{'name': c['name'], 'value': c.get('value',''), 'url': url, 'sameSite': ss}])
                valid += 1
            except: pass
        print(f"[*] Loaded {valid} cookies")
        
        page = context.new_page()
        page.set_default_timeout(30000)
        
        for idx, item in enumerate(contents):
            topic = item.get("topic", "untitled")
            content = item.get("content", "")
            print(f"\n{'='*60}")
            print(f"📝 {topic}")
            print(f"📏 {len(content)} chars")
            print(f"{'='*60}")
            
            ok = post_via_answer_page(page, content, idx)
            if ok:
                print(f"✅ SUCCESS: {topic}")
            else:
                print(f"❌ FAILED: {topic}")
            
            if idx < len(contents) - 1:
                print("  Waiting 30s before next post...")
                time.sleep(30)
        
        browser.close()

if __name__ == "__main__":
    sys.exit(main())
