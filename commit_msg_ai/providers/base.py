from __future__ import annotations
from abc import ABC, abstractmethod

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
- output language: {language}
- never include the diff or markdown code fences
- never wrap in quotes
- output ONLY the commit message
"""

def build_user_prompt(diff, scope_hint=""):
    extra = f"\n\nScope hint: {scope_hint}" if scope_hint else ""
    return f"Here is the staged diff:\n\n```diff\n{diff}\n```{extra}"

class Provider(ABC):
    @abstractmethod
    def generate(self, diff, scope_hint=""):
        raise NotImplementedError
