from .base import Provider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider


def get_provider(name, config):
    name = name.lower()
    if name == "openai":
        return OpenAIProvider(config.openai, config.options)
    if name == "ollama":
        return OllamaProvider(config.ollama, config.options)
    raise ValueError(f"Unknown provider: {name!r}")

__all__ = ["Provider", "OpenAIProvider", "OllamaProvider", "get_provider"]
