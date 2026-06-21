import os
import io
import re
import json
import base64
import hashlib
import random
import urllib.parse
import logging
import traceback
from typing import Optional, Dict, List, Any

import cv2
import numpy as np
from PIL import Image
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ─── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("luxor-stylist")

# ─── App Setup ─────────────────────────────────────────────────────────────
app = FastAPI(title="Luxor Pro Stylist Tweaks")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Config ────────────────────────────────────────────────────────────────
ZEN_FABLE_URL = os.getenv(
    "ZEN_FABLE_URL",
    "https://opencode.ai/zen/v1/chat/completions"
)
ZEN_API_KEY = os.getenv("ZEN_API_KEY", "")
POLLINATIONS_TIMEOUT = int(os.getenv("POLLINATIONS_TIMEOUT", "15"))

# ─── Rich Fashion Color Name Lookup ───────────────────────────────────────
COLOR_NAMES: Dict[str, str] = {
    # Reds
    "#8B0000": "Dark Crimson", "#B22222": "Firebrick", "#DC143C": "Crimson",
    "#FF0000": "Vibrant Red", "#FF4500": "Burnt Orange", "#CD5C5C": "Indian Red",
    "#F08080": "Light Coral", "#FA8072": "Salmon", "#E9967A": "Dark Salmon",
    "#FFA07A": "Light Salmon", "#FF6347": "Tomato Red", "#FF69B4": "Hot Pink",
    "#FF1493": "Deep Pink", "#C71585": "Medium Violet Red",
    # Pinks
    "#FFB6C1": "Light Pink", "#FFC0CB": "Baby Pink", "#DB7093": "Pale Violet Red",
    "#FFF0F5": "Lavender Blush", "#FFE4E1": "Misty Rose",
    # Oranges
    "#FF8C00": "Dark Orange", "#FFA500": "Orange", "#FFD700": "Gold",
    "#FFE4B5": "Moccasin", "#FFDEAD": "Navajo White", "#F5DEB3": "Wheat",
    "#D2691E": "Chocolate", "#CD853F": "Peru", "#F4A460": "Sandy Brown",
    "#DA70D6": "Orchid",
    # Yellows
    "#FFFF00": "Lemon Yellow", "#FFFFE0": "Light Yellow", "#FFFACD": "Lemon Chiffon",
    "#FAFAD2": "Light Goldenrod", "#FFEFD5": "Papaya Whip",
    # Greens
    "#006400": "Dark Forest Green", "#008000": "Forest Green", "#228B22": "Kelly Green",
    "#2E8B57": "Sea Green", "#3CB371": "Medium Sea Green", "#66CDAA": "Medium Aquamarine",
    "#8FBC8F": "Dark Sage", "#90EE90": "Light Green", "#98FB98": "Pale Green",
    "#00FF7F": "Spring Green", "#00FA9A": "Medium Spring Green", "#ADFF2F": "Yellow Green",
    "#7CFC00": "Lawn Green", "#7FFF00": "Chartreuse", "#32CD32": "Lime Green",
    "#556B2F": "Olive Green", "#6B8E23": "Olive Drab", "#808000": "Khaki Olive",
    "#BCF5B1": "Mint", "#C1E1C1": "Sage",
    # Blues
    "#000080": "Navy", "#00008B": "Dark Blue", "#0000CD": "Medium Blue",
    "#0000FF": "Royal Blue", "#191970": "Midnight Blue", "#4169E1": "Cornflower Blue",
    "#4682B4": "Steel Blue", "#5B9BD5": "Sky Blue", "#6495ED": "Dodger Blue",
    "#6A5ACD": "Slate Blue", "#7B68EE": "Medium Slate Blue", "#87CEEB": "Light Sky Blue",
    "#87CEFA": "Powder Blue", "#B0C4DE": "Light Steel Blue", "#ADD8E6": "Baby Blue",
    "#00BFFF": "Deep Sky Blue", "#1E90FF": "Dodger Blue", "#00CED1": "Dark Turquoise",
    "#00FFFF": "Cyan", "#E0FFFF": "Light Cyan",
    # Purples
    "#800080": "Purple", "#8B008B": "Dark Magenta", "#9370DB": "Medium Purple",
    "#9400D3": "Dark Violet", "#9932CC": "Dark Orchid", "#A020F0": "Violet",
    "#BA55D3": "Medium Orchid", "#DDA0DD": "Plum", "#EE82EE": "Lavender",
    "#E6E6FA": "Lavender Mist", "#D8BFD8": "Thistle",
    # Browns / Neutrals
    "#3E2723": "Espresso", "#4E342E": "Dark Brown", "#5D4037": "Saddle Brown",
    "#6D4C41": "Leather Brown", "#795548": "Brown", "#8D6E63": "Cognac",
    "#A1887F": "Taupe", "#BCAAA4": "Mushroom", "#D7CCC8": "Beige",
    "#C0A080": "Camel", "#D2B48C": "Tan", "#DEB887": "Burlywood",
    "#F5DEB3": "Wheat", "#FAEBD7": "Antique White", "#FFE4C4": "Biscuit",
    "#E1C699": "Sand", "#C19A6B": "Camel Hair", "#A67B5B": "Caramel",
    # Grays
    "#2F2F2F": "Charcoal", "#404040": "Dark Gray", "#696969": "Gray",
    "#808080": "Medium Gray", "#A9A9A9": "Light Gray", "#C0C0C0": "Silver",
    "#D3D3D3": "Soft Silver", "#DCDCDC": "Gainsboro", "#F5F5F5": "White Smoke",
    # Whites / Creams
    "#FFFFFF": "White", "#FFFAF0": "Ivory", "#FFF8DC": "Cornsilk",
    "#FFF5EE": "Seashell", "#FFF0F5": "Lavender Blush", "#FDF5E6": "Old Lace",
    "#FAF0E6": "Linen", "#F5FFFA": "Mint Cream", "#F0FFF0": "Honeydew",
}


