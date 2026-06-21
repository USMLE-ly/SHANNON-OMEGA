"""
orchestrator.py — Zencode Client Wrapper + Intelligent Cache
==============================================================
Production-hardened proxy/router/cache layer for the external
Open Zencode API used by the Luxor "Pro Stylist Tweaks" feature.

Architecture:
  - ZencodeClient:  Wraps all HTTP calls to the external image-gen API
  - MaskCache:      content-addressable cache keyed on (image_hash, prompt)
  - TweaksPipeline: Orchestrates mask → generate → blend → cache pipeline
"""

import asyncio
import base64
import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import aiohttp
import diskcache

logger = logging.getLogger("stylist-tweaks.orchestrator")

# ─── Configuration ───────────────────────────────────────────────────────────
ZENCODE_API_URL = os.getenv("ZENCODE_API_URL", "https://opencode.ai/zen/v1")
ZENCODE_MODEL = os.getenv("ZENCODE_MODEL", "deepseek-v4-flash-free")
CACHE_DIR = os.getenv("TWEAK_CACHE_DIR", "/tmp/luxor-tweak-cache")
CACHE_TTL_SECONDS = int(os.getenv("TWEAK_CACHE_TTL", "86400"))  # 24h default
MAX_PAYLOAD_BYTES = int(os.getenv("ZENCODE_MAX_PAYLOAD", "10_485_760"))  # 10 MB
REQUEST_TIMEOUT_SECONDS = int(os.getenv("ZENCODE_TIMEOUT", "30"))


# ─── Data Models ─────────────────────────────────────────────────────────────

@dataclass
class TweakRequest:
    """Inbound tweak generation request."""
    image_base64: str
    prompt: str
    mask_prompt: Optional[str] = None        # e.g. "the green bag"
    strength: float = 0.85                    # edit strength 0.0–1.0
    request_id: str = ""
    timestamp: float = field(default_factory=time.time)

    @property
    def image_hash(self) -> str:
        """SHA-256 of the image content for cache key generation."""
        return hashlib.sha256(
            self.image_base64.encode("utf-8")
        ).hexdigest()[:16]

    @property
    def cache_key(self) -> str:
        """Deterministic cache key combining image + prompt."""
        raw = f"{self.image_hash}:::{self.prompt.strip().lower()}:::{self.mask_prompt or ''}"
        return hashlib.sha256(raw.encode()).hexdigest()


@dataclass
class TweakResult:
    """Outbound tweak result."""
    image_base64: str
    request_id: str
    generation_time_ms: int
    cached: bool = False
    model: str = ZENCODE_MODEL


# ─── Zencode Client ──────────────────────────────────────────────────────────

