# Assumptions Register

A single place listing every assumption in the project, so observed evidence and
analytical assumptions are never conflated. Each entry notes the basis and where
it is used.

| # | Assumption | Value / choice | Basis | Where used |
|---|---|---|---|---|
| A1 | Nutri-Score is a reasonable A–E lens for exposure in an India scenario | Use official Nutri-Score grades | Nutri-Score is a validated, published FOP scheme; India's INR is analogous in intent (graded FOP) | Whole project (framed as a scenario) |
| A2 | Sodium can be derived from salt | Na = salt ÷ 2.5 (`sodium_mg = salt_g × 400`) | Standard stoichiometric relationship (NaCl) | Cleaning, scoring |
| A3 | Missing saturated fat & fibre score 0 in the re-implementation | 0 points each | These fields are absent in this export; re-implementation is validation only | Scoring (Limitation L2) |
| A4 | Category can be inferred from product name | 28-bucket keyword classifier | Transparent rule-based NLP; 75.5% coverage reported, remainder left Unclassified | Cleaning, all category analysis |
| A5 | ≥300 products (category) / ≥80 (brand) for stable rates | Thresholds | Avoids percentages driven by tiny samples | Analysis |
| A6 | Consumer sensitivity varies by category | Ordinal 0.3–1.0 (impulse/indulgence high, staples low) | FOP evidence shows labels bite hardest on discretionary purchases | Scenario model, Q6 risk |
| A7 | Base consumer switch rates | Low 4% / Moderate 10% / High 20% of D/E demand | Anchored to the range in published FOP studies (Chile, Nutri-Score RCTs, meta-analyses) | Scenario model |
| A8 | Commercial importance ≈ Indian assortment share | BigBasket SKU share per category (normalised) | Assortment breadth is a public, defensible proxy for commercial weight (sales data not public) | Scenario model, Q6 risk |
| A9 | Business-risk drivers weighted equally in the base case | 1/3 each; sensitivity check at 0.5/0.3/0.2 | Equal weight is the neutral default; rank stability (ρ=0.94) shown | Q6 risk |
| A10 | SKU counts proxy volume for exposure indices | Counts, not sales | SKU-level Indian sales/volume data is not public | Scenario model (no rupee revenue) |
| A11 | Cross-source join is valid at category level | Same classifier applied to both datasets | Category nutrition patterns are near-universal; join is category-, not product-level | Q5, Q6, scenario |

**Not assumptions (these are computed from real data):** all grade distributions,
category/brand exposure percentages, nutrient means, correlations, p-values,
effect sizes, confidence intervals, and every count. See
`reports/computed_metrics.json`.
