# Data used in PauseBeforeBuy

**No real personal or financial data is used anywhere in this project.**

## 1. Inputs to the product

| Data | Source | Where |
|---|---|---|
| Example user profiles and purchases | Synthetic, written for testing | `backend/tests/`, `notebooks/` |
| Study scenario (laptop SGD 6,000, 12 instalments, 0.6% per instalment; income 3,500; savings 5,000; essentials 2,200; existing repayments 300) | Fictional | `study/`, report Appendix E |
| Ten evaluation cases (5 typical, 3 edge, 2 adversarial) | Synthetic | `evals/README.md`, `notebooks/03_evaluation_10_cases.ipynb` |

Real users’ inputs are never sent to us for storage: they stay in the user’s browser and are only sent to the API to calculate one result.

## 2. Reference figures behind the risk rules

Instead of retrieval (RAG), the few authoritative figures are encoded as deterministic rules in `backend/app/calculator.py` (`Settings`).

| Figure | Used for | Source |
|---|---|---|
| Emergency fund target of 3 months (guide recommends 3–6) | `below_emergency_target` flag | Monetary Authority of Singapore (2023) *Basic Financial Planning Guide* |
| 55% of income on repayments | `severe_debt_to_income` (high risk) | Monetary Authority of Singapore (2026) *Mortgage Servicing Ratio and Total Debt Servicing Ratio Rules* (TDSR cap for property loans) |
| 35% of income on repayments | `high_debt_to_income` (medium risk) | **Design assumption**, not a regulatory figure |
| Emergency runway under 1 month | high risk | **Design assumption** |
| SGD 2,000 outstanding per BNPL provider before income assessment | problem framing (intro page, report Section 1) | Singapore FinTech Association (2022) *BNPL Code of Conduct* |
| BNPL outside rate caps and aggregate limits | problem framing | Lim (2026), Research Square preprint, not peer reviewed |

Full Harvard references: report Appendix G.

## 3. User-study data

`study/PauseBeforeBuy_comprehension_scoring.xlsx` contains the eight anonymised responses (IDs P1–P8, no names, emails or timestamps) and the scoring. See `study/README.md`.
