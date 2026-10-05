# Critical Mineral Supply Risk Intelligence

Country- and import-source-level concentration risk analysis for rare earth
magnets, applied as a case study to BMW's Spartanburg/Woodruff, South
Carolina EV campus. Built as Component 3 (predictive risk intelligence) of
the AI-Powered Predictive Supply Chain Resilience Framework described in
Mithila Zaman Samapti's EB-2 NIW Professional Plan.

Same core idea as [pharma-shortage-risk](https://github.com/MIthila-Samapti/pharma-shortage-risk):
concentration of supply is the risk signal.

## What's here

- `data/` — USGS Mineral Commodity Summaries (MCS2025, MCS2026) production,
  reserves, and heavy-rare-earth import-reliance data, transcribed directly
  from the official published reports; plus the 2025 China export-control
  shock event data (labeled secondary throughout, source Wood Mackenzie via
  supply-chain press). Full source documentation and honest caveats in
  `data/README.md`.
- `src/concentration_risk.py` — HHI and top-1-share concentration metrics;
  heavy-REE risk tiering.
- `src/buffer_stock_policy.py` — illustrative buffer-stock sizing and
  avoided-stoppage-cost tradeoff, applied to BMW Spartanburg, with every
  dollar figure labeled verified or illustrative.
- `notebooks/01_concentration_risk.ipynb` — Phase 1 analysis notebook.
- `dashboard/` — accessibility-validated HTML/PNG dashboard.
- `tests/` — 17 passing pytest tests.

## Key honest findings

1. China's apparent mine-production share jump between MCS2025 and MCS2026
   is a USGS reporting-basis revision for Burma/Madagascar estimates, not a
   real 2025 event. Documented explicitly rather than misreported as a trend.
2. US net import reliance on rare earths has been *declining*, not
   worsening, 2021-2025, likely reflecting real domestic processing
   capacity coming online (e.g. MP Materials).
3. Terbium, holmium, and lutetium sit at 100% US import reliance on China:
   severe single-source dependence in exactly the elements that matter most
   for magnet performance.

## BMW Spartanburg case study

BMW's Spartanburg plant (11,000+ jobs onsite, ~1,500 vehicles/day) and the
new Woodruff, SC battery plant, part of BMW's completed $1.7B investment,
depend on permanent-magnet EV motor technology built from these
import-concentrated heavy rare earths. In 2025, BMW was one of several
automakers with documented production impacts from China's rare earth
export-control shock. This project's risk tiers would have flagged that
exposure in advance, from public data alone.

Full writeup: `NIW_Project4_Explanation.docx` (not committed here;
available on request as it's a petition document, not project
documentation).

## License

MIT
