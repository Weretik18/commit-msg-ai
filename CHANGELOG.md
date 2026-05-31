# Changelog

## [0.2.4] - 2026-06-01

### Fixed
- `__version__` is now read dynamically from package metadata via `importlib.metadata`, so `gitmsg-ai --version` always matches the installed package version
- Removed hardcoded version string in `commit_msg_ai/__init__.py` that was stuck at 0.2.2

## [0.2.3] - 2026-06-01

### Fixed
- README: corrected PyPI badges and install instructions to use `gitmsg-ai` package name
- Cleaned up references mixing old (`commit-msg-ai`) and new (`gitmsg-ai`) package names

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2026-06-01

### Added
- 📦 Published to PyPI as `gitmsg-ai`
- 🚀 GitHub Actions CI/CD with PyPI Trusted Publishing
- 🧪 CI runs lint (ruff) + tests (pytest) on Python 3.10, 3.11, 3.12 across Ubuntu/macOS/Windows
- 🏷️ Auto-publish to PyPI on git tag push (`v*`)

### Changed
- 📛 Renamed package from `commit-msg-ai` to `gitmsg-ai` (PyPI name was taken)
- 🔧 Both CLI commands (`gitmsg-ai` and `commit-msg-ai`) work for backwards compatibility

### Fixed
- 🪟 Windows console encoding (cp1251 → UTF-8) for emoji and Cyrillic output
- 🌍 Russian language mapping (`--lang ru`) now correctly uses Russian in prompts

## [0.2.1] - 2026-05-31

### Fixed
- 🐛 Russian language code mapping in prompt templates
- 🪟 Windows encoding issues when piping output

## [0.2.0] - 2026-05-31

### Added
- 🌍 `--lang` flag for multi-language commit messages (16+ languages)
- 🎨 `--emoji` / `--no-emoji` for gitmoji prefixes
- 🎲 `-i` / `--interactive` mode — generate 3 options, pick the best
- 📊 `--amend` flag — regenerate message for last commit
- 💾 Smart caching with `--no-cache` opt-out
- `clear-cache` command

## [0.1.0] - 2026-05-31

### Added
- ✨ Initial release
- Conventional Commits generation from staged Git diff
- Ollama (local) and OpenAI providers
- `install-hook` / `uninstall-hook` commands for Git integration
- `--scope`, `--no-body`, `--dry-run`, `--provider`, `--model` flags

[0.2.2]: https://github.com/Weretik18/commit-msg-ai/releases/tag/v0.2.2
[0.2.1]: https://github.com/Weretik18/commit-msg-ai/releases/tag/v0.2.1
[0.2.0]: https://github.com/Weretik18/commit-msg-ai/releases/tag/v0.2.0
[0.1.0]: https://github.com/Weretik18/commit-msg-ai/releases/tag/v0.1.0