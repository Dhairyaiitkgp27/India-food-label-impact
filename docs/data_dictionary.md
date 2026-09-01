# Data Dictionary

Field-level documentation for the cleaned and final datasets. Units are per
100 g / 100 ml unless stated.

## `data/cleaned/cleaned_food_products.csv` (Open Food Facts, cleaned)

| Column | Type | Description |
|---|---|---|
| `product_name` | text | Product name (source field) |
| `brand_clean` | text | Normalised brand (accent-stripped, de-cased, first brand, major-owner aliased); `Unknown` if absent |
| `brands` | text | Original raw brand string (kept for traceability) |
| `category` | text | Engineered category (28-bucket keyword taxonomy) or `Other / Unclassified` |
| `official_grade` | text | Official Open Food Facts Nutri-Score A–E (authoritative) |
| `energy_kj_100g` | float | Energy, kJ |
| `fat_g_100g` | float | Total fat, g (note: **saturated** fat is not available) |
| `carbohydrates_g_100g` | float | Carbohydrates, g |
| `sugars_g_100g` | float | Sugars, g |
| `proteins_g_100g` | float | Protein, g |
| `salt_g_100g` | float | Salt, g |
| `sodium_mg_100g` | float | Sodium, mg — **derived**: salt_g × 400 (Na = salt ÷ 2.5) |
| `energy_outlier_flag` | int | 1 if energy above IQR upper fence (kept, flagged) |

## `data/final/food_market_analytics.csv` (product-level analytical dataset)

Adds to the above:

| Column | Type | Description |
|---|---|---|
| `nutrition_grade` | text | Authoritative grade A–E (= official Nutri-Score) |
| `rating_category` | text | `Green / Favourable` (A/B), `Amber / Intermediate` (C), `Red / Exposed` (D/E) |
| `nutrition_score` | int | 1 = A (best) … 5 = E (worst) |
| `nutrition_score_computed` | int | From-scratch Nutri-Score re-implementation (validation only; partial inputs) |

## `data/cleaned/cleaned_bigbasket_products.csv` (Indian catalogue, cleaned)

| Column | Type | Description |
|---|---|---|
| `product` | text | Product name |
| `brand_clean` | text | Normalised brand |
| `category` | text | BigBasket top-level food category |
| `sub_category` | text | BigBasket sub-category |
| `analytical_category` | text | Coarse mapping to the shared analytical taxonomy |
| `sale_price` | float | Selling price, INR |
| `market_price` | float | List price, INR |
| `discount_pct` | float | (market − sale) / market × 100 |
| `rating` | float | Catalogue star rating (0–5) where present |

## `data/final/category_exposure.csv`

`category`, `products`, `de_pct`, `ab_pct`, `avg_score`, `avg_sugar_g`,
`avg_sodium_mg`, `avg_satfat_proxy_fat_g`, `avg_energy_kj` — per-category
exposure summary (categories with ≥300 graded products).

## `data/final/brand_exposure.csv`

`brand_clean`, `products`, `ab_pct`, `c_pct`, `de_pct`, `avg_score` — per-brand
summary (brands with ≥80 graded products).

## `data/final/price_vs_nutrition_category.csv`

`category`, `off_products`, `de_pct`, `avg_score`, `avg_sugar_g`, `bb_skus`,
`median_price_inr`, `mean_price_inr` — cross-source category join (categories
with ≥30 matched Indian SKUs).

## `data/final/category_business_risk.csv`

`category`, `de_pct`, `nutrition_exposure`, `consumer_sensitivity`,
`commercial_importance`, `business_risk`, `business_risk_alt` — Q6 framework.

## `data/final/scenario_results.csv`

`category`, `off_products`, `de_products`, `de_share`, `d_products`,
`e_products`, `commercial_importance`, `consumer_sensitivity`,
`effective_switch_rate`, `at_risk_de_skus`, `revenue_exposure_index`,
`fixable_share_of_de`, `reformulation_priority`, `scenario`,
`revenue_exposure_index_0_100`, `reformulation_priority_0_100` — one row per
category × scenario.

## `data/consumer_evidence/fop_label_studies.csv`

`study`, `year`, `country`, `label_type`, `study_design`, `scope`,
`main_finding`, `relevance_to_project` — index of published FOP-label evidence.
