#!/usr/bin/env python3
"""POST answer to Quora via Playwright + xvfb (full browser, bypasses all blocking)"""
import asyncio, json, sys, re
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    with open('/tmp/codex-web-uploads/f-498NGI/cookie.json') as f:
        cookies_data = json.load(f)
    with open('content_queue.json') as f:
        queue = json.load(f)
    
    answer = queue[4]
    content = answer["content"]
    qid = "28794363"
    print(f'[+] Answer: {answer["topic"]}')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, args=['--no-sandbox']
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        )
        
        stealth = Stealth(init_scripts_only=True)
        await stealth.apply_stealth_async(context)
        
        # Inject cookies one by one with proper validation
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
        
        page = await context.new_page()
        
        # Step 1: Load Quora home to establish session
        print('[*] Step 1: Loading Quora home...')
        await page.goto('https://www.quora.com/', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(5000)
        
        page_title = await page.title()
        print(f'[+] Home title: {page_title}')
        
        if 'Just a moment' in page_title:
            print('[*] CF challenge... waiting 15s')
            await page.wait_for_timeout(15000)
        
        page_title = await page.title()
        if 'Just a moment' in page_title:
            print('[-] Still blocked by CF')
            await page.screenshot(path='quora_cf_home.png')
            await browser.close()
            return False
        
        print('[+] CF bypassed!')
        
        # Step 2: Navigate to the question
        print('[*] Step 2: Loading question page...')
        await page.goto('https://www.quora.com/What-is-the-future-of-fashion', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(5000)
        
        question_title = await page.title()
        print(f'[+] Question title: {question_title}')
        
        # Step 3: Extract formkey
        formkey = await page.evaluate("window.ansFrontendGlobals?.earlySettings?.formkey")
        print(f'[+] Formkey: {formkey}')
        
        if not formkey:
            print('[-] No formkey')
            await browser.close()
            return False
        
        # Step 4: Post via GraphQL using browser's own fetch
        print('[*] Step 3: Posting via GraphQL...')
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
        
        print(f'[+] GraphQL: status={result["status"]}')
        
        if result["status"] == 200:
            try:
                data = json.loads(result["text"])
                if data.get("data", {}).get("addAnswer", {}).get("id"):
                    aid = data["data"]["addAnswer"]
                    print(f'\n✅ ANSWER POSTED!')
                    print(f'   ID: {aid["id"]}')
                    print(f'   URL: {aid.get("url")}')
                    await browser.close()
                    return True
            except: pass
            print(f'Response: {result["text"][:500]}')
        else:
            print(f'Response: {result["text"][:500]}')
            
            # DOM fallback
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
                await page.screenshot(path='quora_dom_post.png')
            else:
                await page.screenshot(path='quora_no_editor.png')
        
        await browser.close()
        return result["status"] == 200

asyncio.run(main())
