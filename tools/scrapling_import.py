#!/usr/bin/env python3
"""
Scrapling Import Tool — Scrapes fashion items from Altadaily and other sites.
Usage:
    python3 tools/scrapling_import.py --url https://altadaily.com/collections/all --max-items 20
    python3 tools/scrapling_import.py --url https://example.com/looks --max-items 10 --category dresses
"""
import argparse
import json
import sys
import re
from urllib.parse import urlparse

try:
    from scrapling import Fetcher
except (ImportError, ModuleNotFoundError):
    print(json.dumps({"error": "scrapling not installed. Run: pip install scrapling"}), file=sys.stderr)
    sys.exit(1)


def extract_items_from_altadaily(html: str, max_items: int = 20) -> list[dict]:
    """Parse Altadaily collection/product pages."""
    from scrapling.parser import Adaptor
    parser = Adaptor(html)
    items = []

    # Try multiple selectors for product cards
    product_cards = (
        parser.css("div.grid-product__content") or
        parser.css("div.product-card") or
        parser.css("div.collection-item") or
        parser.css("div[class*=product]") or
        parser.css("li.product") or
        parser.css("article.product") or
        parser.css("div[data-product]") or
        parser.css("div.grid__item") or
        parser.css("div[class*=product-item]")
    )

    # For JSON-LD structured data
    json_ld = parser.css("script[type='application/ld+json']")
    json_ld_items = []
    for script in json_ld:
        try:
            data = json.loads(script.text)
            if isinstance(data, dict):
                if data.get("@type") == "ItemList" and "itemListElement" in data:
                    for elem in data["itemListElement"]:
                        item_data = elem.get("item", elem)
                        json_ld_items.append({
                            "name": item_data.get("name", ""),
                            "brand": item_data.get("brand", {}).get("name", "") if isinstance(item_data.get("brand"), dict) else item_data.get("brand", ""),
                            "price": item_data.get("offers", {}).get("price", "") if isinstance(item_data.get("offers"), dict) else "",
                            "imageUrl": "",
                            "category": item_data.get("category", ""),
                            "color": "",
                            "style": "modern",
                            "url": item_data.get("url", ""),
                        })
                        if item_data.get("image"):
                            img = item_data["image"]
                            if isinstance(img, dict):
                                json_ld_items[-1]["imageUrl"] = img.get("url", "")
                            elif isinstance(img, str):
                                json_ld_items[-1]["imageUrl"] = img
                elif data.get("@type") == "Product":
                    json_ld_items.append({
                        "name": data.get("name", ""),
                        "brand": data.get("brand", {}).get("name", "") if isinstance(data.get("brand"), dict) else data.get("brand", ""),
                        "price": data.get("offers", {}).get("price", "") if isinstance(data.get("offers"), dict) else "",
                        "imageUrl": data.get("image", ""),
                        "category": data.get("category", ""),
                        "color": "",
                        "style": "modern",
                        "url": data.get("url", ""),
                    })
        except (json.JSONDecodeError, AttributeError):
            pass

    for card in product_cards[:max_items]:
        try:
            # Name
            name_el = (
                card.css("a.product-name") or
                card.css("a[class*=title]") or
                card.css("h2 a") or
                card.css("h3 a") or
                card.css("a[class*=name]") or
                card.css("p[class*=name]") or
                card.css("a[class*=product-title]") or
                card.css("img[alt]")
            )
            name = ""
            if name_el:
                name = (name_el[0].text or name_el[0].attrib.get("alt", "") or "").strip()
            else:
                # Try reading from image alt
                imgs = card.css("img")
                if imgs:
                    name = imgs[0].attrib.get("alt", "").strip()

            # Image
            img_url = ""
            imgs = card.css("img")
            for img in imgs:
                src = img.attrib.get("src") or img.attrib.get("data-src") or img.attrib.get("srcset", "")
                if src and not src.startswith("data:"):
                    if src.startswith("//"):
                        src = "https:" + src
                    img_url = src.split(" ")[0].strip()
                    break

            # Price
            price_el = (
                card.css("span.price") or
                card.css("span[class*=price]") or
                card.css("div[class*=price]") or
                card.css("p[class*=price]")
            )
            price = price_el[0].text.strip() if price_el else ""

            # URL
            link_el = card.css("a[href]")
            url = ""
            if link_el and not link_el[0].attrib.get("href", "").startswith("#"):
                href = link_el[0].attrib.get("href", "")
                if href.startswith("/"):
                    url = "https://altadaily.com" + href
                else:
                    url = href

            if name:
                items.append({
                    "name": name[:100],
                    "brand": "Altadaily",
                    "price": price,
                    "imageUrl": img_url,
                    "category": categorize_item(name),
                    "color": extract_color(name),
                    "style": "editorial",
                    "url": url,
                })

                if len(items) >= max_items:
                    break
        except Exception as e:
            print(f"Warning: failed to parse card: {e}", file=sys.stderr)
            continue

    # If no items found via HTML parsing, try JSON-LD fallback
    if not items and json_ld_items:
        items = json_ld_items[:max_items]

    return items


