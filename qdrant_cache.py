"""
Qdrant Semantic Cache for Luxor Fashion Omega Backend
=====================================================
Drop this file into your Replit project alongside main.py.

Uses MD5 image hashing (lightweight, no GPU/RAM needed) to cache
Atomesus analysis results in Qdrant Cloud free tier.

Environment variables (set in Replit Secrets):
  QDRANT_URL      — Qdrant Cloud cluster URL (e.g. https://xxxx.us-east-1-0.aws.cloud.qdrant.io:6333)
  QDRANT_API_KEY  — Qdrant Cloud API key

If either is missing, caching is silently disabled.
"""

import os
import logging
import hashlib
import uuid
import base64
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger("luxor-qdrant")

# ──────────────────────────────────────────────
#  Lazy Qdrant client (only init if env vars set)
# ──────────────────────────────────────────────
_qdrant_client = None
_collection_name = "luxor_outfits"


def _ensure_collection(client):
    """Create the collection + payload index if they don't exist."""
    from qdrant_client.http import models
    from qdrant_client.http.exceptions import UnexpectedResponse

    collections = client.get_collections()
    names = [c.name for c in collections.collections]

    if _collection_name not in names:
        logger.info("[QDRANT] Creating collection '%s'", _collection_name)
        client.create_collection(
            collection_name=_collection_name,
            vectors_config=models.VectorParams(
                size=4,
                distance=models.Distance.COSINE,
            ),
        )

    # Ensure payload index on image_hash for fast lookups
    try:
        client.create_payload_index(
            collection_name=_collection_name,
            field_name="image_hash",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
    except UnexpectedResponse as e:
        # Index already exists — not an error
        if "already exists" not in str(e).lower():
            raise


def _get_qdrant_client():
    """Return the singleton Qdrant client, or None if not configured/available."""
    global _qdrant_client
    if _qdrant_client is not None:
        return _qdrant_client

    url = os.environ.get("QDRANT_URL", "").strip()
    api_key = os.environ.get("QDRANT_API_KEY", "").strip()

    if not url or not api_key:
        logger.warning("[QDRANT] QDRANT_URL or QDRANT_API_KEY not set — caching disabled")
        _qdrant_client = False  # sentinel
        return None

    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(url=url, api_key=api_key, timeout=10)
        _ensure_collection(client)
        _qdrant_client = client
        logger.info("[QDRANT] Connected to Qdrant Cloud successfully")
        return client

    except Exception as exc:
        logger.warning("[QDRANT] Failed to connect: %s — caching disabled", exc)
        _qdrant_client = False
        return None


# ──────────────────────────────────────────────
#  Hash helpers
# ──────────────────────────────────────────────

def image_hash(image_b64: str) -> str:
    """
    Generate a deterministic MD5 hash from the raw image BYTES.

    We hash the DECODED binary, not the base64 string, because
    base64 whitespace/encoding variations would produce different
    hashes for the same image.

    If image_b64 is a data-URL (with a leading data:image/...;base64, prefix),
    this function strips it automatically.
    """
    raw = image_b64
    if "," in raw:
        raw = raw.split(",", 1)[1]
    try:
        binary = base64.b64decode(raw)
    except Exception:
        binary = raw.encode()
    return hashlib.md5(binary).hexdigest()


# ──────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────

def check_cache(image_b64: str) -> Optional[Dict[str, Any]]:
    """
    Look up an image by its hash in Qdrant.

    Returns the cached analysis JSON (dict) on a hit, or None on a miss.
    Returns None if Qdrant is unreachable (caller should proceed normally).
    """
    client = _get_qdrant_client()
    if not client:
        return None

    try:
        from qdrant_client.http import models

        h = image_hash(image_b64)
        logger.info("[QDRANT] Checking cache for hash %s", h[:12])

        result = client.scroll(
            collection_name=_collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="image_hash",
                        match=models.MatchValue(value=h),
                    )
                ]
            ),
            limit=1,
            with_payload=True,
        )

        points = result[0] if isinstance(result, tuple) else result
        if points and len(points) > 0:
            payload = points[0].payload
            logger.info("[QDRANT] CACHE HIT for hash %s", h[:12])
            return dict(payload.get("analysis_json", {}))

        logger.info("[QDRANT] CACHE MISS for hash %s", h[:12])
        return None

    except Exception as exc:
        logger.warning("[QDRANT] Cache check failed: %s — skipping", exc)
        return None


def write_cache(image_b64: str, analysis_json: Dict[str, Any]) -> bool:
    """
    Store a successful analysis result in Qdrant.

    Returns True on success, False if Qdrant is offline or write fails.
    The caller should NEVER fail based on this return value.
    """
    client = _get_qdrant_client()
    if not client:
        return False

    try:
        from qdrant_client.http import models

        h = image_hash(image_b64)
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, h))

        client.upsert(
            collection_name=_collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=[0.0, 0.0, 0.0, 0.0],
                    payload={
                        "image_hash": h,
                        "analysis_json": analysis_json,
                        "created_at": datetime.utcnow().isoformat(),
                    },
                )
            ],
        )
        logger.info("[QDRANT] Cached hash %s", h[:12])
        return True

    except Exception as exc:
        logger.warning("[QDRANT] Cache write failed: %s", exc)
        return False
