"""Offline EDA smoke test; never substitutes for the live LLM baseline."""
import json
from pathlib import Path
from src.simulator import verify

print("Offline fixture only: hand-written RTL, no LLM call.")
result = {"mode": "hand-written-fixture", "model": None,
          "rtl_path": "tests/fixtures/counter_good.sv",
          **verify(Path("tests/fixtures/counter_good.sv"), Path("examples/counter/tb.sv"))}
Path("results").mkdir(exist_ok=True)
Path("results/fixture_results.json").write_text(json.dumps(result, indent=2) + "\n")
print(f"Compilation: {'PASS' if result['compile_success'] else 'FAIL'}")
print(f"Simulation: {'PASS' if result['simulation_success'] else 'FAIL'}")
print(result["simulation_stdout"], end="")
print(f"Functional verification: {'TEST_PASS' if result['functional_pass'] else 'FAIL'}")
raise SystemExit(0 if result["functional_pass"] else 1)
