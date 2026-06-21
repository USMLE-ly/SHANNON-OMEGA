#!/usr/bin/env python3
"""
SHANNON-Ω PDF DeDRM Tool
=========================
Removes Adobe Adept DRM (EBX_HANDLER) from PDFs.

All 5 fashion PDFs have EBX_HANDLER DRM — full content encryption.
No content can be extracted without the ADE private key.

USAGE:
  With ADE key:   python3 dedrm_books.py /path/to/adeptkey.der
  Without key:    python3 dedrm_books.py --guide

REQUIREMENTS for Method 1:
  - '/tmp/dedrm_tools/DeDRM_plugin/ineptpdf.py' (already present)
  - an adeptkey.der from Adobe Digital Editions
    Get it from: ~/.adobe-digital-editions/adeptkey.der (Linux)
                 %APPDATA%/Adobe/Digital Editions/adeptkey.der (Windows)
                 ~/Library/Application Support/Adobe/Digital Editions/adeptkey.der (macOS)
"""

import sys, os, glob, subprocess, tempfile, shutil, re
from pathlib import Path

TOOLS_DIR = '/tmp/dedrm_tools/DeDRM_plugin'
BOOKS_DIR = 'aa_books'


def get_source_pdfs():
    pdfs = []
    for f in sorted(glob.glob(f'{BOOKS_DIR}/*.pdf')):
        base = os.path.basename(f)
        if any(x in base for x in ['_decrypted', '_OCR', '_reconstructed', '_textonly', '_clean']):
            continue
        pdfs.append(f)
    return pdfs


def method_adept_key(keypath):
    """Decrypt all PDFs using an ADE private key."""
    if not os.path.exists(keypath):
        print(f"\n  ✗ Key file not found: {keypath}")
        return False

    # Install DeDRM tools if needed
    plugin = os.path.join(TOOLS_DIR, 'ineptpdf.py')
    if not os.path.exists(plugin):
        print("\n  ⚠ DeDRM plugin not found. Attempting to download...")
        os.makedirs(TOOLS_DIR, exist_ok=True)
        url = "https://raw.githubusercontent.com/apprenticeharper/DeDRM_tools/master/DeDRM_plugin/ineptpdf.py"
        try:
            import urllib.request
            urllib.request.urlretrieve(url, plugin)
            print("  ✓ Downloaded ineptpdf.py")
        except Exception as e:
            print(f"  ✗ Download failed: {e}")
            return False

    sys.path.insert(0, TOOLS_DIR)
    try:
        from ineptpdf import decryptBook
    except ImportError as e:
        print(f"\n  ✗ Failed to import decryptBook: {e}")
        print(f"    Check that {plugin} exists and is valid.")
        return False

    with open(keypath, 'rb') as f:
        userkey = f.read()

    success = True
    for fname in get_source_pdfs():
        outpath = fname.replace('.pdf', '_decrypted.pdf')
        if os.path.exists(outpath):
            print(f"  ⏭ {os.path.basename(outpath)} exists")
            continue

        print(f"\n  ▶ {os.path.basename(fname)}...", end=' ')
        sys.stdout.flush()
        try:
            result = decryptBook(userkey, fname, outpath)
            if result == 0:
                sz = os.path.getsize(outpath) / 1024 / 1024
                print(f"✓ ({sz:.1f} MB)")
            else:
                print(f"✗ error {result}")
                success = False
        except Exception as e:
            print(f"✗ {str(e)[:100]}")
            success = False

    return success


def show_guide():
    """Show comprehensive guide and status."""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  SHANNON-Ω PDF DeDRM — Status & Guide                  ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    # Show PDFs
    print("\n── PDF Status ──")
    for fname in get_source_pdfs():
        sz = os.path.getsize(fname) / 1024 / 1024
        out_exists = os.path.exists(fname.replace('.pdf', '_decrypted.pdf'))
        status = "✓ DeCRYPTED" if out_exists else "✗ ENCRYPTED (EBX_HANDLER)"
        print(f"  {os.path.basename(fname):55s} ({sz:.1f} MB) {status}")

    # Check if DeDRM tools are in place
    has_plugin = os.path.exists(os.path.join(TOOLS_DIR, 'ineptpdf.py'))
    print(f"\n── Required Tools ──")
    print(f"  DeDRM plugin (ineptpdf.py): {'✓ Found' if has_plugin else '✗ Missing'}")
    
    # Check for adeptkey.der in common locations
    key_paths = [
        os.path.expanduser('~/.adobe-digital-editions/adeptkey.der'),
        os.path.expanduser('~/AppData/Roaming/Adobe/Digital Editions/adeptkey.der'),
        os.path.expanduser('~/Library/Application Support/Adobe/Digital Editions/adeptkey.der'),
        '/tmp/adeptkey.der',
        'adeptkey.der',
    ]
    found_keys = [p for p in key_paths if os.path.exists(p)]
    if found_keys:
        for p in found_keys:
            print(f"  ADE key found: {p}")
    else:
        print(f"  ADE key: NOT FOUND")
    
    print(f"\n── How to Get an ADE Key ──")
    print(f"  1. Install Adobe Digital Editions on a desktop computer")
    print(f"  2. Authorize it with an Adobe ID")
    print(f"  3. Open one of these PDFs in ADE (it will autorize the device)")
    print(f"  4. The decryption key is then saved as 'adeptkey.der':")
    print(f"     - Windows: %APPDATA%\\Adobe\\Digital Editions\\adeptkey.der")
    print(f"     - macOS: ~/Library/Application Support/Adobe/Digital Editions/adeptkey.der")
    print(f"     - Linux: ~/.adobe-digital-editions/adeptkey.der")
    print(f"  5. Copy the file here and run:")
    print(f"     python3 dedrm_books.py /path/to/adeptkey.der")
    print()
    print(f"  Or download from IA on an unrestricted machine and copy here.")
    print(f"  IA direct links for clean PDFs:")
    for fname in get_source_pdfs():
        isbn = os.path.basename(fname).split('_')[0]
        ia_ids = {
            '9781350193901': 'fashiondesigners0000roth',
            '9781501382567': 'guidetofashionse0000amad_k7x4',
            '9781472532664': 'guidetofashionse0000amad',
            '9781607053552': 'fieldguidetofabr0000kigh',
            '9781854799975': 'artofzandrarhode0000zand',
        }
        ia_id = ia_ids.get(isbn, '')
        if ia_id:
            print(f"    https://archive.org/download/{ia_id}/{ia_id}.pdf")
    
    print(f"\n── Alternative routes ──")
    print(f"  • Anna's Archive (annasarchive.org): Search by ISBN, download clean PDF")
    print(f"  • Z-Library (singlelogin.re): Register, search by ISBN")
    print(f"  • Library Genesis (libgen.is): May have some titles")


def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║  SHANNON-Ω PDF DeDRM Tool                       ║")
    print("╚══════════════════════════════════════════════════╝")

    if not os.path.exists(BOOKS_DIR):
        print(f"\n  ✗ Books directory '{BOOKS_DIR}' not found!")
        return 1

    if len(sys.argv) < 2:
        show_guide()
        print("\nUsage: python3 dedrm_books.py /path/to/adeptkey.der")
        print("       python3 dedrm_books.py --guide")
        return 0

    cmd = sys.argv[1]
    
    if cmd == '--guide':
        show_guide()
    elif cmd in ('-h', '--help'):
        show_guide()
    else:
        method_adept_key(cmd)

    return 0


if __name__ == '__main__':
    main()
