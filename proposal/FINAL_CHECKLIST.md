# CSE 598 Capstone Proposal Submission

Deadline: **September 6, 2026, 11:59 PM Phoenix Time (UTC−07:00)**

Repository: https://github.com/ytliu74/rtlrepair-agent

**Status: submission-ready.** GPT-4.1 counter + FIFO, one call per design, no
repair. Both designs passed in the initial suite and the fresh public clone.
Only the student's Canvas upload remains.

## Submission checklist

- [x] Proposal completed using instructor template's structure and Word reference styles
- [x] Proposal is approximately 1–2 pages (PDF and Word: 2 pages each)
- [x] Public repository URL inserted
- [x] Repository accessible to everyone
- [x] README.md complete
- [x] Dependencies documented
- [x] Setup documented
- [x] API/environment variables documented
- [x] Exact run command documented
- [x] Input location documented
- [x] Output location documented
- [x] Concrete test cases included: counter and FIFO
- [x] Baseline actually executed through real LLM calls
- [x] Generated RTL saved
- [x] Actual successful baseline output saved
- [x] Successful screenshot captured
- [x] Screenshot clearly shows FIFO command, model, execution, and both outcomes
- [x] No API keys committed (actual-key and pattern scans; `.env` excluded)
- [x] Final repository changes pushed
- [x] Repository link tested
- [ ] Canvas submission completed before 11:59 PM Phoenix Time

## Manual action remaining: Canvas submission

Upload `proposal/capstone_proposal.pdf` (or Word if Canvas
requires it) and `artifacts/baseline_screenshot.png`, with the public repository
link. Confirm the files and submission timestamp before the deadline.
The screenshot is also embedded in both proposal exports.
Canvas submission has not been performed.

## Actual GPT-4.1 evidence

Model requested and returned: `gpt-4.1-2025-04-14`; API root:
`https://api.openai.com/v1`. Sampling uses provider defaults, with a
4,096-completion-token limit, one request per task, and no retries or repair.
Neither testbench nor reference fixture is included in generation.

| Task | First run start (UTC, September 6) | Generation | Functional verification | Tokens |
| --- | --- | --- | --- | --- |
| Counter | 22:37:29 | 1.984719 s | TEST_PASS; 853 checks | 329 |
| FIFO | 22:37:32 | 3.477588 s | TEST_PASS; 744 cycles / 2,233 checks | 1,099 |

Fresh-public-clone repetitions (same model and testbench hashes):

| Task | Start (UTC, September 6) | Generation | Compile / simulation / functional result | Tokens |
| --- | --- | --- | --- | --- |
| Counter | 22:42:47 | 1.274676 s | PASS / PASS / TEST_PASS | 322 |
| FIFO | 22:42:49 | 3.712335 s | PASS / PASS / TEST_PASS | 1,234 |

Both compiler and simulator exit codes were zero for both tasks.
The FIFO compile warning about ignored `unique/unique0` qualities is preserved,
not suppressed. Generated code was not manually corrected.

Primary files: `generated/counter.sv`, `generated/fifo.sv`,
`results/baseline_results.json`, `results/fifo_results.json`,
`artifacts/baseline_output.txt`, `artifacts/fifo_output.txt`, and
`artifacts/suite_output.txt`.

Reproduction files: `results/reproduction_results.json` (counter),
`results/fifo_reproduction_results.json`, `generated/counter_reproduction.sv`,
`generated/fifo_reproduction.sv`, and the `reproduction_output.txt`,
`fifo_reproduction_output.txt`, and `suite_reproduction_output.txt` logs in
`artifacts/`. JSON retains original paths from the fresh clone; the saved modules
match its generated-RTL hashes. All four actual model calls passed; none were
discarded or repaired. The screenshot records the first suite.

`artifacts/baseline_screenshot.png` is a real macOS capture of the Terminal
window where `./scripts/run_examples.sh` executed. Its visible portion includes
the FIFO subcommand, full FIFO result, and counter/FIFO summary.
No terminal screenshot was generated from text.

Earlier GPT-5.6 Sol counter results, logs, generated modules, and screenshot are
preserved under each output directory's `archive/gpt-5.6-sol/` subdirectory.
Those are historical results and are not evidence for the current model.

## Verification

- Python 3.13.1; Icarus Verilog 12.0.
- All 20 tests pass, including seven faulty counters and ten faulty FIFOs
  rejected by the real simulators. Tests also cover parser failures, timeouts,
  secret-safe API errors, and a clearly mocked CLI run.
- FIFO hand-written fixture passes 744 cycles and 2,233 state checks. Results/log:
  `results/fifo_fixture_results.json`, `artifacts/fifo_fixture_output.txt`.
- Counter fixture independently passes 853 checks.
- The FIFO scoreboard uses a shift queue, independently of the DUT's ring-buffer
  pointers. Coverage includes full/empty simultaneous requests, overflow,
  underflow, data-out hold, reset priority, and pointer wrap.
- `./scripts/check_environment.sh` passes with the configured GPT-4.1 snapshot.
- `./scripts/run_examples.sh` passed in the actual Terminal.
- Fresh unauthenticated HTTPS clone of `a3c7b1c9d4f069c34c599528c28aff03304e25ed`:
  created a virtual environment, installed requirements, configured a protected
  local `.env`, passed environment checks and all 20 tests, then ran
  `./scripts/run_examples.sh`. Both live tasks passed. Temporary credential copy
  removed afterward; original local `.env` retained and untracked.
- Input and generated-source SHA-256 hashes checked against all four live results.
- PDF pages visually checked; Microsoft Word's actual page-count query reports 2.
- Public repository, README, screenshot, and proposal links checked without authentication.

## Proposal exports

Source: `proposal/capstone_proposal.md`. It retains Basic Information and all
seven instructor sections, with actual counter/FIFO results and the screenshot.
The original instructor `.docx` remains unchanged and supplies Word reference
styles. Run `./scripts/build_proposal.sh` with Pandoc and XeLaTeX to export PDF
and Word; the Word formatting script applies compact spacing and 0.8-inch
margins. Document tools are not required to execute the baseline.
