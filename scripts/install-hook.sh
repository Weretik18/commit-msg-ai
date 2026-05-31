#!/usr/bin/env bash
set -e
if ! command -v commit-msg-ai >/dev/null 2>&1; then
    echo "not installed" >&2
    exit 1
fi
commit-msg-ai install-hook