def _name_from_hsv(r: int, g: int, b: int) -> str:
    """Generate a human-readable color name from RGB using HSV logic."""
    mx = max(r, g, b)
    mn = min(r, g, b)
    lum = (mx + mn) / 2 / 255.0
    sat = (mx - mn) / (mx + 1e-6) if mx > 0 else 0

    if mx == mn:
        hue = 0
    else:
        d = mx - mn
        if mx == r:
            hue = ((g - b) / d) % 6
        elif mx == g:
            hue = (b - r) / d + 2
        else:
            hue = (r - g) / d + 4
        hue *= 60

    if sat < 0.15:
        if lum < 0.2:
            return "Black"
        if lum < 0.4:
            return "Charcoal"
        if lum < 0.6:
            return "Gray"
        if lum < 0.8:
            return "Light Gray"
        return "White"

    prefix = ""
    if lum < 0.3:
        prefix = "Dark "
    elif lum > 0.75:
        prefix = "Light "

    if hue < 30:
        return prefix + "Red"
    if hue < 60:
        return prefix + "Orange"
    if hue < 90:
        return prefix + "Yellow"
    if hue < 150:
        return prefix + "Green"
    if hue < 210:
        return prefix + "Teal"
    if hue < 270:
        return prefix + "Blue"
    if hue < 330:
        return prefix + "Purple"
    return prefix + "Rose"


def nearest_color_name(r: int, g: int, b: int) -> str:
    """Find closest named color or generate a descriptive name."""
    hex_str = "#{:02X}{:02X}{:02X}".format(r, g, b).upper()
    if hex_str in COLOR_NAMES:
        return COLOR_NAMES[hex_str]
    best_name = None
    best_dist = float("inf")
    for code, name in COLOR_NAMES.items():
        hx = code.lstrip("#")
        cr = int(hx[0:2], 16)
        cg = int(hx[2:4], 16)
        cb = int(hx[4:6], 16)
        d = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        if d < best_dist:
            best_dist = d
            best_name = name
    return best_name if best_dist < 5000 else _name_from_hsv(r, g, b)


# ─── Models ────────────────────────────────────────────────────────────────
class TweakRequest(BaseModel):
    image_b64: str
    prompt: Optional[str] = None
    target_area: Optional[str] = None


# ─── MediaPipe Person Segmentation ────────────────────────────────────────
_segmentation_model = None


def _get_segmentation():
    """Lazy-load MediaPipe SelfieSegmentation."""
    global _segmentation_model
    if _segmentation_model is None:
        try:
            import mediapipe as mp
            _segmentation_model = mp.solutions.selfie_segmentation.SelfieSegmentation(
                model_selection=0
            )
            log.info("[INIT] MediaPipe SelfieSegmentation loaded")
        except Exception as e:
            log.warning(f"[INIT] MediaPipe not available: {e}. Using center-crop fallback.")
            _segmentation_model = False
    return _segmentation_model


