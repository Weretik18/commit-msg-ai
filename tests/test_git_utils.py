from unittest.mock import MagicMock, patch

from commit_msg_ai.git_utils import get_staged_diff, get_staged_files, truncate_diff


@patch("commit_msg_ai.git_utils.subprocess.run")
def test_get_staged_diff_returns_output(mock_run):
    mock_run.return_value = MagicMock(stdout="diff --git a/x b/x\n+hello\n")
    assert "hello" in get_staged_diff()


@patch("commit_msg_ai.git_utils.subprocess.run")
def test_get_staged_files_parses_lines(mock_run):
    mock_run.return_value = MagicMock(stdout="a.py\nb.py\n\n")
    assert get_staged_files() == ["a.py", "b.py"]


def test_truncate_diff_passthrough():
    assert truncate_diff("small", max_chars=100) == "small"


def test_truncate_diff_shortens():
    out = truncate_diff("x" * 20000, max_chars=12000)
    assert len(out) < 20000
    assert "truncated" in out
