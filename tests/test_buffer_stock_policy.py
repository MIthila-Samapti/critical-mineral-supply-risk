import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import buffer_stock_policy as bsp


def test_value_at_risk_uses_verified_vehicles_per_day():
    out = bsp.value_at_risk_per_stoppage_day()
    assert out["vehicles_per_day"] == bsp.VERIFIED["vehicles_per_day"]
    assert out["vehicles_per_day_verified"] is True
    assert out["assumed_avg_vehicle_value_verified"] is False


def test_value_at_risk_math_is_correct():
    out = bsp.value_at_risk_per_stoppage_day(vehicles_per_day=1000, avg_vehicle_value=50000)
    assert out["illustrative_output_value_at_risk_per_day_usd"] == 50_000_000


def test_buffer_stock_cost_by_tier_only_covers_defined_tiers():
    rows = bsp.buffer_stock_cost_by_tier()
    tiers_seen = {r["risk_tier"] for r in rows}
    # moderate tier has no elements in the heavy-REE table, so it's fine
    # for it to be absent; severe and high must be present.
    assert "severe (single-source dependent)" in tiers_seen
    assert "high (majority single-source)" in tiers_seen


def test_severe_tier_gets_more_buffer_weeks_than_high_tier():
    rows = bsp.buffer_stock_cost_by_tier()
    severe_weeks = {r["illustrative_weeks_of_buffer"] for r in rows if r["risk_tier"] == "severe (single-source dependent)"}
    high_weeks = {r["illustrative_weeks_of_buffer"] for r in rows if r["risk_tier"] == "high (majority single-source)"}
    assert min(severe_weeks) > max(high_weeks)


def test_carrying_cost_scales_with_weeks_of_buffer():
    rows = bsp.buffer_stock_cost_by_tier()
    severe = next(r for r in rows if r["risk_tier"] == "severe (single-source dependent)")
    high = next(r for r in rows if r["risk_tier"] == "high (majority single-source)")
    # same unit cost/consumption rate underlies both, so cost per week
    # of buffer should be equal
    severe_per_week = severe["illustrative_annual_carrying_cost_usd"] / severe["illustrative_weeks_of_buffer"]
    high_per_week = high["illustrative_annual_carrying_cost_usd"] / high["illustrative_weeks_of_buffer"]
    assert abs(severe_per_week - high_per_week) < 1e-6


def test_breakeven_compares_one_stoppage_day_to_annual_carrying_cost():
    out = bsp.stoppage_vs_carrying_cost_breakeven(days_of_stoppage_avoided=1)
    assert out["representative_element"] == "Terbium"
    assert out["illustrative_stoppage_value_at_risk_usd"] == out["illustrative_value_at_risk_per_stoppage_day_usd"]
    assert out["illustrative_ratio_stoppage_to_annual_carrying_cost"] > 1


def test_summarize_phase2_separates_verified_from_illustrative():
    out = bsp.summarize_phase2()
    assert set(out.keys()) == {
        "verified_facts",
        "illustrative_assumptions",
        "value_at_risk_per_stoppage_day",
        "buffer_stock_cost_by_tier",
        "stoppage_vs_carrying_cost_breakeven",
    }
    # verified facts block must not contain any of the illustrative keys
    assert "assumed_avg_vehicle_value_usd" not in out["verified_facts"]
    assert "jobs_onsite" not in out["illustrative_assumptions"]
