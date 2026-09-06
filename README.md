# RTLRepair-Agent

## Project Overview

**RTLRepair-Agent: Verification-Guided Agentic RTL Generation** investigates whether
an LLM using compiler/simulator feedback can produce correct RTL more reliably than
one-shot generation. The current implementation is the experimental control:
**one-shot LLM-based RTL generation + automated verification**. Iterative repair
is proposed semester work and is not implemented.

Repository: https://github.com/ytliu74/rtlrepair-agent

**Current evidence:** the hand-written fixture passes the real counter testbench
(853 checks). The live baseline attempt is blocked by missing API configuration;
there is no claimed LLM-generated success yet. See
[the submission checklist](proposal/FINAL_CHECKLIST.md).

## Baseline Architecture

```text
Specification
     ↓
   LLM (one call; receives specification and interface only)
     ↓
Generated RTL
     ↓
Icarus Verilog (compiles RTL + independent testbench)
     ↓
Testbench (executed by vvp)
     ↓
PASS / FAIL
```

The testbench source is **withheld from generation**. It remains publicly available
for reproducibility, but is never included in the API request. There are no retries,
repair calls, or substitutions of the known-good fixture into the live baseline.

## Repository Structure

| Path | Purpose |
| --- | --- |
| `src/llm_client.py` | Literal `.env` loading and isolated Chat Completions adapter |
| `src/rtl_generator.py` | Fixed prompt template and RTL response cleanup |
| `src/simulator.py` | Compilation, simulation, timeouts, and PASS/FAIL parsing |
| `src/baseline.py` | One-shot CLI and machine-readable results |
| `examples/counter/spec.txt` | Natural-language specification and exact interface |
| `examples/counter/tb.sv` | Independent, self-checking evaluator |
| `tests/fixtures/counter_good.sv` | Hand-written offline infrastructure fixture |
| `scripts/` | Environment check, canonical run, and offline fixture check |
| `generated/` | LLM-generated RTL (created after a successful generation) |
| `results/`, `artifacts/` | Actual JSON results, terminal logs, and screenshot if captured |
| `proposal/` | Proposal, export files, and submission checklist |

## Requirements

- Python **3.10+**; tested locally with **3.13.1**.
- Icarus Verilog **12.0** (`iverilog` and `vvp` on `PATH`); tested locally with 12.0.
- Bash and standard Unix utilities (`tee`, `mkdir`). macOS and Linux are supported;
  use WSL on Windows.
- **No third-party Python packages.** `requirements.txt` intentionally contains
  only comments; Python's standard library implements the client and tests.
- An API key, quota, and model access for an OpenAI-compatible **Chat Completions**
  endpoint supporting `max_completion_tokens`. A model must be explicitly set.

## Installation

```bash
git clone https://github.com/ytliu74/rtlrepair-agent.git
cd rtlrepair-agent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Install Icarus using the command for your operating system:

```bash
# macOS with Homebrew
brew install icarus-verilog
```

```bash
# Ubuntu / Debian (package versions depend on your distribution)
sudo apt-get update
sudo apt-get install -y iverilog python3-venv
```

If `python3 -m venv` was unavailable, install `python3-venv` first, then repeat
the virtual-environment setup. Ensure `iverilog` and `vvp` are available on `PATH`.

## API Setup

From the repository root, copy the configuration template **once**:

```bash
cp .env.example .env
```

Edit `.env` locally:

```dotenv
OPENAI_API_KEY=your-provider-api-key
OPENAI_MODEL=gpt-4.1-mini-2025-04-14
OPENAI_BASE_URL=
```

`OPENAI_API_KEY` contains the secret. `OPENAI_MODEL` is the exact model ID to call.
The ID above is an example configuration using the documented
[GPT-4.1 mini snapshot](https://developers.openai.com/api/docs/models/gpt-4.1-mini);
it is **not an observed experiment result**. No model was configured in the saved
live attempt. Choose a model your account can access; subsequent runs record the
requested and returned model IDs in JSON.

Leave `OPENAI_BASE_URL` empty for `https://api.openai.com/v1`. For another compatible
provider, set its HTTPS API root (usually ending in `/v1`), **without** appending
`/chat/completions`, and use that provider's model ID and key. HTTP is accepted only
for localhost. Shell variables take precedence over `.env`; `.env` is automatically
loaded, so **do not `source .env`**. It supports literal assignments, quoted values,
and comments, but does not execute shell commands or expand variables.

The adapter follows the official
[Chat Completions API](https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create):
one request, at most 4,096 completion tokens, 120-second network timeout, no automatic
retries. Sampling settings are left at provider defaults. API calls may incur a
charge. There is no cost estimator; returned token usage is saved when available.
`.env` is ignored by Git. Never add a real key to a tracked file.

## Reproduce the Baseline

Install the tools and fill `.env` as above. From the repository root run:

