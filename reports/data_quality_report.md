# Data Quality Report

Every number here is emitted by the cleaning pipeline
(`src/cleaning/clean_data.py`) and stored in `reports/computed_metrics.json`.
The pipeline is deterministic, so this report regenerates exactly.

---

## Open Food Facts (nutrition engine)

| Metric | Raw | After cleaning |
|---|---:|---:|
| Rows | **257,387** | **239,635** |
| Columns | 10 | 13 (derived fields added) |
| Missing cells | 24,497 | — |
| Products missing a Nutri-Score grade | 21,618 (8.4%) | retained; excluded from graded analysis |
| Grade coverage | 91.6% | **91.9%** |

**Rows removed and why**

| Step | Rows removed |
|---|---:|
| Exact duplicate rows | 6,797 |
| Duplicate `product_name` + `brand` | 10,256 |
| Physically impossible nutrient values | 699 |
| **Total removed** | **17,752** |

**Impossible-value breakdown (699 rows)**

| Rule | Rows |
|---|---:|
| sugars > carbohydrates (+0.5 g tolerance) | 546 |
| energy outside 0–3,900 kJ/100 g | 82 |
| salt outside 0–100 g/100 g | 61 |
| carbohydrates/fat/protein/sugars out of range | 17 |

**Kept but flagged:** 804 products whose energy exceeds the IQR upper fence are
marked with `energy_outlier_flag = 1` (legitimately energy-dense foods such as
oils, so flagged rather than deleted).

**Derived / standardised fields**
- `sodium_mg_100g` derived from salt (Na = salt ÷ 2.5).
- Column names standardised to explicit units (`energy_kj_100g`,
  `sugars_g_100g`, …).
- Brands normalised (accent-stripped, de-cased, first-brand extraction, major-
  owner aliasing): **34,752** distinct cleaned brands; 2,758 products had no
  usable brand and were set to `Unknown`.
- Categories engineered from product name: **75.5%** classified into 28 buckets;
  ~24.5% retained as *Other / Unclassified*.

**Authoritative grade distribution (220,315 graded products)**

| A | B | C | D | E |
|---:|---:|---:|---:|---:|
| 35,166 | 33,294 | 45,947 | 62,597 | 43,311 |

---

## BigBasket (Indian market structure + price)

| Metric | Raw | After cleaning |
|---|---:|---:|
| Rows | **27,555** | **12,207** |
| Columns | 10 | 9 |
| Non-food SKUs removed | — | 14,732 |
| Missing product/price removed | — | 1 |
| Duplicates removed | — | 615 |
| Food categories | 11 (all) | 7 (food only) |
| Sub-categories | 90 | 55 |
| Distinct brands (cleaned) | 2,313 | 1,160 |
| Median sale price | — | **₹140.25** |

**Standardisation applied**
- `sale_price`, `market_price`, `rating` coerced to numeric; non-positive prices
  dropped.
- `discount_pct` derived from market vs sale price.
- Brand normalised with the same function used for Open Food Facts.
- `category` mapped to a shared analytical taxonomy for cross-source joins.

---

## Integrity checks (re-runnable in SQL)

`sql/data_quality.sql` re-verifies, directly against `database/food_market.db`:
every product carries a valid A–E grade; no nutrient values remain outside
physical bounds; no `sugars > carbohydrates`; category coverage = 75.5%; no
duplicate `product_name`+`brand` groups; all BigBasket prices positive and
≤ list price. The post-clean database passes all checks; the market D/E share
computed in SQL (48.07%) matches the Python pipeline exactly.
