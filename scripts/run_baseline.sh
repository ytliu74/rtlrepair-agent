#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p artifacts
if [[ -x .venv/bin/python ]]; then
    task_python=.venv/bin/python
else
    task_python=python3
fi
# tee captures real stdout/stderr; pipefail preserves a failed baseline exit code.
{
    echo '$ ./scripts/run_baseline.sh'
    ./scripts/check_environment.sh || echo 'Environment check failed; recording the baseline attempt below.'
    # Continue into baseline on missing API configuration to save failure JSON.
    "$task_python" -u -m src.baseline
} 2>&1 | tee artifacts/baseline_output.txt