def _segment_person(img_np: np.ndarray) -> np.ndarray:
    """Returns a binary mask isolating the person. Falls back to center crop."""
    h, w = img_np.shape[:2]
    seg = _get_segmentation()

    if seg and seg is not False:
        try:
            rgb = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            results = seg.process(rgb)
            if results.segmentation_mask is not None:
                mask = (results.segmentation_mask > 0.5).astype(np.uint8) * 255
                valid_pct = np.sum(mask > 0) / (h * w)
                if valid_pct > 0.01:
                    log.info(f"[SEGMENT] Person isolated: {valid_pct * 100:.0f}% of frame")
                    return mask
        except Exception as e:
            log.warning(f"[SEGMENT] Mask failed: {e}. Falling back to center crop.")

    # Fallback: center crop
    log.info("[SEGMENT] Using center-crop fallback (60% of frame)")
    crop_ratio = 0.6
    cy, cx = h // 2, w // 2
    ch, cw = int(h * crop_ratio), int(w * crop_ratio)
    mask = np.zeros((h, w), dtype=np.uint8)
    y1 = max(0, cy - ch // 2)
    y2 = min(h, cy + ch // 2)
    x1 = max(0, cx - cw // 2)
    x2 = min(w, cx + cw // 2)
    mask[y1:y2, x1:x2] = 255
    return mask


# ─── Pixel Analysis Engine ───────────────────────────────────────────────
def analyze_pixels(image_b64: str) -> Optional[Dict[str, Any]]:
    """Extract clothing-focused pixel data using person segmentation."""
    try:
        img_bytes = base64.b64decode(image_b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_np = np.array(img)
        h, w = img_np.shape[:2]

        log.info(f"[PIXEL] Image loaded: {w}x{h}")

        # 1. Segment person from background
        mask = _segment_person(img_np)
        masked = np.zeros_like(img_np)
        masked[mask > 0] = img_np[mask > 0]

        # 2. Edge density (on masked region)
        gray = cv2.cvtColor(masked, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = round(float(np.sum(edges > 0)) / max(np.sum(mask > 0), 1), 4)

        # 3. Brightness, saturation, contrast (on masked pixels only)
        hsv = cv2.cvtColor(masked, cv2.COLOR_RGB2HSV)
        mask_bool = mask > 0
        bright_vals = hsv[:, :, 2][mask_bool]
        sat_vals = hsv[:, :, 1][mask_bool]
        if len(bright_vals) > 0:
            brightness_avg = round(float(np.mean(bright_vals)) / 255.0, 2)
        else:
            brightness_avg = 0.0
        if len(sat_vals) > 0:
            saturation_avg = round(float(np.mean(sat_vals)) / 255.0, 2)
        else:
            saturation_avg = 0.0

        masked_vals = masked[mask_bool]
        if len(masked_vals) > 0:
            contrast_ratio = round(float(np.std(masked_vals)), 2)
        else:
            contrast_ratio = 0.0

        # 4. Dominant colors (Pillow quantize - lightweight, no sklearn)
        def get_colors(section: np.ndarray, k: int = 3) -> List[Dict]:
            pil_img = Image.fromarray(section.astype("uint8"), "RGB")
            quantized = pil_img.quantize(colors=k)
            palette = quantized.getpalette()
            if not palette:
                return [{"hex": "#000000", "name": "Black", "percentage": 100.0}]
            total = quantized.size[0] * quantized.size[1]
            idx_counts = {}
            for px in quantized.getdata():
                idx_counts[px] = idx_counts.get(px, 0) + 1
            sorted_idx = sorted(idx_counts.items(), key=lambda x: x[1], reverse=True)
            result = []
            for idx, count in sorted_idx[:k]:
                offset = idx * 3
                r, g, b = palette[offset:offset + 3]
                hex_code = "#{:02X}{:02X}{:02X}".format(r, g, b)
                result.append({
                    "hex": hex_code,
                    "name": nearest_color_name(r, g, b),
                    "percentage": round(count / total * 100, 1),
                })
            return result

        mid = h // 2
        top_section = masked[:mid]
        bottom_section = masked[mid:]
        top_mask = mask[:mid]
        bottom_mask = mask[mid:]
        top_masked = np.zeros_like(top_section)
        bottom_masked = np.zeros_like(bottom_section)
        top_masked[top_mask > 0] = top_section[top_mask > 0]
        bottom_masked[bottom_mask > 0] = bottom_section[bottom_mask > 0]

        top_colors = get_colors(top_masked, 3)
        bottom_colors = get_colors(bottom_masked, 3)

        # 5. Aspect ratio
        ratio = h / w
        if ratio > 1.8:
            aspect = "full_body_portrait"
        elif ratio > 1.2:
            aspect = "portrait"
        elif ratio < 0.6:
            aspect = "full_body_landscape"
        else:
            aspect = "landscape"

        pixel_data = {
            "aspect_ratio": aspect,
            "edge_density": edge_density,
            "brightness_avg": brightness_avg,
            "saturation_avg": saturation_avg,
            "contrast_ratio": contrast_ratio,
            "top_colors": top_colors,
            "bottom_colors": bottom_colors,
        }
        log.info(f"[PIXEL] aspect={aspect}, bright={brightness_avg}, sat={saturation_avg}")
        log.info(f"[PIXEL] Top colors: {[c['name'] for c in top_colors]}")
        log.info(f"[PIXEL] Bottom colors: {[c['name'] for c in bottom_colors]}")
        return pixel_data

    except Exception as e:
        log.error(f"[PIXEL] Analysis failed: {e}")
        log.error(traceback.format_exc())
        return None


# ─── Local Deterministic Stylist ──────────────────────────────────────────
_STYLIST_SUGGESTIONS = [
    "a structured cream leather belt with a gold buckle",
    "a pair of tortoiseshell oversized sunglasses",
    "a pair of brown leather Chelsea boots",
    "a silver chain necklace with a pendant",
    "a navy blue cashmere scarf",
    "a beige trench coat draped over the shoulders",
    "a burgundy leather crossbody bag",
    "a pair of hoop earrings in brushed gold",
    "a black leather tote bag",
    "a wide-brim fedora hat in camel",
    "a silk lavender pocket square",
    "white leather sneakers with minimal detailing",
    "a gold statement ring with geometric design",
    "a charcoal wool blazer",
    "a pair of pearl stud earrings",
    "a cognac leather satchel bag",
    "a patterned silk necktie in navy and gold",
    "a mustard yellow wool beanie",
    "a delicate gold bracelet",
    "a pair of black pointed-toe pumps",
    "a cream silk blouse",
    "a leather bracelet with silver studs",
    "a wool overcoat in camel",
    "a pair of aviator sunglasses",
    "a suede crossbody bag in olive green",
    "a pair of dark wash skinny jeans",
    "a silk scarf tied around the neck in leopard print",
    "a gold watch with a brown leather strap",
    "a pair of chunky white sneakers",
    "a denim jacket with oversized fit",
    "a leather backpack in cognac",
    "a pair of statement sunglasses with colored lenses",
    "a woven leather belt in tan",
    "a pair of suede ankle boots in taupe",
    "a silver bangle set",
    "a linen blazer in light beige",
    "a pair of heeled sandals with gold hardware",
    "a quilted leather shoulder bag in black",
    "a cashmere cardigan in cream",
]


def local_stylist_decision(pixel_data: Dict[str, Any]) -> str:
    """Deterministic local suggestion based on pixel data. Same outfit = same suggestion."""
    stable = json.dumps(pixel_data, sort_keys=True)
    seed = int(hashlib.md5(stable.encode()).hexdigest(), 16)
    rng = random.Random(seed)

    idx = seed % len(_STYLIST_SUGGESTIONS)
    choice = _STYLIST_SUGGESTIONS[idx]
    log.info(f"[LOCAL STYLIST] Seed={seed % 10000}, selected #{idx}: {choice}")
    return choice


# ─── Fable 5 API (OpenCode Zen) ──────────────────────────────────────────
def call_fable5(pixel_data: Dict[str, Any]) -> Optional[str]:
    """Send pixel data to Fable 5. Returns missing_item string or None."""
    if not ZEN_FABLE_URL:
        log.warning("[FABLE5] No ZEN_FABLE_URL configured, skipping")
        return None

    top_str = ", ".join(
        [f"{c['name']} ({c['percentage']}%)" for c in pixel_data.get("top_colors", [])]
    )
    bottom_str = ", ".join(
        [f"{c['name']} ({c['percentage']}%)" for c in pixel_data.get("bottom_colors", [])]
    )

    prompt = (
        f"You are Fable 5, a Vogue/GQ fashion editor. Analyze this outfit data and suggest ONE improvement.\n"
        f"Aspect: {pixel_data.get('aspect_ratio', 'unknown')} | "
        f"Brightness: {pixel_data.get('brightness_avg', 0.5)} | "
        f"Saturation: {pixel_data.get('saturation_avg', 0.5)} | "
        f"Contrast: {pixel_data.get('contrast_ratio', 0)} | "
        f"Edge Density: {pixel_data.get('edge_density', 0)}\n"
        f"Top colors: {top_str}\n"
        f"Bottom colors: {bottom_str}\n"
        f"Based on this, suggest ONE fashion improvement (accessory, color swap, footwear change, or outerwear).\n"
        f"Output ONLY this JSON and nothing else: "
        f'{{\"missing_item\": \"detailed 12-word editorial description\"}}'
    )

    headers = {"Content-Type": "application/json"}
    if ZEN_API_KEY:
        headers["Authorization"] = f"Bearer {ZEN_API_KEY}"

    payload = {
        "model": "deepseek-v4-flash-free",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "max_tokens": 2048,
    }

    try:
        log.info(f"[FABLE5] Sending request to {ZEN_FABLE_URL}")
        resp = requests.post(ZEN_FABLE_URL, json=payload, headers=headers, timeout=25)
        log.info(f"[FABLE5] Response status: {resp.status_code}")

        if resp.status_code != 200:
            log.warning(f"[FABLE5] API returned {resp.status_code}: {resp.text[:300]}")
            return None

        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        log.info(f"[FABLE5] Raw: {content[:300]}")

        content = re.sub(r"```(?:json)?\s*", "", content).strip()
        parsed = json.loads(content)
        missing = parsed.get("missing_item", "")
        if missing:
            log.info(f"[FABLE5] Suggestion: {missing}")
            return missing
        log.warning("[FABLE5] Response missing 'missing_item' field")
        return None

    except json.JSONDecodeError as e:
        log.warning(f"[FABLE5] JSON parse error: {e}")
        return None
    except requests.Timeout:
        log.warning("[FABLE5] Request timed out (8s)")
        return None
    except Exception as e:
        log.warning(f"[FABLE5] Request failed: {e}")
        return None


# ─── Pollinations Image Generation ──────────────────────────────────────
def generate_pollinations_url(suggestion: str) -> str:
    """Convert text suggestion into a Pollinations.ai image URL."""
    editorial = (
        f"High fashion editorial studio photograph of {suggestion}, "
        f"soft studio lighting, luxury texture detail, isolated on premium dark background, "
        f"shot on medium format film, 8K quality, fashion photography, sharp focus"
    )
    safe = urllib.parse.quote(editorial)
    return (
        f"https://image.pollinations.ai/prompt/{safe}"
        f"?width=1024&height=1024&nologin=true&seed=42"
    )


# ─── Config toggle ────────────────────────────────────────────────────────
_FORCE_LOCAL_ONLY = os.getenv("FORCE_LOCAL_ONLY", "1") == "1"


# ─── API Endpoints ──────────────────────────────────────────────────────
@app.get("/health")
@app.get("/")
async def health_check():
    seg_status = "mediapipe" if _get_segmentation() and _get_segmentation() is not False else "center-crop"
    return {
        "status": "ok",
        "service": "luxor-pro-stylist-tweaks",
        "pipeline": "local_stylist" if _FORCE_LOCAL_ONLY else "fable5+local",
        "segmentation": seg_status,
    }


@app.post("/api/v1/pro-tweak/generate")
async def generate_tweak(request: TweakRequest):
    if not request.image_b64:
        return JSONResponse({"error": True, "message": "image_b64 is required"}, status_code=400)

    log.info("[PIPELINE] Step 1/4: Analyzing pixels...")
    pixel_data = analyze_pixels(request.image_b64)

    if pixel_data is None:
        log.error("[PIPELINE] Pixel analysis failed! Using emergency fallback.")
        suggestion = "a gold and pearl vintage brooch with intricate filigree detailing"
        log.info(f"[RESULT] Emergency fallback: {suggestion}")
    else:
        if not _FORCE_LOCAL_ONLY:
            log.info("[PIPELINE] Step 2/4: Calling Fable 5...")
            suggestion = call_fable5(pixel_data)
            if suggestion:
                log.info(f"[RESULT] Fable 5: {suggestion}")
            else:
                log.info("[PIPELINE] Fable 5 failed → local stylist")
                suggestion = local_stylist_decision(pixel_data)
                log.info(f"[RESULT] Local stylist: {suggestion}")
        else:
            log.info("[PIPELINE] FORCE_LOCAL_ONLY=True")
            suggestion = local_stylist_decision(pixel_data)
            log.info(f"[RESULT] Local stylist: {suggestion}")

    log.info(f"[PIPELINE] Step 3/4: Generating Pollinations image...")
    image_url = generate_pollinations_url(suggestion)

    log.info(f"[PIPELINE] Step 4/4: Returning result")
    return {
        "tweaked_image_url": image_url,
        "suggestion": suggestion,
        "pixel_data": pixel_data if pixel_data else {},
    }


if __name__ == "__main__":
    import uvicorn
    PORT = int(os.getenv("PORT", 8767))
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, workers=1)
