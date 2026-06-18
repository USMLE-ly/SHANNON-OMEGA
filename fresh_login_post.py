#!/usr/bin/env python3
"""Fresh login to Quora from Playwright + post answer immediately"""
import asyncio, json, sys, re, os
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

EMAIL = "luxor.offacial@gmail.com"
PASSWORD = "Hesoyam$11011"

async def main():
    with open('content_queue.json') as f:
        queue = json.load(f)
    answer = queue[4]
    content = answer["content"]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        )
        stealth = Stealth(init_scripts_only=True)
        await stealth.apply_stealth_async(context)
        page = await context.new_page()
        
        print('[*] Loading Quora...')
        await page.goto('https://www.quora.com/', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(5000)
        
        title = await page.title()
        print(f'[+] Title: {title}')
        
        # Handle CF challenge
        if 'Just a moment' in title:
            print('[*] CF challenge... waiting up to 90s')
            for i in range(6):
                await page.wait_for_timeout(15000)
                title = await page.title()
                print(f'[+] After {15*(i+1)}s: {title}')
                if 'Just a moment' not in title:
                    break
        
        if 'Just a moment' in title:
            print('[-] CF still blocking')
            await page.screenshot(path='quora_cf_fresh.png')
            await browser.close()
            return False
        
        print('[+] CF bypassed!')
        await page.screenshot(path='quora_fresh_home.png')
        
        # Check if already logged in by cookies
        cookies = await context.cookies()
        has_session = any(c['name'] == 'm-b' for c in cookies)
        print(f'[+] Already logged in: {has_session}')
        
        if not has_session:
            # Click login
            login_btn = await page.query_selector('button:has-text("Log In"), a:has-text("Log In")')
            if login_btn:
                await login_btn.click()
                await page.wait_for_timeout(3000)
            
            # Find email input
            email_input = await page.query_selector('input[name="email"], input[type="email"]')
            if email_input:
                await email_input.click()
                await email_input.fill(EMAIL)
                await page.wait_for_timeout(1000)
                
                # Password
                pw_input = await page.query_selector('input[type="password"]')
                if pw_input:
                    await pw_input.click()
                    await pw_input.fill(PASSWORD)
                    await page.wait_for_timeout(1000)
                    
                    # Submit
                    submit = await page.query_selector('button[type="submit"]')
                    if submit:
                        await submit.click()
                    else:
                        await page.keyboard.press("Enter")
                    
                    await page.wait_for_timeout(5000)
                    print(f'[+] After login: {await page.title()}')
                    await page.screenshot(path='quora_after_login_fresh.png')
        
        # Save cookies
        cookies = await context.cookies()
        with open('cookies_quora_fresh.json', 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f'[+] Saved {len(cookies)} fresh cookies')
        
        # Navigate to question
        await page.goto('https://www.quora.com/What-is-the-future-of-fashion',
                       wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(5000)
        print(f'[+] Question: {await page.title()}')
        
        # Get formkey
        formkey = await page.evaluate("window.ansFrontendGlobals?.earlySettings?.formkey")
        print(f'[+] Formkey: {formkey}')
        
        if not formkey:
            print('[-] No formkey')
            await browser.close()
            return False
        
        # Post via GraphQL
        print('[*] Posting answer...')
        result = await page.evaluate(f"""
            async () => {{
                const resp = await fetch('/graphql', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json', 'X-Formkey': '{formkey}' }},
                    body: JSON.stringify({{
                        operationName: 'AddAnswerMutation',
                        variables: {{ questionId: '28794363', text: {json.dumps(content)}, isDraft: false }},
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
                aid = data.get("data", {}).get("addAnswer", {})
                if aid.get("id"):
                    print(f'\n{"="*50}')
                    print(f'✅ ANSWER POSTED!')
                    print(f'   ID: {aid["id"]}')
                    print(f'   URL: {aid.get("url")}')
                    print(f'{"="*50}')
                    await browser.close()
                    return True
            except: pass
            print(f'Response: {result["text"][:300]}')
        else:
            print(f'Response: {result["text"][:300]}')
        
        await browser.close()
        return result["status"] == 200

success = asyncio.run(main())
sys.exit(0 if success else 1)
