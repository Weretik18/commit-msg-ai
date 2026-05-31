# commit-msg-ai

AI-generated Conventional Commit messages from your staged Git diff.

Works with local models via [Ollama](https://ollama.com) (free, private) or OpenAI (paid).

## Features

- ✨ **Conventional Commits** — `feat`, `fix`, `docs`, `refactor`, etc.
- 🎨 **Gitmoji support** — `✨ feat:`, `🐛 fix:`, `📝 docs:` with `--emoji`
- 🎲 **Interactive mode** — generate 3 options, pick the best with `--interactive`
- 💾 **Smart caching** — re-running on the same diff is instant
- 📊 **Amend support** — regenerate message for last commit with `--amend`
- 🌍 **Multi-language** — `--lang ru`, `--lang en`, anything the model understands
- 🪝 **Git hook** — auto-generate on every `git commit`
- 🔌 **Two providers** — Ollama (local) or OpenAI (API)

## Install

```bash
git clone https://github.com/Weretik18/commit-msg-ai.git
cd commit-msg-ai
pip install -e .
```

Then create a config:
```bash
mkdir -p ~/.commit-msg-ai
cp config.example.yaml ~/.commit-msg-ai/config.yaml
```

## Quick start (Ollama, recommended)

1. Install [Ollama](https://ollama.com)
2. Pull a coding model: `ollama pull qwen2.5-coder:7b`
3. Edit `~/.commit-msg-ai/config.yaml` to use that model
4. Stage changes and run:

```bash
git add .
commit-msg-ai
```

## Usage

```bash
# Default: generate one commit message
commit-msg-ai

# With emoji
commit-msg-ai --emoji

# Pick from 3 options
commit-msg-ai --interactive

# In Russian
commit-msg-ai --lang ru

# Regenerate for last commit (use with git commit --amend)
commit-msg-ai --amend

# Skip cache (always call the model)
commit-msg-ai --no-cache

# Subject line only, no body
commit-msg-ai --no-body

# Pipe straight into git
commit-msg-ai | git commit -F -
```

## Git hook (automatic mode)

```bash
commit-msg-ai install-hook
```

Now every `git commit` will pre-fill the commit message editor with an AI-generated one.

To remove:
```bash
commit-msg-ai uninstall-hook
```

## Commands

| Command | What it does |
|---|---|
| `commit-msg-ai` | Generate a commit message |
| `commit-msg-ai install-hook` | Install prepare-commit-msg hook |
| `commit-msg-ai uninstall-hook` | Remove the hook |
| `commit-msg-ai clear-cache` | Delete all cached messages |
| `commit-msg-ai --version` | Show version |

## Config

`~/.commit-msg-ai/config.yaml`:

```yaml
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
```

## License

MIT
