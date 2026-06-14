"""
reCAPTCHA v3 Enterprise Solver — Instagram Signup
Two approaches:
1. Direct API (free, IP-dependent)
2. 2Captcha API (paid, ~$1/1000 solves, reliable)

Usage:
    # Free API (may not work on all IPs)
    solver = V3CaptchaSolver()
    token = solver.solve_token(sitekey, page_url)
    
    # 2Captcha (needs API key)
    solver = V3CaptchaSolver(twocaptcha_key="YOUR_KEY")
    token = solver.solve_token(sitekey, page_url, use_twocaptcha=True)
"""
import requests, re, base64, random, os

class V3CaptchaSolver:
    """Combined reCAPTCHA v3/v2 Enterprise solver."""
    
    def __init__(self, twocaptcha_key=None, verbose=False):
        self.verbose = verbose
        self.twocaptcha_key = twocaptcha_key or os.environ.get("TWOCAPTCHA_KEY", "")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
    
    def log(self, msg):
        if self.verbose:
            print(f'[V3] {msg}')
    
    def extract_sitekey_from_page(self, page):
        """Extract sitekey from a Playwright page."""
        try:
            sitekey = page.evaluate("""() => {
                const iframes = document.querySelectorAll('iframe');
                for (let f of iframes) {
                    const src = f.src || '';
                    const match = src.match(/[?&]k=([^&]+)/);
                    if (match && src.includes('recaptcha')) return match[1];
                }
                return null;
            }""")
            if sitekey:
                self.log(f'Sitekey from iframe: {sitekey}')
                return sitekey
            html = page.content()
            match = re.search(r'[?&]k=([^&"\']+)', html)
            if match:
                self.log(f'Sitekey from HTML: {match.group(1)}')
                return match.group(1)
        except Exception as e:
            self.log(f'Extract error: {e}')
        return None
    
    def solve_token_free(self, sitekey, page_url, page_action="signup"):
        """Free direct API approach. May not work on all IPs."""
        # Instagram uses Facebook's domain for reCAPTCHA
        # co = base64("https://www.fbsbx.com:443") with dots for = padding
        co_value = "aHR0cHM6Ly93d3cuZmJzYnguY29tOjQ0Mw.."
        
        for api_type in ["enterprise"]:
            self.log(f'Trying {api_type}...')
            anchor_url = (
                f"https://www.google.com/recaptcha/{api_type}/anchor"
                f"?ar=1&k={sitekey}&co={co_value}&hl=en&size=invisible"
                f"&cb={random.random()}"
            )
            
            try:
                r = self.session.get(anchor_url, timeout=15)
                match = re.search(r'recaptcha-token" value="(.*?)"', r.text)
                if match:
                    anchor_token = match.group(1)
                    payload = f"reason=q&c={anchor_token}&k={sitekey}&co={co_value}"
                    r2 = self.session.post(
                        f"https://www.google.com/recaptcha/{api_type}/reload",
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        params={"k": sitekey},
                        data=payload,
                        timeout=15
                    )
                    match2 = re.search(r'"rresp","(.*?)"', r2.text)
                    if match2:
                        token = match2.group(1)
                        self.log('Token obtained via direct API')
                        return token
                    self.log(f'No token in reload: {r2.text[:100]}')
                else:
                    self.log(f'No anchor: {r.text[:80]}')
            except Exception as e:
                self.log(f'Error: {e}')
        return None
    
    def solve_token_2captcha(self, sitekey, page_url, page_action="signup"):
        """Paid 2Captcha API approach."""
        if not self.twocaptcha_key:
            self.log('No 2Captcha API key set')
            return None
        
        try:
            from twocaptcha import TwoCaptcha
            solver = TwoCaptcha(self.twocaptcha_key)
            
            self.log('Sending to 2Captcha...')
            result = solver.recaptcha(
                sitekey=sitekey,
                url=page_url,
                version='v3',
                enterprise=1,
                action=page_action,
                score=0.8,
            )
            
            if result and 'code' in result:
                self.log(f'Token from 2Captcha: {result["code"][:50]}...')
                return result['code']
            self.log(f'2Captcha failed: {result}')
            return None
            
        except ImportError:
            self.log('2captcha-python not installed')
            return None
        except Exception as e:
            self.log(f'2Captcha error: {e}')
            return None
    
    def solve_token(self, sitekey, page_url, page_action="signup", use_twocaptcha=False):
        """Get a reCAPTCHA token. 
        
        Args:
            sitekey: The reCAPTCHA sitekey
            page_url: Full URL of the page
            page_action: Action name (e.g. 'signup')
            use_twocaptcha: Force 2Captcha usage
            
        Returns:
            Token string or None
        """
        if use_twocaptcha:
            return self.solve_token_2captcha(sitekey, page_url, page_action)
        
        token = self.solve_token_free(sitekey, page_url, page_action)
        if token:
            return token
        
        self.log('Free API failed, falling back to 2Captcha...')
        return self.solve_token_2captcha(sitekey, page_url, page_action)
    
    def inject_token(self, page, token):
        """Inject a reCAPTCHA token into the page context."""
        self.log('Injecting token into page...')
        try:
            page.evaluate("""(token) => {
                // Try to set on the response textarea
                const ta = document.querySelector('#g-recaptcha-response, .g-recaptcha-response');
                if (ta) ta.value = token;
                
                // Try to trigger callback
                if (window.___grecaptcha_cfg) {
                    for (let key in window.___grecaptcha_cfg) {
                        try {
                            const cfg = window.___grecaptcha_cfg[key];
                            if (cfg && cfg.callback) cfg.callback(token);
                        } catch(e) {}
                    }
                }
                
                // Try grecaptcha
                if (typeof grecaptcha !== 'undefined') {
                    try {
                        if (grecaptcha.enterprise) {
                            grecaptcha.enterprise.ready(() => {
                                if (grecaptcha.enterprise.execute) {
                                    const orig = grecaptcha.enterprise.execute;
                                    grecaptcha.enterprise.execute = () => Promise.resolve(token);
                                }
                            });
                        }
                    } catch(e) {}
                }
            }""", token)
            return True
        except Exception as e:
            self.log(f'Inject error: {e}')
            return False
