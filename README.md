# PauseBeforeBuy

**Making the true cost of instalments visible before you pay.**

A decision-support tool for students and young working adults. It compares **paying in full**, **paying in instalments** and **waiting to save**, and shows what each does to total cost, monthly cash flow and emergency savings, including the true yearly cost of instalment fees (0.6% per instalment = 13.84% a year).

NTU MSc Enterprise AI · PE6201 Emerging AI Technologies · End-of-course project · Yao Lu (Section C)

| | |
|---|---|
| Live product | https://judylou0117-stack.github.io/PauseBeforeBuy/ |
| Back end (API) | https://pausebeforebuy.onrender.com (free tier: the first request may take up to a minute to wake the server) |
| Demo video | [add the demo video link here] |
| Report | [`report/PauseBeforeBuy_Final_Report_YaoLu.docx`](report/) |

## Documentation

| Document | Contents |
|---|---|
| [`PRODUCT.md`](PRODUCT.md) | Persona, input, output, architecture diagram, metrics targeted versus reached |
| [`data/README.md`](data/README.md) | What data is used (all synthetic or fictional) and the cited sources behind the risk thresholds |
| [`evals/README.md`](evals/README.md) | L1 tests, live-response checks, the ten-case set and results, prompt iteration, human review |
| [`study/README.md`](study/README.md) | User comprehension study: method, questionnaire script, anonymised responses, scoring, diagnosis |
| [`notebooks/`](notebooks/) | 01 prototype and prompt v1→v2 · 02 back-end verification and prompt v3→v4 · 03 ten-case evaluation against the live API |

## Design principle: calculation in code, language in the model

| Layer | What it does | Built or rented |
|---|---|---|
| Calculator (`backend/app/calculator.py`) | Every number: repayments, effective annual rate (IRR), emergency runway, risk rules | Built, deterministic Python (standard library only) |
| Explainer (`backend/app/explainer.py`) | Turns the results into plain English or Chinese (prompt v4) | Rented: Claude Haiku 4.5 via OpenRouter |
| Checks (`backend/app/explainer.py`) | JSON schema check and number validator: every number the model writes must trace back to the calculator | Built |
| Pipeline (`backend/app/service.py`, `backend/app/main.py`) | Validate → calculate → explain → check; FastAPI endpoints `POST /simulate`, `GET /health` | Built |
| Front end (`docs/index.html`) | Intro, two-step form, 5-second pause, side-by-side results; never calculates | Built, GitHub Pages |

If the model fails, returns invalid JSON or writes a number that is not in the calculation, the explanation is withheld and the user sees the calculated results only.

## Repository layout

```
backend/
  app/calculator.py   deterministic calculations and risk rules
  app/explainer.py    prompt v4, model call, schema and number checks
  app/service.py      full pipeline, independent of the web framework
  app/main.py         FastAPI: POST /simulate, GET /health, rate limit
  tests/              19 tests: calculator (L1) and pipeline with a fake model
docs/index.html       front end (GitHub Pages)
notebooks/            Colab notebooks 01–03
data/  evals/  study/ explainers, evaluation set, study materials
assets/               architecture diagram and screenshots
report/               final report
render.yaml           back-end deployment settings
```

## Run the tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest -q        # expected: 19 passed (no API key or network needed)
```

## Run the back end locally

```bash
cd backend
pip install -r requirements.txt
export OPENROUTER_API_KEY=your-key     # optional: without it, the API returns calculations only
uvicorn app.main:app --reload
```

Then open `docs/index.html` and set `API_BASE_URL` at the top of its script to `http://127.0.0.1:8000`. With `API_BASE_URL` empty, the page runs in demo mode with a sample case.

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

**Back end (Render):** Web Service from this repository, root directory `backend`, build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (or use `render.yaml`). Environment variables: `OPENROUTER_API_KEY` (never committed), `ALLOWED_ORIGINS` (the GitHub Pages origin), `PYTHON_VERSION=3.12.8`.

**Front end (GitHub Pages):** Settings → Pages → branch `main`, folder `/docs`; set `API_BASE_URL` in `docs/index.html` to the Render URL.

## Results in brief

Ten-case set: 10/10 deterministic checks, 8/8 explanations verified, 6/8 passed human review, 2/2 invalid inputs blocked, 0 injection leaks, about USD 0.0047 and 7.7 s per simulation. User study (8 classmates): 50% passed against a 70% target; all three participants who entered the scenario correctly scored 5 of 5. See `PRODUCT.md` for the full metrics table.

Educational decision support, not financial advice.
