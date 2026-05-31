from __future__ import annotations
from .base import Provider, SYSTEM_PROMPT, build_user_prompt

class OpenAIProvider(Provider):
    def __init__(self, openai_cfg, options):
        self.cfg = openai_cfg
        self.options = options
        if not openai_cfg.api_key:
            raise RuntimeError("OpenAI API key missing.")
        from openai import OpenAI
        self.client = OpenAI(api_key=openai_cfg.api_key, base_url=openai_cfg.base_url)

    def generate(self, diff, scope_hint=""):
        system = SYSTEM_PROMPT.format(max_length=self.options.max_length, language=self.options.language)
        if not self.options.include_body:
            system += "\n\nIMPORTANT: output ONLY the subject line."
        response = self.client.chat.completions.create(
            model=self.cfg.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": build_user_prompt(diff, scope_hint)},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
