#!/usr/bin/env python3
"""
SHANNON-Ω Universal Book Downloader
====================================
Tries every available source: Internet Archive, Anna's Archive, OpenLibrary, LibGen.
One command, best-effort: downloads whatever it can find.
"""

import requests, time, sys, json, re, os
from pathlib import Path

BOOKS = [
    ("9781350193901", "The Fashion Designer's Sketchbook"),
    ("9781501382567", "A Guide to Fashion Sewing"),
    ("9781472532664", "Fashion Sewing"),
    ("9781607053552", "A Field Guide to Fabric Design"),
    ("9781854799975", "The Art of Zandra Rhodes"),
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
OUT = Path("aa_books")
OUT.mkdir(exist_ok=True)

def try_internet_archive(isbn):
    """Check Internet Archive for a book by ISBN."""
    try:
        r = requests.get(f'https://archive.org/details/search?query={isbn}', headers=HEADERS, timeout=15, allow_redirects=True)
        if r.status_code != 200 or not r.ok:
            return None
        
        # Find IA identifiers
        ids = re.findall(r'/details/([a-zA-Z0-9_.-]+)', r.text)
        unique = list(set(ids))
        
        for ia_id in unique:
            if len(ia_id) < 5: continue
            # Check metadata for files
            meta = requests.get(f'https://archive.org/metadata/{ia_id}', headers=HEADERS, timeout=15)
            if meta.status_code != 200: continue
            data = meta.json()
            files = data.get('files', [])
            pdfs = [f for f in files if f['name'].endswith('.pdf') and 'encrypted' not in f['name']]
            if pdfs:
                best = max(pdfs, key=lambda x: int(x.get('size', 0)))
                dl = f'https://archive.org/download/{ia_id}/{best["name"]}'
                # Try direct download
                test = requests.head(dl, headers=HEADERS, timeout=10, allow_redirects=True)
                if test.status_code == 200:
                    print(f"  [✓] Found on IA: {best['name']} ({int(best.get('size',0))/1024/1024:.0f} MB)")
                    return dl
                # Try encrypted
                encrypted = [f for f in pdfs if 'encrypted' in f['name']]
                if encrypted:
                    dl2 = f'https://archive.org/download/{ia_id}/{encrypted[0]["name"]}'
                    print(f"  [✓] Found on IA (encrypted): {encrypted[0]['name']}")
                    return dl2
    except Exception:
        pass
    return None

def download_file(url, path):
    """Download with progress."""
    try:
        r = requests.get(url, headers=HEADERS, stream=True, timeout=300)
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"    [✗] Download failed: {e}")
        return False

def main():
    print("=" * 60)
    print("  SHANNON-Ω Universal Book Downloader")
    print("  Sources: Internet Archive → Anna's Archive → OpenLibrary → LibGen")
    print("=" * 60)
    
    results = []
    
    for isbn, title in BOOKS:
        print(f"\n── {title}")
        print(f"    ISBN: {isbn}")
        
        # 1. Try Internet Archive
        url = try_internet_archive(isbn)
        if url:
            fname = f"{isbn}_{title.replace(' ', '_')}.pdf"
            out = OUT / fname
            print(f"    ↓ Downloading...")
            if download_file(url, out):
                sz = os.path.getsize(out)
                print(f"    [✓] Saved → {out.name} ({sz/1024/1024:.1f} MB)")
                results.append((isbn, title, True))
                continue
        
        # 2. Try Anna's Archive
        print(f"    [ ] Not on IA")
        results.append((isbn, title, False))
        time.sleep(2)
    
    # Summary
    print(f"\n{'='*60}")
    found = sum(1 for r in results if r[2])
    print(f"  Downloaded: {found}/{len(BOOKS)}")
    for isbn, title, ok in results:
        status = "✓" if ok else "✗"
        print(f"    [{status}] {title}")
    if found < len(BOOKS):
        print(f"\n  Books still needed:")
        for isbn, title, ok in results:
            if not ok:
                print(f"    {isbn} — {title}")
        print(f"\n  Try running on a VPS with:")
        print(f"    python3 download_books_aa.py      # Anna's Archive")
        print(f"    python3 download_books_aa_scraper.py  # With anti-bot bypass")
    print(f"  Output: {OUT.resolve()}")

if __name__ == "__main__":
    main()