class ZencodeClient:
    """
    Production HTTP client for the Open Zencode API.
    Handles auth, retries, streaming, and error normalization.
    """

    def __init__(
        self,
        api_url: str = ZENCODE_API_URL,
        model: str = ZENCODE_MODEL,
        timeout: int = REQUEST_TIMEOUT_SECONDS,
        max_retries: int = 2,
    ):
        self.api_url = api_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_remaining = 60
        self._rate_limit_reset = time.time()

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "LuxorStylistTweaks/1.0",
                },
            )
        return self._session

    async def _rate_limit_wait(self):
        """Respect rate-limit headers from upstream."""
        if self._rate_limit_remaining < 2 and time.time() < self._rate_limit_reset:
            wait = self._rate_limit_reset - time.time() + 0.5
            logger.info("rate-limit wait: %.1fs", wait)
            await asyncio.sleep(wait)

    async def generate_edit(self, image_base64: str, prompt: str) -> str:
        """
        Send a generation request to the Zencode API and return the
        resulting base64-encoded edited image.

        The API expects:
          POST {api_url}/chat/completions
          {
            "model": "...",
            "messages": [{
              "role": "user",
              "content": [
                { "type": "image_url", "image_url": { "url": "data:image/png;base64,..." } },
                { "type": "text", "text": "<prompt>" }
              ]
            }]
          }

        Returns the base64 string of the edited image from the response.
        """
        await self._rate_limit_wait()
        session = await self._get_session()

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                f"You are an expert fashion image editor. "
                                f"Edit the outfit photo according to this instruction: {prompt}. "
                                f"Make the edit realistic, preserving the original lighting, "
                                f"shadows, and image quality. Return ONLY the edited image."
                            ),
                        },
                    ],
                }
            ],
            "max_tokens": 4096,
        }

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(
                    "zencode request | attempt %d/%d | prompt=%.60s",
                    attempt + 1, self.max_retries + 1, prompt,
                )
                async with session.post(
                    urljoin(self.api_url, "/chat/completions"),
                    json=payload,
                ) as resp:
                    # Track rate limits
                    self._rate_limit_remaining = int(
                        resp.headers.get("X-RateLimit-Remaining", 60)
                    )
                    reset_ts = resp.headers.get("X-RateLimit-Reset", "")
                    if reset_ts:
                        self._rate_limit_reset = float(reset_ts)

                    if resp.status == 429:
                        retry_after = int(resp.headers.get("Retry-After", "5"))
                        logger.warning("rate-limited, retrying after %ds", retry_after)
                        await asyncio.sleep(retry_after)
                        continue

                    if resp.status == 200:
                        result = await resp.json()
                        return self._extract_image(result)

                    # Non-200 error
                    error_body = await resp.text()
                    logger.error("zencode error %d: %.200s", resp.status, error_body)
                    last_error = f"APIError({resp.status}): {error_body[:200]}"

                    if resp.status >= 500 and attempt < self.max_retries:
                        await asyncio.sleep(1.5 ** attempt)
                        continue
                    break

            except asyncio.TimeoutError:
                logger.warning("zencode timeout on attempt %d", attempt + 1)
                last_error = "Request timed out"
                if attempt < self.max_retries:
                    await asyncio.sleep(1.0)
                    continue
            except aiohttp.ClientError as e:
                logger.warning("zencode connection error: %s", e)
                last_error = str(e)
                if attempt < self.max_retries:
                    await asyncio.sleep(1.0)
                    continue

        raise RuntimeError(f"Zencode generation failed: {last_error}")

    def _extract_image(self, response: dict) -> str:
        """Extract base64 image from the Zencode API response."""
        try:
            choices = response.get("choices", [])
            if not choices:
                raise ValueError("No choices in response")
            content = choices[0].get("message", {}).get("content", "")
            if not content:
                raise ValueError("Empty message content")

            # The API may return a markdown image tag or direct base64
            # Try direct base64 first
            if len(content) > 100 and not content.startswith("data:"):
                # Could be a raw base64 string
                try:
                    base64.b64decode(content, validate=True)
                    return content
                except Exception:
                    pass

            # Try markdown image format: ![alt](data:image/...;base64,...)
            import re
            m = re.search(r'!\[.*?\]\(data:image/[^;]+;base64,([^)]+)\)', content)
            if m:
                return m.group(1)

            # Try bare data URL
            m = re.search(r'data:image/[^;]+;base64,([^"\')\s]+)', content)
            if m:
                return m.group(1)

            # Try direct markdown link
            m = re.search(r'\((https?://[^)]+)\)', content)
            if m:
                url = m.group(1)
                logger.info("zencode returned URL, fetching: %.80s", url)
                # Download the image and base64 it
                import urllib.request
                with urllib.request.urlopen(url) as img_resp:
                    img_data = img_resp.read()
                return base64.b64encode(img_data).decode()

            # Fallback: treat entire response as base64
            cleaned = content.strip().strip('"').strip("'")
            try:
                base64.b64decode(cleaned, validate=True)
                return cleaned
            except Exception:
                pass

            raise ValueError(f"Cannot extract image from response: {content[:200]}")

        except Exception as e:
            logger.error("extract_image failed: %s | response: %.200s", e, str(response))
            raise

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


# ─── Mask Cache ──────────────────────────────────────────────────────────────

