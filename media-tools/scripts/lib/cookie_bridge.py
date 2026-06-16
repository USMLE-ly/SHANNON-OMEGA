"""
SHANNON-Ω Cookie Bridge — Cookie-Editor import + Tampermonkey automation
Injects exported cookies into Playwright sessions. No login needed.
"""
import os, json, time, random
from typing import Optional

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_cookie_file(filepath: str) -> list:
    """Load cookies exported from Cookie-Editor extension."""
    with open(filepath) as f:
        data = json.load(f)
    
    # Cookie-Editor exports as array of cookie objects
    # Format: [{"name":"...","value":"...","domain":"...","path":"/","httpOnly":false,"secure":true,...}]
    if isinstance(data, dict) and "cookies" in data:
        cookies = data["cookies"]
    elif isinstance(data, list):
        cookies = data
    else:
        raise ValueError(f"Unknown cookie format. Expected list or dict with 'cookies' key")
    
    return cookies

def format_for_playwright(cookies: list) -> list:
    """Convert Cookie-Editor format to Playwright add_cookies format."""
    pw_cookies = []
    for c in cookies:
        entry = {
            "name": c.get("name", ""),
            "value": c.get("value", ""),
            "domain": c.get("domain", ""),
            "path": c.get("path", "/"),
        }
        if "httpOnly" in c:
            entry["httpOnly"] = c["httpOnly"]
        if "secure" in c:
            entry["secure"] = c["secure"]
        if "sameSite" in c:
            entry["sameSite"] = c["sameSite"]
        if "expirationDate" in c:
            entry["expires"] = c["expirationDate"]
        pw_cookies.append(entry)
    return pw_cookies

def inject_into_playwright(context, cookie_file: str) -> bool:
    """Load cookies from file and inject into Playwright browser context."""
    if not os.path.exists(cookie_file):
        print(f"❌ Cookie file not found: {cookie_file}")
        return False
    
    cookies = load_cookie_file(cookie_file)
    pw_cookies = format_for_playwright(cookies)
    
    context.add_cookies(pw_cookies)
    
    # Log success with session info
    domains = set(c["domain"] for c in cookies if "domain" in c)
    print(f"✅ Injected {len(pw_cookies)} cookies for domains: {', '.join(list(domains)[:5])}")
    return True

def get_session_age(cookie_file: str) -> Optional[int]:
    """Check how old the cookie export is (in hours)."""
    if not os.path.exists(cookie_file):
        return None
    age = time.time() - os.path.getmtime(cookie_file)
    return int(age / 3600)  # hours

def verify_session(context, test_url: str) -> bool:
    """Verify cookies are still valid by loading a page."""
    from playwright.sync_api import sync_playwright
    
    page = context.new_page()
    try:
        page.goto(test_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        
        # Check if we get a login page or authenticated page
        if "login" in page.url.lower() or "signin" in page.url.lower() or "auth" in page.url.lower():
            print(f"⚠️ Session expired — redirected to: {page.url[:60]}")
            return False
        
        print(f"✅ Session valid — on: {page.url[:60]}")
        return True
    except Exception as e:
        print(f"❌ Session check failed: {e}")
        return False
    finally:
        page.close()


# ─── TAMPERMONKEY USERSCRIPT GENERATION ──────────────────────────

TAMPERMONKEY_SCRIPT = """// ==UserScript==
// @name         SHANNON-Ω Cookie Relay
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Auto-export cookies to SHANNON-Ω server for automation
// @author       ZORG-Ω
// @match        https://*.quora.com/*
// @match        https://*.twitter.com/*
// @match        https://*.x.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_cookie
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    const SERVER_URL = 'http://YOUR_SERVER_IP:7777/cookies';
    const INTERVAL_MS = 6 * 60 * 60 * 1000; // Every 6 hours

    function getCookiesForDomain() {
        // Try using document.cookie first (limited but works for many sites)
        var cookies = document.cookie.split(';').map(function(c) {
            var parts = c.trim().split('=');
            return {name: parts[0], value: parts.slice(1).join('=')};
        });
        return cookies;
    }

    function sendCookies() {
        var cookies = getCookiesForDomain();
        var payload = {
            url: window.location.hostname,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            cookies: cookies,
            localStorage: Object.entries(localStorage).map(function(e) {
                return {name: e[0], value: e[1]};
            })
        };

        GM_xmlhttpRequest({
            method: 'POST',
            url: SERVER_URL,
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(payload),
            onload: function(rsp) {
                console.log('[SHANNON-Ω] Cookies relayed: ' + rsp.status);
            },
            onerror: function(err) {
                console.log('[SHANNON-Ω] Relay failed: ' + err);
            }
        });
    }

    // Send on page load + every 6 hours
    setTimeout(sendCookies, 5000);  // First send after 5s
    setInterval(sendCookies, INTERVAL_MS);

    console.log('[SHANNON-Ω] Cookie Relay active — auto-sending every 6h');
})();"""

def generate_userscript(server_ip: str = "localhost", server_port: int = 7777) -> str:
    """Generate a Tampermonkey userscript for cookie relay."""
    return TAMPERMONKEY_SCRIPT.replace("YOUR_SERVER_IP:7777", f"{server_ip}:{server_port}")

def save_userscript(server_ip: str = "localhost", server_port: int = 7777, 
                   output_path: str = None):
    """Save the userscript to a file."""
    if output_path is None:
        output_path = os.path.join(BASE, "omega", "shannon_cookie_relay.user.js")
    
    script = generate_userscript(server_ip, server_port)
    with open(output_path, "w") as f:
        f.write(script)
    print(f"✅ Userscript saved to {output_path}")
    print(f"   Install in Tampermonkey → Create new script → Paste contents → Save")
    return output_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        ip = sys.argv[2] if len(sys.argv) > 2 else "localhost"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 7777
        save_userscript(ip, port)
    elif len(sys.argv) > 1 and sys.argv[1] == "inject":
        cookie_file = sys.argv[2] if len(sys.argv) > 2 else "omega/quora_cookies.json"
        print(f"Load these cookies in your script:")
        cookies = load_cookie_file(cookie_file)
        print(f"  {len(cookies)} cookies loaded")
        print(f"  Domains: {set(c['domain'] for c in cookies if 'domain' in c)}")
    elif len(sys.argv) > 1 and sys.argv[1] == "check":
        cookie_file = sys.argv[2] if len(sys.argv) > 2 else "omega/quora_cookies.json"
        age = get_session_age(cookie_file)
        if age is not None:
            print(f"Session age: {age} hours ({age/24:.1f} days)")
            print(f"Still valid within ~7 days: {age < 168}")
        else:
            print("No cookie file found")
    else:
        print("SHANNON-Ω Cookie Bridge")
        print("")
        print("Commands:")
        print("  generate [ip] [port]   Generate Tampermonkey userscript")
        print("  inject <file>          Preview cookie file contents")
        print("  check <file>           Check session age")
        print("")
        print("WORKFLOW:")
        print("  1. User logs into Quora/Twitter from home browser")
        print("  2. Uses Cookie-Editor extension → Export cookies as JSON")
        print("  3. Sends JSON file to omega/quora_cookies.json (or twitter_cookies.json)")
        print("  4. Run: python3 automation_engine.py quora (uses cookies, no login)")
