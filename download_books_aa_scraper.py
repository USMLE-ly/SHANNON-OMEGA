#!/usr/bin/env python3
"""
Cloudscraper variant — bypasses Cloudflare/ParkLogic anti-bot protection.
Run this if download_books_aa.py gets blocked.

Usage: python3 download_books_aa_scraper.py
"""
import cloudscraper, time, re, json
from pathlib import Path

ISBNS = [
    "9781350193901", "9781501382567", "9781472532664",
    "9781607053552", "9781854799975",
]
DOMAINS = [
    "https://annasarchive.org",
    "https://annas-archive.org",
    "https://annasarchive.li",
    "https://annas-archive.gs",
]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}
DELAY = 5
TIMEOUT = 60
OUTPUT_DIR = Path("aa_books")
OUTPUT_DIR.mkdir(exist_ok=True)

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

def search_isbn(isbn):
    for domain in DOMAINS:
        url = f"{domain}/search?q={isbn}&format=json&limit=1"
        try:
            r = scraper.get(url, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code != 200:
                continue
            try:
                data = r.json()
                results = data.get("results", [])
                if results:
                    md5 = results[0].get("md5") or results[0].get("id", "")
                    if md5:
                        print(f"  [+] Found MD5 on {domain}: {md5}")
                        return md5
            except (json.JSONDecodeError, ValueError):
                md5s = re.findall(r'"md5"\s*:\s*"([a-fA-F0-9]{32})"', r.text)
                if md5s:
                    print(f"  [+] MD5 extracted from {domain}: {md5s[0]}")
                    return md5s[0]
                md5s = re.findall(r'md5=([a-fA-F0-9]{32})', r.text)
                if md5s:
                    print(f"  [+] MD5 (url) from {domain}: {md5s[0]}")
                    return md5s[0]
        except Exception:
            continue
    return None

def get_download_url(md5):
    for domain in DOMAINS:
        url = f"{domain}/dyn/api/fast_download.json?md5={md5}"
        try:
            r = scraper.get(url, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 200:
                try:
                    data = r.json()
                    dl = data.get("download_url") or data.get("url")
                    if dl:
                        return dl
                except (json.JSONDecodeError, ValueError):
                    # Sometimes the download URL is in the HTML
                    for m in re.finditer(r'(https?://[^"\']+\.(?:pdf|epub|zip))', r.text):
                        return m.group(1)
        except Exception:
            continue
    return None

def main():
    print("=" * 60)
    print("  Anna's Archive Book Downloader — Cloudscraper Mode")
    print("=" * 60)
    for isbn in ISBNS:
        print(f"\n── ISBN {isbn} ──")
        md5 = search_isbn(isbn)
        if not md5:
            print("  [✗] Not found")
            time.sleep(DELAY)
            continue
        time.sleep(DELAY)
        dl = get_download_url(md5)
        if not dl:
            print("  [✗] No download URL")
            continue
        out = OUTPUT_DIR / f"{isbn}.pdf"
        print(f"  ↓ {out.name}")
        try:
            r = scraper.get(dl, headers=HEADERS, stream=True, timeout=300)
            r.raise_for_status()
            with open(out, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            print(f"  [✓] Done — {out.stat().st_size/1024/1024:.1f} MB → {out}")
        except Exception as e:
            print(f"  [✗] {e}")
        time.sleep(DELAY)
    print(f"\nOutput: {OUTPUT_DIR.resolve()}")

if __name__ == "__main__":
    main()
