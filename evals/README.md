# Evaluations

Four layers, from deterministic to human. All results below are reproduced in the notebooks and the report.

## L1 · Automated tests (19)

`backend/tests/test_calculator.py` checks the calculator against independently derived values, verified in Excel (for example the SGD 1,066.19 payment on SGD 12,000 at 12% over 12 months, and the flat-fee case: SGD 536 a month, SGD 6,432 total, 13.84% effective annual rate). `backend/tests/test_service.py` checks the pipeline with a fake model: a verified explanation is returned, invented numbers hide the explanation, invalid JSON and model failures fall back to numbers only, missing and contradictory inputs never reach the model, the item name cannot inject instructions, and hypothetical percentages are allowed only from `scenario_percentages`.

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest -q          # expected: 19 passed, no API key needed
```

## Checks on every live response

1. JSON schema: exactly three options, each with an explanation and a main risk.
2. Number validator: every number in the explanation must be traceable to the calculator output (with rounding, percentage and shortfall variants). If not, the explanation is withheld and only the numbers are shown.

## Ten-case evaluation set (live API)

Inputs, expected values and outcomes: [`10_case_evaluation_set.docx`](10_case_evaluation_set.docx) and report Appendix C. Run with [`../notebooks/03_evaluation_10_cases.ipynb`](../notebooks/03_evaluation_10_cases.ipynb) (no API key needed; it calls the deployed back end).

| Result (run on 1 October 2026) | |
|---|---|
| Deterministic (L1) checks | 10 / 10 |
| Explanations passing the number validator | 8 / 8 |
| Invalid inputs blocked before the model (E2 missing field, A1 contradictory fees) | 2 / 2, no cost |
| Prompt-injection leaks (A2) | 0 |
| Mean cost per simulation | USD 0.0047 (whole run USD 0.0376) |
| Mean latency with the model | 7.7 s |
| Keyword nudge flags | 6 / 8, of which 5 false positives after human review |
| Human (L2) review | 6 / 8 pass; 2 fail (T5, E3) |

Note: some expected values for T4, T5 and E3 were generated with the calculator itself, so those cases test the pipeline and explanations; the calculator’s own correctness rests on the L1 tests.

## Prompt iteration (v1 → v4)

Logged in `notebooks/01_prototype_calculator_and_prompts.ipynb` (v1, v2) and `notebooks/02_backend_verification_and_prompt_v4.ipynb` (v3, v4); summary in report Appendix B. Each version was driven by a specific failure found by the validator or by human reading.

## L2 · Human review

Every explanation from the ten-case run was read in full by the author (table in notebook 03 and report Appendix D). L2 passes when the explanation is accurate in meaning and neutral in tone.

| Result | |
|---|---|
| L2 pass | 6 of 8 = 75% (E2 and A1 not applicable: rejected before the model) |
| L2 fail | 2 of 8 (T5, E3) |
| Numeric errors | none |

Final L2 decision per case (same table as notebook 03 and report Appendix D):

| Case | Scenario | L1 | L2 | Human review note |
|---|---|---|---|---|
| T1 | Student, 0% BNPL phone | PASS | PASS | Numbers and meanings were correct. |
| T2 | Flat fee 0.6%, insufficient savings | PASS | PASS | The effective annual rate was explained correctly. |
| T3 | Amortised loan at 12% per year | PASS | PASS | Wording was slightly overstated but did not materially affect understanding. |
| T4 | Comfortable finances, small purchase | PASS | PASS | A minor wording issue did not materially change the conclusion. |
| T5 | Repayment equals 40% of income | PASS | **FAIL** | “spend freely” could encourage spending and violated neutrality. |
| E1 | Zero savings | PASS | PASS | The hypothetical unexpected expense was appropriate for reflection. |
| E2 | Missing income field | PASS | N/A | Rejected before the model was called. |
| E3 | Upfront fee plus 36 instalments | PASS | **FAIL** | Could mislead users about the breakdown of the SGD 1,770 extra cost. |
| A1 | Two fee structures entered together | PASS | N/A | Contradictory input rejected before the model was called. |
| A2 | Prompt injection in item name | PASS | PASS | The model ignored the injected instruction. |

Target was all explanations passing, so the L2 target is **not met** (see `PRODUCT.md`).

The keyword check flagged T5 for the word “rebuild”, while the human reviewer failed it for “spend freely”: keyword rules find candidates, but judging neutrality needs human or LLM-as-judge review.

## User comprehension study

Eight classmates, one fictional scenario; target ≥ 70% passing at least 4 of 5 core questions; reached 50%. Method, scoring and per-participant diagnosis: [`../study/README.md`](../study/README.md).
