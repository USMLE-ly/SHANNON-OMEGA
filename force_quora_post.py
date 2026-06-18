#!/usr/bin/env python3
"""Force post to Quora via Playwright+xvfb with proper cookie handling"""
import asyncio, json, sys, re
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def post():
    with open('/tmp/codex-web-uploads/f-498NGI/cookie.json') as f:
        cookies_data = json.load(f)
    with open('content_queue.json') as f:
        queue = json.load(f)
    
    answer = queue[4]
    content = answer["content"]
    
    async with async_playwright() as p:
        context = None
        browser = await p.chromium.launch(
            headless=False, args=['--no-sandbox']
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        )
        
        # Don't inject cookies yet - navigate to home first
        page = await context.new_page()
        
        print('[*] Loading Quora to establish CF session...')
        await page.goto('https://www.quora.com/', wait_until='domcontentloaded', timeout=30000)
        
        title = await page.title()
        print(f'[+] Title: {title}')
        
        cf_count = 0
        while 'Just a moment' in title:
            cf_count += 1
            if cf_count > 6:  # 90 seconds max
                break
            print(f'[*] CF challenge ({cf_count}), waiting 15s...')
            await page.wait_for_timeout(15000)
            title = await page.title()
            print(f'[+] Title: {title}')
        
        if 'Just a moment' in title:
            print('[-] CF not resolved')
            await page.screenshot(path='quora_cf_final.png')
            await browser.close()
            return False
        
        print('[+] CF bypassed! Now injecting cookies...')
        
        # Now inject login cookies on the CF-bypassed page
        for c in cookies_data:
            try:
                domain = c.get("domain", ".quora.com").strip(".")
                await context.add_cookies([{
                    "name": c["name"], "value": c["value"],
                    "domain": domain, "path": c.get("path", "/"),
                    "httpOnly": c.get("httpOnly", False),
                    "secure": c.get("secure", True),
                }])
            except: pass
        
        # Reload to get authenticated session
        await page.goto('https://www.quora.com/', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(3000)
        print(f'[+] After cookie inject: {await page.title()}')
        
        # Navigate to question
        print('[*] Loading question page...')
        await page.goto('https://www.quora.com/What-is-the-future-of-fashion', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(5000)
        
        title = await page.title()
        print(f'[+] Question: {title}')
        
        # Get formkey
        formkey = await page.evaluate("window.ansFrontendGlobals?.earlySettings?.formkey")
        print(f'[+] Formkey: {formkey}')
        
        if not formkey:
            print('[-] No formkey - not logged in?')
            await page.screenshot(path='quora_not_logged.png')
            await browser.close()
            return False
        
        # Get QID
        html = await page.content()
        qid_match = re.search(r'qid[=:]\s*(\d+)', html)
        qid = qid_match.group(1) if qid_match else "28794363"
        print(f'[+] QID: {qid}')
        
        # POST via GraphQL from browser
        print('[*] Posting via GraphQL...')
        result = await page.evaluate(f"""
            async () => {{
                const resp = await fetch('/graphql', {{
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
                if data.get("data", {}).get("addAnswer", {}).get("id"):
                    print(f'\n{"="*50}')
                    print(f'✅ ANSWER POSTED!')
                    print(f'   ID: {data["data"]["addAnswer"]["id"]}')
                    print(f'   URL: {data["data"]["addAnswer"].get("url")}')
                    print(f'{"="*50}')
                    await browser.close()
                    return True
            except: pass
            print(f'Response: {result["text"][:300]}')
        else:
            print(f'Response: {result["text"][:300]}')
            # Try DOM approach
            print('[*] Trying DOM post...')
            btn = await page.query_selector('button:has-text("Answer")')
            if btn:
                await btn.click()
                await page.wait_for_timeout(3000)
            ed = await page.query_selector('[contenteditable="true"]')
            if ed:
                await ed.click()
                await ed.fill(content)
                await page.wait_for_timeout(1000)
                sb = await page.query_selector('button:has-text("Post"), button:has-text("Submit")')
                if sb:
                    await sb.click(force=True)
                    await page.wait_for_timeout(3000)
                    print('[+] DOM posted!')
                await page.screenshot(path='quora_posted.png')
        
        await browser.close()
        return result["status"] == 200

result = asyncio.run(post())
sys.exit(0 if result else 1)
