"""
Playwright Quora Poster — Uses real browser context to bypass 405
Key: page.request.post() uses Chromium's native HTTP stack with real session
"""
import json, asyncio
from playwright.async_api import async_playwright

async def post_to_quora(cookies_file, question_url, answer_text):
    """Post an answer to Quora using Playwright's real browser context."""
    
    with open(cookies_file) as f:
        raw_cookies = json.load(f)
    
    print(f"[*] Loaded {len(raw_cookies)} cookies")
    
    async with async_playwright() as p:
        # Launch with ARM-safe flags
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--headless',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-webgl',
                '--disable-features=VizDisplayCompositor',
                '--enable-features=NetworkService,NetworkServiceInProcess',
                '--disable-blink-features=AutomationControlled',
            ]
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.83 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
        )
        
        # Add cookies before navigating
        cookies = []
        for c in raw_cookies:
            domain = c.get('domain', '').lstrip('.')
            if not domain:
                continue
            cookies.append({
                'name': c['name'],
                'value': c['value'],
                'domain': domain,
                'path': c.get('path', '/'),
                'httpOnly': c.get('httpOnly', False),
                'secure': c.get('secure', False),
                'sameSite': c.get('sameSite', 'Lax') if c.get('sameSite') in ('Strict', 'Lax', 'None') else 'Lax',
            })
        
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        # Navigate to Quora
        print(f"[*] Loading Quora...")
        await page.goto('https://www.quora.com/', timeout=30000, wait_until='domcontentloaded')
        title = await page.title()
        print(f"[*] Title: {title}")
        
        if 'just a moment' in title.lower():
            print("[-] Cloudflare challenge - waiting...")
            await page.wait_for_timeout(15000)
            title = await page.title()
            print(f"[*] After wait: {title}")
        
        # Extract formkey
        formkey = await page.evaluate("""
            () => {
                const match = document.documentElement.innerHTML.match(/"formkey"\\s*:\\s*"([^"]+)"/);
                return match ? match[1] : '';
            }
        """)
        print(f"[*] Formkey: {formkey}")
        
        # Navigate to the question
        print(f"[*] Loading question page...")
        await page.goto(question_url, timeout=30000, wait_until='domcontentloaded')
        print(f"[*] Question URL: {page.url}")
        
        # Extract question ID
        qid = await page.evaluate("""
            () => {
                const html = document.documentElement.innerHTML;
                const m1 = html.match(/"qid"\\s*:\\s*"(\\d+)"/);
                if (m1) return m1[1];
                const m2 = html.match(/"questionId"\\s*:\\s*"(\\d+)"/);
                if (m2) return m2[1];
                const m3 = window.location.href.match(/\\/qid=(\\d+)/);
                if (m3) return m3[1];
                return '';
            }
        """)
        print(f"[*] QID: {qid}")
        
        if not qid:
            print("[-] Could not find QID")
            await browser.close()
            return False
        
        # Post via page.request.post() — uses REAL browser context!
        print(f"[*] Posting answer via browser context ({len(answer_text)} chars)...")
        
        mutation = {
            "operationName": "AddAnswerMutation",
            "variables": {
                "questionId": qid,
                "text": answer_text,
                "isDraft": False
            },
            "query": "mutation AddAnswerMutation($questionId: String!, $text: String!, $isDraft: Boolean) { addAnswer(questionId: $questionId, text: $text, isDraft: $isDraft) { id url __typename } }"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Formkey": formkey,
        }
        
        response = await page.request.post(
            "https://www.quora.com/graphql",
            data=json.dumps(mutation),
            headers=headers
        )
        
        status = response.status
        body = await response.text()
        
        print(f"[*] Response: {status}")
        print(f"[*] Body: {body[:500]}")
        
        if status == 200 and '"id"' in body:
            data = json.loads(body)
            answer_id = data.get('data', {}).get('addAnswer', {}).get('id', '')
            print(f"[+] ✅ ANSWER POSTED! ID: {answer_id}")
            await browser.close()
            return True
        
        if status == 405:
            print("[*] Got 405 - trying alt endpoint...")
            response2 = await page.request.post(
                "https://www.quora.com/graphql/gql_para_POST?q=AddAnswerMutation",
                data=json.dumps(mutation),
                headers=headers
            )
            status2 = response2.status
            body2 = await response2.text()
            print(f"[*] Alt result: {status2} - {body2[:300]}")
        
        await browser.close()
        return False


async def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 playwright_quora_poster.py <question_url> <answer_text>")
        print("  Reads cookies from cookies_quora_working.json")
        sys.exit(1)
    
    question_url = sys.argv[1]
    answer_text = sys.argv[2]
    cookies_file = 'cookies_quora_working.json'
    
    ok = await post_to_quora(cookies_file, question_url, answer_text)
    print(f"\n{'✅ SUCCESS' if ok else '❌ FAILED'}")

if __name__ == '__main__':
    asyncio.run(main())
