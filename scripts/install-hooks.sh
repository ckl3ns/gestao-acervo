#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
git config core.hooksPath "$ROOT_DIR/.githooks"
echo "Git hooks configured to use $ROOT_DIR/.githooks"
