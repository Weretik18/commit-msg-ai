"""Tests for cli.py main command and helpers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from commit_msg_ai.cli import _build_options_sig, _post_process, _resolve_model, main
from commit_msg_ai.git_utils import GitError

# ---------- helpers ----------


def _make_cfg(
    provider="openai",
    openai_model="gpt-4",
    ollama_model="llama3",
    language="en",
    include_body=True,
    max_length=72,
):
    cfg = MagicMock()
    cfg.provider = provider
    cfg.openai.model = openai_model
    cfg.ollama.model = ollama_model
    cfg.options.language = language
    cfg.options.include_body = include_body
    cfg.options.max_length = max_length
    return cfg


# ---------- _resolve_model ----------


def test_resolve_model_openai():
    cfg = _make_cfg(provider="openai", openai_model="gpt-4o")
    assert _resolve_model(cfg) == "gpt-4o"


def test_resolve_model_ollama():
    cfg = _make_cfg(provider="ollama", ollama_model="llama3.1")
    assert _resolve_model(cfg) == "llama3.1"


# ---------- _build_options_sig ----------


def test_build_options_sig_calls_emoji_module():
    cfg = _make_cfg(language="ru", include_body=False, max_length=50)
    with patch("commit_msg_ai.cli.emoji_mod.options_signature", return_value="SIG") as sig:
        result = _build_options_sig(cfg, use_emoji=True)
    assert result == "SIG"
    sig.assert_called_once_with(emoji=True, language="ru", include_body=False, max_length=50)


# ---------- _post_process ----------


def test_post_process_with_emoji():
    with patch("commit_msg_ai.cli.emoji_mod.prepend_emoji", return_value="🎨 feat: x") as p:
        result = _post_process("feat: x", use_emoji=True)
    assert result == "🎨 feat: x"
    p.assert_called_once_with("feat: x")


def test_post_process_without_emoji():
    with patch("commit_msg_ai.cli.emoji_mod.prepend_emoji") as p:
        result = _post_process("feat: x", use_emoji=False)
    assert result == "feat: x"
    p.assert_not_called()


# ---------- main: diff acquisition ----------


def test_main_no_staged_diff_exits_1():
    runner = CliRunner()
    with patch("commit_msg_ai.cli.get_staged_diff", return_value="   \n  "):
        result = runner.invoke(main, [])
    assert result.exit_code == 1
    assert "nothing is staged" in result.output


def test_main_amend_no_diff_exits_1():
    runner = CliRunner()
    with patch("commit_msg_ai.cli.get_last_commit_diff", return_value=""):
        result = runner.invoke(main, ["--amend"])
    assert result.exit_code == 1
    assert "last commit has no diff" in result.output


def test_main_git_error_exits_1():
    runner = CliRunner()
    with patch("commit_msg_ai.cli.get_staged_diff", side_effect=GitError("not a repo")):
        result = runner.invoke(main, [])
    assert result.exit_code == 1
    assert "not a repo" in result.output


def test_main_amend_git_error_exits_1():
    runner = CliRunner()
    with patch("commit_msg_ai.cli.get_last_commit_diff", side_effect=GitError("bad amend")):
        result = runner.invoke(main, ["--amend"])
    assert result.exit_code == 1
    assert "bad amend" in result.output


# ---------- main: dry-run ----------


def test_main_dry_run_prints_diff_and_exits():
    runner = CliRunner()
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff content"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
    ):
        result = runner.invoke(main, ["--dry-run"])
    assert result.exit_code == 0
    assert "diff content" in result.output
