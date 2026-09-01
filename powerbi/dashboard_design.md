# Power BI — Dashboard Design (5 pages)

A five-page report that walks an FMCG executive from "how big is the problem" to
"what do we do Monday morning." Colour convention throughout: **Green** = A/B,
**Amber** = C, **Red** = D/E. Keep one slicer panel (Category, Grade, Scenario)
docked on the left of every page.

---

## Page 1 — Executive Summary
**Question: how exposed is the packaged-food market to an A–E label?**

- **KPI cards (top row):** Total Products (`[Total Products]` ≈ 220k), D/E
  Exposure % (`[D/E Exposure %]` ≈ 48%), A/B Favourable % (≈ 31%), Avg Nutrition
  Score (≈ 3.2 / 5).
- **100% stacked bar** — grade mix A→E for the whole market (single bar) using
  `dim_grade` colours.
- **Bar chart** — Top 8 most-exposed categories by `[D/E Exposure %]`.
- **Callout / text box** — headline sentence generated from the data (e.g.
  "Nearly half of products would carry a Red D/E label; confectionery and
  sugary drinks are most exposed").
- **KPI** — full-sugar carbonated/energy drinks D/E % (≈ 85%) to make the
  beverage story concrete.

## Page 2 — Category Intelligence
**Question: which categories drive the exposure, and why?**

- **Matrix** — category rows; columns A/B %, C %, D/E %, Avg Sugar, Avg Sodium,
  Avg Energy; data bars on D/E % and conditional colour via `[Exposure Colour]`.
- **Scatter** — x = Avg Sugar (g/100g), y = D/E Exposure %, bubble size = product
  count; category labels. Shows sugar as the dominant exposure driver.
- **Decomposition tree** — Total Products → Category → Grade, for guided
  drill-down.
- **Pareto (line + column)** — categories sorted by D/E count with a cumulative
  % line (which few categories account for most D/E products).

## Page 3 — Brand Exposure
**Question: which brands are most / least exposed?**

- **Bar** — Top 15 most-exposed brands (`[Brand D/E % (min 80)]`), red palette.
- **Bar** — Top 15 best-positioned brands (highest A/B %), green palette.
- **Table** — brand, products, A/B %, C %, D/E %, Avg Score, `[Brand D/E Rank]`.
- **Slicer** — minimum SKU count (numeric) so the user can raise the threshold
  above 80 and see only large portfolios.
- **Tooltip page** — on hover over a brand, show its grade mix donut.

## Page 4 — Consumer & Market Impact (Scenario)
**Question: how might demand and revenue exposure move under a label?**

- **What-if slider** — Switch Rate (0–30%). Drives `[At-Risk SKUs (live)]`.
- **Scenario slicer** — Low / Moderate / High (pre-computed `fact_scenario`).
- **Column chart** — At-Risk D/E SKUs by category for the selected scenario.
- **KPI cards** — Total At-Risk D/E SKUs (Moderate ≈ 6.1k; High ≈ 12.2k),
  Mean Effective Switch Rate.
- **Scatter (price vs nutrition)** — x = Median Price (INR), y = Nutrition
  Badness (1–5), one point per category; trendline. Card showing
  `[Price-Nutrition Correlation]` (≈ +0.3 → pricier ≠ healthier).
- **Text** — reminder that indices are unit-less exposure, **not** rupee revenue.

## Page 5 — Management Action
**Question: where should we act first?**

- **Bubble/quadrant** — x = Commercial Importance, y = Nutrition Exposure, size =
  Reformulation Priority, colour = Business Risk. Top-right quadrant = "act now".
- **Ranked bar** — `[Business Risk]` by category with `[Risk Rank]`.
- **Table** — Reformulation Priority (0–100) leaders under the Moderate scenario.
- **Action cards (static text tied to data):** Reformulate (highest fixable-D
  categories), Reposition (premium categories that are not healthier),
  Portfolio shift (grow A/B ranges), Monitor (low-risk staples).
- **Weighting toggle** — bookmark switching Business Risk between equal-weight
  and nutrition-weighted (0.5/0.3/0.2) to show rank stability (ρ ≈ 0.94).

---

### Build notes
- Import mode; single date-independent model (no time dimension needed).
- Put all measures in `_Measures`; use `dim_grade` for every colour.
- Every headline number on Page 1 is reproducible from
  `reports/computed_metrics.json`.
