from __future__ import annotations
import requests
from .base import Provider, SYSTEM_PROMPT, build_user_prompt

class OllamaProvider(Provider):
    def __init__(self, ollama_cfg, options):
        self.cfg = ollama_cfg
        self.options = options

    def generate(self, diff, scope_hint=""):
        system = SYSTEM_PROMPT.format(max_length=self.options.max_length, language=self.options.language)
        if not self.options.include_body:
            system += "\n\nIMPORTANT: output ONLY the subject line."
        url = f"{self.cfg.host.rstrip('/')}/api/chat"
        payload = {
            "model": self.cfg.model,
            "stream": False,
            "options": {"temperature": 0.3},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": build_user_prompt(diff, scope_hint)},
            ],
        }
        try:
            r = requests.post(url, json=payload, timeout=120)
            r.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to reach Ollama at {self.cfg.host}: {e}") from e
        return r.json()["message"]["content"].strip()
