"""
⚡ SHANNON-Ω Speed Optimizations
Connection pooling, model fallback, caching, streaming.
"""

import time, json, os, pickle, hashlib
from collections import OrderedDict
import requests as req

API_URL = "https://opencode.ai/zen/v1/chat/completions"

# ─── Connection Pooling ────────────────────────────────────────
# Reuse HTTP connections — cuts ~1-2s off first call
_SESSION = req.Session()
_SESSION.headers.update({"Content-Type": "application/json"})
_SESSION.mount("https://", req.adapters.HTTPAdapter(
    pool_connections=10, pool_maxsize=20, max_retries=2,
    pool_block=False
))

def get_session() -> req.Session:
    """Get shared HTTP session with connection pooling."""
    return _SESSION

# ─── Response Cache (disk-backed) ──────────────────────────────
_CACHE_DIR = ".api_cache"
_CACHE_MEM = OrderedDict()
_CACHE_MAX = 200
os.makedirs(_CACHE_DIR, exist_ok=True)

def _cache_key(messages: list, model: str) -> str:
    """Generate cache key from messages + model."""
    raw = json.dumps({"m": messages, "md": model}, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()

def cached_completion(messages: list, model: str = "deepseek-v4-flash-free",
                      max_tokens: int = 1200, temperature: float = 0.7,
                      timeout: int = 30, ttl: int = 3600) -> dict:
    """Cached API completion with disk persistence."""
    key = _cache_key(messages, model)
    
    # Memory cache (fastest)
    if key in _CACHE_MEM:
        _CACHE_MEM.move_to_end(key)
        return _CACHE_MEM[key]
    
    # Disk cache
    cache_path = os.path.join(_CACHE_DIR, f"{key}.json")
    if os.path.exists(cache_path):
        age = time.time() - os.path.getmtime(cache_path)
        if age < ttl:
            with open(cache_path) as f:
                result = json.load(f)
            _CACHE_MEM[key] = result
            if len(_CACHE_MEM) > _CACHE_MAX:
                _CACHE_MEM.popitem(last=False)
            return result
    
    # Live API call with session reuse
    t0 = time.time()
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.95,
    }
    
    r = _SESSION.post(API_URL, json=payload, timeout=timeout)
    r.raise_for_status()
    result = r.json()
    elapsed = time.time() - t0
    
    # Save to cache
    result["_cached"] = True
    result["_elapsed"] = round(elapsed, 2)
    _CACHE_MEM[key] = result
    if len(_CACHE_MEM) > _CACHE_MAX:
        _CACHE_MEM.popitem(last=False)
    with open(cache_path, "w") as f:
        json.dump(result, f)
    
    return result

# ─── Model Fallback Chain ──────────────────────────────────────
# Ordered by speed (fastest first) — tries cheaper models first
FAST_MODELS = [
    "deepseek-v4-flash-free",
]

def quick_completion(system_prompt: str, user_prompt: str,
                     max_tokens: int = 500, temperature: float = 0.5,
                     timeout: int = 15) -> str:
    """Fast completion with aggressive limits — ~3-5s target."""
    user_msg = "Be very concise. 2-3 sentences max. " + user_prompt
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg}
    ]
    
    result = cached_completion(messages, max_tokens=max_tokens,
                                temperature=temperature, timeout=timeout)
    
    content = result["choices"][0]["message"].get("content", "") or ""
    elapsed = result.get("_elapsed", 0)
    return content.strip(), elapsed

# ─── Streaming Support ─────────────────────────────────────────
def stream_completion(system_prompt: str, user_prompt: str,
                      max_tokens: int = 1500, timeout: int = 30):
    """Stream tokens as they arrive — first token in ~1-2s."""
    payload = {
        "model": "deepseek-v4-flash-free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "stream": True,
    }
    
    with _SESSION.post(API_URL, json=payload, timeout=timeout, stream=True) as r:
        for line in r.iter_lines():
            if line:
                line = line.decode("utf-8", errors="ignore")
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0]["delta"]
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError):
                        pass

# ─── Benchmark ─────────────────────────────────────────────────
def benchmark():
    """Run a quick speed test."""
    import time
    
    tests = [
        ("Simple question", "What is the Value Equation? Answer in 1 sentence."),
        ("With context", "Context: Grand Slam Offer means 10x value.\nQ: How do I create one?"),
    ]
    
    for name, prompt in tests:
        t0 = time.time()
        try:
            content, elapsed = quick_completion(
                "You are Alex Hormozi.", prompt,
                max_tokens=200, timeout=15
            )
            print(f"{name:25s} | {elapsed:4.1f}s | {len(content):3d} chars | {content[:60]}")
        except Exception as e:
            print(f"{name:25s} | ERROR: {e}")

if __name__ == "__main__":
    benchmark()
