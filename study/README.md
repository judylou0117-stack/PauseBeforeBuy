# User comprehension study

| File | What it is |
|---|---|
| `questionnaire_and_results..pdf` | Every question and option, with the answer distribution from all eight participants (exported from Google Forms). |
| `create_pausebeforebuy_form.gs` | Google Apps Script that recreates the exact questionnaire (pages, questions, options, number validation). Run it at script.google.com to rebuild the form. |
| `PauseBeforeBuy_comprehension_scoring.xlsx` | Scoring sheet with the eight anonymised responses (P1–P8). Sheets: Guide, Summary, Key (answer key and tolerances), Responses, Scoring. |

## Method

- **Participants:** 8 classmates, anonymous; no names, emails or timestamps kept.
- **Scenario (fictional):** laptop SGD 6,000, 12 instalments, 0.6% per instalment on the original price; income SGD 3,500; savings SGD 5,000; essentials SGD 2,200; existing repayments SGD 300. A bilingual scenario card with a QR code introduced the product.
- **Questionnaire:** Part A before using the tool (A1 prior use of instalments, A2 estimate of the yearly cost of 0.6% per month); Part C on the results page (C1 total paid, C2 monthly payment, C3 emergency runway during the plan, C4 option not possible, C5 main risk, C6 true yearly cost); Part D/E (D1–D3 on 1–5 scales, D4 whether the tool told them what to choose, E1 comments). The website link was shown only after Part A.
- **Scoring:** tolerances of ±1 SGD, ±0.05 months and ±0.1 percentage points; C4 and C5 by keyword. Pass = at least 4 of 5 core items (C1–C5). Google Forms’ own quiz score was not used because it mixes the pre-test item A2 with post-test items.

## Answer key

C1 6,432 · C2 536 · C3 1.65 months · C4 pay in full · C5 emergency savings fall below the 3-month target and you pay extra to borrow · C6 13.84% · A2 about 14%

## Results

| | |
|---|---|
| Passed (target 70%) | 4 of 8 = 50%, not met |
| Accuracy per question | C1 50% · C2 50% · C3 38% · C4 100% · C5 75% |
| Knew the true cost before (A2) → found it after (C6) | 2 → 4 |
| Experience means (1–5) | easy to understand 4.3 · trusted the numbers 4.4 · the pause made me rethink 4.8 |
| D4: did the tool tell you what to choose? | Yes 3 · No 3 · Not sure 2 |

## Diagnosis

Inputs were not logged, so this is an inference: reverse-calculating each answer shows which inputs it is consistent with. P2’s answers match a price of 2,000; P4’s a fee of 0.9%; P6’s a fee of 0.05 (0.6% divided by 12); P8’s missing existing repayments; P7’s answers match no input. All three participants whose answers matched the correct scenario (P1, P3, P5) scored 5 of 5; judged against the inferred inputs, 5 of 8 read the results correctly. With eight people, each participant moves the pass rate by 12.5 points. Full table: report Appendix E.
