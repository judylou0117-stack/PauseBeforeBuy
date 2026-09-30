"""PauseBeforeBuy calculator: deterministic Python, no AI. ｜ 计算器：确定性 Python 计算，不使用 AI。"""
import math
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class UserProfile:
    monthly_income: float            # monthly take-home income / 每月税后收入
    cash_savings: float              # current cash savings / 现有现金储蓄
    essential_expenses: float        # monthly essentials: rent, food, transport / 每月必要支出（房租、饭钱、交通等）
    existing_debt_payments: float = 0.0          # existing monthly debt repayments / 每月已有的还款
    monthly_saving_capacity: Optional[float] = None  # monthly saving for the delay option; defaults to monthly surplus / 延迟购买时每月能存多少，不填则默认为每月结余


@dataclass
class Purchase:
    price: float                     # purchase price / 商品价格
    instalment_months: int           # number of instalments / 分期期数
    monthly_fee_rate: float = 0.0    # flat fee per instalment on the original price, e.g. 0.006 = 0.6% / 按原价每期收取的手续费率
    annual_interest_rate: float = 0.0  # amortised annual interest rate, e.g. 0.12 = 12% / 等额本息年利率
    upfront_fee: float = 0.0         # one-time upfront fee / 一次性手续费


@dataclass
class Settings:
    emergency_target_months: float = 3.0   # target emergency runway in months / 应急金目标月数
    max_debt_to_income: float = 0.35       # debt-to-income warning line; adjustable, not a regulatory standard / 月还款收入比警戒线（可调，非监管标准）
    severe_debt_to_income: float = 0.55    # severe line, based on MAS TDSR cap for property loans / 严重线，参考 MAS 房贷 TDSR 上限
    currency: str = "SGD"


# ---------------------------------------------------------------- Helpers / 工具函数
class StepLog:
    """Records every calculation step (label, formula, numbers, result) for display.
    记录每一步运算：名称、公式、代入数字、结果，前端可直接展示。"""
    def __init__(self):
        self.steps = []

    def add(self, option, label, formula, substitution, result):
        self.steps.append({"option": option, "label": label, "formula": formula,
                           "substitution": substitution, "result": result})
        return result


def money(x):
    return f"{x:,.2f}"


def pct(x):
    return f"{x * 100:.2f}%"


def r2(x):
    return None if x is None else round(x, 2)


def r4(x):
    return None if x is None else round(x, 4)


# ---------------------------------------------------------------- Input validation / 输入校验
def validate_inputs(p: UserProfile, q: Purchase):
    errors = []
    if p.monthly_income <= 0:
        errors.append("monthly_income must be greater than 0.")
    for name in ["cash_savings", "essential_expenses", "existing_debt_payments"]:
        if getattr(p, name) is None or getattr(p, name) < 0:
            errors.append(f"{name} must be 0 or greater.")
    if p.monthly_saving_capacity is not None and p.monthly_saving_capacity < 0:
        errors.append("monthly_saving_capacity must be 0 or greater.")
    if q.price <= 0:
        errors.append("price must be greater than 0.")
    if not isinstance(q.instalment_months, int) or q.instalment_months < 1:
        errors.append("instalment_months must be a whole number of at least 1.")
    if q.monthly_fee_rate < 0 or q.annual_interest_rate < 0 or q.upfront_fee < 0:
        errors.append("Fees and interest rates cannot be negative.")
    if q.monthly_fee_rate > 0 and q.annual_interest_rate > 0:
        errors.append("Provide either monthly_fee_rate or annual_interest_rate, not both.")
    return errors


# ---------------------------------------------------------------- Effective annual rate (IRR) / 实际年化利率
def effective_monthly_rate(amount_received, payment, n):
    """Solve monthly rate r so that amount_received = Σ payment / (1+r)^t, t = 1..n (bisection).
    用二分法求月利率 r。"""
    if payment * n <= amount_received + 1e-9:
        return 0.0

    def pv(r):
        return sum(payment / (1 + r) ** t for t in range(1, n + 1))

    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if pv(mid) > amount_received:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------- Main simulation / 主计算
