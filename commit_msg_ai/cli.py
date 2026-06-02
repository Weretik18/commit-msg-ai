"""CLI."""

from __future__ import annotations

import sys

import click

from . import __version__
from . import cache as cache_mod
from . import emoji as emoji_mod
from . import interactive as interactive_mod
from .config import load_config
from .git_utils import (
    GitError,
    get_last_commit_diff,
    get_repo_root,
    get_staged_diff,
    truncate_diff,
)
from .providers import get_provider

HOOK_SCRIPT = """#!/usr/bin/env bash
COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2
if [ -n "$COMMIT_SOURCE" ]; then exit 0; fi
if [ -s "$COMMIT_MSG_FILE" ] && grep -qv '^#' "$COMMIT_MSG_FILE"; then exit 0; fi
GENERATED=$(commit-msg-ai 2>/dev/null) || exit 0
if [ -n "$GENERATED" ]; then
    printf '%s\n\n%s' "$GENERATED" "$(cat "$COMMIT_MSG_FILE")" > "$COMMIT_MSG_FILE"
fi
"""


def _resolve_model(cfg):
    return cfg.openai.model if cfg.provider == "openai" else cfg.ollama.model


def _build_options_sig(cfg, use_emoji):
    return emoji_mod.options_signature(
        emoji=use_emoji,
        language=cfg.options.language,
        include_body=cfg.options.include_body,
        max_length=cfg.options.max_length,
    )


def _post_process(message, use_emoji):
    if use_emoji:
        message = emoji_mod.prepend_emoji(message)
    return message


@click.group(invoke_without_command=True)
@click.option("--provider", help="Override provider (openai|ollama).")
@click.option("--model", help="Override model name.")
@click.option("--no-body", "no_body", is_flag=True, help="Subject line only.")
@click.option("--scope", default="", help="Scope hint.")
@click.option("--lang", "language", help="Output language (overrides config).")
@click.option("--emoji/--no-emoji", default=None, help="Prepend gitmoji to commit type.")
@click.option("--interactive", "-i", is_flag=True, help="Generate 3 options and let you pick.")
@click.option(
    "--amend", is_flag=True, help="Generate from last commit's diff (for git commit --amend)."
)
@click.option("--no-cache", is_flag=True, help="Skip cache (always call the model).")
@click.option("--dry-run", is_flag=True, help="Print diff and exit.")
@click.version_option(__version__, prog_name="commit-msg-ai")
@click.pass_context
def main(
    ctx, provider, model, no_body, scope, language, emoji, interactive, amend, no_cache, dry_run
):
    if ctx.invoked_subcommand is not None:
        return

    # Get diff (staged by default, or last commit if --amend)
    try:
        if amend:
            diff = get_last_commit_diff()
            if not diff.strip():
                click.echo("error: last commit has no diff (initial commit?).", err=True)
                sys.exit(1)
        else:
            diff = get_staged_diff()
            if not diff.strip():
                click.echo("error: nothing is staged. run `git add` first.", err=True)
                sys.exit(1)
    except GitError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)

    diff = truncate_diff(diff)

    if dry_run:
        click.echo(diff)
        return

    # Load + override config
    cfg = load_config()
    if provider:
        cfg.provider = provider
    if model:
        if cfg.provider == "openai":
            cfg.openai.model = model
        else:
            cfg.ollama.model = model
    if no_body:
        cfg.options.include_body = False
    if language:
        cfg.options.language = language

    use_emoji = emoji if emoji is not None else False

    resolved_model = _resolve_model(cfg)
    options_sig = _build_options_sig(cfg, use_emoji)

    # Cache lookup (single-message mode only — not for interactive)
    if not interactive and not no_cache:
        cached = cache_mod.get(diff, resolved_model, options_sig)
        if cached:
            click.echo(cached)
            return

    try:
        prov = get_provider(cfg.provider, cfg)

        if interactive:

            def _gen_many():
                raw = prov.generate_many(diff, scope_hint=scope, n=3)
                return [_post_process(m, use_emoji) for m in raw]

            candidates = _gen_many()
            chosen = interactive_mod.choose(candidates, regenerate_fn=_gen_many)
            if chosen is None:
                click.echo("aborted.", err=True)
                sys.exit(130)
            message = chosen
        else:
            raw = prov.generate(diff, scope_hint=scope)
            message = _post_process(raw, use_emoji)

    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(2)

    # Store in cache (skip interactive — user already saw options)
    if not interactive and not no_cache:
        try:
            cache_mod.put(diff, resolved_model, options_sig, message)
        except Exception:
            pass

    click.echo(message)


@main.command("install-hook")
def install_hook():
    try:
        root = get_repo_root()
    except GitError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
    hook_path = root / ".git" / "hooks" / "prepare-commit-msg"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(HOOK_SCRIPT, encoding="utf-8")
    try:
        hook_path.chmod(0o755)
    except Exception:
        pass
    click.echo(f"installed hook at {hook_path}")


@main.command("uninstall-hook")
def uninstall_hook():
    try:
        root = get_repo_root()
    except GitError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
    hook_path = root / ".git" / "hooks" / "prepare-commit-msg"
    if hook_path.exists():
        hook_path.unlink()
        click.echo(f"removed {hook_path}")
    else:
        click.echo("no hook installed")


@main.command("clear-cache")
def clear_cache():
    removed = cache_mod.clear()
    click.echo(f"cleared {removed} cached entries.")


if __name__ == "__main__":
    main()
