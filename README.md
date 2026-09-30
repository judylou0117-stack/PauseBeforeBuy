# PauseBeforeBuy

Decision support for young adults who are about to buy something in instalments. It compares three options, **pay in full**, **pay in instalments** and **wait and save**, and shows what each one does to total cost, monthly cash flow and emergency savings, including the true yearly cost of instalment fees.

NTU MSc Enterprise AI · PE6201 Emerging AI Technologies · End-of-course project · Yao Lu

## Design principle: calculation in code, language in the model

| Layer | What it does | Owned or rented |
|---|---|---|
| Calculator (`backend/app/calculator.py`) | Every number: repayments, true annual rate (IRR), emergency runway, risk rules | Owned, deterministic Python |
| Explainer (`backend/app/explainer.py`) | Turns the results into plain English or Chinese (prompt v4) | Rented: Claude Haiku 4.5 via OpenRouter |
| Checks (`backend/app/explainer.py`) | JSON schema check and a number validator: every number the model writes must trace back to the calculator | Owned |
| Front end (`docs/index.html`) | Intro, two-step form, pause moment, results | Owned, static page on GitHub Pages |

If the model fails, returns invalid JSON or writes a number that is not in the calculation, the explanation is hidden and the user sees the calculated results only.

## Repository layout

```
backend/
  app/calculator.py   deterministic calculations and risk rules
  app/explainer.py    prompt v4, model call, schema and number checks
  app/service.py      full pipeline, independent of the web framework
  app/main.py         FastAPI: POST /simulate, GET /health
  tests/              L1 calculator tests and pipeline tests with a fake model
docs/index.html       front end (GitHub Pages)
notebooks/
  01_prototype_calculator_and_prompts.ipynb      Colab prototype, L1 tests, prompt v1 → v2 iteration log
  02_backend_verification_and_prompt_v4.ipynb    back-end tests in Colab, real model call, prompt v3 → v4 iteration
render.yaml           back-end deployment settings
```

## Run the tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest -q
```

No API key or network is needed: the pipeline tests use a fake model.

## API

`POST /simulate`

```json
{
  "profile": {"monthly_income": 3500, "cash_savings": 5000, "essential_expenses": 2200, "existing_debt_payments": 300},
  "purchase": {"item_name": "Laptop", "price": 6000, "instalment_months": 12, "monthly_fee_rate": 0.006, "annual_interest_rate": 0, "upfront_fee": 0},
  "settings": {"emergency_target_months": 3, "max_debt_to_income": 0.35, "currency": "SGD"},
  "language": "English"
}
```

Returns `calc` (all numbers and calculation steps), `explanation` (only when verified), `checks`, `usage` and `cost_usd`.

## Deploy

**Back end (Render).** Create a Web Service from this repository with root directory `backend`, build command `pip install -r requirements.txt` and start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (or use `render.yaml`). Environment variables:

| Variable | Value |
|---|---|
| `OPENROUTER_API_KEY` | your OpenRouter key (never commit it) |
| `ALLOWED_ORIGINS` | your GitHub Pages origin, e.g. `https://username.github.io` |
| `PYTHON_VERSION` | `3.12.8` |

**Front end (GitHub Pages).** Settings → Pages → deploy from branch `main`, folder `/docs`. Then set `API_BASE_URL` at the top of the script in `docs/index.html` to the Render URL. With `API_BASE_URL` empty, the page runs in demo mode with a sample case.

## Cost

About USD 0.004 per simulation with Claude Haiku 4.5 (about 1,200 input and 650 output tokens). The API limits each IP address to 30 requests per 10 minutes.

## Limitations

Educational decision support, not financial advice. Late fees, missed payments and income changes are not modelled. Thresholds (3-month emergency target from the MAS Basic Financial Planning Guide; 35% repayment warning line as a design assumption; 55% severe line with reference to the MAS TDSR cap for property loans) are adjustable settings. The number validator guarantees traceability, not correct use of each number; see the iteration log in the notebook.
