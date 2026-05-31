"""OpenAI provider."""
from __future__ import annotations

from .base import Provider, SYSTEM_PROMPT, build_user_prompt, resolve_language


class OpenAIProvider(Provider):
    def __init__(self, openai_cfg, options):
        self.cfg = openai_cfg
        self.options = options
        self.language = resolve_language(options.language)

        if not openai_cfg.api_key:
            raise RuntimeError(
                "OpenAI API key missing. Set it in config.yaml or via OPENAI_API_KEY env var."
            )

        from openai import OpenAI
        self.client = OpenAI(api_key=openai_cfg.api_key, base_url=openai_cfg.base_url)

    def _build_system(self):
        system = SYSTEM_PROMPT.format(
            max_length=self.options.max_length,
            language=self.language,
        )
        if not self.options.include_body:
            system += "\n\nIMPORTANT: include_body is false — output ONLY the subject line."
        return system

    def generate(self, diff, scope_hint=""):
        response = self.client.chat.completions.create(
            model=self.cfg.model,
            messages=[
                {"role": "system", "content": self._build_system()},
                {"role": "user", "content": build_user_prompt(diff, scope_hint, self.language)},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()

    def generate_many(self, diff, scope_hint="", n=3):
        response = self.client.chat.completions.create(
            model=self.cfg.model,
            messages=[
                {"role": "system", "content": self._build_system()},
                {"role": "user", "content": build_user_prompt(diff, scope_hint, self.language)},
            ],
            temperature=0.7,
            max_tokens=300,
            n=n,
        )
        return [c.message.content.strip() for c in response.choices]
