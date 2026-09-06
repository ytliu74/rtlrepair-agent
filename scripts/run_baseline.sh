#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p artifacts
if [[ $# -gt 1 || ( ${1:-counter} != counter && ${1:-counter} != fifo ) ]]; then
    echo 'Usage: ./scripts/run_baseline.sh [counter|fifo]' >&2
    exit 2
fi
example=${1:-counter}
result_file=results/baseline_results.json
log_file=artifacts/baseline_output.txt
if [[ "$example" == fifo ]]; then
    result_file=results/fifo_results.json
    log_file=artifacts/fifo_output.txt
fi
if [[ -x .venv/bin/python ]]; then
    task_python=.venv/bin/python
else
    task_python=python3
fi
# tee captures real stdout/stderr; pipefail preserves a failed baseline exit code.
{
    echo "\$ ./scripts/run_baseline.sh $example"
    ./scripts/check_environment.sh || echo 'Environment check failed; recording the baseline attempt below.'
    # Continue into baseline on missing API configuration to save failure JSON.
    "$task_python" -u -m src.baseline \
        --spec "examples/$example/spec.txt" --testbench "examples/$example/tb.sv" \
        --output "generated/$example.sv" --results "$result_file"
} 2>&1 | tee "$log_file"