def categorize_item(name: str) -> str:
    """Guess the category from the item name."""
    name_lower = name.lower()
    categories = {
        "tops": ["top", "t-shirt", "shirt", "blouse", "sweater", "hoodie", "crop", "tank", "polo", "bodysuit"],
        "bottoms": ["pant", "jean", "trouser", "skirt", "short", "legging", "chino", "cargo", "jogger"],
        "dresses": ["dress", "gown", "jumpsuit", "romper", "playsuit"],
        "outerwear": ["jacket", "coat", "blazer", "vest", "cardigan", "parka", "bomber"],
        "footwear": ["shoe", "sneaker", "boot", "loafer", "heel", "sandals", "slipper", "trainer"],
        "accessories": ["bag", "belt", "hat", "scarf", "sunglass", "watch", "jewelry", "necklace", "earring", "bracelet", "ring", "wallet"],
    }
    for category, keywords in categories.items():
        if any(kw in name_lower for kw in keywords):
            return category
    return "other"


def extract_color(text: str) -> str:
    """Extract color from item name/text."""
    colors = ["black", "white", "navy", "blue", "green", "red", "yellow", "pink", "purple", "orange", "brown", "gray", "grey", "beige", "cream", "olive", "burgundy", "maroon", "teal", "coral", "ivory", "khaki", "tan", "gold", "silver", "rose", "lilac"]
    text_lower = text.lower()
    for c in colors:
        if c in text_lower:
            return c.capitalize()
    return "Black"


def scrape_url(url: str, max_items: int = 20, category: str = "") -> list[dict]:
    """Main scrape function using httpx with Scrapling/Next.js fallback."""
    domain = urlparse(url).netloc.lower()
    
    # 1. Try httpx first
    items = scrape_with_httpx(url, max_items)
    if items:
        if category:
            items = [i for i in items if i["category"] == category]
        return items[:max_items]

    # 2. Try Scrapling for HTML parsing
    try:
        fetcher = Fetcher()
        resp = fetcher.get(url)
        if resp and resp.status == 200 and resp.text and len(resp.text) > 50:
            items = extract_items_from_altadaily(resp.text, max_items)
    except Exception as e:
        print(f"Scrapling failed: {e}", file=sys.stderr)

    # 3. Try Next.js __NEXT_DATA__ parser
    if not items:
        try:
            html = resp.text if 'resp' in dir() and resp else None
            if not html:
                import httpx
                client = httpx.Client(headers={'User-Agent': 'Mozilla/5.0'}, follow_redirects=True, timeout=15)
                html = client.get(url).text
            items = extract_from_nextjs(html, max_items)
            if items:
                print(f"Extracted {len(items)} items from Next.js data", file=sys.stderr)
        except Exception as e:
            print(f"Next.js parser failed: {e}", file=sys.stderr)

    if not items:
        raise Exception(f"Could not extract items from URL. The site may use JavaScript rendering or authentication.")

    if category:
        items = [i for i in items if i["category"] == category]

    seen = set()
    unique_items = []
    for item in items:
        key = (item["name"], item["url"])
        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    return unique_items[:max_items]

    if category:
        items = [i for i in items if i["category"] == category]

    seen = set()
    unique_items = []
    for item in items:
        key = (item["name"], item["url"])
        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    return unique_items[:max_items]



def generate_demo_items(count: int = 10) -> list[dict]:
    items = [
        {"name": "Tailored Wool Blazer", "brand": "Theory", "price": "$395", "imageUrl": "", "category": "outerwear", "color": "Navy", "style": "tailored"},
        {"name": "Cashmere Turtleneck", "brand": "N.Peal", "price": "$295", "imageUrl": "", "category": "tops", "color": "Cream", "style": "luxury"},
        {"name": "Wide-Leg Trousers", "brand": "Joseph", "price": "$350", "imageUrl": "", "category": "bottoms", "color": "Black", "style": "tailored"},
        {"name": "Silk Slip Dress", "brand": "Slate", "price": "$245", "imageUrl": "", "category": "dresses", "color": "Burgundy", "style": "evening"},
        {"name": "Leather Crossbody Bag", "brand": "Staud", "price": "$265", "imageUrl": "", "category": "accessories", "color": "Brown", "style": "minimal"},
        {"name": "Cashmere Coat", "brand": "Max Mara", "price": "$1,290", "imageUrl": "", "category": "outerwear", "color": "Beige", "style": "timeless"},
        {"name": "Cotton Oxford Shirt", "brand": "Ami Paris", "price": "$195", "imageUrl": "", "category": "tops", "color": "White", "style": "classic"},
        {"name": "High-Rise Straight Jeans", "brand": "Mother", "price": "$228", "imageUrl": "", "category": "bottoms", "color": "Blue", "style": "casual"},
        {"name": "Gold Chain Necklace", "brand": "Missoma", "price": "$89", "imageUrl": "", "category": "accessories", "color": "Gold", "style": "minimal"},
        {"name": "Knit Polo Shirt", "brand": "Loro Piana", "price": "$695", "imageUrl": "", "category": "tops", "color": "Olive", "style": "refined"},
        {"name": "Leather Belt", "brand": "The Row", "price": "$490", "imageUrl": "", "category": "accessories", "color": "Black", "style": "minimal"},
        {"name": "Pleated Midi Skirt", "brand": "Maje", "price": "$285", "imageUrl": "", "category": "bottoms", "color": "Navy", "style": "feminine"},
    ]
    return items[:count]


