"""Run actual Icarus tools, using an independent testbench as top module tb."""

from pathlib import Path
import re
import subprocess
import tempfile
from time import perf_counter


def parse_functional_pass(stdout: str, stderr: str = "") -> bool:
    # An explicit failure anywhere wins, even if TEST_PASS also appears.
    combined = stdout + "\n" + stderr
    return (any(line.strip() == "TEST_PASS" for line in stdout.splitlines())
            and re.search(r"\bTEST_FAIL\b", combined) is None)


def _run(command: list[str], timeout: float, cwd: str) -> dict:
    start = perf_counter()
    try:
        process = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        result = {"success": process.returncode == 0, "returncode": process.returncode,
                  "stdout": process.stdout, "stderr": process.stderr, "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        def decode(value):
            return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else (value or "")
        result = {"success": False, "returncode": None, "stdout": decode(exc.stdout),
                  "stderr": decode(exc.stderr) + "\nProcess timed out.", "timed_out": True}
    except OSError:
        result = {"success": False, "returncode": None, "stdout": "",
                  "stderr": f"Could not execute {command[0]}; verify installation and PATH.", "timed_out": False}
    result["latency_seconds"] = round(perf_counter() - start, 6)
    return result


def empty_verification() -> dict:
    return {"compile_success": False, "simulation_success": False, "functional_pass": False,
            "compile_latency_seconds": None, "simulation_latency_seconds": None,
            "compiler_stdout": "", "compiler_stderr": "", "simulation_stdout": "",
            "simulation_stderr": "", "compile_returncode": None, "simulation_returncode": None,
            "compile_timed_out": False, "simulation_timed_out": False}


def verify(rtl: Path, testbench: Path, timeout: float = 10) -> dict:
    result = empty_verification()
    with tempfile.TemporaryDirectory(prefix="rtlrepair-") as directory:
        executable = str(Path(directory) / "simulation.vvp")
        compile_result = _run(["iverilog", "-g2012", "-s", "tb", "-o", executable,
                               str(testbench.resolve()), str(rtl.resolve())], timeout, directory)
        for key in ("success", "returncode", "latency_seconds", "timed_out"):
            result[f"compile_{key}"] = compile_result[key]
        for key in ("stdout", "stderr"):
            result[f"compiler_{key}"] = compile_result[key]
        if not compile_result["success"]:
            return result
        simulation = _run(["vvp", executable], timeout, directory)
        for key in ("success", "returncode", "latency_seconds", "timed_out", "stdout", "stderr"):
            result[f"simulation_{key}"] = simulation[key]
        result["functional_pass"] = simulation["success"] and parse_functional_pass(simulation["stdout"], simulation["stderr"])
    return result
