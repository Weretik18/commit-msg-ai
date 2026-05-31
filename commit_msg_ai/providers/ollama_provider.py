"""Ollama provider."""
from __future__ import annotations

import requests

from .base import SYSTEM_PROMPT, Provider, build_user_prompt, resolve_language


class OllamaProvider(Provider):
    def __init__(self, ollama_cfg, options):
        self.cfg = ollama_cfg
        self.options = options
        self.language = resolve_language(options.language)

    def _build_system(self):
        system = SYSTEM_PROMPT.format(
            max_length=self.options.max_length,
            language=self.language,
        )
        if not self.options.include_body:
            system += "\n\nIMPORTANT: include_body is false — output ONLY the subject line."
        return system

    def _call(self, diff, scope_hint, temperature):
        url = f"{self.cfg.host.rstrip('/')}/api/chat"
        payload = {
            "model": self.cfg.model,
            "stream": False,
            "options": {"temperature": temperature},
            "messages": [
                {"role": "system", "content": self._build_system()},
                {"role": "user", "content": build_user_prompt(diff, scope_hint, self.language)},
            ],
        }
        try:
            r = requests.post(url, json=payload, timeout=180)
            r.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(
                f"Failed to reach Ollama at {self.cfg.host}. "
                f"Is `ollama serve` running? Underlying error: {e}"
            ) from e
        return r.json()["message"]["content"].strip()

    def generate(self, diff, scope_hint=""):
        return self._call(diff, scope_hint, temperature=0.3)

    def generate_many(self, diff, scope_hint="", n=3):
        """Generate N variants via N calls with high temperature for diversity."""
        results = []
        for _ in range(n):
            results.append(self._call(diff, scope_hint, temperature=0.8))
        # Keep all results — even similar ones — so interactive menu always has options
        return results
