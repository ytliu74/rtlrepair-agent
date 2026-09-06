"""Offline EDA smoke test; never substitutes for the live LLM baseline."""
import json
import argparse
from pathlib import Path
from src.simulator import verify

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("example", nargs="?", default="counter", choices=("counter", "fifo"))
example = parser.parse_args().example
print(f"Offline fixture only: {example}, hand-written RTL, no LLM call.")
result = {"mode": "hand-written-fixture", "model": None,
          "rtl_path": f"tests/fixtures/{example}_good.sv",
          **verify(Path(f"tests/fixtures/{example}_good.sv"), Path(f"examples/{example}/tb.sv"))}
Path("results").mkdir(exist_ok=True)
result_path = "results/fixture_results.json" if example == "counter" else "results/fifo_fixture_results.json"
Path(result_path).write_text(json.dumps(result, indent=2) + "\n")
print(f"Compilation: {'PASS' if result['compile_success'] else 'FAIL'}")
print(f"Simulation: {'PASS' if result['simulation_success'] else 'FAIL'}")
print(result["simulation_stdout"], end="")
print(f"Functional verification: {'TEST_PASS' if result['functional_pass'] else 'FAIL'}")
raise SystemExit(0 if result["functional_pass"] else 1)
