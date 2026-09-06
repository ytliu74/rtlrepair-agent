#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
if [[ -x .venv/bin/python ]]; then
    task_python=.venv/bin/python
else
    task_python=python3
fi
if ! command -v "$task_python" >/dev/null 2>&1; then
    echo '[FAIL] Python 3.10+ is required; see README.md.'
    exit 1
fi
"$task_python" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' || {
    echo '[FAIL] Python 3.10+ is required.'
    exit 1
}
exec "$task_python" -m src.check_environment