```bash
./scripts/run_baseline.sh
```

This is the canonical end-to-end command. It selects `.venv/bin/python` if present
(otherwise `python3`), checks the environment, generates RTL, compiles, simulates,
prints the result, and saves the actual transcript and JSON. You do not need to
activate the virtual environment again. A failed run exits nonzero. The standalone
environment check is `./scripts/check_environment.sh`; it checks configuration
presence and tools, not whether the provider will accept the credentials.

A small counter normally takes one API request plus well under a second of local
EDA work. Compiler and simulator stages each have a 10-second wall-clock timeout.
Provider availability and generation time vary; functional success is not guaranteed.

## Input

- `examples/counter/spec.txt`: an 8-bit rising-edge counter with active-high
  synchronous reset, enable/hold, reset priority, and modulo-256 wrap-around.
- `examples/counter/tb.sv`: the independent evaluator; top-level module `tb`.

The testbench performs 853 comparisons, including checks between rising edges to
catch an asynchronous reset and falling-edge updates. It detects unknown values
with case inequality and contains a simulation-time watchdog.

## Output

- `generated/counter.sv`: generated module, written only after a valid response.
- `results/baseline_results.json`: model, generation/compile/simulation/functional
  status, stage latencies, return codes, timeouts, stdout/stderr, prompt, input/RTL
  SHA-256 hashes, timestamp, and usage if the provider supplies it.
- `artifacts/baseline_output.txt`: real stdout/stderr captured by `tee`.
- `artifacts/baseline_screenshot.png`: required submission screenshot, once captured.

Each canonical run replaces its JSON/log and, if generation succeeds, its generated
RTL. An old RTL file can remain after a failed generation; the **current JSON** is
authoritative (`generation_success=false`, `generated_rtl_path=null` means no RTL
was generated in that attempt). Save copies of evidence before further experiments.
Compiled binaries are temporary and are removed automatically.

## Expected Output

The saved live attempt currently reports this **actual configuration failure**:

```text
Model: (not configured)
Generating RTL (one LLM call; testbench withheld)...
Error: Set OPENAI_API_KEY and OPENAI_MODEL in .env (see README.md).
Compilation: NOT RUN
Simulation: NOT RUN
Functional verification: FAIL
Results: results/baseline_results.json
```

Successful generation must produce `Generation: PASS`; compilation and simulation
must each report `PASS`, and the testbench must emit `TEST_PASS`. A live success
has not yet been observed. Do not confuse the following offline smoke test with
an LLM-generated result:

```bash
python -m scripts.run_fixture
```

Actual offline fixture output includes:

```text
Offline fixture only: hand-written RTL, no LLM call.
Compilation: PASS
Simulation: PASS
Checks: 853
TEST_PASS
Functional verification: TEST_PASS
```

Full fixture evidence is in `results/fixture_results.json` and
`artifacts/fixture_output.txt`. Run all unpaid tests with:

```bash
python -m unittest discover -s tests -v
```

These tests exercise Markdown cleanup, malformed responses, marker parsing,
compiler failures, timeouts, and the actual simulator. Seven faulty counter variants
test that the evaluator rejects broken reset, enable, increment, and wrap behavior.

## PASS/FAIL Definition

A functional pass requires all three conditions:

1. `iverilog` exits with code zero.
2. `vvp` exits with code zero before the timeout.
3. The simulator stdout contains an exact `TEST_PASS` line, and neither stdout nor
   stderr contains a `TEST_FAIL` marker.

A zero exit status without `TEST_PASS` is a failure. `TEST_FAIL` overrides
`TEST_PASS`. Configuration/generation failure prevents compilation; compilation
failure prevents simulation. The JSON distinguishes these stages. HTTP 401/403
usually indicates credential/access trouble, 429 quota or rate limiting, and 400
may indicate an incompatible model/parameter. Error bodies are not logged because
providers may echo secrets. The script never silently retries a failed experiment.

## Known Limitations

One counter is insufficient to establish a pass rate or research claim. A passing
simulation only establishes agreement with tested behavior; synthesis and formal
correctness are not checked. The prompt requests synthesizable RTL and the response
validator rejects obvious simulation constructs, but this is not a complete HDL
parser or a security sandbox. Use trusted example specifications and testbenches.
Models are nondeterministic; API availability, usage limits, model access, and
provider compatibility can change. The current baseline performs **no repair**.

## Planned Capstone Extension

Add a bounded generate–verify–diagnose–repair loop that feeds compiler and simulator
failures back to the same model. Compare functional pass rate against one-shot
generation on additional curated RTL tasks, using held-out testbenches, repeated
trials, fixed model/prompt settings, and a documented call budget. Track compilation
rate, calls, repair iterations, token usage, latency, and cost when measurable.
VerilogEval and RTLLM are possible later datasets. Yosys synthesis/PPA feedback is a
stretch goal; it is not part of this submission's baseline.
