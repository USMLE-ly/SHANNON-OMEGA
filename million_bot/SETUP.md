# SHANNON-Ω Million Dollar Bot — Setup Guide

## What You Need

### Option A: 2Captcha ($10) — Fully Automated
1. Go to https://2captcha.com and create an account
2. Add funds ($10 = 10,000 CAPTCHA solves)
3. Get your API key from https://2captcha.com/setting
4. Run:
```bash
export TWOCAPTCHA_KEY='your_2captcha_api_key'
python3 media-tools/scripts/lib/ig_creator.py full "Vaulex Watches" "vaulex_watches"
```

### Option B: Manual Account (Free)
1. On your phone, install Instagram
2. Sign up with your phone number (not email — phone bypasses reCAPTCHA)
3. Username: `vaulex_watches` (or similar)
4. Then run the bot:
```bash
./million_bot/start.sh login vaulex_watches your_password
./million_bot/start.sh grow vaulex_watches your_password 50
```

## How It Works

```
IG Creator with 2Captcha Extension:
─────────────────────────────────────
1. Playwright launches Chromium WITH 2Captcha extension loaded
2. The extension auto-detects reCAPTCHA v3 Enterprise on the challenge page
3. Extension sends the challenge to 2Captcha's API
4. 2Captcha solves it using residential proxy pool (Google trusts their IPs)
5. Extension injects the token → Instagram accepts it → Account created!
6. Verification email arrives → Auto-extracted → Account verified
7. Bot engine takes over → Follows, likes, grows

Without 2Captcha:
─────────────────────────────────────
Instagram's reCAPTCHA v3 Enterprise blocks ALL automated signup attempts.
Google has blacklisted datacenter IPs for their API.
35+ open-source bypass repos tested — all fail on Instagram.
```

## Bot Growth Strategy

After account is created:
```bash
# Phase 1: Follow competitors' followers (300/day)
./million_bot/start.sh grow user pass 10

# Phase 2: Like from hashtags (500/day)
python3 million_bot/scripts/bot_engine.py --login user pass --like 50

# Phase 3: Content strategy via SHANNON-Ω
./million_bot/start.sh api "Write 10 viral captions for luxury watch brand"
```
