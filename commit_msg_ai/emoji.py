"""Gitmoji-style emoji mapping for Conventional Commits types."""

from __future__ import annotations

import re

# Standard gitmoji-style mapping
EMOJI_MAP = {
    "feat": "✨",
    "fix": "🐛",
    "docs": "📝",
    "style": "💄",
    "refactor": "♻️",
    "perf": "⚡️",
    "test": "✅",
    "build": "📦",
    "ci": "👷",
    "chore": "🔧",
    "revert": "⏪",
}

# Matches "type(scope): subject" or "type: subject" at start of line
_TYPE_RE = re.compile(r"^([a-z]+)(\([^)]*\))?:\s")


def prepend_emoji(message: str) -> str:
    """Add the matching emoji to the first line of a commit message.

    Idempotent: if the line already starts with a recognized emoji, returns unchanged.
    """
    if not message:
        return message

    lines = message.splitlines()
    first = lines[0]

    # Skip if first line already starts with a known emoji
    for emoji in EMOJI_MAP.values():
        if first.startswith(emoji):
            return message

    match = _TYPE_RE.match(first)
    if not match:
        return message

    type_ = match.group(1).lower()
    emoji = EMOJI_MAP.get(type_)
    if not emoji:
        return message

    lines[0] = f"{emoji} {first}"
    return "\n".join(lines)


def options_signature(emoji: bool, language: str, include_body: bool, max_length: int) -> str:
    """Compact string of options that affect output — used for cache key."""
    return f"emoji={emoji}|lang={language}|body={include_body}|max={max_length}"
