"""
Export Power BI-ready tables into powerbi/data/.

Power BI ingests flat CSVs. This writes a small star-schema-friendly set:

    fact_products.csv        product grain (Open Food Facts) - the main fact
    dim_category.csv         category dimension + exposure + risk attributes
    dim_brand.csv            brand dimension + exposure attributes
    dim_grade.csv            A-E grade lookup (band, numeric score)
    fact_scenario.csv        category x scenario model output
    price_vs_nutrition.csv   category-level Indian price x nutrition

Run:
    python -m powerbi.export_powerbi_data
"""
from __future__ import annotations
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src import config  # noqa: E402

OUT = config.POWERBI / "data"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    # fact_products (trim to the columns a dashboard needs)
    p = pd.read_csv(config.OFF_FINAL, low_memory=False)
    p = p[["product_name", "brand_clean", "category", "nutrition_grade",
           "rating_category", "nutrition_score", "energy_kj_100g",
           "sugars_g_100g", "sodium_mg_100g", "proteins_g_100g"]]
    p.to_csv(OUT / "fact_products.csv", index=False)

    # dim_grade
    pd.DataFrame({
        "nutrition_grade": ["A", "B", "C", "D", "E"],
        "rating_band": ["Green / Favourable", "Green / Favourable",
                        "Amber / Intermediate", "Red / Exposed", "Red / Exposed"],
        "nutrition_score": [1, 2, 3, 4, 5],
        "is_exposed": [0, 0, 0, 1, 1],
    }).to_csv(OUT / "dim_grade.csv", index=False)

    # dim_category = exposure + risk
    cat = pd.read_csv(config.CATEGORY_FINAL)
    risk = pd.read_csv(config.FINAL / "category_business_risk.csv")
    dim_cat = cat.merge(risk, on="category", how="left", suffixes=("", "_risk"))
    dim_cat.to_csv(OUT / "dim_category.csv", index=False)

    # dim_brand
    pd.read_csv(config.BRAND_FINAL).to_csv(OUT / "dim_brand.csv", index=False)

    # fact_scenario
    pd.read_csv(config.SCENARIO_FINAL).to_csv(OUT / "fact_scenario.csv", index=False)

    # price vs nutrition
    pd.read_csv(config.FINAL / "price_vs_nutrition_category.csv").to_csv(
        OUT / "price_vs_nutrition.csv", index=False)

    for f in sorted(OUT.glob("*.csv")):
        n = sum(1 for _ in open(f)) - 1
        print(f"  {f.relative_to(config.POWERBI)}  ({n:,} rows)")
    print(f"\nPower BI data exported -> {OUT}")


if __name__ == "__main__":
    main()
