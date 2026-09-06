# RTLRepair-Agent

## Project Overview

**RTLRepair-Agent: Verification-Guided Agentic RTL Generation** investigates
whether compiler/simulator feedback improves an LLM's functional RTL pass rate.
Implemented now: **one-shot LLM-based RTL generation + automated verification**.
Each design receives one API call. There are no repair iterations.

Repository: https://github.com/ytliu74/rtlrepair-agent

The selected baseline model is **GPT-4.1**, pinned to
`gpt-4.1-2025-04-14`. Its first live counter and FIFO runs both passed.
The earlier GPT-5.6 Sol counter results are preserved under the
`artifacts/archive/`, `results/archive/`, and `generated/archive/` directories.

## Baseline Architecture

```text
Natural-language specification + module interface
                       ↓
                LLM (one call)
                       ↓
                Generated RTL
                       ↓
 Icarus Verilog (RTL + independent testbench)
                       ↓
              Testbench via vvp
                       ↓
                   PASS / FAIL
```

The model never receives the testbench, its seed, or the reference fixture.
Public testbenches make evaluation reproducible but are withheld from the API
request. Model-generated RTL is never replaced with a fixture.

## Repository Structure

| Path | Purpose |
| --- | --- |
| `src/llm_client.py` | Configuration and isolated Chat Completions client |
| `src/rtl_generator.py` | Fixed prompt and response cleanup/validation |
| `src/simulator.py` | Real compilation, simulation, timeouts, marker parsing |
| `src/baseline.py` | Single-design CLI and structured results |
| `examples/counter/`, `examples/fifo/` | Specifications and independent testbenches |
| `tests/fixtures/` | Hand-written counter and FIFO infrastructure fixtures |
| `scripts/run_examples.sh` | Run both examples, one call per design |
| `scripts/run_baseline.sh` | Run counter (default) or FIFO |
| `generated/`, `results/`, `artifacts/` | Actual generated RTL, JSON, logs, screenshot |
| `proposal/` | Proposal Markdown, Word/PDF exports, submission checklist |

## Requirements

- Python **3.10+**; tested with **3.13.1**.
- Icarus Verilog **12.0**, including `iverilog` and `vvp` on `PATH`.
- Bash and standard Unix utilities. Use macOS/Linux, or WSL on Windows.
- **No third-party Python packages**; `requirements.txt` documents standard-library-only operation.
- API key, quota, and access to the selected model through an OpenAI-compatible
  Chat Completions endpoint supporting `max_completion_tokens`.

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
# Ubuntu / Debian; distribution package versions vary
sudo apt-get update
sudo apt-get install -y iverilog python3-venv
```

If virtual-environment creation failed, install `python3-venv` first and repeat
that setup step. Ensure both Icarus executables are on `PATH`.

## API Setup

Copy the configuration template **once**, then edit it locally:

```bash
cp .env.example .env
```

```dotenv
OPENAI_API_KEY=your-provider-api-key
OPENAI_MODEL=gpt-4.1-2025-04-14
OPENAI_BASE_URL=
```

`OPENAI_API_KEY` holds the secret. The chosen
[GPT-4.1 snapshot](https://developers.openai.com/api/docs/models/gpt-4.1) is a
non-reasoning model and fixes the model version for this experiment.
The saved live runs requested and returned `gpt-4.1-2025-04-14`.
A different model is a different experimental configuration.

Leave `OPENAI_BASE_URL` empty for `https://api.openai.com/v1`. To use a compatible
provider, supply its HTTPS API root, without appending `/chat/completions`, and
use its model ID/key. HTTP is accepted only for localhost.

The scripts load `.env` automatically; **do not source it**. It supports literal
assignments, quoted values, and comments, not shell execution or variable
expansion. Existing shell variables take precedence. Never commit `.env`.

The adapter follows the official
[Chat Completions API](https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create):
one request per design, a 4,096-completion-token limit, a 120-second network
timeout, and no automatic retries. Sampling uses provider defaults.
Calls can incur charges; token usage is saved when supplied. There is no cost estimator.

## Reproduce the Baseline

After installing dependencies and filling `.env`, run **both examples**:

```bash
./scripts/run_examples.sh
```

This calls the model twice in total, records each design separately, and prints
an overall summary. It evaluates FIFO even if the counter fails; the suite exits
nonzero if either design fails.

To run one example:

```bash
./scripts/run_baseline.sh       # Original canonical counter example: one call
./scripts/run_baseline.sh fifo  # FIFO only: one call
```

The scripts select `.venv/bin/python` if present, otherwise `python3`, so
activation is not required after setup. They save actual stdout/stderr with
`tee`, preserve failure exit codes, and record configuration/generation failures
in JSON when Python can run.

`./scripts/check_environment.sh` independently checks Python, tools, and API
configuration presence. It does not make a network request or validate quota.
Compilation and simulation each have a 10-second wall-clock timeout.

## Input

- `examples/counter/spec.txt`, `examples/counter/tb.sv`: 8-bit rising-edge counter
  with synchronous reset, reset priority, enable/hold, and modulo-256 wrap.
  The evaluator makes 853 comparisons.
