"""
Simple FlareSolverr-like service using Playwright + xvfb
Solves Cloudflare challenges and returns HTML/cookies
"""
import asyncio, json, sys, os, time, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

BROWSER = None
CONTEXT = None
LOCK = asyncio.Lock()

async def init_browser():
    global BROWSER, CONTEXT
    p = await async_playwright().__aenter__()
    BROWSER = await p.chromium.launch(
        headless=False,
        args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
    )
    CONTEXT = await BROWSER.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    )
    stealth = Stealth(init_scripts_only=True)
    await stealth.apply_stealth_async(CONTEXT)

async def request_page(url, cookies=None, post_data=None, return_raw=False):
    async with LOCK:
        page = await CONTEXT.new_page()
        try:
            if cookies:
                for c in cookies:
                    try:
                        await CONTEXT.add_cookies([{
                            "name": c["name"], "value": c["value"],
                            "domain": c.get("domain",".quora.com").lstrip("."),
                            "path": c.get("path","/"),
                            "httpOnly": c.get("httpOnly",False),
                            "secure": c.get("secure",True),
                        }])
                    except: pass
            
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(5000)
            
            # Handle CF challenge
            title = await page.title()
            if 'Just a moment' in title:
                await page.wait_for_timeout(15000)
            
            if return_raw:
                return await page.content(), dict(await CONTEXT.cookies())
            
            result = await page.evaluate("""() => ({
                html: document.documentElement.innerHTML,
                title: document.title,
                url: window.location.href,
                formkey: window.ansFrontendGlobals?.earlySettings?.formkey || null,
            })""")
            
            cookies_out = await CONTEXT.cookies()
            return result, cookies_out
        finally:
            await page.close()

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('utf-8')
        try:
            data = json.loads(body)
        except:
            data = {}
        
        cmd = data.get('cmd', 'request.get')
        url = data.get('url', '')
        cookies = data.get('cookies', [])
        post_data = data.get('postData', None)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if cmd == 'request.get':
                result, cookies_out = loop.run_until_complete(request_page(url, cookies))
                response = {
                    "solution": {
                        "url": result.get("url", url),
                        "status": 200,
                        "cookies": cookies_out,
                        "response": result.get("html", ""),
                        "formkey": result.get("formkey"),
                    },
                    "status": "ok",
                }
        except Exception as e:
            response = {"status": "error", "message": str(e)}
        finally:
            loop.close()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def log_message(self, format, *args):
        pass

async def start_service(port=8191):
    await init_browser()
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'[+] FlareSolverr-like service running on http://0.0.0.0:{port}/v1')
    print(f'    Send POST with: {"cmd":"request.get","url":"..."}')
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, server.serve_forever)

if __name__ == '__main__':
    asyncio.run(start_service())
