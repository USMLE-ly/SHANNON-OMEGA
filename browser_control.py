#!/usr/bin/env python3
"""Web-based browser control - view and interact with a Playwright browser from your phone"""
import asyncio, json, base64, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

BROWSER = None
CONTEXT = None
PAGE = None
LOCK = asyncio.Lock()

async def init_browser():
    global BROWSER, CONTEXT, PAGE
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
    PAGE = await CONTEXT.new_page()
    print('[+] Browser ready!')

async def screenshot():
    async with LOCK:
        if PAGE:
            await PAGE.screenshot(path='/tmp/browser_view.png', full_page=False)
            with open('/tmp/browser_view.png', 'rb') as f:
                return base64.b64encode(f.read()).decode()
    return ''

async def navigate(url):
    async with LOCK:
        if PAGE:
            await PAGE.goto(url, wait_until='domcontentloaded', timeout=30000)
            return await PAGE.title()
    return ''

async def click(x, y):
    async with LOCK:
        if PAGE:
            await PAGE.mouse.click(x, y)
            await asyncio.sleep(1)
            return True
    return False

async def type_text(text):
    async with LOCK:
        if PAGE:
            await PAGE.keyboard.type(text, delay=10)
            return True
    return False

async def press_key(key):
    async with LOCK:
        if PAGE:
            await PAGE.keyboard.press(key)
            return True
    return False

async def evaluate(js):
    async with LOCK:
        if PAGE:
            return await PAGE.evaluate(js)
    return ''

# Initialize browser on startup
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(init_browser())
loop.close()

# HTTP Handler
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        query = {}
        if '?' in path:
            path, qs = path.split('?', 1)
            for pair in qs.split('&'):
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    query[k] = v
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = '''<!DOCTYPE html>
<html><head><title>Browser Control</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:monospace;background:#111;color:#eee;margin:0;padding:10px}
img{width:100%;max-width:1280px;border:1px solid #444;border-radius:4px}
.btn{background:#1a73e8;color:#fff;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;margin:2px}
.inp{background:#222;color:#fff;border:1px solid #444;padding:8px;width:300px;border-radius:4px;margin:2px}
#log{background:#000;padding:8px;font-size:12px;max-height:200px;overflow:auto}
</style></head><body>
<h2>🖥 Browser Remote Control</h2>
<div id="log">Ready</div>
<img id="screen" src="/screenshot">
<div style="margin:8px 0">
<input class="inp" id="url" value="https://www.quora.com/" style="width:70%">
<button class="btn" onclick="navigate()">Go</button>
</div>
<div>
<button class="btn" onclick="send('click_login')">🔑 Click Login</button>
<button class="btn" onclick="send('enter')">⏎ Enter</button>
<button class="btn" onclick="send('screenshot')">📷 Refresh</button>
</div>
<div style="margin:4px 0">
<input class="inp" id="text" placeholder="Type text..." style="width:50%">
<button class="btn" onclick="typeText()">⌨ Type</button>
</div>
<div id="result"></div>
<script>
function log(m){document.getElementById('log').innerHTML=m+'<br>'+document.getElementById('log').innerHTML}
function send(action){
    fetch('/action?cmd='+action).then(r=>r.text()).then(t=>{log(t);document.getElementById('screen').src='/screenshot?'+Date.now()})
}
function navigate(){
    const u=document.getElementById('url').value;
    fetch('/action?cmd=navigate&url='+encodeURIComponent(u)).then(r=>r.text()).then(t=>{log(t);document.getElementById('screen').src='/screenshot?'+Date.now()})
}
function typeText(){
    const t=document.getElementById('text').value;
    fetch('/action?cmd=type&text='+encodeURIComponent(t)).then(r=>r.text()).then(t=>{log(t);document.getElementById('text').value=''})
}
setInterval(()=>{document.getElementById('screen').src='/screenshot?'+Date.now()},5000);
</script></body></html>'''
            self.wfile.write(html.encode())
        elif path == '/screenshot':
            loop2 = asyncio.new_event_loop()
            asyncio.set_event_loop(loop2)
            img = loop2.run_until_complete(screenshot())
            loop2.close()
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(base64.b64decode(img) if img else b'')
        elif path.startswith('/action'):
            cmd = query.get('cmd', '')
            loop2 = asyncio.new_event_loop()
            asyncio.set_event_loop(loop2)
            result = ''
            if cmd == 'screenshot':
                result = 'Refreshed'
            elif cmd == 'navigate':
                url = query.get('url', 'https://www.quora.com/')
                title = loop2.run_until_complete(navigate(url))
                result = f'Navigated: {title}'
            elif cmd == 'click_login':
                # Try clicking login button
                try:
                    loop2.run_until_complete(PAGE.evaluate('''() => {
                        const btns = document.querySelectorAll('button, a');
                        for(let b of btns){
                            if(b.textContent.match(/log.?in|sign.?in|log.?out/i)){
                                b.click(); return 'Clicked: '+b.textContent;
                            }
                        }
                        return 'No login button found';
                    }'''))
                except: pass
                result = 'Clicked login'
            elif cmd == 'enter':
                loop2.run_until_complete(press_key('Enter'))
                result = 'Enter pressed'
            elif cmd.startswith('type='):
                text = cmd.split('=', 1)[1]
                loop2.run_until_complete(type_text(text))
                result = f'Typed: {text[:30]}'
            elif cmd == 'type':
                text = query.get('text', '')
                if text:
                    loop2.run_until_complete(type_text(text))
                    result = f'Typed: {text[:30]}'
            loop2.close()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(result.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, *args):
        pass

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8082
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'[+] Browser Control: http://0.0.0.0:{port}')
    server.serve_forever()