- `examples/fifo/spec.txt`, `examples/fifo/tb.sv`: 16-entry, 8-bit FIFO with
  registered read output, 5-bit occupancy, full/empty flags, reset, and ordering.
  The independent shift-queue scoreboard checks 744 cycles at three observation
  points per cycle plus initial reset: **2,233 state comparisons**. It includes
  directed boundary tests and 512 deterministic LFSR-driven cycles.

FIFO acceptance rules are explicitly defined using pre-edge occupancy:

| Situation | Accepted read | Accepted write | Occupancy change |
| --- | --- | --- | --- |
| Empty, read + write requested | No; no bypass | Yes | +1 |
| Full, read + write requested | Yes; return old oldest byte | Yes | 0 |
| Full, write only | No | No | 0 |
| Nonempty, read only | Yes | No | −1 |
| Not full, write only | No | Yes | +1 |
| Interior, read + write requested | Yes | Yes | 0 |

An unaccepted read holds `data_out`, including when empty. Synchronous reset
overrides requests and clears occupancy/read output. Internal memory need not be
cleared. Tests check pointer wrap, data ordering, between-edge stability, reset
priority, blocked operations, and both simultaneous boundary cases.
All testbench tops are named `tb`.

## Output

| Design/run | Generated RTL | JSON | Raw console log |
| --- | --- | --- | --- |
| Counter | `generated/counter.sv` | `results/baseline_results.json` | `artifacts/baseline_output.txt` |
| FIFO | `generated/fifo.sv` | `results/fifo_results.json` | `artifacts/fifo_output.txt` |
| Combined suite | The two files above | The two results above | `artifacts/suite_output.txt` |

`artifacts/baseline_screenshot.png` is a genuine Terminal capture showing the
FIFO command, model, generation, compilation, simulation, and the suite summary.

Each JSON records model IDs, stage statuses/latencies, return codes, timeouts,
compiler/simulator stdout/stderr, prompt, timestamps, token usage, and SHA-256
hashes of the specification, testbench, and generated RTL.

Running an example replaces its current JSON/log and, on valid generation, its
RTL. After failed generation an older RTL file can remain; the current JSON is
authoritative (`generation_success=false`, `generated_rtl_path=null` means no
RTL was generated in that attempt). Archive evidence before another experiment.
Temporary simulation binaries are removed automatically.

## Expected Output

Actual first GPT-4.1 suite result on September 6, 2026:

```text
=== One-shot suite (one API call per design) ===
Counter: PASS
FIFO: PASS
```

| Task | Generation latency | Compiler | Simulator | Functional result | API tokens |
| --- | --- | --- | --- | --- | --- |
| Counter | 1.984719 s | PASS | PASS | TEST_PASS; 853 checks | 329 |
| FIFO | 3.477588 s | PASS | PASS | TEST_PASS; 2,233 checks / 744 cycles | 1,099 |

The FIFO compiler reported that `unique/unique0` case qualities are ignored.
Compilation still exited zero; the independent scoreboard passed. The warning
is preserved in the raw log and JSON. The generated RTL was not hand-edited.

![Genuine GPT-4.1 FIFO execution and suite summary](artifacts/baseline_screenshot.png)

These are two tasks, not thousands of independent design examples. A later
model invocation may generate different RTL or fail.

Offline infrastructure checks, without any API call:

```bash
python -m unittest discover -s tests -v
python -m scripts.run_fixture
python -m scripts.run_fixture fifo
```

All 20 tests pass. Seven broken counter variants and ten broken FIFO variants
are rejected by the real testbenches. Other tests cover malformed output,
Markdown cleanup, marker parsing, compiler failure, timeout, credential-safe
errors, and a clearly mocked CLI completion using the real simulator.
Fixture results remain separately labeled as hand-written, not LLM-generated.

## PASS/FAIL Definition

Success requires all three conditions:

1. `iverilog` exits zero.
2. `vvp` exits zero before its timeout.
3. Simulator stdout contains an exact `TEST_PASS` line, with no `TEST_FAIL`
   marker in stdout or stderr.

A zero simulator exit code without the marker fails. A failure marker overrides
a pass marker. Configuration/generation failure prevents compilation; compiler
failure prevents simulation. JSON distinguishes these stages. The suite reports
both outcomes and does not repair or retry either design.

For API errors, check credentials/access, quota, model ID, endpoint, and parameter
support. Provider error bodies are omitted because they may echo credentials.

## Known Limitations

Two small tasks do not establish general RTL accuracy or a model ranking. Passing
simulation checks only covered behavior and does not establish synthesizability.
The validator rejects obvious simulation constructs but is not a complete HDL
parser or security sandbox. Use trusted specifications/testbenches. API access,
model availability, and provider behavior can change. Model output is
nondeterministic. The current baseline performs **no repair**.

## Planned Capstone Extension

Add bounded verification-guided diagnosis and repair, then compare functional
pass rate against this one-shot control with the same model/prompts/testbenches
across repeated trials. Include budget-matched independent resampling to separate
feedback benefit from additional calls. Track compile rate, iterations, calls,
tokens, latency, and measurable cost. Expand beyond the counter/FIFO to curated
tasks; VerilogEval and RTLLM are possible later datasets. Synthesis/PPA feedback
is a stretch goal, not implemented baseline behavior.
