#!/usr/bin/env python3
"""Login to Quora from Playwright browser, then post answer"""
import asyncio, json, sys, re, os
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    email = "luxor.offacial@gmail.com"
    password = "Hesoyam$11011"
    
    with open('content_queue.json') as f:
        queue = json.load(f)
    answer = queue[4]
    content = answer["content"]
    
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
        
        page = await context.new_page()
        
        print('[*] Loading Quora login...')
        await page.goto('https://www.quora.com/', wait_until='domcontentloaded', timeout=30000)
        
        title = await page.title()
        print(f'[+] Title: {title}')
        
        # Handle CF
        if 'Just a moment' in title:
            print('[*] CF challenge, waiting up to 90s...')
            for i in range(6):
                await page.wait_for_timeout(15000)
                title = await page.title()
                print(f'[+] After {15*(i+1)}s: {title}')
                if 'Just a moment' not in title:
                    break
        
        if 'Just a moment' in title:
            print('[-] CF not resolved')
            await browser.close()
            return False
        
        print('[+] CF bypassed! Looking for login...')
        await page.screenshot(path='quora_home.png')
        
        # Try clicking login/sign-in button
        login_btn = None
        for selector in ['button:has-text("Log In")', 'button:has-text("Sign In")', 
                         'a:has-text("Log In")', 'a:has-text("Sign In")',
                         '[href*="login"]', '[href*="signin"]']:
            try:
                login_btn = await page.query_selector(selector)
                if login_btn:
                    print(f'[+] Found login button: {selector}')
                    break
            except: pass
        
        if login_btn:
            await login_btn.click()
            await page.wait_for_timeout(3000)
        
        # Try to find email/username input
        email_input = None
        for selector in ['input[name="email"]', 'input[type="email"]', 
                         'input[name="username"]', 'input[autocomplete="username"]',
                         'input[placeholder*="email"]', 'input[placeholder*="Email"]']:
            try:
                email_input = await page.query_selector(selector)
                if email_input:
                    print(f'[+] Found email input: {selector}')
                    break
            except: pass
        
        if email_input:
            await email_input.click()
            await email_input.fill(email)
            await page.wait_for_timeout(1000)
            
            # Find password input
            pw_input = await page.query_selector('input[type="password"]')
            if pw_input:
                await pw_input.click()
                await pw_input.fill(password)
                await page.wait_for_timeout(1000)
                
                # Click submit
                submit = await page.query_selector('button[type="submit"], input[type="submit"]')
                if submit:
                    await submit.click()
                    await page.wait_for_timeout(5000)
                    print(f'[+] Login submitted! Title: {await page.title()}')
                    await page.screenshot(path='quora_after_login.png')
                else:
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(5000)
                    print(f'[+] Enter pressed. Title: {await page.title()}')
        
        # Check if logged in
        await page.goto('https://www.quora.com/', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(3000)
        
        # Check for login indicators
        html = await page.content()
        if 'm-b' in html or 'Sign Out' in html or 'luxor' in html.lower():
            print('[+] Logged in!')
            await page.screenshot(path='quora_logged_in.png')
            
            # Save cookies for future use
            cookies = await context.cookies()
            with open('cookies_quora_fresh.json', 'w') as f:
                json.dump(cookies, f, indent=2)
            print(f'[+] Saved {len(cookies)} cookies to cookies_quora_fresh.json')
            
            # Now post to question
            await page.goto('https://www.quora.com/What-is-the-future-of-fashion', wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(5000)
            print(f'[+] Question page: {await page.title()}')
            
            formkey = await page.evaluate("window.ansFrontendGlobals?.earlySettings?.formkey")
            print(f'[+] Formkey: {formkey}')
            
            if formkey:
                # Get QID
                content_html = await page.content()
                qm = re.search(r'qid[=:]["\']*(\d+)', content_html)
                qid = qm.group(1) if qm else "28794363"
                
                # Post via GraphQL
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
                
                print(f'[+] GraphQL: status={result["status"]}')
                if result["status"] == 200:
                    data = json.loads(result["text"])
                    if data.get("data", {}).get("addAnswer", {}).get("id"):
                        print(f'\n{"="*50}')
                        print(f'✅ ANSWER POSTED!')
                        print(f'   ID: {data["data"]["addAnswer"]["id"]}')
                        print(f'{"="*50}')
                        await browser.close()
                        return True
                    else:
                        print(f'Response: {result["text"][:500]}')
                else:
                    print(f'Response: {result["text"][:500]}')
        else:
            print('[-] Not logged in')
            await page.screenshot(path='quora_login_failed.png')
        
        await browser.close()
        return False

success = asyncio.run(main())
sys.exit(0 if success else 1)
