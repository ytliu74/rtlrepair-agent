# CSE 598 Capstone Proposal Submission

Deadline: **September 6, 2026, 11:59 PM Phoenix Time (UTC−07:00)**

Repository: https://github.com/ytliu74/rtlrepair-agent

**Current revision:** GPT-4.1 counter + FIFO, one call per design, no repair.
Both first live runs passed. Public-clone reproduction and final document checks
are being refreshed for this expanded baseline.

## Submission checklist

- [ ] Proposal completed using instructor template's structure and Word reference styles
- [ ] Proposal is approximately 1–2 pages (recheck updated PDF and Word)
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
- [ ] No API keys committed (repeat scan for new artifacts)
- [ ] Final repository changes pushed
- [x] Repository link tested
- [ ] Canvas submission completed before 11:59 PM Phoenix Time

## Manual action remaining: Canvas submission

After final checks, upload `proposal/capstone_proposal.pdf` (or Word if Canvas
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

Both compiler and simulator exit codes were zero for both tasks.
The FIFO compile warning about ignored `unique/unique0` qualities is preserved,
not suppressed. Generated code was not manually corrected.

Primary files: `generated/counter.sv`, `generated/fifo.sv`,
`results/baseline_results.json`, `results/fifo_results.json`,
`artifacts/baseline_output.txt`, `artifacts/fifo_output.txt`, and
`artifacts/suite_output.txt`.

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
- Fresh public-clone reproduction for this revision remains to be recorded.

## Proposal exports

Source: `proposal/capstone_proposal.md`. It retains Basic Information and all
seven instructor sections, with actual counter/FIFO results and the screenshot.
The original instructor `.docx` remains unchanged and supplies Word reference
styles. Run `./scripts/build_proposal.sh` with Pandoc and XeLaTeX to export PDF
and Word; the Word formatting script applies compact spacing and 0.8-inch
margins. Document tools are not required to execute the baseline.
