"""
Phase 2: buffer-stock / avoided-stoppage cost layer for rare earth magnet
supply risk, applied as a case study to BMW's Spartanburg, SC campus.

This module does NOT claim to know BMW's actual procurement costs, margins,
or buffer-stock policy. BMW has not published any of that, and none of it
is treated here as fact. What it does instead, in the same spirit as the
newsvendor-based safety stock work in Projects 1 and 2, is take verified
public facts about the Spartanburg plant and combine them with clearly
labeled illustrative assumptions to show the SHAPE of the tradeoff a
concentration-risk signal is meant to inform: a few extra weeks of magnet/
motor buffer stock, held against a severe single-source risk, costs real
but bounded money every year; a single day of full line stoppage for lack
of a part costs much more. The risk-tiering from Phase 1 (concentration_risk.py)
is what would tell a planner which parts deserve that extra buffer in the
first place.

Verified facts used (see data/README.md and docstrings below for sources):
  - BMW Plant Spartanburg: 11,000+ jobs onsite, ~1,500 vehicles/day across
    two shifts (bmwgroup-werke.com/spartanburg/en/our-plant.html).
  - $1.7B investment (announced Oct 2022, completed July 2026): ~$1.0B at
    Spartanburg for EV assembly prep, ~$700M for the new Woodruff, SC
    high-voltage battery assembly plant, plus a battery-cell supply
    agreement with Envision AESC (press.bmwgroup.com, T0458864EN).
  - BMW is among the named automakers (with Ford and Suzuki) that
    experienced documented 2025 production impacts tied to the China
    rare-earth magnet export shock (data/2025_export_shock_events.csv,
    Wood Mackenzie via supply-chain trade press, labeled secondary
    throughout).

Illustrative, explicitly-labeled assumptions used (NOT verified BMW figures):
  - An average per-vehicle value for Spartanburg's X3/X5/X6/X7 output,
    used only to express a plausible order of magnitude for "value of
    vehicle output at risk per stoppage day." BMW does not publish
    plant-level unit economics, so this is a round, conservative,
    stated assumption, not a quoted BMW figure.
  - An annual inventory carrying-cost rate, using the commonly-cited
    general supply-chain benchmark range of 20-30% of inventory value
    per year (see e.g. the Wikipedia "Carrying cost" summary of
    standard operations-management treatments), applied here to a
    hypothetical magnet/motor-component buffer, not a disclosed BMW cost.
  - A hypothetical magnet/motor-component unit cost and weekly
    consumption rate, used only to size what "N extra weeks of buffer"
    would cost to hold, scaled off Spartanburg's real production rate,
    not an actual BMW parts cost.

Every function that returns a dollar figure says explicitly, in its return
dict, which inputs were verified facts and which were illustrative
assumptions, so this is never silently presented as more certain than it is.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import concentration_risk as cr

# --- Verified facts (Spartanburg / Woodruff) ---------------------------
VERIFIED = {
    "jobs_onsite": 11000,
    "vehicles_per_day": 1500,
    "total_investment_usd": 1_700_000_000,
    "woodruff_battery_plant_investment_usd": 700_000_000,
    "spartanburg_ev_prep_investment_usd": 1_000_000_000,
    "models_assembled": ["X3", "X5", "X6", "X7", "XM"],
    "source": "bmwgroup-werke.com/spartanburg (plant facts); "
    "press.bmwgroup.com T0458864EN (investment completion, July 2026)",
}

# --- Illustrative assumptions (clearly separated from VERIFIED) -------
ILLUSTRATIVE = {
    "assumed_avg_vehicle_value_usd": 55_000,
    "assumed_avg_vehicle_value_note": (
        "Round, conservative illustrative assumption for the Spartanburg "
        "X3/X5/X6/X7/XM lineup. BMW does not publish plant-level unit "
        "economics; this is NOT a disclosed BMW figure."
    ),
    "annual_carrying_cost_rate": 0.25,
    "annual_carrying_cost_rate_note": (
        "Midpoint of the commonly-cited general supply-chain benchmark "
        "range of 20-30% of inventory value per year. A standard "
        "operations-management rule of thumb, not a BMW-specific cost."
    ),
    "assumed_magnet_motor_unit_cost_usd": 150,
    "assumed_magnet_motor_unit_cost_note": (
        "Hypothetical per-vehicle cost of the permanent-magnet motor "
        "component(s) exposed to heavy-rare-earth supply risk, used only "
        "to size a buffer-stock dollar example. Not a disclosed BMW or "
        "supplier cost."
    ),
}


def value_at_risk_per_stoppage_day(vehicles_per_day=None, avg_vehicle_value=None):
    """
    Illustrative value of vehicle output exposed per full day of line
    stoppage. This is a production-value figure, not a profit or cost
    figure (BMW's margin per vehicle is not public), so it should be read
    as "value of output at risk," not "BMW's dollar loss."
    """
    vehicles_per_day = vehicles_per_day or VERIFIED["vehicles_per_day"]
    avg_vehicle_value = avg_vehicle_value or ILLUSTRATIVE["assumed_avg_vehicle_value_usd"]
    return {
        "vehicles_per_day": vehicles_per_day,
        "vehicles_per_day_verified": True,
        "assumed_avg_vehicle_value_usd": avg_vehicle_value,
        "assumed_avg_vehicle_value_verified": False,
        "illustrative_output_value_at_risk_per_day_usd": vehicles_per_day * avg_vehicle_value,
    }


def buffer_stock_cost_by_tier(weeks_of_buffer_by_tier=None):
    """
    For each Phase 1 heavy-REE risk tier, an illustrative "how many extra
    weeks of magnet/motor-component buffer would this tier justify, and
    what would holding it cost per year" calculation. The tier labels and
    china_share_pct figures come from verified Phase 1 data; the number of
    weeks assigned to each tier, the unit cost, and the carrying-cost rate
    are illustrative policy choices, not observed BMW decisions.
    """
    if weeks_of_buffer_by_tier is None:
        # Illustrative policy: more weeks of buffer for more concentrated
        # (riskier) supply. A simple, transparent, non-fitted rule, not a
        # derived optimum.
        weeks_of_buffer_by_tier = {
            "severe (single-source dependent)": 8,
            "high (majority single-source)": 4,
            "moderate (diversified sourcing)": 1,
        }

    tiers = cr.heavy_ree_risk_tiers(cr.load_heavy_ree_import_reliance())
    vehicles_per_day = VERIFIED["vehicles_per_day"]
    unit_cost = ILLUSTRATIVE["assumed_magnet_motor_unit_cost_usd"]
    carrying_rate = ILLUSTRATIVE["annual_carrying_cost_rate"]

    # Illustrative daily consumption: one magnet/motor-relevant component
    # set per vehicle produced (a simplifying assumption, not a verified
    # bill-of-materials figure).
    weekly_consumption_units = vehicles_per_day * 7

    rows = []
    for _, r in tiers.iterrows():
        tier = r["risk_tier"]
        weeks = weeks_of_buffer_by_tier.get(tier)
        if weeks is None:
            continue
        buffer_units = weekly_consumption_units * weeks
        buffer_value_usd = buffer_units * unit_cost
        annual_carrying_cost_usd = buffer_value_usd * carrying_rate
        rows.append(
            {
                "element": r["element"],
                "china_share_pct": r["china_share_pct"],
                "risk_tier": tier,
                "illustrative_weeks_of_buffer": weeks,
                "illustrative_buffer_units": buffer_units,
                "illustrative_buffer_value_usd": round(buffer_value_usd, 2),
                "illustrative_annual_carrying_cost_usd": round(annual_carrying_cost_usd, 2),
            }
        )
    return rows


def stoppage_vs_carrying_cost_breakeven(days_of_stoppage_avoided=1):
    """
    The headline comparison: illustrative annual carrying cost of holding
    the "severe" tier's recommended buffer, versus the illustrative value
    of output protected by avoiding just N day(s) of full-line stoppage.
    Both numbers are illustrative dollar magnitudes built from the
    assumptions above, meant to show the SHAPE of the tradeoff (carrying
    cost is bounded and annual; a single stoppage day is a one-time shock
    of comparable or larger size), not a claimed BMW savings figure.
    """
    severe_rows = [
        r for r in buffer_stock_cost_by_tier() if r["risk_tier"] == "severe (single-source dependent)"
    ]
    if not severe_rows:
        return None
    # Use the first severe-tier element as the representative example.
    rep = severe_rows[0]
    var = value_at_risk_per_stoppage_day()
    stoppage_value = var["illustrative_output_value_at_risk_per_day_usd"] * days_of_stoppage_avoided
    return {
        "representative_element": rep["element"],
        "illustrative_annual_carrying_cost_usd": rep["illustrative_annual_carrying_cost_usd"],
        "illustrative_value_at_risk_per_stoppage_day_usd": var[
            "illustrative_output_value_at_risk_per_day_usd"
        ],
        "days_of_stoppage_in_comparison": days_of_stoppage_avoided,
        "illustrative_stoppage_value_at_risk_usd": stoppage_value,
        "illustrative_ratio_stoppage_to_annual_carrying_cost": (
            round(stoppage_value / rep["illustrative_annual_carrying_cost_usd"], 2)
            if rep["illustrative_annual_carrying_cost_usd"]
            else None
        ),
        "note": (
            "Both figures are illustrative dollar magnitudes built from "
            "stated assumptions (see ILLUSTRATIVE dict), anchored to "
            "verified Spartanburg production facts (vehicles/day, jobs "
            "onsite). Neither is a disclosed BMW cost or savings figure."
        ),
    }


def summarize_phase2():
    return {
        "verified_facts": VERIFIED,
        "illustrative_assumptions": ILLUSTRATIVE,
        "value_at_risk_per_stoppage_day": value_at_risk_per_stoppage_day(),
        "buffer_stock_cost_by_tier": buffer_stock_cost_by_tier(),
        "stoppage_vs_carrying_cost_breakeven": stoppage_vs_carrying_cost_breakeven(),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(summarize_phase2(), indent=2, default=str))