class MaskCache:
    """
    Content-addressable cache for (image_hash × prompt) combos.
    Uses diskcache for persistence across restarts with TTL eviction.
    """

    def __init__(self, cache_dir: str = CACHE_DIR, ttl: int = CACHE_TTL_SECONDS):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self._store = diskcache.Cache(str(self.cache_dir / "tweaks"), size_limit=2_000_000_000)
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[str]:
        """Return cached base64 image or None."""
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            return None

        # Check TTL
        cached_time = entry.get("ts", 0)
        if time.time() - cached_time > self.ttl:
            self._store.delete(key)
            self._misses += 1
            return None

        self._hits += 1
        logger.info("cache HIT | key=%.16s | hit_rate=%.1f%%", key, self.hit_rate * 100)
        return entry["data"]

    def set(self, key: str, base64_data: str):
        """Cache a generated result."""
        self._store.set(
            key,
            {"data": base64_data, "ts": time.time()},
            expire=self.ttl,
        )
        logger.info("cache SET | key=%.16s", key)

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def stats(self) -> dict:
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self.hit_rate, 3),
            "size_bytes": self._store.volume(),
            "entries": len(self._store),
        }

    def close(self):
        self._store.close()


# ─── Tweaks Pipeline ─────────────────────────────────────────────────────────

class TweaksPipeline:
    """
    End-to-end pipeline: receives a TweakRequest, checks cache,
    calls ZencodeClient to generate the edit, caches, and returns the result.
    """

    def __init__(
        self,
        zencode_client: Optional[ZencodeClient] = None,
        cache: Optional[MaskCache] = None,
    ):
        self.client = zencode_client or ZencodeClient()
        self.cache = cache or MaskCache()

    async def run(self, request: TweakRequest) -> TweakResult:
        """
        Execute the full tweak generation pipeline.

        1. Compute cache key from image hash + prompt
        2. Check cache — return immediately if hit
        3. Call Zencode API to generate the edit
        4. Cache the result
        5. Return TweakResult with timing metadata
        """
        start = time.time()
        cache_key = request.cache_key

        # Step 1: Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            elapsed = int((time.time() - start) * 1000)
            return TweakResult(
                image_base64=cached,
                request_id=request.request_id,
                generation_time_ms=elapsed,
                cached=True,
            )

        # Step 2: Generate via Zencode API
        try:
            result_base64 = await self.client.generate_edit(
                image_base64=request.image_base64,
                prompt=request.prompt,
            )
        except Exception as e:
            logger.error("pipeline generation failed: %s", e)
            raise

        elapsed = int((time.time() - start) * 1000)

        # Step 3: Cache result
        self.cache.set(cache_key, result_base64)

        return TweakResult(
            image_base64=result_base64,
            request_id=request.request_id,
            generation_time_ms=elapsed,
            cached=False,
        )

    async def warmup(self):
        """Pre-warm connections. Call once at startup."""
        await self.client._get_session()
        logger.info("pipeline warmed up")

    async def shutdown(self):
        """Graceful shutdown."""
        await self.client.close()
        self.cache.close()
        logger.info("pipeline shut down")


# ─── Utility ─────────────────────────────────────────────────────────────────

def validate_base64(s: str) -> bool:
    """Check if a string is valid base64."""
    try:
        if isinstance(s, str):
            s_bytes = s.encode("ascii")
        else:
            s_bytes = s
        return base64.b64decode(s_bytes, validate=True) is not None
    except Exception:
        return False


def compress_base64(base64_str: str, max_bytes: int = MAX_PAYLOAD_BYTES) -> str:
    """
    Downsize a base64 image payload if it exceeds the limit.
    Uses JPEG quality reduction to meet size constraints.
    """
    if len(base64_str) <= max_bytes:
        return base64_str

    try:
        from PIL import Image
        import io

        img_data = base64.b64decode(base64_str)
        img = Image.open(io.BytesIO(img_data))

        # Reduce quality iteratively
        for quality in [85, 70, 55, 40, 25]:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            encoded = base64.b64encode(buf.getvalue()).decode()
            if len(encoded) <= max_bytes:
                logger.info(
                    "compressed base64 %.1fKB → %.1fKB @ quality=%d",
                    len(base64_str) / 1024, len(encoded) / 1024, quality,
                )
                return encoded

        # Last resort: resize
        max_dim = 1024
        img.thumbnail((max_dim, max_dim))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=60, optimize=True)
        encoded = base64.b64encode(buf.getvalue()).decode()
        logger.info(
            "resized+compressed %.1fKB → %.1fKB",
            len(base64_str) / 1024, len(encoded) / 1024,
        )
        return encoded

    except Exception as e:
        logger.warning("image compression failed: %s — returning original", e)
        return base64_str
