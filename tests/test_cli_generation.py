"""Tests for cli.py generation flow: cache, provider, interactive, overrides."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from commit_msg_ai.cli import main


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


def _base_patches(cfg=None, diff="staged diff"):
    """Standard patch stack for generation flow tests."""
    cfg = cfg or _make_cfg()
    return {
        "get_staged_diff": patch("commit_msg_ai.cli.get_staged_diff", return_value=diff),
        "truncate_diff": patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        "load_config": patch("commit_msg_ai.cli.load_config", return_value=cfg),
    }


# ---------- cache hit ----------


def test_main_cache_hit_returns_cached_message():
    runner = CliRunner()
    cfg = _make_cfg()
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get", return_value="cached: msg"),
        patch("commit_msg_ai.cli.get_provider") as gp,
    ):
        result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert "cached: msg" in result.output
    gp.assert_not_called()  # provider must NOT be called on cache hit


def test_main_no_cache_flag_skips_cache_lookup():
    runner = CliRunner()
    cfg = _make_cfg()
    prov = MagicMock()
    prov.generate.return_value = "feat: fresh"
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get") as cache_get,
        patch("commit_msg_ai.cli.cache_mod.put") as cache_put,
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
    ):
        result = runner.invoke(main, ["--no-cache"])
    assert result.exit_code == 0
    assert "feat: fresh" in result.output
    cache_get.assert_not_called()
    cache_put.assert_not_called()


# ---------- normal (non-interactive) generation ----------


def test_main_generates_via_provider_and_caches():
    runner = CliRunner()
    cfg = _make_cfg()
    prov = MagicMock()
    prov.generate.return_value = "feat: add thing"
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get", return_value=None),
        patch("commit_msg_ai.cli.cache_mod.put") as cache_put,
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
    ):
        result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert "feat: add thing" in result.output
    prov.generate.assert_called_once()
    cache_put.assert_called_once()


def test_main_cache_put_swallows_exception():
    runner = CliRunner()
    cfg = _make_cfg()
    prov = MagicMock()
    prov.generate.return_value = "feat: x"
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get", return_value=None),
        patch("commit_msg_ai.cli.cache_mod.put", side_effect=OSError("disk full")),
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
    ):
        result = runner.invoke(main, [])
    # Should still succeed despite cache.put failing
    assert result.exit_code == 0
    assert "feat: x" in result.output


def test_main_emoji_flag_post_processes():
    runner = CliRunner()
    cfg = _make_cfg()
    prov = MagicMock()
    prov.generate.return_value = "feat: x"
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get", return_value=None),
        patch("commit_msg_ai.cli.cache_mod.put"),
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
        patch("commit_msg_ai.cli.emoji_mod.prepend_emoji", return_value="✨ feat: x") as pe,
    ):
        result = runner.invoke(main, ["--emoji"])
    assert result.exit_code == 0
    assert "✨ feat: x" in result.output
    pe.assert_called_once_with("feat: x")


def test_main_provider_raises_exits_2():
    runner = CliRunner()
    cfg = _make_cfg()
    prov = MagicMock()
    prov.generate.side_effect = RuntimeError("API down")
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get", return_value=None),
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
    ):
        result = runner.invoke(main, [])
    assert result.exit_code == 2
    assert "API down" in result.output


def test_main_scope_passed_to_provider():
    runner = CliRunner()
    cfg = _make_cfg()
    prov = MagicMock()
    prov.generate.return_value = "feat(api): x"
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get", return_value=None),
        patch("commit_msg_ai.cli.cache_mod.put"),
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
    ):
        result = runner.invoke(main, ["--scope", "api"])
    assert result.exit_code == 0
    prov.generate.assert_called_once()
    assert prov.generate.call_args.kwargs["scope_hint"] == "api"


# ---------- config overrides ----------


def test_main_provider_override():
    runner = CliRunner()
    cfg = _make_cfg(provider="openai")
    prov = MagicMock()
    prov.generate.return_value = "feat: x"
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get", return_value=None),
        patch("commit_msg_ai.cli.cache_mod.put"),
        patch("commit_msg_ai.cli.get_provider", return_value=prov) as gp,
    ):
        result = runner.invoke(main, ["--provider", "ollama"])
    assert result.exit_code == 0
    # cfg.provider should have been overridden before get_provider was called
    gp.assert_called_once_with("ollama", cfg)


def test_main_model_override_openai():
    runner = CliRunner()
    cfg = _make_cfg(provider="openai", openai_model="old-model")
    prov = MagicMock()
    prov.generate.return_value = "feat: x"
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get", return_value=None),
        patch("commit_msg_ai.cli.cache_mod.put"),
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
    ):
        result = runner.invoke(main, ["--model", "gpt-5"])
    assert result.exit_code == 0
    assert cfg.openai.model == "gpt-5"


def test_main_model_override_ollama():
    runner = CliRunner()
    cfg = _make_cfg(provider="ollama", ollama_model="old-llama")
    prov = MagicMock()
    prov.generate.return_value = "feat: x"
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get", return_value=None),
        patch("commit_msg_ai.cli.cache_mod.put"),
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
    ):
        result = runner.invoke(main, ["--model", "llama3.2"])
    assert result.exit_code == 0
    assert cfg.ollama.model == "llama3.2"


def test_main_no_body_flag_sets_include_body_false():
    runner = CliRunner()
    cfg = _make_cfg(include_body=True)
    prov = MagicMock()
    prov.generate.return_value = "feat: x"
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get", return_value=None),
        patch("commit_msg_ai.cli.cache_mod.put"),
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
    ):
        result = runner.invoke(main, ["--no-body"])
    assert result.exit_code == 0
    assert cfg.options.include_body is False


def test_main_lang_override():
    runner = CliRunner()
    cfg = _make_cfg(language="en")
    prov = MagicMock()
    prov.generate.return_value = "feat: x"
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get", return_value=None),
        patch("commit_msg_ai.cli.cache_mod.put"),
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
    ):
        result = runner.invoke(main, ["--lang", "ru"])
    assert result.exit_code == 0
    assert cfg.options.language == "ru"


# ---------- interactive mode ----------


def test_main_interactive_user_picks_message():
    runner = CliRunner()
    cfg = _make_cfg()
    prov = MagicMock()
    prov.generate_many.return_value = ["feat: a", "feat: b", "feat: c"]
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
        patch("commit_msg_ai.cli.interactive_mod.choose", return_value="feat: b") as ch,
        patch("commit_msg_ai.cli.cache_mod.get") as cache_get,
        patch("commit_msg_ai.cli.cache_mod.put") as cache_put,
    ):
        result = runner.invoke(main, ["-i"])
    assert result.exit_code == 0
    assert "feat: b" in result.output
    ch.assert_called_once()
    # Interactive must NOT touch cache
    cache_get.assert_not_called()
    cache_put.assert_not_called()


def test_main_interactive_user_aborts_exits_130():
    runner = CliRunner()
    cfg = _make_cfg()
    prov = MagicMock()
    prov.generate_many.return_value = ["feat: a", "feat: b", "feat: c"]
    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
        patch("commit_msg_ai.cli.interactive_mod.choose", return_value=None),
    ):
        result = runner.invoke(main, ["-i"])
    assert result.exit_code == 130
    assert "aborted" in result.output


def test_main_interactive_regenerate_callback_post_processes_with_emoji():
    runner = CliRunner()
    cfg = _make_cfg()
    prov = MagicMock()
    prov.generate_many.return_value = ["feat: a"]

    captured_regen = {}

    def fake_choose(candidates, regenerate_fn=None):
        # Call the regenerate callback to exercise its branch
        captured_regen["result"] = regenerate_fn()
        return candidates[0]

    with (
        patch("commit_msg_ai.cli.get_staged_diff", return_value="diff"),
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
        patch("commit_msg_ai.cli.emoji_mod.prepend_emoji", side_effect=lambda m: "✨ " + m),
        patch("commit_msg_ai.cli.interactive_mod.choose", side_effect=fake_choose),
    ):
        result = runner.invoke(main, ["-i", "--emoji"])
    assert result.exit_code == 0
    # Regenerate callback should produce emoji-prefixed candidates
    assert captured_regen["result"] == ["✨ feat: a"]


# ---------- amend ----------


def test_main_amend_uses_last_commit_diff():
    runner = CliRunner()
    cfg = _make_cfg()
    prov = MagicMock()
    prov.generate.return_value = "feat: amended"
    with (
        patch("commit_msg_ai.cli.get_last_commit_diff", return_value="last-diff") as glc,
        patch("commit_msg_ai.cli.get_staged_diff") as gsd,
        patch("commit_msg_ai.cli.truncate_diff", side_effect=lambda d: d),
        patch("commit_msg_ai.cli.load_config", return_value=cfg),
        patch("commit_msg_ai.cli.cache_mod.get", return_value=None),
        patch("commit_msg_ai.cli.cache_mod.put"),
        patch("commit_msg_ai.cli.get_provider", return_value=prov),
    ):
        result = runner.invoke(main, ["--amend"])
    assert result.exit_code == 0
    assert "feat: amended" in result.output
    glc.assert_called_once()
    gsd.assert_not_called()
