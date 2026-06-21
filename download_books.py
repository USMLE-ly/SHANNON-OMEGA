#!/usr/bin/env python3
"""
SHANNON-Ω Book Downloader
=========================
Downloads books from Library Genesis / Anna's Archive by ISBN.
Tries multiple mirrors with fallback logic.

Usage:
  python3 download_books.py [isbn1 isbn2 ...]
  python3 download_books.py --search "fashion design"
  python3 download_books.py --list
  
Dependencies: requests, beautifulsoup4, lxml
"""

import requests
import re
import time
import sys
import json
import random
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- ISBNs for Fashion Books ---
DEFAULT_ISBNS = [
    ("9781350193901", "The Fashion Designer's Sketchbook"),
    ("9781501382567", "A Guide to Fashion Sewing"),
    ("9781472532664", "Fashion Sewing"),
    ("9781607053552", "A Field Guide to Fabric Design"),
    ("9781854799975", "The Art of Zandra Rhodes"),
]

# Mirrors to try (ordered by reliability)
SEARCH_MIRRORS = [
    "https://libgen.ee/search.php",
    "https://libgen.li/search.php",
    "https://libgen.lc/search.php",
    "https://libgen.gs/search.php",
]

DOWNLOAD_MIRRORS = [
    ("https://libgen.li/ads.php?md5=", "libgen.li"),
    ("https://libgen.ee/ads.php?md5=", "libgen.ee"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
TIMEOUT = 30
DELAY = 5

OUTPUT_DIR = Path("downloaded_books")
OUTPUT_DIR.mkdir(exist_ok=True)

def try_all_searches(isbn):
    """Search all mirrors for an ISBN and return the first md5 found."""
    for search_url in SEARCH_MIRRORS:
        try:
            resp = requests.get(
                search_url,
                params={"req": isbn},
                headers=HEADERS,
                timeout=TIMEOUT
            )
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "lxml")
            
            # Try multiple link patterns
            for a in soup.find_all("a", href=True):
                href = a["href"]
                m = re.search(r'md5=([a-fA-F0-9]{32})', href)
                if m:
                    print(f"  [✓] Found MD5 on {search_url}: {m.group(1)}")
                    return m.group(1)
        except Exception as e:
            print(f"  [ ] {search_url} failed: {type(e).__name__}")
            continue
    return None

def try_direct_download(md5):
    """Try to get a direct PDF download URL for an MD5 hash."""
    for mirror_url, name in DOWNLOAD_MIRRORS:
        try:
            url = f"{mirror_url}{md5}"
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "lxml")
            
            # Look for download links
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.endswith(".pdf") or "get.php" in href or "download" in href.lower():
                    dl_url = urljoin(url, href)
                    print(f"  [✓] Found download on {name}: {dl_url[:80]}...")
                    return dl_url
            
            # Check for img download button
            for img in soup.find_all("img"):
                alt = img.get("alt", "")
                if "download" in alt.lower():
                    parent = img.find_parent("a")
                    if parent and parent.get("href"):
                        dl_url = urljoin(url, parent["href"])
                        return dl_url
        except Exception as e:
            print(f"  [ ] {name} download failed: {type(e).__name__}")
            continue
    
    # Fallback: try direct libgen links
    fallbacks = [
        f"https://libgen.li/get.php?md5={md5}",
        f"https://libgen.ee/get.php?md5={md5}",
        f"http://libgen.la/get.php?md5={md5}",
    ]
    for url in fallbacks:
        try:
            r = requests.head(url, headers=HEADERS, timeout=15, allow_redirects=True)
            if r.status_code == 200:
                print(f"  [✓] Fallback download: {url}")
                return url
        except:
            continue
    
    return None

def download_file(url, filename):
    """Download a file with progress indicator."""
    print(f"  ↓ Downloading {Path(filename).name} ...")
    try:
        resp = requests.get(url, headers=HEADERS, stream=True, timeout=120)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(filename, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    pct = int(100 * downloaded / total)
                    if pct % 25 == 0 and pct > 0:
                        print(f"    ... {pct}%")
        return True
    except Exception as e:
        print(f"  [✗] Download error: {e}")
        return False

def main():
    isbns = DEFAULT_ISBNS
    
    # Parse args
    args = sys.argv[1:]
    if args and args[0] == "--search":
        query = " ".join(args[1:])
        print(f"Searching for: {query}")
        for url in SEARCH_MIRRORS:
            try:
                r = requests.get(url, params={"req": query}, headers=HEADERS, timeout=30)
                soup = BeautifulSoup(r.text, "lxml")
                links = soup.find_all("a", href=re.compile(r"md5=[a-fA-F0-9]{32}"))
                print(f"  {url}: {len(links)} results")
                for a in links[:5]:
                    print(f"    → {a.get('href', '')}")
            except Exception as e:
                print(f"  {url}: {type(e).__name__}")
        return
    elif args and args[0] == "--list":
        print("Available books:")
        for isbn, title in DEFAULT_ISBNS:
            print(f"  {isbn} — {title}")
        return
    elif args and args[0].isdigit():
        isbns = [(args[0], f"book_{args[0]}")]
    
    results = {"found": [], "not_found": []}
    
    for isbn, title in isbns:
        print(f"\n{'='*60}")
        print(f"📖 {title}")
        print(f"   ISBN: {isbn}")
        print(f"{'='*60}")
        
        md5 = try_all_searches(isbn)
        if not md5:
            print(f"  [✗] Not found on any mirror")
            results["not_found"].append(isbn)
            time.sleep(DELAY)
            continue
        
        time.sleep(DELAY)
        dl_url = try_direct_download(md5)
        if not dl_url:
            print(f"  [✗] No download link available")
            results["not_found"].append(isbn)
            continue
        
        out_path = OUTPUT_DIR / f"{isbn}.pdf"
        if download_file(dl_url, out_path):
            print(f"  [✓] Saved → {out_path}")
            size = out_path.stat().st_size
            print(f"      Size: {size/1024/1024:.1f} MB")
            results["found"].append(isbn)
        else:
            results["not_found"].append(isbn)
        
        time.sleep(DELAY)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Download Summary:")
    print(f"  Found:     {len(results['found'])} books")
    print(f"  Not found: {len(results['not_found'])} books")
    if results["not_found"]:
        print(f"\n  Books not available on LibGen from this network:")
        for isbn in results["not_found"]:
            title = next((t for i, t in DEFAULT_ISBNS if i == isbn), isbn)
            print(f"    {isbn} — {title}")
        print(f"\n  Try on a different network or use the Goodreads session to access these.")
    print(f"\n  Output directory: {OUTPUT_DIR.resolve()}")

if __name__ == "__main__":
    main()
