"""L1 tests for the calculator (same cases as Part 3 of the notebook). ｜ 计算器 L1 测试（与笔记本第 3 部分相同）。
Run ｜ 运行:  python -m pytest -q   (from the backend folder)"""
from app.calculator import UserProfile, Purchase, simulate


def approx(a, b, tol=0.01):
    return abs(a - b) <= tol


def test_zero_percent_instalment():
    i = simulate(UserProfile(2000, 3000, 1400), Purchase(1800, 12))["options"]["instalment"]
    assert approx(i["monthly_payment"], 150) and approx(i["total_paid"], 1800) and i["effective_annual_rate"] == 0


def test_flat_fee_and_true_annual_rate():
    c = simulate(UserProfile(3500, 5000, 2200, 300), Purchase(6000, 12, monthly_fee_rate=0.006))
    i = c["options"]["instalment"]
    assert approx(i["monthly_payment"], 536) and approx(i["total_paid"], 6432) and approx(i["cost_of_credit"], 432)
    assert approx(i["monthly_fee_amount"], 36)
    assert i["effective_annual_rate"] > 0.072 * 1.8
    assert c["options"]["pay_in_full"]["risk_level"] == "high"


def test_amortised_reference_value():
    c = simulate(UserProfile(5000, 10000, 2000), Purchase(12000, 12, annual_interest_rate=0.12))
    assert approx(c["options"]["instalment"]["monthly_payment"], 1066.19)


def test_delay_months():
    c = simulate(UserProfile(3500, 5000, 2200, 300), Purchase(6000, 12))
    assert c["options"]["delay"]["months_to_save"] == 6


def test_zero_savings():
    c = simulate(UserProfile(2500, 0, 2000), Purchase(1200, 6))
    assert c["ok"] and all(o["risk_level"] == "high" for o in c["options"].values())


def test_no_surplus():
    c = simulate(UserProfile(2000, 1000, 2000), Purchase(500, 3))
    assert c["options"]["delay"]["months_to_save"] is None and "cannot_save_up" in c["options"]["delay"]["risk_flags"]


def test_invalid_and_contradictory_input_rejected():
    c = simulate(UserProfile(0, -1, 100), Purchase(100, 0, monthly_fee_rate=0.01, annual_interest_rate=0.1))
    assert not c["ok"] and len(c["errors"]) == 4


def test_two_tier_debt_to_income():
    c = simulate(UserProfile(2000, 20000, 500), Purchase(8000, 10))
    assert "high_debt_to_income" in c["options"]["instalment"]["risk_flags"] and c["options"]["instalment"]["risk_level"] == "medium"
    c = simulate(UserProfile(2000, 20000, 500), Purchase(12000, 10))
    assert "severe_debt_to_income" in c["options"]["instalment"]["risk_flags"] and c["options"]["instalment"]["risk_level"] == "high"
