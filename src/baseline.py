"""Canonical one-shot experiment. No retries and no verification-guided repair."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
from time import perf_counter

from .llm_client import GenerationError, load_env
from .rtl_generator import generate
from .simulator import empty_verification, verify


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=Path("examples/counter/spec.txt"))
    parser.add_argument("--testbench", type=Path, default=Path("examples/counter/tb.sv"))
    parser.add_argument("--output", type=Path, default=Path("generated/counter.sv"))
    parser.add_argument("--results", type=Path, default=Path("results/baseline_results.json"))
    args = parser.parse_args()
    result = {"test_name": args.spec.parent.name, "mode": "one-shot",
              "started_at_utc": datetime.now(timezone.utc).isoformat(),
              "model": os.environ.get("OPENAI_MODEL") or None, "generation_success": False,
              "generation_latency_seconds": None, "generated_rtl_path": None,
              "spec_path": str(args.spec), "testbench_path": str(args.testbench),
              "python_version": platform.python_version(), "error": None,
              **empty_verification()}
    start = None
    try:
        load_env()
        result["model"] = os.environ.get("OPENAI_MODEL") or None
        # Check evaluator input exists before spending an API call; never send it.
        spec = args.spec.read_text(encoding="utf-8")
        testbench_bytes = args.testbench.read_bytes()
        result["spec_sha256"] = hashlib.sha256(spec.encode()).hexdigest()
        result["testbench_sha256"] = hashlib.sha256(testbench_bytes).hexdigest()
        print(f"Model: {result['model'] or '(not configured)'}", flush=True)
        print("Generating RTL (one LLM call; testbench withheld)...", flush=True)
        start = perf_counter()
        rtl, metadata, messages = generate(spec)
        result["generation_latency_seconds"] = round(perf_counter() - start, 6)
        result.update(metadata)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rtl, encoding="utf-8")
        result.update(generation_success=True, generated_rtl_path=str(args.output),
                      generated_rtl_sha256=hashlib.sha256(rtl.encode()).hexdigest(), prompt=messages)
        print(f"Generation: PASS -> {args.output}", flush=True)
        result.update(verify(args.output, args.testbench))
    except (GenerationError, ValueError, OSError) as exc:
        if start is not None and result["generation_latency_seconds"] is None:
            result["generation_latency_seconds"] = round(perf_counter() - start, 6)
        # Do not persist raw OS errors that may include configuration values.
        result["error"] = "Input/output error; check file paths and permissions." if isinstance(exc, OSError) else str(exc)
        print(f"Error: {result['error']}", flush=True)
    for label, field in (("Compilation", "compile_success"), ("Simulation", "simulation_success")):
        attempted = result["generation_success"] if field == "compile_success" else result["compile_success"]
        status = "PASS" if result[field] else ("FAIL" if attempted else "NOT RUN")
        print(f"{label}: {status}", flush=True)
    for field in ("compiler_stdout", "compiler_stderr", "simulation_stdout", "simulation_stderr"):
        if result[field].strip():
            print(f"--- {field} ---\n{result[field].rstrip()}", flush=True)
    print(f"Functional verification: {'TEST_PASS' if result['functional_pass'] else 'FAIL'}", flush=True)
    result["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.results.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Results: {args.results}", flush=True)
    return 0 if result["functional_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
