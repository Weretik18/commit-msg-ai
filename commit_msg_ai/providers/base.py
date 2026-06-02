"""Provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

# Map common language codes/names to their full English name.
# Models follow instructions much better when the language is named explicitly
# in English rather than passed as a 2-letter code like "ru".
LANGUAGE_NAMES = {
    "en": "English",
    "ru": "Russian",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "zh": "Chinese",
    "ko": "Korean",
    "uk": "Ukrainian",
    "pl": "Polish",
    "tr": "Turkish",
    "nl": "Dutch",
    "ar": "Arabic",
    "hi": "Hindi",
}


def resolve_language(lang):
    """Convert a language code or name into a model-friendly English name."""
    if not lang:
        return "English"
    key = lang.strip().lower()
    if key in LANGUAGE_NAMES:
        return LANGUAGE_NAMES[key]
    # Already a full name like "Russian" — return capitalized as-is
    return lang.strip().capitalize()


SYSTEM_PROMPT = """You are an expert at writing concise, accurate Git commit messages.

Given a unified diff of staged changes, output a single commit message in
Conventional Commits format:

    <type>(<optional scope>): <subject>

    <optional body explaining WHY, wrapped at 72 chars>

Rules:
- type must be one of: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
- subject line: imperative mood, no trailing period, max {max_length} chars
- if include_body is true and the change is non-trivial, add a short body
- if include_body is false, output ONLY the subject line
- never include the diff or markdown code fences
- never wrap in quotes or backticks
- never add commentary, explanations, or notes before/after the message
- output ONLY the commit message — nothing else

CRITICAL LANGUAGE REQUIREMENT:
You MUST write the entire commit message (subject AND body) in {language}.
The Conventional Commit TYPE keyword (feat/fix/docs/etc.) stays in English,
but the SUBJECT TEXT after the colon and the BODY must be written in {language}.

Example if language is Russian:
    feat(auth): добавить валидацию пароля

    Усилена проверка пароля при регистрации пользователя.

Example if language is English:
    feat(auth): add password validation

    Strengthen password checks during user registration.

Do not write the subject or body in English unless {language} is English.
"""


def build_user_prompt(diff, scope_hint="", language="English"):
    extra = f"\n\nSuggested scope hint: {scope_hint}" if scope_hint else ""
    lang_reminder = (
        f"\n\nReminder: write the commit message in {language}."
        if language.lower() != "english"
        else ""
    )
    return f"Here is the staged diff:\n\n```diff\n{diff}\n```{extra}{lang_reminder}"


class Provider(ABC):
    @abstractmethod
    def generate(self, diff, scope_hint=""):
        raise NotImplementedError
