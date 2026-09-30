"""FastAPI entry point: a thin web layer around service.run_simulation.
FastAPI 入口：对 service.run_simulation 的一层薄包装。

Run locally ｜ 本地运行:  uvicorn app.main:app --reload
Environment variables ｜ 环境变量:
  OPENROUTER_API_KEY   required for AI explanations (without it, only calculations are returned)
  MODEL                default "anthropic/claude-haiku-4.5"
  ALLOWED_ORIGINS      comma-separated front-end origins, e.g. "https://yourname.github.io" (default "*")
  RATE_LIMIT_PER_10MIN default 30 requests per IP
"""
import os
import time
from collections import defaultdict, deque
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .service import run_simulation

MODEL = os.getenv("MODEL", "anthropic/claude-haiku-4.5")
API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_10MIN", "30"))

client = None
if API_KEY:
    from openai import OpenAI
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY, timeout=40, max_retries=1)

app = FastAPI(title="PauseBeforeBuy API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=ORIGINS, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


class Profile(BaseModel):
    monthly_income: float
    cash_savings: float
    essential_expenses: float
    existing_debt_payments: float = 0


class PurchaseIn(BaseModel):
    item_name: str = Field("", max_length=200)
    price: float
    instalment_months: int = Field(ge=1, le=120)
    monthly_fee_rate: float = 0
    annual_interest_rate: float = 0
    upfront_fee: float = 0


class SettingsIn(BaseModel):
    emergency_target_months: float = Field(3.0, gt=0, le=24)
    max_debt_to_income: float = Field(0.35, gt=0, lt=1)
    currency: str = "SGD"


class SimulateRequest(BaseModel):
    profile: Profile
    purchase: PurchaseIn
    settings: SettingsIn = SettingsIn()
    language: Literal["English", "Chinese"] = "English"


# Simple in-memory rate limit, so a public link cannot run up the model bill
# 简单的内存限流，防止公开链接被刷而产生大量模型费用
_hits = defaultdict(deque)


def _allowed(ip):
    now, window = time.time(), 600
    q = _hits[ip]
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= RATE_LIMIT:
        return False
    q.append(now)
    return True


@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL, "model_configured": client is not None}


@app.post("/simulate")
def simulate_endpoint(body: SimulateRequest, request: Request):
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown").split(",")[0].strip()
    if not _allowed(ip):
        return JSONResponse(status_code=429, content={"detail": "Too many requests. Please wait a few minutes."})
    return run_simulation(body.model_dump(), client=client, model=MODEL)
