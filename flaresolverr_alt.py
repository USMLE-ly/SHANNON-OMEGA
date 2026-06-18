"""
FlareSolverr Alternative — using Playwright + threading
Runs an HTTP API that solves Cloudflare challenges for Quora
"""
import asyncio, json, sys, os, threading, time, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# Global browser resources
BROWSER = None
CONTEXT = None
PLAYWRIGHT = None

def init_sync():
    """Initialize browser synchronously in a thread"""
    global BROWSER, CONTEXT, PLAYWRIGHT
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def init():
        global BROWSER, CONTEXT, PLAYWRIGHT
        PLAYWRIGHT = await async_playwright().__aenter__()
        BROWSER = await PLAYWRIGHT.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        CONTEXT = await BROWSER.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        )
        stealth = Stealth(init_scripts_only=True)
        await stealth.apply_stealth_async(CONTEXT)
        print('[+] Browser initialized')
    
    loop.run_until_complete(init())
    loop.close()

def fetch_sync(url, cookies=None, return_html=False):
    """Fetch a page using the browser (sync wrapper)"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def fetch():
        global CONTEXT
        page = await CONTEXT.new_page()
        try:
            if cookies:
                for c in cookies:
                    try:
                        domain = c.get("domain", ".quora.com").lstrip(".")
                        await CONTEXT.add_cookies([{
                            "name": c["name"], "value": c["value"],
                            "domain": domain, "path": c.get("path","/"),
                            "httpOnly": c.get("httpOnly", False),
                            "secure": c.get("secure", True),
                        }])
                    except: pass
            
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(5000)
            
            title = await page.title()
            if 'Just a moment' in title:
                print(f'[*] CF challenge for {url}, waiting...')
                await page.wait_for_timeout(15000)
                title = await page.title()
            
            # Get all cookies from context
            all_cookies = await CONTEXT.cookies()
            
            if return_html:
                html = await page.content()
                formkey = None
                try:
                    formkey = await page.evaluate(
                        "window.ansFrontendGlobals?.earlySettings?.formkey"
                    )
                except: pass
                return html, all_cookies, formkey
            else:
                result = await page.evaluate("""() => ({
                    title: document.title,
                    url: window.location.href,
                    formkey: window.ansFrontendGlobals?.earlySettings?.formkey || null,
                    cookies: document.cookie,
                })""")
                return result, all_cookies, None
        finally:
            await page.close()
    
    result = loop.run_until_complete(fetch())
    loop.close()
    return result

def graphql_post_sync(url, payload, formkey):
    """Execute a GraphQL mutation from the browser context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def execute():
        global CONTEXT
        page = await CONTEXT.new_page()
        try:
            result = await page.evaluate(f"""
                async () => {{
                    const resp = await fetch('{url}', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json', 'X-Formkey': '{formkey}' }},
                        body: JSON.stringify({json.dumps(payload)})
                    }});
                    return {{ status: resp.status, text: await resp.text() }};
                }}
            """)
            return result
        finally:
            await page.close()
    
    result = loop.run_until_complete(execute())
    loop.close()
    return result

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
        
        print(f'[*] Request: {cmd} {url[:60]}...')
        
        try:
            if cmd == 'request.get':
                result, all_cookies, _ = fetch_sync(url, cookies)
                
                # Also try to get the page content with return_html
                html, _, formkey = fetch_sync(url, cookies, return_html=True)
                
                response = {
                    "status": "ok",
                    "solution": {
                        "url": result.get("url", url),
                        "status": 200,
                        "cookies": [{"name": c["name"], "value": c["value"],
                                     "domain": c["domain"], "path": c["path"]} 
                                    for c in all_cookies],
                        "response": html,
                        "formkey": formkey,
                    }
                }
            elif cmd == 'request.post':
                post_data = data.get('postData', '{}')
                if isinstance(post_data, str):
                    post_data = json.loads(post_data)
                formkey = data.get('formkey', '')
                
                result = graphql_post_sync(data.get('url'), post_data, formkey)
                response = {
                    "status": "ok",
                    "solution": {
                        "status": result["status"],
                        "response": result["text"],
                    }
                }
            else:
                response = {"status": "error", "message": f"Unknown cmd: {cmd}"}
        except Exception as e:
            response = {"status": "error", "message": str(e)}
            import traceback
            traceback.print_exc()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'FlareSolverr Alternative - POST JSON with cmd, url, cookies')
    
    def log_message(self, format, *args):
        pass

def start_server(port=8191):
    print(f'[+] Starting FlareSolverr alternative on port {port}...')
    print(f'    Endpoint: http://localhost:{port}/v1')
    
    # Init browser in a thread
    t = threading.Thread(target=init_sync, daemon=True)
    t.start()
    t.join(timeout=60)
    
    if not BROWSER:
        print('[-] Browser initialization failed')
        return
    
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'[+] Server ready on http://0.0.0.0:{port}/v1')
    server.serve_forever()

if __name__ == '__main__':
    start_server()
