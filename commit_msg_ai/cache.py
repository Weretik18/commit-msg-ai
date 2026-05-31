"""Diff-based cache to avoid re-generating identical commits."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".commit-msg-ai" / "cache"
CACHE_TTL_SECONDS = 60 * 60 * 24 * 7  # 1 week


def _hash_diff(diff: str, model: str, options_signature: str) -> str:
    """Hash diff + model + relevant options so cache invalidates on settings change."""
    h = hashlib.sha256()
    h.update(diff.encode("utf-8"))
    h.update(b"|")
    h.update(model.encode("utf-8"))
    h.update(b"|")
    h.update(options_signature.encode("utf-8"))
    return h.hexdigest()


def _cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"


def get(diff: str, model: str, options_signature: str) -> str | None:
    """Return cached message or None if miss/expired."""
    key = _hash_diff(diff, model, options_signature)
    path = _cache_path(key)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if time.time() - data.get("ts", 0) > CACHE_TTL_SECONDS:
        try:
            path.unlink()
        except Exception:
            pass
        return None
    return data.get("message")


def put(diff: str, model: str, options_signature: str, message: str) -> None:
    """Store generated message in cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = _hash_diff(diff, model, options_signature)
    path = _cache_path(key)
    payload = {"ts": time.time(), "message": message, "model": model}
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def clear() -> int:
    """Delete all cached entries. Returns number of files removed."""
    if not CACHE_DIR.exists():
        return 0
    count = 0
    for p in CACHE_DIR.glob("*.json"):
        try:
            p.unlink()
            count += 1
        except Exception:
            pass
    return count
