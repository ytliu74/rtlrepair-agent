"""No network calls and no credential values printed."""

import os
import platform
import shutil
import sys

from .llm_client import GenerationError, configuration, load_env


def main() -> int:
    checks = [(sys.version_info >= (3, 10), f"Python {platform.python_version()} (requires 3.10+)"),
              (bool(shutil.which("iverilog")), "iverilog found"),
              (bool(shutil.which("vvp")), "vvp found"),
              (True, "Python dependencies: standard library only")]
    try:
        load_env()
        for key in ("OPENAI_API_KEY", "OPENAI_MODEL"):
            checks.append((bool(os.environ.get(key, "").strip()), f"{key} configured"))
        if all(ok for ok, _ in checks[-2:]):
            configuration()
            checks.append((True, "API URL configuration"))
    except (ValueError, GenerationError, OSError) as exc:
        checks.append((False, str(exc) if not isinstance(exc, OSError) else "Cannot read .env"))
    for ok, label in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    return 0 if all(ok for ok, _ in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
