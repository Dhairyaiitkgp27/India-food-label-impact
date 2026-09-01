# Power BI — Data Model

The report uses a compact **star schema**. Load the six CSVs from
`powerbi/data/` (Get Data → Text/CSV) and set the relationships below.

## Tables

| Table | Grain | Role | Key |
|---|---|---|---|
| `fact_products` | one packaged-food product (Open Food Facts) | Fact | `category`, `brand_clean`, `nutrition_grade` |
| `fact_scenario` | one category × scenario | Fact | `category`, `scenario` |
| `price_vs_nutrition` | one category (Indian price × nutrition) | Fact/bridge | `category` |
| `dim_category` | one category | Dimension | `category` |
| `dim_brand` | one brand | Dimension | `brand_clean` |
| `dim_grade` | one grade A–E | Dimension | `nutrition_grade` |

## Relationships

```
dim_category[category]      1 —— *  fact_products[category]
dim_category[category]      1 —— *  fact_scenario[category]
dim_category[category]      1 —— 1  price_vs_nutrition[category]
dim_brand[brand_clean]      1 —— *  fact_products[brand_clean]
dim_grade[nutrition_grade]  1 —— *  fact_products[nutrition_grade]
```

All relationships are single-direction (dimension → fact) with one exception:
if you want category slicers to cross-filter the scenario page, set the
`dim_category → fact_scenario` relationship to **both** directions.

## Modelling notes

- **`dim_grade`** carries `rating_band` (Green/Amber/Red), `nutrition_score`
  (1–5) and `is_exposed` (1 for D/E). Use it so the colour banding is defined
  once and reused across every visual.
- **`scenario`** in `fact_scenario` is a text column (`Low`/`Moderate`/`High`);
  add it as a slicer, or drive it from a what-if parameter (see DAX doc).
- Keep `fact_products` as the only large table (~220k rows). Everything else is
  tiny, so the model stays fast in import mode.
- The Indian market data (`price_vs_nutrition`, and BigBasket-derived
  `commercial_importance` in `dim_category`) is joined at **category** level —
  the documented cross-source integration point. Do not imply product-level
  price for Open Food Facts items; there is none.

## Suggested measure table

Create an empty table `_Measures` (Enter Data → one dummy column, hide it) and
store all DAX measures there so they are not scattered across fact tables.
