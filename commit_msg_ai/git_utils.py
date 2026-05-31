"""Git helpers."""
from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


def _run(args, cwd=None):
    try:
        result = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, check=True,
        )
    except FileNotFoundError as e:
        raise GitError("git executable not found on PATH") from e
    except subprocess.CalledProcessError as e:
        raise GitError(e.stderr.strip() or e.stdout.strip()) from e
    return result.stdout


def get_staged_diff(cwd=None):
    return _run(["diff", "--staged", "--no-color"], cwd=cwd)


def get_staged_files(cwd=None):
    out = _run(["diff", "--staged", "--name-only"], cwd=cwd)
    return [line for line in out.splitlines() if line.strip()]


def get_last_commit_diff(cwd=None):
    """Get diff of the most recent commit (for --amend mode)."""
    return _run(["show", "HEAD", "--no-color", "--pretty=format:"], cwd=cwd)


def get_repo_root(cwd=None):
    return Path(_run(["rev-parse", "--show-toplevel"], cwd=cwd).strip())


def truncate_diff(diff, max_chars=12000):
    if len(diff) <= max_chars:
        return diff
    head = diff[: max_chars - 200]
    return head + f"\n\n... [diff truncated, original was {len(diff)} chars] ..."
