# CSE 598 Capstone Proposal Submission

Deadline: **September 6, 2026, 11:59 PM Phoenix Time (UTC−07:00)**

Repository: https://github.com/ytliu74/rtlrepair-agent

**Status: NOT submission-ready.** Live LLM generation is blocked by missing
`OPENAI_API_KEY` and `OPENAI_MODEL`. The actual fixture passed 853 checks; it is
not evidence of LLM generation. The proposal explicitly reflects this distinction.

## Submission checklist

- [ ] Proposal completed using instructor template
- [x] Proposal is approximately 1–2 pages (PDF verified: 2 pages; check Word after final edits)
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
- [ ] Baseline actually executed through a real LLM call
- [ ] Generated RTL saved
- [x] Actual baseline attempt output saved (configuration failure, not success)
- [ ] Successful screenshot captured
- [ ] Screenshot clearly shows execution and output
- [x] No API keys committed (staged secret-pattern scan clear; `.env` excluded)
- [ ] Final repository changes pushed
- [x] Repository link tested
- [ ] Canvas submission completed before 11:59 PM Phoenix Time

## Required actions to finish

1. Fill the existing local `.env` with your API key and model ID. Do not paste the
   key into chat or commit it. Run `./scripts/check_environment.sh`, then
   `./scripts/run_baseline.sh`. The latter must show generation, compilation,
   simulation, and functional success. A failed live generation must be reported
   honestly; never substitute `tests/fixtures/counter_good.sv` as a generated result.
2. Reproduce the live baseline a second time using the README workflow. Preserve
   the actual generated RTL, JSON, and transcript. Update README's evidence status
   and proposal Sections 3–5 and 7 with the actual model and observed result.
3. Capture the screenshot as below, then update the screenshot checklist items.
4. Regenerate the proposal exports after updating the Markdown, verify the 1–2 page
   limit in Word/PDF, and ensure Section 4 includes/references the real screenshot.
5. Commit and push updated result, screenshot, and proposal files (never `.env`).
6. Upload the completed proposal and screenshot to Canvas with the public
   repository link before the deadline. Confirm Canvas shows the submitted files.

## MANDATORY MANUAL ACTION: screenshot

After configuring the API, run in a visible terminal:

```bash
./scripts/run_baseline.sh
```

Then take a screenshot of the terminal showing:

1. The command.
2. Successful generation.
3. Compilation success.
4. Simulation success.
5. `TEST_PASS`.

Save as `artifacts/baseline_screenshot.png` and save/upload this screenshot with
the Canvas submission. On macOS use Shift–Command–4 and capture the terminal
window/region containing the command and final output. Do not capture API keys.
A fixture screenshot does not satisfy evidence of the complete live baseline.
No screenshot has been fabricated or generated from text.

## Validation evidence

- Python 3.13.1 and Icarus Verilog 12.0 installed.
- `python -m unittest discover -s tests -v`: 16 tests passed, including seven
  counter mutation cases, real compilation failure, and real simulation timeout.
- `python -m scripts.run_fixture`: PASS, 853 comparisons; evidence in
  `results/fixture_results.json` and `artifacts/fixture_output.txt`.
- `./scripts/check_environment.sh`: failed only for absent key/model configuration.
- `./scripts/run_baseline.sh`: exits 1; actual blocked-at-generation result saved
  in `results/baseline_results.json` and `artifacts/baseline_output.txt`.
- Repository created public; unauthenticated GitHub page returned HTTP 200 on
  September 6, 2026. Final source/README availability will be rechecked after push.

The provided instructor template is preserved at
`CSE598-capstone-proposal-template.docx`. The proposal uses its Basic Information
and seven section headings. Substantive work is recorded in
`proposal/capstone_proposal.md`; blocked requirements remain explicit.

Word and PDF drafts are available at `proposal/capstone_proposal.docx` and
`proposal/capstone_proposal.pdf`. The Word export uses the instructor document as
its Pandoc reference template. The PDF is 2 pages, visually checked for clipping
and complete content. Neither export is submission-ready until the live evidence
is filled in. Rebuild with `./scripts/build_proposal.sh` if Pandoc and XeLaTeX are
installed; these are document-authoring tools, not baseline dependencies.

Automatic desktop inspection failed with an Apple Events timeout, and no live
generation success exists to capture. The screenshot therefore remains a
mandatory manual action.