def simulate(p: UserProfile, q: Purchase, s: Settings = Settings()):
    errors = validate_inputs(p, q)
    if errors:
        return {"ok": False, "errors": errors}

    log = StepLog()
    c = s.currency
    n = q.instalment_months

    # ---- Baseline / 基础量
    base_outflow = p.essential_expenses + p.existing_debt_payments
    log.add("baseline", "Monthly fixed outflow",
            "essential expenses + existing debt payments",
            f"{money(p.essential_expenses)} + {money(p.existing_debt_payments)}",
            f"{c} {money(base_outflow)}")

    disposable = p.monthly_income - base_outflow
    log.add("baseline", "Monthly surplus before purchase",
            "income - monthly fixed outflow",
            f"{money(p.monthly_income)} - {money(base_outflow)}",
            f"{c} {money(disposable)}")

    runway_now = p.cash_savings / base_outflow if base_outflow > 0 else None
    log.add("baseline", "Emergency runway today",
            "cash savings / monthly fixed outflow",
            f"{money(p.cash_savings)} / {money(base_outflow)}",
            f"{runway_now:.2f} months" if runway_now is not None else "unlimited (no fixed outflow)")

    # ---- Option A: pay in full / 方案 A：全款
    savings_after_full = p.cash_savings - q.price
    log.add("pay_in_full", "Savings left after paying in full",
            "cash savings - price",
            f"{money(p.cash_savings)} - {money(q.price)}",
            f"{c} {money(savings_after_full)}")
    runway_full = (max(savings_after_full, 0) / base_outflow) if base_outflow > 0 else None
    log.add("pay_in_full", "Emergency runway after paying in full",
            "max(savings left, 0) / monthly fixed outflow",
            f"{money(max(savings_after_full, 0))} / {money(base_outflow)}",
            f"{runway_full:.2f} months" if runway_full is not None else "unlimited")

    full = {
        "feasible": savings_after_full >= 0,
        "total_paid": r2(q.price),
        "cost_of_credit": 0.0,
        "monthly_payment": 0.0,
        "savings_after_purchase": r2(savings_after_full),
        "monthly_surplus_after": r2(disposable),
        "emergency_runway_months": r2(runway_full),
        "debt_to_income": r4(p.existing_debt_payments / p.monthly_income),
    }

    # ---- Option B: instalment / 方案 B：分期
    P = q.price
    if q.annual_interest_rate > 0:
        i = q.annual_interest_rate / 12
        pmt = P * i / (1 - (1 + i) ** -n)
        log.add("instalment", "Monthly instalment (amortised interest)",
                "P × i / (1 - (1 + i)^-n), i = annual rate / 12",
                f"{money(P)} × {i:.6f} / (1 - (1 + {i:.6f})^-{n})",
                f"{c} {money(pmt)}")
    else:
        principal_part = P / n
        fee_part = P * q.monthly_fee_rate
        pmt = principal_part + fee_part
        log.add("instalment", "Monthly instalment (flat fee on original price)",
                "price / n + price × monthly fee rate",
                f"{money(P)} / {n} + {money(P)} × {q.monthly_fee_rate}",
                f"{money(principal_part)} + {money(fee_part)} = {c} {money(pmt)}")

    total_inst = pmt * n + q.upfront_fee
    log.add("instalment", "Total repaid",
            "monthly instalment × n + upfront fee",
            f"{money(pmt)} × {n} + {money(q.upfront_fee)}",
            f"{c} {money(total_inst)}")

    cost_credit = total_inst - P
    log.add("instalment", "Extra cost of borrowing",
            "total repaid - price",
            f"{money(total_inst)} - {money(P)}",
            f"{c} {money(cost_credit)}")

    r_m = effective_monthly_rate(P - q.upfront_fee, pmt, n)
    ear = (1 + r_m) ** 12 - 1
    log.add("instalment", "Effective annual rate (what the fees really cost)",
            "solve r: price - upfront fee = Σ instalment / (1+r)^t; EAR = (1+r)^12 - 1",
            f"{money(P - q.upfront_fee)} = Σ {money(pmt)} / (1+r)^t, t = 1..{n}",
            f"monthly r = {pct(r_m)}, EAR = {pct(ear)}")

    surplus_inst = disposable - pmt
    log.add("instalment", "Monthly surplus during instalment",
            "monthly surplus before purchase - monthly instalment",
            f"{money(disposable)} - {money(pmt)}",
            f"{c} {money(surplus_inst)}")

    dti_inst = (p.existing_debt_payments + pmt) / p.monthly_income
    log.add("instalment", "Debt-to-income ratio",
            "(existing debt payments + instalment) / income",
            f"({money(p.existing_debt_payments)} + {money(pmt)}) / {money(p.monthly_income)}",
            pct(dti_inst))

    savings_after_inst = p.cash_savings - q.upfront_fee
    outflow_inst = base_outflow + pmt
    runway_inst = savings_after_inst / outflow_inst if outflow_inst > 0 else None
    log.add("instalment", "Emergency runway during instalment",
            "(cash savings - upfront fee) / (monthly fixed outflow + instalment)",
            f"{money(savings_after_inst)} / {money(outflow_inst)}",
            f"{runway_inst:.2f} months" if runway_inst is not None else "unlimited")

    inst = {
        "feasible": surplus_inst >= 0,
        "total_paid": r2(total_inst),
        "cost_of_credit": r2(cost_credit),
        "monthly_payment": r2(pmt),
        "monthly_fee_amount": r2(P * q.monthly_fee_rate),   # fee part of each instalment ｜ 每期月供中的手续费部分
        "instalment_months": n,
        "effective_annual_rate": r4(ear),
        "savings_after_purchase": r2(savings_after_inst),
        "monthly_surplus_after": r2(surplus_inst),
        "emergency_runway_months": r2(runway_inst),
        "debt_to_income": r4(dti_inst),
    }

    # ---- Option C: delay; assumes saving only from monthly surplus, savings untouched
    #      方案 C：延迟购买（假设只用每月结余攒钱，现有储蓄不动）
    capacity = p.monthly_saving_capacity if p.monthly_saving_capacity is not None else max(disposable, 0)
    if capacity > 0:
        months_wait = math.ceil(P / capacity)
        log.add("delay", "Months needed to save up",
                "ceil(price / monthly saving capacity)",
                f"ceil({money(P)} / {money(capacity)})",
                f"{months_wait} months")
    else:
        months_wait = None
        log.add("delay", "Months needed to save up",
                "ceil(price / monthly saving capacity)",
                f"monthly saving capacity = {money(capacity)}",
                "not reachable: no monthly surplus to save")

    delay = {
        "feasible": months_wait is not None,
        "total_paid": r2(P),
        "cost_of_credit": 0.0,
        "monthly_payment": 0.0,
        "monthly_saving_capacity": r2(capacity),
        "months_to_save": months_wait,
        "savings_after_purchase": r2(p.cash_savings),
        "monthly_surplus_after": r2(disposable),
        "emergency_runway_months": r2(runway_now),
        "debt_to_income": r4(p.existing_debt_payments / p.monthly_income),
    }

    options = {"pay_in_full": full, "instalment": inst, "delay": delay}
    for name, o in options.items():
        o["risk_flags"], o["risk_level"] = assess_risk(name, o, s)

    return {
        "ok": True,
        "currency": c,
        "inputs": {**asdict(p), **asdict(q)},
        "settings": asdict(s),
        "baseline": {
            "monthly_fixed_outflow": r2(base_outflow),
            "monthly_surplus": r2(disposable),
            "emergency_runway_months": r2(runway_now),
        },
        "options": options,
        "steps": log.steps,
        "assumptions": [
            "Delay option saves only from the monthly surplus and leaves current savings untouched.",
            "Emergency runway = savings divided by fixed monthly outflow (essentials + debt payments).",
            "No late fees, missed payments or income changes are modelled.",
        ],
    }


