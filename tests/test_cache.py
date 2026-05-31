import tempfile
from pathlib import Path
from unittest.mock import patch
from commit_msg_ai import cache as cache_mod


def test_put_then_get(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "CACHE_DIR", tmp_path)
    cache_mod.put("diff text", "model-x", "sig", "feat: hi")
    assert cache_mod.get("diff text", "model-x", "sig") == "feat: hi"

def test_miss_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "CACHE_DIR", tmp_path)
    assert cache_mod.get("nope", "model-x", "sig") is None

def test_different_model_misses(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "CACHE_DIR", tmp_path)
    cache_mod.put("diff", "model-a", "sig", "feat: hi")
    assert cache_mod.get("diff", "model-b", "sig") is None

def test_clear(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "CACHE_DIR", tmp_path)
    cache_mod.put("d1", "m", "s", "msg1")
    cache_mod.put("d2", "m", "s", "msg2")
    assert cache_mod.clear() == 2
