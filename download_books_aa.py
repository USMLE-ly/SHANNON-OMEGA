#!/usr/bin/env python3
"""
Download the first PDF for each ISBN from Anna's Archive.
Aggregates Z-Library, Sci-Hub, LibGen, and more.
==================================================================
USAGE:
    python3 download_books_aa.py

Requires: pip install requests beautifulsoup4

If hitting Cloudflare/ParkLogic anti-bot:
    pip install cloudscraper
    Then set USE_CLOUDSCRAPER = True below, or use the companion
    script download_books_aa_scraper.py
==================================================================
"""

import sys, time, json, re
from pathlib import Path

# --- Toggle ---
USE_CLOUDSCRAPER = False  # Set True if requests gets blocked

if USE_CLOUDSCRAPER:
    import cloudscraper
    _http = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
else:
    import requests
    _http = requests

# --- Configuration ---
ISBNS = [
    "9781350193901",
    "9781501382567",
    "9781472532664",
    "9781607053552",
    "9781854799975",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}
DELAY = 4
TIMEOUT = 30
OUTPUT_DIR = Path("aa_books")
OUTPUT_DIR.mkdir(exist_ok=True)

# Anna's Archive mirrors (some resolve where others don't)
DOMAINS = [
    "https://annasarchive.org",
    "https://annas-archive.org",
    "https://annasarchive.li",
    "https://annas-archive.gs",
]

# ---------------------------------------------------------------------------

def search_isbn(isbn):
    """Search multiple AA mirrors for an ISBN, return the first md5 found."""
    for domain in DOMAINS:
        url = f"{domain}/search?q={isbn}&format=json&limit=1"
        try:
            r = _http.get(url, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code != 200:
                continue
            # Try JSON
            try:
                data = r.json()
            except (json.JSONDecodeError, ValueError):
                # Anti-bot page — try to extract md5 from HTML/JS
                md5s = re.findall(r'"md5"\s*:\s*"([a-fA-F0-9]{32})"', r.text)
                if md5s:
                    print(f"  [+] MD5 extracted from {domain}: {md5s[0]}")
                    return md5s[0]
                # Also try plain URL-embedded md5s
                md5s = re.findall(r'md5=([a-fA-F0-9]{32})', r.text)
                if md5s:
                    print(f"  [+] MD5 extracted (url) from {domain}: {md5s[0]}")
                    return md5s[0]
                continue
            results = data.get("results", [])
            if results:
                md5 = results[0].get("md5") or results[0].get("id", "")
                if md5:
                    print(f"  [+] Found MD5 on {domain}: {md5}")
                    return md5
        except Exception as e:
            continue
    return None


def get_download_url(md5):
    """Use fast_download API across mirrors."""
    for domain in DOMAINS:
        url = f"{domain}/dyn/api/fast_download.json?md5={md5}"
        try:
            r = _http.get(url, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 200:
                try:
                    data = r.json()
                except (json.JSONDecodeError, ValueError):
                    continue
                dl = data.get("download_url") or data.get("url")
                if dl:
                    print(f"  [+] Download URL obtained")
                    return dl
        except Exception:
            continue
    return None


def download_file(url, filename):
    """Stream the file to disk."""
    try:
        r = _http.get(url, headers=HEADERS, stream=True, timeout=300)
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  [!] Download failed: {e}")
        return False


def main():
    print("=" * 60)
    print("  Anna's Archive — ISBN Book Downloader")
    f"  Mode: {'cloudscraper' if USE_CLOUDSCRAPER else 'requests'}"
    print("=" * 60)

    results = {"found": 0, "failed": 0}

    for isbn in ISBNS:
        print(f"\n── ISBN {isbn} ──")
        md5 = search_isbn(isbn)
        if not md5:
            print("  [✗] Not found on any reachable AA mirror")
            results["failed"] += 1
            time.sleep(DELAY)
            continue

        time.sleep(DELAY)
        dl_url = get_download_url(md5)
        if not dl_url:
            print("  [✗] Download URL unavailable")
            results["failed"] += 1
            continue

        out_path = OUTPUT_DIR / f"{isbn}.pdf"
        print(f"  ↓ Downloading {out_path.name} ...")
        if download_file(dl_url, out_path):
            size = out_path.stat().st_size
            print(f"  [✓] Saved — {size/1024/1024:.1f} MB → {out_path}")
            results["found"] += 1
        else:
            results["failed"] += 1

        time.sleep(DELAY)

    print(f"\n{'='*60}")
    print(f"  Done. Downloaded: {results['found']}  Failed: {results['failed']}")
    if results["found"] == 0:
        print(f"\n  ⚠ No books were downloaded from this network.")
        print(f"  Anna's Archive requires a network without DNS/anti-bot blocks.")
        print(f"  Try running this on a VPS or from a different machine.")
        print(f"  Or: USE_CLOUDSCRAPER=True  (pip install cloudscraper)")
        print(f"  Or: python3 download_books_aa_scraper.py")
    print(f"  Output: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
