# gitmsg-ai

[![CI](https://github.com/Weretik18/commit-msg-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/Weretik18/commit-msg-ai/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/gitmsg-ai.svg)](https://pypi.org/project/gitmsg-ai/)
[![Python versions](https://img.shields.io/pypi/pyversions/gitmsg-ai.svg)](https://pypi.org/project/gitmsg-ai/)
[![Downloads](https://img.shields.io/pypi/dm/gitmsg-ai.svg)](https://pypi.org/project/gitmsg-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-generated Conventional Commit messages from your staged Git diff.

Works with local models via [Ollama](https://ollama.com) (free, private) or OpenAI (paid).

> 📦 Previously published as `commit-msg-ai`. Both CLI commands (`gitmsg-ai` and `commit-msg-ai`) work for backwards compatibility.

## Features

- ✨ **Conventional Commits** — `feat`, `fix`, `docs`, `refactor`, etc.
- 🎨 **Gitmoji support** — `✨ feat:`, `🐛 fix:`, `📝 docs:` with `--emoji`
- 🎲 **Interactive mode** — generate 3 options, pick the best with `--interactive`
- 💾 **Smart caching** — re-running on the same diff is instant
- 📊 **Amend support** — regenerate message for last commit with `--amend`
- 🌍 **Multi-language** — `--lang ru`, `--lang en`, 16+ languages
- 🪝 **Git hook** — auto-generate on every `git commit`
- 🔌 **Two providers** — Ollama (local) or OpenAI (API)

## Install

### From PyPI (recommended)

```bash

pip install gitmsg-ai
From source

git clone https://github.com/Weretik18/commit-msg-ai.git

cd commit-msg-ai

pip install -e .
Then create a config:


mkdir -p ~/.commit-msg-ai

cp config.example.yaml ~/.commit-msg-ai/config.yaml
Quick start (Ollama, recommended)
Install Ollama
Pull a coding model: ollama pull qwen2.5-coder:7b
Edit ~/.commit-msg-ai/config.yaml to use that model
Stage changes and run:

git add .

gitmsg-ai
Usage
undefined
Default: generate one commit message
gitmsg-ai

With emoji
gitmsg-ai --emoji

Pick from 3 options
gitmsg-ai --interactive

In Russian
gitmsg-ai --lang ru

Regenerate for last commit (use with git commit --amend)
gitmsg-ai --amend

Skip cache (always call the model)
gitmsg-ai --no-cache

Subject line only, no body
gitmsg-ai --no-body

Pipe straight into git
gitmsg-ai | git commit -F -


## Git hook (automatic mode)

```bash

gitmsg-ai install-hook
Now every git commit will pre-fill the commit message editor with an AI-generated one.

To remove:


gitmsg-ai uninstall-hook
Commands
Command	What it does
gitmsg-ai	Generate a commit message
gitmsg-ai install-hook	Install prepare-commit-msg hook
gitmsg-ai uninstall-hook	Remove the hook
gitmsg-ai clear-cache	Delete all cached messages
gitmsg-ai --version	Show version
Config
~/.commit-msg-ai/config.yaml:


provider: ollama  # or "openai"



ollama:

  host: http://localhost:11434

  model: qwen2.5-coder:7b



openai:

  api_key: ""  # or set OPENAI_API_KEY env var

  model: gpt-4o-mini



options:

  max_length: 72

  include_body: true

  language: en
Development
undefined
Clone and install in dev mode
git clone https://github.com/Weretik18/commit-msg-ai.git

cd commit-msg-ai

pip install -e ".[dev]"

Run tests
pytest tests/ -v

Lint
ruff check commit_msg_ai/ tests/


## License

MIT — see [LICENSE](LICENSE) for details.