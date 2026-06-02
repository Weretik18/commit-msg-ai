"""commit-msg-ai / gitmsg-ai - AI-powered git commit message generator."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gitmsg-ai")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
