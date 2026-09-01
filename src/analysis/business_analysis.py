"""
Core business analysis (answers Q1-Q6 of the brief).

Reads the scored Open Food Facts dataset (authoritative official Nutri-Score)
and the cleaned BigBasket Indian catalogue, then computes:

  Q1  Overall market exposure (A-E distribution, D/E %)
  Q2  Category exposure (ranked; most / least exposed)
  Q3  Brand exposure (major brands; A/B, C, D/E %)
  Q4  Product analysis (worst / healthiest / nutrient outliers)
  Q5  Price vs nutrition (category-level cross-source: BigBasket price x OFF nutrition)
  Q6  Category business-risk framework (nutrition x consumer sensitivity x commercial importance)

All outputs are written to data/final/ and reports/computed_metrics.json so every
figure quoted in the reports is reproducible. No values are invented.

Run:
    python -m src.analysis.business_analysis
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src import config  # noqa: E402
from src.cleaning.clean_data import classify_categories  # reuse the same taxonomy

DE = ["D", "E"]
AB = ["A", "B"]
MIN_CAT_N = 300     # a category must have >=300 graded products to be ranked
MIN_BRAND_N = 80    # a brand must have >=80 graded products to be ranked


def _grade_shares(s: pd.Series) -> dict:
    vc = s.value_counts(normalize=True)
    return {g: round(float(vc.get(g, 0.0) * 100), 2) for g in config.GRADE_ORDER}


# --------------------------------------------------------------------------- #
def q1_market(df: pd.DataFrame) -> dict:
    shares = _grade_shares(df["nutrition_grade"])
    de = round(float(df["nutrition_grade"].isin(DE).mean() * 100), 2)
    ab = round(float(df["nutrition_grade"].isin(AB).mean() * 100), 2)
    res = {
        "graded_products": int(len(df)),
        "grade_share_pct": shares,
        "de_share_pct": de,
        "ab_share_pct": ab,
        "avg_nutrition_score_1to5": round(float(df["nutrition_score"].mean()), 3),
    }
    print(f"Q1  D/E={de}%  A/B={ab}%  shares={shares}")
    return res


# --------------------------------------------------------------------------- #
def q2_category(df: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    d = df[df["category"] != config.UNCLASSIFIED]
    g = d.groupby("category")
    tbl = pd.DataFrame({
        "products": g.size(),
        "de_pct": g["nutrition_grade"].apply(lambda s: s.isin(DE).mean() * 100),
        "ab_pct": g["nutrition_grade"].apply(lambda s: s.isin(AB).mean() * 100),
        "avg_score": g["nutrition_score"].mean(),
        "avg_sugar_g": g["sugars_g_100g"].mean(),
        "avg_sodium_mg": g["sodium_mg_100g"].mean(),
        "avg_satfat_proxy_fat_g": g["fat_g_100g"].mean(),
        "avg_energy_kj": g["energy_kj_100g"].mean(),
    }).round(2)
    tbl = tbl[tbl["products"] >= MIN_CAT_N].sort_values("de_pct", ascending=False)
    tbl.to_csv(config.CATEGORY_FINAL)
    most = tbl.index[0]
    least = tbl.index[-1]
    res = {
        "n_categories_ranked": int(len(tbl)),
        "most_exposed_category": most,
        "most_exposed_de_pct": float(tbl.loc[most, "de_pct"]),
        "least_exposed_category": least,
        "least_exposed_de_pct": float(tbl.loc[least, "de_pct"]),
        "top5_by_de_pct": tbl.head(5)["de_pct"].round(2).to_dict(),
        "bottom5_by_de_pct": tbl.tail(5)["de_pct"].round(2).to_dict(),
        "highest_avg_sugar_category": tbl["avg_sugar_g"].idxmax(),
        "highest_avg_sugar_value": float(tbl["avg_sugar_g"].max()),
        "highest_avg_sodium_category": tbl["avg_sodium_mg"].idxmax(),
        "highest_avg_sodium_value": float(tbl["avg_sodium_mg"].max()),
    }
    print(f"Q2  most exposed: {most} ({res['most_exposed_de_pct']:.1f}% D/E) | "
          f"least: {least} ({res['least_exposed_de_pct']:.1f}% D/E)")
    return res, tbl


# --------------------------------------------------------------------------- #
def q3_brand(df: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    d = df[df["brand_clean"] != "Unknown"]
    g = d.groupby("brand_clean")
    tbl = pd.DataFrame({
        "products": g.size(),
        "ab_pct": g["nutrition_grade"].apply(lambda s: s.isin(AB).mean() * 100),
        "c_pct": g["nutrition_grade"].apply(lambda s: (s == "C").mean() * 100),
        "de_pct": g["nutrition_grade"].apply(lambda s: s.isin(DE).mean() * 100),
        "avg_score": g["nutrition_score"].mean(),
    }).round(2)
    tbl = tbl[tbl["products"] >= MIN_BRAND_N]
    tbl_exposed = tbl.sort_values(["de_pct", "products"], ascending=[False, False])
    tbl_healthy = tbl.sort_values(["ab_pct", "products"], ascending=[False, False])
    tbl_exposed.to_csv(config.BRAND_FINAL)
    res = {
        "n_brands_ranked": int(len(tbl)),
        "min_products_threshold": MIN_BRAND_N,
        "top10_exposed_brands": tbl_exposed.head(10)[["products", "de_pct", "avg_score"]]
                                 .reset_index().to_dict("records"),
        "top10_favourable_brands": tbl_healthy.head(10)[["products", "ab_pct", "avg_score"]]
                                    .reset_index().to_dict("records"),
    }
    print(f"Q3  ranked {len(tbl)} brands (>= {MIN_BRAND_N} products). "
          f"Most exposed: {tbl_exposed.index[0]} ({tbl_exposed.iloc[0]['de_pct']:.0f}% D/E)")
    return res, tbl_exposed


# --------------------------------------------------------------------------- #
def q4_products(df: pd.DataFrame) -> dict:
    def top(frame, col, asc, k=10):
        cols = ["product_name", "brand_clean", "category", "nutrition_grade", col]
        return (frame.sort_values(col, ascending=asc)
                .head(k)[cols].round(2).to_dict("records"))
    worst = df[df["nutrition_grade"] == "E"]
    best = df[df["nutrition_grade"] == "A"]
    res = {
        "worst_by_sugar": top(df, "sugars_g_100g", False),
        "worst_by_sodium": top(df, "sodium_mg_100g", False),
        "worst_by_energy": top(df, "energy_kj_100g", False),
        "healthiest_examples_gradeA_lowest_energy": top(best, "energy_kj_100g", True),
        "n_grade_E": int(len(worst)),
        "n_grade_A": int(len(best)),
        "sugar_p99_g": round(float(df["sugars_g_100g"].quantile(0.99)), 2),
        "sodium_p99_mg": round(float(df["sodium_mg_100g"].quantile(0.99)), 2),
    }
    print(f"Q4  grade-E products: {len(worst):,} | grade-A products: {len(best):,}")
    return res


# --------------------------------------------------------------------------- #
def q5_price_nutrition(off: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """Category-level cross-source: real Indian price (BigBasket) vs nutrition (OFF)."""
    bb = pd.read_csv(config.BB_CLEAN, low_memory=False)
    # apply the SAME classifier to BigBasket products -> shared taxonomy
    bb["category"] = classify_categories(bb["product"])
    bb_cat = (bb[bb["category"] != config.UNCLASSIFIED]
              .groupby("category")
              .agg(bb_skus=("product", "size"),
                   median_price_inr=("sale_price", "median"),
                   mean_price_inr=("sale_price", "mean")))
    off_cat = (off[off["category"] != config.UNCLASSIFIED]
               .groupby("category")
               .agg(off_products=("product_name", "size"),
                    de_pct=("nutrition_grade", lambda s: s.isin(DE).mean() * 100),
                    avg_score=("nutrition_score", "mean"),
                    avg_sugar_g=("sugars_g_100g", "mean")))
    joined = off_cat.join(bb_cat, how="inner")
    joined = joined[joined["bb_skus"] >= 30].round(2)   # need enough Indian SKUs
    joined.to_csv(config.FINAL / "price_vs_nutrition_category.csv")

    from scipy.stats import spearmanr, pearsonr
    rho, p_rho = spearmanr(joined["median_price_inr"], joined["avg_score"])
    r, p_r = pearsonr(joined["median_price_inr"], joined["avg_score"])
    res = {
        "n_categories_matched": int(len(joined)),
        "spearman_price_vs_badness": round(float(rho), 3),
        "spearman_p_value": round(float(p_rho), 4),
        "pearson_price_vs_badness": round(float(r), 3),
        "pearson_p_value": round(float(p_r), 4),
        "interpretation": ("nutrition_score is 1=A(best)..5=E(worst); a positive "
                           "price-vs-score correlation would mean pricier categories "
                           "are LESS healthy, a negative one that they are healthier"),
        "matched_table": joined.reset_index().to_dict("records"),
    }
    print(f"Q5  matched {len(joined)} categories | Spearman(price, badness)="
          f"{rho:.2f} (p={p_rho:.3f})")
    return res, joined


# --------------------------------------------------------------------------- #
# Q6 consumer-sensitivity ordinal (documented, not arbitrary):
# label impact is largest for discretionary / impulse / indulgence categories and
# smallest for staples that are bought regardless of a front-of-pack colour.
# Justification is written out in reports/methodology.md.
CONSUMER_SENSITIVITY = {
    "Sugar-Sweetened Beverages": 1.0, "Chocolate & Confectionery": 1.0,
    "Chips, Crisps & Salty Snacks": 1.0, "Ice Cream & Frozen Desserts": 0.9,
    "Biscuits, Cookies & Wafers": 0.9, "Cakes, Pastries & Sweet Bakery": 0.9,
    "Breakfast Cereals & Muesli": 0.8, "Juices & Nectars": 0.8,
    "Instant Noodles, Pasta & Soups": 0.8, "Ready Meals & Frozen Foods": 0.8,
    "Spreads, Jam, Honey & Syrups": 0.7, "Sauces, Ketchup & Condiments": 0.6,
    "Yogurt & Dairy Drinks": 0.6, "Tea, Coffee & Hot Drink Mixes": 0.6,
    "Protein, Diet & Nutrition Bars": 0.6, "Cheese": 0.5,
    "Processed Meat & Seafood": 0.5, "Bread & Savoury Bakery": 0.5,
    "Milk, Butter & Cream": 0.4, "Nuts, Seeds & Dried Fruit": 0.4,
    "Pickles & Preserved Vegetables": 0.4, "Sugar, Sweeteners & Baking": 0.4,
    "Water & Unsweetened Drinks": 0.3, "Edible Oils & Fats": 0.3,
    "Staples: Flour, Rice, Pulses & Grains": 0.3,
    "Fruits & Vegetables (packaged/plain)": 0.3, "Baby & Infant Food": 0.7,
}


def q6_risk(cat_tbl: pd.DataFrame, price_join: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    t = cat_tbl.copy()
    # Nutrition Exposure = D/E share, normalised 0-1
    t["nutrition_exposure"] = t["de_pct"] / 100.0
    # Consumer Sensitivity (documented ordinal)
    t["consumer_sensitivity"] = t.index.map(CONSUMER_SENSITIVITY).astype(float)
    t["consumer_sensitivity"] = t["consumer_sensitivity"].fillna(t["consumer_sensitivity"].median())
    # Commercial Importance = Indian assortment share (BigBasket SKUs) for the
    # matched category, normalised 0-1. Categories with no Indian SKU match get
    # the minimum observed (least commercial weight), documented as a limitation.
    bb_skus = price_join["bb_skus"] if "bb_skus" in price_join else pd.Series(dtype=float)
    imp = (bb_skus / bb_skus.max()) if len(bb_skus) else pd.Series(dtype=float)
    t["commercial_importance"] = t.index.map(imp).astype(float)
    t["commercial_importance"] = t["commercial_importance"].fillna(
        t["commercial_importance"].min() if t["commercial_importance"].notna().any() else 0.1)

    # Base case: equal weights (no information justifies unequal weights).
    w = {"nutrition_exposure": 1/3, "consumer_sensitivity": 1/3, "commercial_importance": 1/3}
    t["business_risk"] = (w["nutrition_exposure"] * t["nutrition_exposure"] +
                          w["consumer_sensitivity"] * t["consumer_sensitivity"] +
                          w["commercial_importance"] * t["commercial_importance"]).round(3)
    # Sensitivity check: nutrition-weighted alternative (0.5/0.3/0.2)
    t["business_risk_alt"] = (0.5 * t["nutrition_exposure"] +
                              0.3 * t["consumer_sensitivity"] +
                              0.2 * t["commercial_importance"]).round(3)
    t = t.sort_values("business_risk", ascending=False)
    out = t[["de_pct", "nutrition_exposure", "consumer_sensitivity",
             "commercial_importance", "business_risk", "business_risk_alt"]].round(3)
    out.to_csv(config.FINAL / "category_business_risk.csv")

    # rank stability between the two weightings (Spearman)
    from scipy.stats import spearmanr
    rank_rho, _ = spearmanr(t["business_risk"], t["business_risk_alt"])
    res = {
        "weights_base_case": w,
        "weights_sensitivity_case": {"nutrition_exposure": 0.5,
                                     "consumer_sensitivity": 0.3,
                                     "commercial_importance": 0.2},
        "rank_correlation_between_weightings": round(float(rank_rho), 3),
        "top5_highest_risk": out.head(5)["business_risk"].to_dict(),
        "bottom5_lowest_risk": out.tail(5)["business_risk"].to_dict(),
    }
    print(f"Q6  highest-risk category: {out.index[0]} (risk={out.iloc[0]['business_risk']}) "
          f"| weighting-robustness Spearman={rank_rho:.2f}")
    return res, out


# --------------------------------------------------------------------------- #
def main() -> None:
    print("\n=== Business analysis (Q1-Q6) ===")
    df = pd.read_csv(config.FINAL / "food_scored.csv", low_memory=False)

    # persist the product-level analytical dataset (Power BI / SQL ready)
    keep = ["product_name", "brand_clean", "category", "nutrition_grade",
            "rating_category", "nutrition_score", "nutrition_score_computed",
            "energy_kj_100g", "fat_g_100g", "carbohydrates_g_100g", "sugars_g_100g",
            "proteins_g_100g", "salt_g_100g", "sodium_mg_100g", "energy_outlier_flag"]
    df[keep].to_csv(config.OFF_FINAL, index=False)
    print(f"analytical dataset saved: {len(df):,} rows -> {config.OFF_FINAL.name}")

    metrics = json.loads(config.METRICS_JSON.read_text())
    metrics["q1_market"] = q1_market(df)
    metrics["q2_category"], cat_tbl = q2_category(df)
    metrics["q3_brand"], _ = q3_brand(df)
    metrics["q4_products"] = q4_products(df)
    metrics["q5_price_nutrition"], price_join = q5_price_nutrition(df)
    metrics["q6_risk"], _ = q6_risk(cat_tbl, price_join)
    config.METRICS_JSON.write_text(json.dumps(metrics, indent=2, default=str))
    print(f"\nAll findings written to {config.METRICS_JSON.name}")


if __name__ == "__main__":
    main()
