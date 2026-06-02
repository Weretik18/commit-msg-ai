"""Tests for cli.py subcommands: install-hook, uninstall-hook, clear-cache."""

from __future__ import annotations

from unittest.mock import patch

from click.testing import CliRunner

from commit_msg_ai.cli import HOOK_SCRIPT, main
from commit_msg_ai.git_utils import GitError

# ---------- install-hook ----------


def test_install_hook_writes_script(tmp_path):
    runner = CliRunner()
    with patch("commit_msg_ai.cli.get_repo_root", return_value=tmp_path):
        (tmp_path / ".git").mkdir()
        result = runner.invoke(main, ["install-hook"])
    assert result.exit_code == 0
    hook = tmp_path / ".git" / "hooks" / "prepare-commit-msg"
    assert hook.exists()
    assert hook.read_text(encoding="utf-8") == HOOK_SCRIPT
    assert "installed hook" in result.output


def test_install_hook_creates_hooks_dir_if_missing(tmp_path):
    runner = CliRunner()
    with patch("commit_msg_ai.cli.get_repo_root", return_value=tmp_path):
        # .git/hooks does NOT exist yet
        result = runner.invoke(main, ["install-hook"])
    assert result.exit_code == 0
    assert (tmp_path / ".git" / "hooks" / "prepare-commit-msg").exists()


def test_install_hook_git_error_exits_1():
    runner = CliRunner()
    with patch("commit_msg_ai.cli.get_repo_root", side_effect=GitError("not in repo")):
        result = runner.invoke(main, ["install-hook"])
    assert result.exit_code == 1
    assert "not in repo" in result.output


def test_install_hook_chmod_failure_swallowed(tmp_path):
    """chmod can fail on Windows; install should still succeed."""
    runner = CliRunner()
    with (
        patch("commit_msg_ai.cli.get_repo_root", return_value=tmp_path),
        patch("pathlib.Path.chmod", side_effect=OSError("no chmod on windows")),
    ):
        result = runner.invoke(main, ["install-hook"])
    assert result.exit_code == 0
    assert (tmp_path / ".git" / "hooks" / "prepare-commit-msg").exists()


# ---------- uninstall-hook ----------


def test_uninstall_hook_removes_existing(tmp_path):
    runner = CliRunner()
    hooks = tmp_path / ".git" / "hooks"
    hooks.mkdir(parents=True)
    hook = hooks / "prepare-commit-msg"
    hook.write_text("dummy", encoding="utf-8")
    with patch("commit_msg_ai.cli.get_repo_root", return_value=tmp_path):
        result = runner.invoke(main, ["uninstall-hook"])
    assert result.exit_code == 0
    assert not hook.exists()
    assert "removed" in result.output


def test_uninstall_hook_when_not_installed(tmp_path):
    runner = CliRunner()
    with patch("commit_msg_ai.cli.get_repo_root", return_value=tmp_path):
        result = runner.invoke(main, ["uninstall-hook"])
    assert result.exit_code == 0
    assert "no hook installed" in result.output


def test_uninstall_hook_git_error_exits_1():
    runner = CliRunner()
    with patch("commit_msg_ai.cli.get_repo_root", side_effect=GitError("bad repo")):
        result = runner.invoke(main, ["uninstall-hook"])
    assert result.exit_code == 1
    assert "bad repo" in result.output


# ---------- clear-cache ----------


def test_clear_cache_reports_count():
    runner = CliRunner()
    with patch("commit_msg_ai.cli.cache_mod.clear", return_value=7):
        result = runner.invoke(main, ["clear-cache"])
    assert result.exit_code == 0
    assert "cleared 7" in result.output


def test_clear_cache_zero_entries():
    runner = CliRunner()
    with patch("commit_msg_ai.cli.cache_mod.clear", return_value=0):
        result = runner.invoke(main, ["clear-cache"])
    assert result.exit_code == 0
    assert "cleared 0" in result.output
