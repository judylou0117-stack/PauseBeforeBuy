"""The full pipeline, independent of the web framework so it can be tested on its own.
完整流程，不依赖 Web 框架，便于单独测试。

validate input -> Python calculation -> model explanation -> checks -> response
校验输入 -> Python 计算 -> 模型解释 -> 校验 -> 返回结果
"""
from .calculator import UserProfile, Purchase, Settings, simulate
from .explainer import explain, clean_item_name, PROMPT_VERSION

LANGUAGES = {"English", "Chinese"}
REQUIRED = [("profile", "monthly_income"), ("profile", "cash_savings"), ("profile", "essential_expenses"),
            ("purchase", "price"), ("purchase", "instalment_months")]


def _missing_fields(req):
    """Missing or non-numeric required fields (edge case E2). ｜ 缺失或非数字的必填字段（边界案例 E2）。"""
    errors = []
    for group, name in REQUIRED:
        v = (req.get(group) or {}).get(name)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            errors.append(f"{name} is required and must be a number.")
    return errors


def _as_int(v):
    return int(v) if isinstance(v, float) and v.is_integer() else v


def run_simulation(req, client=None, model=""):
    profile = req.get("profile", {})
    purchase = req.get("purchase", {})
    settings = req.get("settings", {}) or {}
    language = req.get("language", "English")
    if language not in LANGUAGES:
        language = "English"
    item_name = clean_item_name(purchase.get("item_name", ""))

    missing = _missing_fields(req)
    if missing:
        return {"calc": {"ok": False, "errors": missing}, "explanation": None, "prompt_version": PROMPT_VERSION,
                "model": model or None,
                "checks": {"ok": False, "schema_problems": [], "unverified_numbers": [], "error": "invalid_input"},
                "usage": {"input_tokens": 0, "output_tokens": 0}, "cost_usd": 0.0}

    calc = simulate(
        UserProfile(
            monthly_income=profile.get("monthly_income"),
            cash_savings=profile.get("cash_savings"),
            essential_expenses=profile.get("essential_expenses"),
            existing_debt_payments=profile.get("existing_debt_payments", 0) or 0,
        ),
        Purchase(
            price=purchase.get("price"),
            instalment_months=_as_int(purchase.get("instalment_months")),
            monthly_fee_rate=purchase.get("monthly_fee_rate", 0) or 0,
            annual_interest_rate=purchase.get("annual_interest_rate", 0) or 0,
            upfront_fee=purchase.get("upfront_fee", 0) or 0,
        ),
        Settings(
            emergency_target_months=settings.get("emergency_target_months", 3.0) or 3.0,
            max_debt_to_income=settings.get("max_debt_to_income", 0.35) or 0.35,
            currency="SGD",
        ),
    )
    response = {"calc": calc, "explanation": None, "prompt_version": PROMPT_VERSION, "model": model or None,
                "checks": {"ok": False, "schema_problems": [], "unverified_numbers": [], "error": None},
                "usage": {"input_tokens": 0, "output_tokens": 0}, "cost_usd": 0.0}
    if not calc["ok"]:
        response["checks"]["error"] = "invalid_input"
        return response
    calc["inputs"]["item_name"] = item_name

    if client is None:
        response["checks"]["error"] = "model_not_configured"
        return response

    r = explain(client, model, calc, item_name=item_name, language=language)
    response["explanation"] = r["explanation"]
    response["checks"] = {"ok": r["ok"], "schema_problems": r["schema_problems"],
                          "unverified_numbers": r["unverified_numbers"], "error": r["error"]}
    response["usage"] = r["usage"]
    response["cost_usd"] = r["cost_usd"]
    return response
