from __future__ import annotations
import sys
from pathlib import Path
import click
from . import __version__
from .config import load_config
from .git_utils import GitError, get_repo_root, get_staged_diff, truncate_diff
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

@click.group(invoke_without_command=True)
@click.option("--provider")
@click.option("--model")
@click.option("--no-body", "no_body", is_flag=True)
@click.option("--scope", default="")
@click.option("--language")
@click.option("--dry-run", is_flag=True)
@click.version_option(__version__, prog_name="commit-msg-ai")
@click.pass_context
def main(ctx, provider, model, no_body, scope, language, dry_run):
    if ctx.invoked_subcommand is not None:
        return
    try:
        diff = get_staged_diff()
    except GitError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
    if not diff.strip():
        click.echo("error: nothing is staged. run `git add` first.", err=True)
        sys.exit(1)
    diff = truncate_diff(diff)
    if dry_run:
        click.echo(diff)
        return
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
    try:
        prov = get_provider(cfg.provider, cfg)
        message = prov.generate(diff, scope_hint=scope)
    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(2)
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

if __name__ == "__main__":
    main()
