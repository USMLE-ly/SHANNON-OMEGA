# Qdrant Semantic Cache — Integration Guide for Replit

## What this does

When a user uploads an outfit photo, the backend calls Atomesus (Cipher Vision)
to analyze it. Atomesus can take 5–20 seconds. If the **exact same image** is
uploaded again (retry, or another user wearing the same outfit), this cache
returns the previous result **instantly** — zero Atomesus calls.

## How it works

1. Compute an MD5 hash of the image bytes (lightning fast, no RAM issues)
2. Check if that hash exists in Qdrant Cloud
3. **Cache hit** → return stored analysis JSON immediately
4. **Cache miss** → call Atomesus, then store the result in Qdrant

## Step 1: Add the dependency

Open your Replit `pyproject.toml` or `requirements.txt` and add:

```
qdrant-client>=1.12
```

## Step 2: Upload qdrant_cache.py

Upload `qdrant_cache.py` to the root of your Replit project
(same directory as `main.py`).

## Step 3: Set up Qdrant Cloud (free tier)

1. Go to https://cloud.qdrant.io and sign up
2. Create a **free tier cluster** (1GB RAM, no credit card needed)
3. Copy the **Cluster URL** and **API Key**
4. In Replit, go to **Secrets** (lock icon in sidebar) and add:
   - `QDRANT_URL` = your cluster URL (e.g. `https://xxxx.us-east-1-0.aws.cloud.qdrant.io:6333`)
   - `QDRANT_API_KEY` = your API key

## Step 4: Wire into main.py

Add this at the top of `main.py` (with the other imports):

```python
try:
    from qdrant_cache import check_cache, write_cache
    logger.info("[BOOT] Qdrant cache module loaded")
except ImportError:
    check_cache = lambda x: None
    write_cache = lambda x, y: False
    logger.warning("[BOOT] qdrant_cache.py not found — caching disabled")
```

Then **wrap your analyze-outfit endpoint** like this:

```python
@app.route('/api/v1/analyze-outfit', methods=['POST', 'OPTIONS'])
def analyze_outfit():
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json(silent=True) or {}
    image_b64 = data.get('image_b64', '')
    if not image_b64:
        return jsonify({"error": "Missing image_b64"}), 400

    # ── CHECK QDRANT CACHE ──
    cached = check_cache(image_b64)
    if cached is not None:
        cached['source'] = 'cipher_vision'
        cached['success'] = True
        return jsonify(cached)

    # ── STANDARD PIPELINE (Atomesus) ──
    result = get_fashion_omega_decision(image_b64)

    # ── WRITE TO QDRANT CACHE ──
    if result.get('source') == 'cipher_vision':
        write_cache(image_b64, result)

    return jsonify({**result, "success": True})
```

## Testing

After deploying:

1. Upload any photo to `luxor.ly/outfit-analysis`
2. Watch the Replit logs — first time you'll see `[QDRANT] CACHE MISS`
3. Upload the **exact same photo** again — you'll see `[QDRANT] CACHE HIT`
   and the result will appear in **<1 second** instead of 10–20 seconds.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `[QDRANT] QDRANT_URL or QDRANT_API_KEY not set` | Add secrets in Replit |
| `[QDRANT] Failed to connect` | Check URL/API key are correct |
| Cache misses every time | Qdrant is working — it only hits cache on **identical** images |
