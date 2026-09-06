# CSE 598 Capstone Proposal Submission

Deadline: **September 6, 2026, 11:59 PM Phoenix Time (UTC−07:00)**

Repository: https://github.com/ytliu74/rtlrepair-agent

**Status: submission-ready. Canvas upload remains the student's final action.**
Two real one-shot runs with `gpt-5.6-sol` each passed 853 checks. The second used
a fresh unauthenticated public clone and the README setup. A genuine Terminal
screenshot shows the command, model, generation, compilation, simulation, and
`TEST_PASS`. No iterative repair is claimed.

## Submission checklist

- [x] Proposal completed using instructor template's structure and Word reference styles
- [x] Proposal is approximately 1–2 pages (PDF and Microsoft Word: 2 pages each)
- [x] Public repository URL inserted
- [x] Repository accessible to everyone
- [x] README.md complete
- [x] Dependencies documented
- [x] Setup documented
- [x] API/environment variables documented
- [x] Exact run command documented
- [x] Input location documented
- [x] Output location documented
- [x] Concrete test case included
- [x] Baseline actually executed through a real LLM call
- [x] Generated RTL saved
- [x] Actual successful baseline output saved
- [x] Successful screenshot captured
- [x] Screenshot clearly shows execution and output
- [x] No API keys committed (actual-key/pattern scan passed; `.env` excluded)
- [x] Final repository changes pushed
- [x] Repository link tested
- [ ] Canvas submission completed before 11:59 PM Phoenix Time

## Manual action remaining: Canvas submission

Upload `proposal/capstone_proposal.pdf` (or the Word version if required by Canvas)
and `artifacts/baseline_screenshot.png`. Include the public repository URL above.
Confirm that Canvas shows the intended files and a submission timestamp before
the deadline. The screenshot is also embedded in the proposal; the separate PNG
provides the full-resolution original. Canvas submission has not been performed.

## Actual live evidence

Both runs used OpenAI's `https://api.openai.com/v1` endpoint with requested and
returned model ID `gpt-5.6-sol`, one call per run, no retries or repair, and a
4,096-completion-token limit. Each reported 242 prompt tokens plus 80 completion
tokens. The model received no testbench source.

| Run | Start (UTC, September 6) | Generation | Compile | Simulation | Result |
| --- | --- | --- | --- | --- | --- |
| Primary | 21:58:25 | 2.644741 s | 0.057887 s | 0.013298 s | TEST_PASS, 853 checks |
| Fresh public clone | 22:00:54 | 1.941901 s | 0.037862 s | 0.013409 s | TEST_PASS, 853 checks |

Primary files: `generated/counter.sv`, `results/baseline_results.json`, and
`artifacts/baseline_output.txt`. Reproduction files:
`generated/counter_reproduction.sv`, `results/reproduction_results.json`, and
`artifacts/reproduction_output.txt`. Reproduction JSON preserves the paths from
the original clone; the archived RTL's SHA-256 matches its recorded hash.

`artifacts/baseline_screenshot.png` is an actual macOS capture of the Terminal
window in which the second run executed. The window was resized to show both
the command and the result; no terminal image was generated from text.

## Validation evidence

- Python 3.13.1 and Icarus Verilog 12.0.
- `python -m unittest discover -s tests -v`: 17 tests passed, including seven
  counter mutation cases, real compilation failure, real simulation timeout,
  and CLI execution using a clearly marked mocked completion with real EDA tools.
- `python -m scripts.run_fixture`: PASS, 853 comparisons; separate hand-written
  fixture evidence in `results/fixture_results.json` and `artifacts/fixture_output.txt`.
- `./scripts/check_environment.sh`: all checks passed after local API setup.
- `./scripts/run_baseline.sh`: live generation, compilation, simulation, and
  functional verification all passed, twice. Generated modules and raw logs saved.
- Fresh public clone of commit `8603331e3f00befdbee9dc1fed60b843b1167e60`:
  virtual environment created, `pip install -r requirements.txt` succeeded,
  local `.env` configured, environment checks passed, and live baseline passed.
- Unauthenticated GitHub page, raw README, and public HTTPS clone succeeded.
- Final staged credential scan covered 35 files and decompressed Word contents;
  no key or credential pattern was found. The temporary reproduction credential
  copy was removed; the original project `.env` remains local and untracked.
- Both live results' specification, testbench, and generated-RTL SHA-256 hashes
  match their saved source files. The unchanged baseline code passed 17 tests.
- `./scripts/build_proposal.sh` exported Word/PDF; `pdfinfo` confirms 2 PDF pages.
  Both PDF pages were visually checked for complete text and the genuine screenshot.
- Microsoft Word's `compute statistics ... statistic pages` confirms 2 pages
  after applying the export script's 11-point body, 12-point headings, and
  0.8-inch margins. All section content and the original screenshot are preserved.

## Proposal files

`proposal/capstone_proposal.md` contains the instructor's Basic Information and
seven required sections, with actual observed model/results and the screenshot.
The original `CSE598-capstone-proposal-template.docx` is preserved and used as the
Word export's reference template. Exports are `proposal/capstone_proposal.docx`
and `proposal/capstone_proposal.pdf`.

Both exports contain all required sections and the embedded screenshot and are
verified at two pages. Submit the PDF or Word version accepted by Canvas. The
original instructor document is unchanged; only the exported Word copy receives
compact paragraph spacing and page margins for the assignment's length limit.

To rebuild exports, run `./scripts/build_proposal.sh` with Pandoc and XeLaTeX
installed. These are document-authoring tools, not baseline runtime dependencies.
