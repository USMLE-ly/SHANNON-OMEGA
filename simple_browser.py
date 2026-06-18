#!/usr/bin/env python3
"""Simple browser remote control via screenshots + action endpoints"""
import asyncio, json, base64, os, sys, threading, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, unquote
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

BROWSER = GLOBAL_CTX = PAGE = None

def init_browser():
    global BROWSER, GLOBAL_CTX, PAGE
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async def init():
        global BROWSER, GLOBAL_CTX, PAGE
        p = await async_playwright().__aenter__()
        BROWSER = await p.chromium.launch(
            headless=False, args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        GLOBAL_CTX = await BROWSER.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        )
        stealth = Stealth(init_scripts_only=True)
        await stealth.apply_stealth_async(GLOBAL_CTX)
        PAGE = await GLOBAL_CTX.new_page()
        print('[+] Browser ready!')
    loop.run_until_complete(init())
    loop.close()

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try: return loop.run_until_complete(coro)
    finally: loop.close()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'''<!DOCTYPE html>
<html><head><title>Browser Control</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#0d0d1a;color:#e0e0e0;margin:0;padding:8px}
#screen{width:100%;max-width:1280px;border:1px solid #1da1f2;border-radius:6px;display:block;margin:4px 0}
.btn{background:#1a73e8;color:#fff;border:none;padding:10px 18px;border-radius:6px;cursor:pointer;margin:3px;font-size:14px}
.inp{background:#16213e;color:#fff;border:1px solid #2a3a6e;padding:10px;border-radius:6px;margin:3px;font-size:14px;width:60%}
#log{background:#000;padding:8px;border-radius:4px;font-size:12px;max-height:150px;overflow:auto;margin:4px 0}
</style></head><body>
<h2>Remote Browser Control</h2>
<div id="log">Ready</div>
<img id="screen" src="/screen">
<div style="margin:4px 0">
<input class="inp" id="url" value="https://www.quora.com/" style="width:70%">
<button class="btn" onclick="go()">Go</button>
</div>
<div>
<button class="btn" onclick="cmd('login')">Login</button>
<button class="btn" onclick="cmd('enter')">Enter</button>
<button class="btn" onclick="cmd('refresh')">Refresh</button>
</div>
<div>
<input class="inp" id="text" placeholder="Type text...">
<button class="btn" onclick="typeText()">Type</button>
</div>
<div id="status"></div>
<script>
function log(m){var l=document.getElementById('log');l.innerHTML=m+'<br>'+l.innerHTML}
function go(){var u=document.getElementById('url').value;log('Going to '+u);fetch('/go?url='+encodeURIComponent(u)).then(function(r){return r.text()}).then(function(t){log(t);document.getElementById('screen').src='/screen?'+Date.now()})}
function cmd(a){log('Action: '+a);fetch('/cmd?action='+a).then(function(r){return r.text()}).then(function(t){log(t);document.getElementById('screen').src='/screen?'+Date.now()})}
function typeText(){var t=document.getElementById('text').value;if(!t)return;fetch('/type?text='+encodeURIComponent(t)).then(function(r){return r.text()}).then(function(t){log(t);document.getElementById('text').value='';document.getElementById('screen').src='/screen?'+Date.now()})}
setInterval(function(){document.getElementById('screen').src='/screen?'+Date.now()},3000);
</script></body></html>''')
        elif path == '/screen':
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            if PAGE:
                try: self.wfile.write(run_async(PAGE.screenshot(full_page=False)))
                except: pass
        elif path == '/go':
            qs = parse_qs(self.path.split('?',1)[1] if '?' in self.path else '')
            url = qs.get('url', ['https://www.quora.com/'])[0]
            title = ''
            if PAGE:
                async def nav():
                    await PAGE.goto(url, wait_until='domcontentloaded', timeout=30000)
                    await PAGE.wait_for_timeout(5000)
                    return await PAGE.title()
                title = run_async(nav())
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(('Navigated: ' + str(title)).encode())
        elif path == '/cmd':
            qs = parse_qs(self.path.split('?',1)[1] if '?' in self.path else '')
            action = qs.get('action', [''])[0]
            result = ''
            if PAGE:
                if action == 'enter':
                    run_async(PAGE.keyboard.press('Enter'))
                    result = 'Enter pressed'
                elif action == 'refresh':
                    result = 'Refreshed'
                elif action == 'login':
                    result = run_async(PAGE.evaluate('''() => {
                        const btns = document.querySelectorAll('button, a, input[type="submit"]');
                        for(let b of btns) {
                            const t = b.textContent.toLowerCase();
                            if(t.includes('log in') || t.includes('sign in') || t.includes('login')) { b.click(); return b.textContent.trim(); }
                        }
                        for(let b of btns) {
                            if(b.textContent.toLowerCase().includes('accept')) { b.click(); return 'Accepted consent'; }
                        }
                        return 'No login button';
                    }'''))
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(result.encode())
        elif path == '/type':
            qs = parse_qs(self.path.split('?',1)[1] if '?' in self.path else '')
            text = unquote(qs.get('text', [''])[0])
            if PAGE and text:
                run_async(PAGE.keyboard.type(text, delay=10))
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(('Typed: ' + text[:30]).encode())
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, *args): pass

t = threading.Thread(target=init_browser, daemon=True)
t.start()
time.sleep(2)

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8082
server = HTTPServer(('0.0.0.0', port), Handler)
print(f'[+] Server: http://0.0.0.0:{port}')
server.serve_forever()
