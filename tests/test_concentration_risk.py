import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import concentration_risk as cr


def test_hhi_single_supplier_is_max():
    assert cr.hhi([100]) == 10000


def test_hhi_two_equal_suppliers():
    assert cr.hhi([50, 50]) == 5000


def test_production_reserves_excludes_world_total_and_other():
    df = cr.load_production_reserves()
    assert "World Total" not in df["country"].values
    assert "Other" not in df["country"].values


def test_production_reserves_has_no_negative_values():
    df = cr.load_production_reserves()
    for col in ["mine_production_tons_reo", "reserves_tons_reo"]:
        valid = df[col].dropna()
        assert (valid >= 0).all()


def test_concentration_by_year_china_is_top_producer_every_edition():
    df = cr.load_production_reserves()
    conc = cr.concentration_by_year(df, "mine_production_tons_reo")
    # China should be the top mine-production country in every (report, year)
    # snapshot, consistent with every public source reviewed for this project.
    assert (conc["top1_country"] == "China").all()


def test_heavy_ree_risk_tiers_terbium_is_severe():
    raw = cr.load_heavy_ree_import_reliance()
    tiers = cr.heavy_ree_risk_tiers(raw)
    terbium = tiers[tiers["element"] == "Terbium"].iloc[0]
    assert terbium["risk_tier"] == "severe (single-source dependent)"
    assert terbium["china_share_pct"] == 100.0


def test_heavy_ree_risk_tiers_handles_missing_dysprosium_gracefully():
    raw = cr.load_heavy_ree_import_reliance()
    tiers = cr.heavy_ree_risk_tiers(raw)
    dysprosium = tiers[tiers["element"] == "Dysprosium"].iloc[0]
    assert "unknown" in dysprosium["risk_tier"]


def test_us_import_reliance_trend_is_declining_not_rising():
    # Real, verified, honest finding: the US's net import reliance figure
    # fell from >95% (2021-2022) to ~53-67% (2024-2025e), the opposite of
    # a simple "crisis getting worse" story. This test guards against ever
    # silently flipping or misreporting that direction.
    trend = cr.load_us_import_reliance_trend()
    first_val = trend.iloc[0]["net_import_reliance_pct"]
    last_val = trend.iloc[-1]["net_import_reliance_pct"]
    # values like ">95" need the leading '>' stripped before comparing
    first_num = float(str(first_val).lstrip(">"))
    last_num = float(str(last_val).lstrip(">"))
    assert last_num < first_num


def test_shock_events_automaker_impact_includes_bmw():
    shocks = cr.load_shock_events()
    row = shocks[shocks["metric"] == "automakers_with_reported_production_impact"].iloc[0]
    assert "BMW" in row["value"]


def test_summarize_returns_all_four_pieces():
    out = cr.summarize()
    assert set(out.keys()) == {
        "concentration",
        "heavy_ree_tiers",
        "us_import_reliance_trend",
        "shock_events",
    }
    for df in out.values():
        assert len(df) > 0
