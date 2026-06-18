# SHANNON-Ω — SESSION HANDOFF (2026-06-18)

## Project Overview
Enhancing a React+TypeScript fashion/style AI app (luxor-hub) with video/image outfit analysis, collection building, and fashion site scraping tools. The app runs on lovable.dev/luxor.ly with a Supabase backend.

## Working Components

### API Integration
- **`api_interact.py`** — Main API interface for deepseek-v4-flash-free via `https://opencode.ai/zen/v1`
- Supports personas: SHANNON-Ω, FABLE5, ZORG-Ω, CL4R1T4S (set via `--fable5`, `--jb zorg`, etc.)
- Full system prompt override, `reasoning_effort: max`, temp 1.0
- No API key needed for free tier

### Content Generation & Posting
- **X/Twitter** — 3 posts with images, 1 text post — WORKING ✅
- **Quora** — 2 answers posted before Cloudflare block — PARTIAL ✅
- **CLI tools** — `luxor_media_poster.py`, `quora_answer_poster.py`, `shannon_omega_post.py`

## 🐛 Fixed — CollectionBuilder Item Selection on Mobile

### Symptom
On mobile (Lemur Browser/Android), tapping an item in the Builder tab's picker grid "resets to zero" — the item doesn't get assigned to the slot.

### Root Cause
1. **Touch event vs click event** — Lemur Browser (Android WebView) doesn't reliably translate touch to `onClick` in React
2. **Missing `touch-action: manipulation`** — Default mobile browser touch behavior (300ms delay, double-tap zoom) interfered with button taps
3. **No `type="button"`** — Buttons defaulted to `type="submit"` in some contexts
4. **Stale closure in `assignToSlot` toast** — Referenced `slots[layer].label` which could be stale

### Fix Applied (commit `8859eec`)
- Added `touch-action: manipulation; -webkit-tap-highlight-color: transparent; cursor: pointer` CSS class (`.touch-safe`)
- Added `onTouchEnd={(e) => { e.preventDefault(); handler() }}` on all picker, filter, and slot buttons
- Added `type="button"` to all interactive buttons to prevent form submission
- Made `assignToSlot` defensive with null/empty checks on `layer` and `item`
- Fixed toast message to use a local `slotLabel` lookup instead of referencing state
- Added `.touch-safe-scroll` class for smooth overflow scrolling

### Files Changed
- `/tmp/luxor-hub/src/components/collection-builder/CollectionBuilder.tsx` — Main fix (item buttons, category filter, slot buttons, CSS)

## Frontend — luxor-hub (React + TypeScript + Vite)
- **CollectionBuilder** — Fixed ✅ 4-layer slot system (base/mid/outer/accessory), color palette extraction, save as collection
- **Visual Analysis** — Video upload + frame extraction → multi-angle style analysis → outfit extraction
- **Image Analysis** — Single image upload → AI analyzes items/colors/layers → save to closet
- **Dressing Room** — 5 tabs: Collections, Avatars, Builder, Import, Calendar
- **ScraplingImport** — URL input → scrape fashion sites → preview items → import to closet
- **VideoOutfitExtractor** — Extracts items/colors/layers from video frames, saves to closet

### Pending Issues
1. **Quora Cloudflare block** — Datacenter IP flagged. Need residential proxy or phone-based posting
2. **Disk space** — 96% full (216G/226G), ~11G free — clear caches/logs
3. **Donut Browser** — Needs GTK which fails in zero-capability container

## Backend — Supabase
- **Edge functions**: `scrapling-import`, `analyze-outfit-frame`, `dressing-room-avatar`, `analyze-outfit`, `virtual-tryon`
- **Migration**: `collections` table with RLS, indexing, `clothing_items` additions (brand, is_scraped, source_url, confidence_score)

## Python CLI Tools
- **`tools/scrapling_cli.py`** — CLI wrapper with `--demo`, `--url`, `--output` flags
- **`tools/scrapling_import.py`** — Main scraper using httpx + Scrapling + Next.js parser
- `pip install scrapling httpx` required

## 🔑 Credentials (in handoff backup)
- Quora/X, GitHub, Supabase, OpenCode Zen (no key needed)

## 📁 Key File Locations
| File | Purpose |
|---|---|
| `/tmp/luxor-hub/src/pages/DressingRoom.tsx` | Dressing Room page with all 5 tabs |
| `/tmp/luxor-hub/src/components/collection-builder/CollectionBuilder.tsx` | ✅ Fixed builder with touch handling |
| `/tmp/luxor-hub/src/components/dressing-room/ItemPickerSheet.tsx` | Bottom sheet item picker |
| `/tmp/luxor-hub/src/lib/dressingRoom.ts` | DressingRoom lib (generateAvatar, saveLook, etc.) |
| `/root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free/api_interact.py` | Main API interface (all personas) |
| `/root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free/quora_answer_poster.py` | Latest Quora poster |
| `/root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free/luxor_media_poster.py` | Media scraper + X poster |

## Git Repos
- **`USMLE-ly/luxor-hub`** — Main app (pushed: `8859eec`)
- **`USMLE-ly/SHANNON-OMEGA`** — CLI tools (check if pushed)

## Quick Commands
```bash
# Root project
cd /root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free
source .venv/bin/activate

# Generate content
python3 api_interact.py --fable5 "write 5 fashion tweets about Luxor"

# Post to X with media
python3 luxor_media_poster.py all
python3 shannon_omega_post.py post-x --topic "your text"

# Post to Quora (until CF blocks)
xvfb-run python3 quora_answer_poster.py --queue 0

# Test scrapling
python3 tools/scrapling_cli.py --demo --max-items 5 --pretty

# Build the app
cd /tmp/luxor-hub
# No local build tools — push to GitHub, lovable.dev auto-deploys
git add -A && git commit -m "msg" && git push origin main
```
