# reCAPTCHA Bypass Research — SHANNON-Ω

## reCAPTCHA v3 Enterprise — Instagram Signup

### Found Sitekey
```
6LdktRgnAAAAAFQ6icovYI2-masYLFjEFyzQzpix
```
Instagram uses Facebook's domain (`fbsbx.com:443`) for reCAPTCHA.

### Methods Tested

| Method | Status | Notes |
|---|---|---|
| Audio solver (v2 iframe) | 🔄 Works if v2 challenge appears | v2 iframe sometimes loads |
| Direct API (x404xx approach) | ❌ Blocked by Google | IP needs better reputation |
| 2Captcha API (paid) | ✅ Works reliably | ~$1/1000 solves, set `TWOCAPTCHA_KEY` |
| Capsolver API (paid) | ✅ Alternative | https://capsolver.com |

### How to Use 2Captcha
```bash
export TWOCAPTCHA_KEY="your_2captcha_api_key"
python3 media-tools/scripts/lib/ig_creator.py full "Name" "username"
# Or via v3_solver:
python3 -c "
from v3_solver import V3CaptchaSolver
solver = V3CaptchaSolver(twocaptcha_key='YOUR_KEY', verbose=True)
token = solver.solve_token('6LdktRgnAAAAAFQ6icovYI2-masYLFjEFyzQzpix',
    'https://www.instagram.com/accounts/emailsignup/?next=',
    page_action='signup', use_twocaptcha=True)
print(f'Token: {token}')
"
```

### Repos Analyzed
- **x404xx/Recaptcha-V3** — Direct API solver (free, IP-dependent)
- **sarperavci/GoogleRecaptchaBypass** — v2 audio via DrissionPage
- **ecthros/uncaptcha2** — v2 audio via pyautogui
- **geohot/lolrecaptcha** — v2 audio via Go
- **2captcha/2captcha-python** — Official 2Captcha Python lib
- **recaptchaUser/ReCaptcha-V3-Solver** — Capsolver wrapper

### Architecture
```
IG Creator → Submit Form → Challenge Page → Audio Solver (v2 iframe)
                                           → Direct API (free)
                                           → 2Captcha (paid, reliable)
                                           → Next button → Verify Email → Done
```
