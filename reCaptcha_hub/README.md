# reCAPTCHA Bypass Research

## Repos cloned and analyzed

| Repo | Approach | Status |
|---|---|---|
| [GoogleRecaptchaBypass](https://github.com/sarperavci/GoogleRecaptchaBypass) | Audio challenge via DrissionPage + Google Speech | v2 only |
| [uncaptcha2](https://github.com/ecthros/uncaptcha2) | Audio via pyautogui + speech_recognition | v2 only, brittle |
| [lolrecaptcha](https://github.com/geohot/lolrecaptcha) | Audio via Go + speech-to-text | v2 only |
| [recaptcha-phish](https://github.com/JohnHammond/recaptcha-phish) | Phish token from real user | Social eng, not automated |
| [recaptcha-cracker](https://github.com/nocturnaltortoise/recaptcha-cracker) | ML + semantic similarity | Research project |
| [recaptcha-v3](https://github.com/abinnovision/recaptcha-v3) | TypeScript library for implementing v3 | Not for bypassing |

## The Instagram Problem

Instagram uses **reCAPTCHA v3 Enterprise** (invisible, score-based). There is no iframe/challenge to interact with. Bypass requires:

1. **Residential proxies** — clean IP reputation
2. **Stealth browser fingerprint** — Playwright + manual patches (implemented)
3. **CAPTCHA solving API** — 2Captcha, Capsolver ($1-2/1k solves)
4. **Manual phone verification** — via SMS services

## What We Implemented

- `media-tools/scripts/lib/recaptcha_solver.py` — Playwright-based reCAPTCHA v2 audio solver
- `media-tools/scripts/lib/ig_creator.py` — Full Instagram signup with stealth + challenge handling
