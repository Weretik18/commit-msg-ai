from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

CONFIG_PATH = Path.home() / ".commit-msg-ai" / "config.yaml"

@dataclass
class OpenAIConfig:
    api_key: str = ""
    model: str = "gpt-4o-mini"
    base_url: str = "https://api.openai.com/v1"

@dataclass
class OllamaConfig:
    host: str = "http://localhost:11434"
    model: str = "llama3.2"

@dataclass
class Options:
    max_length: int = 72
    include_body: bool = True
    language: str = "en"
    scope_hints: str = ""

@dataclass
class Config:
    provider: str = "openai"
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    options: Options = field(default_factory=Options)

def load_config(path: Path | None = None) -> Config:
    path = path or CONFIG_PATH
    if not path.exists():
        return Config()
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    cfg = Config(
        provider=raw.get("provider", "openai"),
        openai=OpenAIConfig(**raw.get("openai", {})),
        ollama=OllamaConfig(**raw.get("ollama", {})),
        options=Options(**raw.get("options", {})),
    )
    if not cfg.openai.api_key:
        cfg.openai.api_key = os.environ.get("OPENAI_API_KEY", "")
    return cfg
