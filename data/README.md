# Data sources and honest caveats

## What's in here

- `usgs_world_production_reserves.csv`: country-level rare earth mine production and reserves, transcribed directly from two consecutive official USGS Mineral Commodity Summaries reports (MCS2025, covering data years 2023-2024e, and MCS2026, covering 2024-2025e). Source: pubs.usgs.gov/periodicals/mcs2025/mcs2025-rare-earths.pdf and .../mcs2026/mcs2026-rare-earths.pdf.
- `usgs_us_salient_stats.csv`: US production/import/export/net-import-reliance figures, same two reports, years 2020-2025e.
- `heavy_ree_import_reliance_2026.csv`: US import-source breakdown for heavy rare earths (terbium, holmium, lutetium, erbium, ytterbium), from the MCS2026 "heavy rare earths" companion report.
- `2025_export_shock_events.csv`: the 2025 Chinese export-control shock (export volume drops, license approval rates, country-level import declines, named automaker production impacts). This is **not** primary government data, it's transcribed from secondary reporting (Wood Mackenzie analysis as relayed in supply-chain trade press). Flagged as such so it's never mistaken for an official statistic.

## Why not a direct trade-data API

US Census international trade API (api.census.gov) and pubs.usgs.gov were both unreachable from this build environment's network policy (and the Census API additionally requires a registered key). UN Comtrade now requires a registered API key with rate limits. Rather than block the project on access, the official USGS annual PDF reports (public, no login, no key) were read and their data tables transcribed directly, exactly as published. This is the same workaround pattern used in the pharma-shortage-risk project when direct openFDA API access wasn't available.

## Nuances to carry into the model, not gloss over

1. **Three different concentration metrics exist and they tell different stories**: mine production share (China ~69% of world total), reserves share (Australia, not China, holds the largest reserve base per MCS2026's 6.3M ton figure, though MCS2025 had shown Australia at 125.7M tons, a large downward revision between editions, most likely a reserves-definition/reclassification change rather than a real-world loss of resources, worth a one-line caveat rather than treating it as noise), and *processing* share (China >90%, per Wood Mackenzie, separate from and not published in USGS's mine-production tables). The model should treat these as three distinct signals, not collapse them into one number.
2. **US net import reliance is declining, not worsening**, over 2021-2025 (>95% down to ~53-67%), likely reflecting domestic separation/processing capacity ramping up (compounds/metals production up from ~95 tons in 2022 to ~8,900 tons in 2025e). That's a real, honest, partially-offsetting trend against the "crisis" framing, it should be reported, not hidden, even though it complicates a simple doom narrative.
3. **Heavy rare earths (terbium, dysprosium) are the specific magnet-performance risk**, not light rare earths generally. Terbium import reliance is 100% China with no breakdown of alternate sources at all. Dysprosium isn't broken out in the 2026 heavy-REE import table and needs a secondary source if a specific number is wanted; don't fabricate one.
4. **The 2025 shock-event numbers are from secondary reporting, not an original pull from Chinese export statistics.** They're credible (multiple reputable outlets, consistent across articles found during research) but should be labeled as secondary throughout the project, the same way the README here labels them.
