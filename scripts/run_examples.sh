#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p artifacts
{
    echo '$ ./scripts/run_examples.sh'
    counter_status=PASS
    fifo_status=PASS
    ./scripts/run_baseline.sh counter || counter_status=FAIL
    ./scripts/run_baseline.sh fifo || fifo_status=FAIL
    echo '=== One-shot suite (one API call per design) ==='
    echo "Counter: $counter_status"
    echo "FIFO: $fifo_status"
    [[ "$counter_status" == PASS && "$fifo_status" == PASS ]]
} 2>&1 | tee artifacts/suite_output.txt
