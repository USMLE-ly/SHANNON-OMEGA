#!/usr/bin/env python3
"""
Scrapling CLI — Import fashion items into your LEXOR® closet.

USAGE:
  python3 tools/scrapling_cli.py --demo                # Try with built-in demo data
  python3 tools/scrapling_cli.py --url <site>           # Scrape a live fashion site
  python3 tools/scrapling_cli.py --demo --max-items 5   # Show 5 demo items
  python3 tools/scrapling_cli.py --demo --output items.json  # Save to file

EXAMPLES:
  python3 tools/scrapling_cli.py --demo --max-items 10 --pretty
  python3 tools/scrapling_cli.py --url "https://altadaily.com" --max-items 10
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.scrapling_import import main
main()
