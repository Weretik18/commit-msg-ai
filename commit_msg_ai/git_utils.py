from __future__ import annotations
import subprocess
from pathlib import Path

class GitError(RuntimeError):
    pass

def _run(args, cwd=None):
    try:
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    except FileNotFoundError as e:
        raise GitError("git not found") from e
    except subprocess.CalledProcessError as e:
        raise GitError(e.stderr.strip() or e.stdout.strip()) from e
    return result.stdout

def get_staged_diff(cwd=None):
    return _run(["diff", "--staged", "--no-color"], cwd=cwd)

def get_staged_files(cwd=None):
    out = _run(["diff", "--staged", "--name-only"], cwd=cwd)
    return [l for l in out.splitlines() if l.strip()]

def get_repo_root(cwd=None):
    return Path(_run(["rev-parse", "--show-toplevel"], cwd=cwd).strip())

def truncate_diff(diff, max_chars=12000):
    if len(diff) <= max_chars:
        return diff
    return diff[:max_chars-200] + f"\n\n... [truncated, was {len(diff)} chars] ..."
