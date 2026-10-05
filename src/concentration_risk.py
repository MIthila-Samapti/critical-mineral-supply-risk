"""
Country/supplier concentration risk for critical minerals (rare earths).

Core idea, same one used in the pharma-shortage-risk project: concentration
of supply is the risk signal. Here that means how few countries (or, for
heavy rare earths, how few source countries for US imports) account for
most of the supply of a given material.

Three separate concentration metrics are computed on purpose, not collapsed
into one score, because they answer different questions (see data/README.md
for why they diverge):

1. Mine production concentration (who digs it up)
2. Reserve concentration (who could dig it up in the future)
3. Import-source concentration for heavy rare earths (who the US actually
   buys the magnet-grade elements from right now)

A country/element is flagged high risk if a small number of suppliers
account for most of the volume, using both a top-1 share and an HHI
(Herfindahl-Hirschman Index, sum of squared market shares, 0-10000, higher
means more concentrated, a standard concentration measure also used in
antitrust analysis).
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Rows that aren't real countries and should be excluded from concentration
# math (including them would understate concentration, since "Other" and
# "World Total" aren't actual competing suppliers).
NON_COUNTRY_ROWS = {"World Total", "Other"}


def _clean_numeric(series):
    """USGS tables use '—' for zero/none and 'NA' for not available."""
    return pd.to_numeric(
        series.astype(str).str.replace(",", "").replace({"—": "0", "NA": None}),
        errors="coerce",
    )


def hhi(shares_pct):
    """Herfindahl-Hirschman Index from a list of percentage shares (0-100)."""
    return sum(s**2 for s in shares_pct)


def load_production_reserves():
    df = pd.read_csv(DATA_DIR / "usgs_world_production_reserves.csv")
    df = df[~df["country"].isin(NON_COUNTRY_ROWS)].copy()
    df["mine_production_tons_reo"] = _clean_numeric(df["mine_production_tons_reo"])
    df["reserves_tons_reo"] = _clean_numeric(df["reserves_tons_reo"])
    return df


def concentration_by_year(df, value_col):
    """
    For each (source_report, data_year), compute each country's share of
    the total, then the top-1 share and HHI across countries.
    Rows with missing/zero value_col are dropped for that metric only.
    """
    results = []
    for (report, year), grp in df.groupby(["source_report", "data_year"]):
        grp = grp.dropna(subset=[value_col])
        grp = grp[grp[value_col] > 0]
        total = grp[value_col].sum()
        if total == 0 or len(grp) == 0:
            continue
        shares = (grp[value_col] / total * 100).round(2)
        top1_country = grp.loc[shares.idxmax(), "country"]
        top1_share = shares.max()
        results.append(
            {
                "source_report": report,
                "data_year": year,
                "metric": value_col,
                "n_countries": len(grp),
                "top1_country": top1_country,
                "top1_share_pct": top1_share,
                "hhi": round(hhi(shares.tolist()), 1),
            }
        )
    return pd.DataFrame(results).sort_values(["metric", "data_year"])


def load_heavy_ree_import_reliance():
    df = pd.read_csv(DATA_DIR / "heavy_ree_import_reliance_2026.csv")
    return df


def heavy_ree_risk_tiers(df):
    """
    Simple, honest tiering for US import-source concentration on heavy
    rare earths (the magnet-grade elements). Not a continuous score here,
    the underlying table only has 5 elements, a 3-bucket tier is more
    honest than pretending there's enough resolution for a smooth index.
    """
    def tier(china_share):
        if pd.isna(china_share):
            return "unknown (not broken out in source table)"
        if china_share >= 95:
            return "severe (single-source dependent)"
        if china_share >= 50:
            return "high (majority single-source)"
        return "moderate (diversified sourcing)"

    df = df.copy()
    df["risk_tier"] = df["china_share_pct"].apply(tier)
    return df[["element", "magnet_relevant", "china_share_pct", "risk_tier", "notes"]]


def load_us_import_reliance_trend():
    df = pd.read_csv(DATA_DIR / "usgs_us_salient_stats.csv")
    df = df.dropna(subset=["net_import_reliance_pct"])
    return df[["source_report", "year", "net_import_reliance_pct"]].sort_values("year")


def load_shock_events():
    return pd.read_csv(DATA_DIR / "2025_export_shock_events.csv")


def summarize():
    """One-call summary used by the notebook and by tests."""
    prod_res = load_production_reserves()
    conc = pd.concat(
        [
            concentration_by_year(prod_res, "mine_production_tons_reo"),
            concentration_by_year(prod_res, "reserves_tons_reo"),
        ]
    )
    heavy = heavy_ree_risk_tiers(load_heavy_ree_import_reliance())
    reliance_trend = load_us_import_reliance_trend()
    shocks = load_shock_events()
    return {
        "concentration": conc,
        "heavy_ree_tiers": heavy,
        "us_import_reliance_trend": reliance_trend,
        "shock_events": shocks,
    }


if __name__ == "__main__":
    out = summarize()
    for name, df in out.items():
        print(f"\n=== {name} ===")
        print(df.to_string(index=False))
