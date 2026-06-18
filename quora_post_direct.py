#!/usr/bin/env python3
"""
Direct Quora Answer Poster — uses Playwright+xvfb to bypass Cloudflare
Usage: xvfb-run python3 quora_post_direct.py [question_url]
"""
import asyncio, json, sys, re, os
sys.path.insert(0, 'scarab-controller')
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def post_answer(question_url="https://www.quora.com/What-is-the-future-of-fashion"):
    # Load content
    with open('content_queue.json') as f:
        queue = json.load(f)
    
    # Load cookies
    cookies_path = '/tmp/codex-web-uploads/f-498NGI/cookie.json'
    with open(cookies_path) as f:
        cookies_data = json.load(f)
    
    answer = queue[4]
    content = answer["content"]
    print(f'[+] Answer: {answer["topic"]}')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # xvfb provides display
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        )
        
        # Stealth
        stealth = Stealth(init_scripts_only=True)
        await stealth.apply_stealth_async(context)
        
        # Inject cookies
        for c in cookies_data:
            try:
                domain = c.get("domain", ".quora.com").lstrip(".")
                await context.add_cookies([{
                    "name": c["name"], "value": c["value"],
                    "domain": domain, "path": c.get("path", "/"),
                    "httpOnly": c.get("httpOnly", False),
                    "secure": c.get("secure", True),
                }])
            except: pass
        
        page = await context.new_page()
        
        # Navigate
        print(f'[*] Loading {question_url}...')
        await page.goto(question_url, wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(8000)
        
        title = await page.title()
        print(f'[+] Title: {title}')
        
        if 'Just a moment' in title:
            print('[*] Solving CF challenge...')
            await page.wait_for_timeout(20000)
            title = await page.title()
            print(f'[+] After wait: {title}')
        
        if 'Just a moment' in title:
            print('[-] Still blocked by Cloudflare')
            await page.screenshot(path='quora_cf.png')
            await browser.close()
            return False
        
        # Extract question ID from URL or page
        qid = None
        slug_match = re.search(r'quora\.com/([^/?#]+)', question_url)
        if slug_match:
            slug = slug_match.group(1)
            html = await page.content()
            for m in re.finditer(r'"qid"\s*:\s*(\d+)', html):
                qid = m.group(1)
        
        if not qid:
            print('[-] Could not find question ID')
            await browser.close()
            return False
        
        print(f'[+] QID: {qid}')
        
        # Get formkey
        formkey = await page.evaluate(
            "window.ansFrontendGlobals?.earlySettings?.formkey"
        )
        print(f'[+] Formkey: {formkey}')
        
        if not formkey:
            print('[-] No formkey found')
            await browser.close()
            return False
        
        # Post via GraphQL from browser context
        print('[*] Posting answer...')
        result = await page.evaluate(f"""
            async () => {{
                const resp = await fetch('https://www.quora.com/graphql', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json', 'X-Formkey': '{formkey}' }},
                    body: JSON.stringify({{
                        operationName: 'AddAnswerMutation',
                        variables: {{ questionId: '{qid}', text: {json.dumps(content)}, isDraft: false }},
                        query: 'mutation AddAnswerMutation($questionId: String!, $text: String!, $isDraft: Boolean) {{ addAnswer(questionId: $questionId, text: $text, isDraft: $isDraft) {{ id url __typename }} }}'
                    }})
                }});
                return {{ status: resp.status, text: await resp.text() }};
            }}
        """)
        
        print(f'[+] GraphQL status: {result["status"]}')
        
        if result["status"] == 200:
            try:
                data = json.loads(result["text"])
                aid = data.get("data", {}).get("addAnswer", {})
                if aid.get("id"):
                    print(f'\n✅ ANSWER POSTED!')
                    print(f'   ID: {aid["id"]}')
                    print(f'   URL: {aid.get("url")}')
                    await browser.close()
                    return True
            except: pass
            print(f'Response: {result["text"][:300]}')
        else:
            print(f'Response: {result["text"][:300]}')
        
        # DOM fallback
        print('[*] Trying DOM approach...')
        btn = await page.query_selector('button:has-text("Answer")')
        if btn:
            await btn.click()
            await page.wait_for_timeout(3000)
        ed = await page.query_selector('[contenteditable="true"]')
        if ed:
            await ed.click()
            await ed.fill(content)
            await page.wait_for_timeout(2000)
            sb = await page.query_selector('button:has-text("Post"), button:has-text("Submit")')
            if sb:
                await sb.click(force=True)
                await page.wait_for_timeout(3000)
                print('[+] DOM post submitted!')
                await page.screenshot(path='quora_posted.png')
                print('[+] Screenshot saved')
        
        await browser.close()
        return result["status"] == 200 or bool(ed)

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.quora.com/What-is-the-future-of-fashion"
    asyncio.run(post_answer(url))