# ---------------------------------------------------------------- Risk rules: deterministic, not the model / 风险规则（确定性，不靠模型）
def assess_risk(name, o, s: Settings):
    flags = []
    severe = {"insufficient_savings", "negative_monthly_cash_flow", "cannot_save_up", "severe_debt_to_income"}

    if name == "pay_in_full" and o["savings_after_purchase"] < 0:
        flags.append("insufficient_savings")
    if o["monthly_surplus_after"] is not None and o["monthly_surplus_after"] < 0:
        flags.append("negative_monthly_cash_flow")
    runway = o["emergency_runway_months"]
    if runway is not None and runway < s.emergency_target_months:
        flags.append("below_emergency_target")
    if o["debt_to_income"] > s.severe_debt_to_income:
        flags.append("severe_debt_to_income")
    elif o["debt_to_income"] > s.max_debt_to_income:
        flags.append("high_debt_to_income")
    if o["cost_of_credit"] > 0:
        flags.append("extra_borrowing_cost")
    if name == "delay" and o["months_to_save"] is None:
        flags.append("cannot_save_up")

    if severe & set(flags) or (runway is not None and runway < 1):
        level = "high"
    elif {"below_emergency_target", "high_debt_to_income"} & set(flags):
        level = "medium"
    else:
        level = "low"
    return flags, level