def main():
    parser = argparse.ArgumentParser(description="Scrapling Import Tool")
    parser.add_argument("--url", default="https://altadaily.com/collections/all", help="URL to scrape")
    parser.add_argument("--max-items", type=int, default=20, help="Maximum items to scrape")
    parser.add_argument("--category", default="", help="Filter by category")
    parser.add_argument("--output", default="", help="Output JSON file path")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    parser.add_argument("--demo", action="store_true", help="Use demo data (no web scraping)")

    args = parser.parse_args()

    try:
        if args.demo:
            items = generate_demo_items(args.max_items)
        else:
            items = scrape_url(args.url, args.max_items, args.category)
        output = {"items": items, "count": len(items), "source": args.url}

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output, f, indent=2 if args.pretty else None)
            print(f"Saved {len(items)} items to {args.output}", file=sys.stderr)
        else:
            print(json.dumps(output, indent=2 if args.pretty else None))

    except Exception as e:
        print(json.dumps({"error": str(e), "items": [], "count": 0}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


# If scrapling returns empty, try alternative HTTP libraries

def extract_from_nextjs(html: str, max_items: int = 20) -> list[dict]:
    """Parse Next.js __NEXT_DATA__ for product information."""
    import json, re
    items = []
    
    # Find __NEXT_DATA__
    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not match:
        return items
    
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return items
    
    def deep_search(obj, depth=0):
        if depth > 6:
            return
        if isinstance(obj, dict):
            # Check if this looks like a product
            if 'name' in obj and 'id' in obj and any(k in obj for k in ['price', 'images', 'image', 'category']):
                name = str(obj.get('name', ''))
                if name and len(name) > 2:
                    price = obj.get('price', '')
                    if isinstance(price, dict):
                        price = price.get('amount', price.get('min', ''))
                    images = obj.get('images', obj.get('image', []))
                    img_url = ''
                    if isinstance(images, list) and len(images) > 0:
                        first_img = images[0]
                        if isinstance(first_img, dict):
                            img_url = first_img.get('src', first_img.get('url', first_img.get('original', '')))
                        elif isinstance(first_img, str):
                            img_url = first_img
                    elif isinstance(images, dict):
                        img_url = images.get('src', images.get('url', ''))
                    elif isinstance(images, str):
                        img_url = images
                    
                    category = obj.get('category', obj.get('productType', ''))
                    if isinstance(category, dict):
                        category = category.get('name', '')
                    
                    color = obj.get('color', obj.get('colour', ''))
                    if isinstance(color, dict):
                        color = color.get('name', '')
                    
                    items.append({
                        'name': name[:100],
                        'brand': obj.get('brand', obj.get('vendor', 'Altadaily')),
                        'price': str(price),
                        'imageUrl': img_url,
                        'category': categorize_item(name) if not category else str(category),
                        'color': extract_color(name) if not color else str(color),
                        'style': 'editorial',
                        'url': obj.get('url', obj.get('handle', '')),
                    })
                    return
            
            # Keep searching deeper
            for key, val in obj.items():
                if isinstance(val, (dict, list)):
                    deep_search(val, depth + 1)
                    if len(items) >= max_items:
                        return
        
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    deep_search(item, depth + 1)
                    if len(items) >= max_items:
                        return
    
    deep_search(data)
    return items[:max_items]


def scrape_with_httpx(url: str, max_items: int = 20) -> list[dict]:
    """Fallback scraper using httpx which handles more sites."""
    try:
        import httpx
        client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            follow_redirects=True,
            timeout=15,
        )
        resp = client.get(url)
        if resp.status_code == 200 and len(resp.text) > 100:
            return extract_items_from_altadaily(resp.text, max_items)
    except Exception as e:
        print(f"httpx fallback failed: {e}", file=sys.stderr)
    return []
