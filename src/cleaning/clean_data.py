"""
Cleaning pipeline: raw  ->  cleaned.

Two real inputs are cleaned here:
  * Open Food Facts branded products  (nutrition engine)
  * BigBasket Indian catalogue         (Indian market structure + price)

The Open Food Facts cleaner performs the eleven steps required by the project
brief (load, schema-validate, standardise names, coerce numerics, standardise
units, handle missing, de-duplicate, standardise categories, standardise
brands, flag outliers, save). Every decision is logged and every audit figure
is written to reports/computed_metrics.json so the data-quality report is fully
reproducible.

Run:
    python -m src.cleaning.clean_data
"""
from __future__ import annotations
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src import config  # noqa: E402


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _log(msg: str) -> None:
    print(f"  {msg}")


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


# Brand aliases: consolidate obvious duplicates of major FMCG owners so brand
# level exposure is not fragmented across spelling variants.
BRAND_ALIASES = {
    "nestle": "Nestle", "nestlé": "Nestle",
    "coca cola": "Coca-Cola", "coca-cola": "Coca-Cola", "cocacola": "Coca-Cola",
    "pepsi": "PepsiCo", "pepsico": "PepsiCo", "lays": "Lay's", "lay s": "Lay's",
    "kellogg s": "Kellogg's", "kelloggs": "Kellogg's", "kellogg": "Kellogg's",
    "mondelez": "Mondelez", "cadbury": "Cadbury", "hershey s": "Hershey's",
    "hersheys": "Hershey's", "unilever": "Unilever", "hindustan unilever": "Unilever",
    "danone": "Danone", "britannia": "Britannia", "amul": "Amul",
    "haldiram s": "Haldiram's", "haldirams": "Haldiram's", "haldiram": "Haldiram's",
    "parle": "Parle", "mtr": "MTR", "mars": "Mars", "ferrero": "Ferrero",
    "general mills": "General Mills", "kraft": "Kraft", "heinz": "Heinz",
    "the coca-cola company": "Coca-Cola",
}


def normalise_brand(raw) -> str:
    if pd.isna(raw) or str(raw).strip() == "":
        return "Unknown"
    # take the first brand if several are comma / semicolon separated
    first = re.split(r"[,;/]", str(raw))[0]
    first = _strip_accents(first).lower().strip()
    first = re.sub(r"[^a-z0-9 &']", " ", first)
    first = re.sub(r"\s+", " ", first).strip()
    if first == "":
        return "Unknown"
    if first in BRAND_ALIASES:
        return BRAND_ALIASES[first]
    return first.title()


# Pre-compile one regex per category for fast vectorised classification.
# Leading word-boundary (\b) matching: a keyword must begin at a word start, so
# "cola" no longer matches "ruCOLA" (a cheese) but still matches "cola",
# "colas" and plural/compound forms. This removes a class of substring errors.
_CATEGORY_REGEX = [
    (name, re.compile(r"\b(?:" + "|".join(re.escape(k.strip()) for k in kws) + r")"))
    for name, kws in config.CATEGORY_KEYWORDS
]


def classify_categories(names: pd.Series) -> pd.Series:
    # accent-strip so French names (lait, creme, legumes...) match ASCII keywords
    ascii_names = (names.fillna("").astype(str)
                   .str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii"))
    text = (" " + ascii_names.str.lower() + " ")
    result = pd.Series(config.UNCLASSIFIED, index=names.index, dtype=object)
    unassigned = pd.Series(True, index=names.index)
    for cat, rgx in _CATEGORY_REGEX:
        if not unassigned.any():
            break
        hit = unassigned & text.str.contains(rgx, na=False)
        result[hit] = cat
        unassigned &= ~hit
    return result


# --------------------------------------------------------------------------- #
# Open Food Facts cleaner
# --------------------------------------------------------------------------- #
EXPECTED_OFF_COLS = {
    "product_name", "brands", "countries", "nutrition_grade_fr",
    "energy_100g", "fat_100g", "carbohydrates_100g", "sugars_100g",
    "proteins_100g", "salt_100g",
}


def clean_off() -> dict:
    print("\n=== Cleaning Open Food Facts ===")
    audit: dict = {}

    # 1. load ----------------------------------------------------------------
    df = pd.read_csv(config.OFF_RAW, low_memory=False)
    audit["raw_rows"] = int(len(df))
    audit["raw_cols"] = int(df.shape[1])
    _log(f"loaded raw: {df.shape[0]:,} rows x {df.shape[1]} cols")

    # 2. schema validation ---------------------------------------------------
    missing_cols = EXPECTED_OFF_COLS - set(df.columns)
    if missing_cols:
        raise ValueError(f"Schema mismatch, missing columns: {missing_cols}")
    _log("schema OK (all expected columns present)")

    # 3. standardise column names -------------------------------------------
    df = df.rename(columns={
        "nutrition_grade_fr": "official_grade",
        "energy_100g": "energy_kj_100g",
        "fat_100g": "fat_g_100g",
        "carbohydrates_100g": "carbohydrates_g_100g",
        "sugars_100g": "sugars_g_100g",
        "proteins_100g": "proteins_g_100g",
        "salt_100g": "salt_g_100g",
    })
    nutrient_cols = ["energy_kj_100g", "fat_g_100g", "carbohydrates_g_100g",
                     "sugars_g_100g", "proteins_g_100g", "salt_g_100g"]

    # 4. coerce numerics -----------------------------------------------------
    for c in nutrient_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # official grade tidy
    df["official_grade"] = df["official_grade"].astype(str).str.upper().str.strip()
    df.loc[~df["official_grade"].isin(config.GRADE_ORDER), "official_grade"] = np.nan
    audit["raw_missing_cells"] = int(df.isna().sum().sum())
    audit["raw_grade_missing"] = int(df["official_grade"].isna().sum())

    # 5. standardise units: derive sodium from salt (sodium = salt / 2.5) ----
    #    salt is g/100g; sodium reported in mg/100g -> salt_g * 1000 / 2.5 = *400
    df["sodium_mg_100g"] = df["salt_g_100g"] * 400.0
    _log("derived sodium_mg_100g from salt (Na = salt / 2.5)")

    # 6. handle missing ------------------------------------------------------
    before = len(df)
    df = df.dropna(subset=["product_name"])
    df = df[df["product_name"].astype(str).str.strip().ne("")]
    audit["removed_missing_name"] = int(before - len(df))
    # a usable product needs at least energy or sugar or salt present
    core = ["energy_kj_100g", "sugars_g_100g", "salt_g_100g", "fat_g_100g"]
    before = len(df)
    df = df.dropna(subset=core, how="all")
    audit["removed_all_core_nutrients_missing"] = int(before - len(df))

    # 7. de-duplicate --------------------------------------------------------
    before = len(df)
    df = df.drop_duplicates()
    audit["removed_full_row_duplicates"] = int(before - len(df))
    before = len(df)
    df = df.drop_duplicates(subset=["product_name", "brands"], keep="first")
    audit["removed_name_brand_duplicates"] = int(before - len(df))

    # 8. standardise categories (engineered from product name) --------------
    df["category"] = classify_categories(df["product_name"])
    audit["pct_classified"] = round(
        float((df["category"] != config.UNCLASSIFIED).mean() * 100), 2)
    audit["n_categories"] = int(df["category"].nunique())
    _log(f"classified {audit['pct_classified']}% of products into "
         f"{audit['n_categories']} categories")

    # 9. standardise brands --------------------------------------------------
    df["brand_clean"] = df["brands"].map(normalise_brand)
    audit["n_brands_clean"] = int(df["brand_clean"].nunique())
    audit["brand_missing_after"] = int((df["brand_clean"] == "Unknown").sum())

    # 10. flag / remove outliers & impossible values -------------------------
    invalid = pd.Series(False, index=df.index)
    detail = {}
    for col, (lo, hi) in config.NUTRIENT_BOUNDS.items():
        newcol = {
            "energy_100g": "energy_kj_100g", "fat_100g": "fat_g_100g",
            "carbohydrates_100g": "carbohydrates_g_100g", "sugars_100g": "sugars_g_100g",
            "proteins_100g": "proteins_g_100g", "salt_100g": "salt_g_100g",
        }[col]
        bad = (df[newcol] < lo) | (df[newcol] > hi)
        detail[newcol] = int(bad.sum())
        invalid |= bad.fillna(False)
    # consistency: sugars cannot exceed carbohydrates (allow 0.5 g rounding)
    sugars_gt_carbs = (df["sugars_g_100g"] > df["carbohydrates_g_100g"] + 0.5)
    detail["sugars_exceed_carbs"] = int(sugars_gt_carbs.sum())
    invalid |= sugars_gt_carbs.fillna(False)
    audit["invalid_value_detail"] = detail
    audit["rows_with_invalid_values"] = int(invalid.sum())

    before = len(df)
    df = df[~invalid].copy()
    audit["removed_invalid_values"] = int(before - len(df))
    _log(f"removed {audit['removed_invalid_values']:,} rows with impossible nutrient values")

    # statistical outlier flag (IQR on energy) -- kept, only marked
    q1, q3 = df["energy_kj_100g"].quantile([0.25, 0.75])
    iqr = q3 - q1
    hi_fence = q3 + 1.5 * iqr
    df["energy_outlier_flag"] = (df["energy_kj_100g"] > hi_fence).astype(int)
    audit["energy_statistical_outliers_flagged"] = int(df["energy_outlier_flag"].sum())

    # 11. save ---------------------------------------------------------------
    df = df.reset_index(drop=True)
    keep = ["product_name", "brand_clean", "brands", "category", "official_grade",
            "energy_kj_100g", "fat_g_100g", "carbohydrates_g_100g", "sugars_g_100g",
            "proteins_g_100g", "salt_g_100g", "sodium_mg_100g", "energy_outlier_flag"]
    df[keep].to_csv(config.OFF_CLEAN, index=False)
    audit["cleaned_rows"] = int(len(df))
    audit["cleaned_cols"] = int(len(keep))
    audit["cleaned_grade_coverage_pct"] = round(
        float(df["official_grade"].notna().mean() * 100), 2)
    _log(f"saved cleaned OFF: {len(df):,} rows -> {config.OFF_CLEAN.name}")
    return audit


# --------------------------------------------------------------------------- #
# BigBasket cleaner
# --------------------------------------------------------------------------- #
def clean_bigbasket() -> dict:
    print("\n=== Cleaning BigBasket (Indian catalogue) ===")
    audit: dict = {}
    df = pd.read_csv(config.BB_RAW, low_memory=False)
    audit["raw_rows"] = int(len(df))
    audit["raw_cols"] = int(df.shape[1])
    _log(f"loaded raw: {df.shape[0]:,} rows x {df.shape[1]} cols")

    # keep only real food categories
    before = len(df)
    df = df[df["category"].isin(config.BB_FOOD_CATEGORIES)].copy()
    audit["removed_non_food"] = int(before - len(df))
    _log(f"kept {len(df):,} food SKUs (removed {audit['removed_non_food']:,} non-food)")

    # numerics
    for c in ["sale_price", "market_price", "rating"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    audit["raw_missing_cells"] = int(df.isna().sum().sum())

    # missing product/price handling
    before = len(df)
    df = df.dropna(subset=["product", "sale_price"])
    df = df[df["sale_price"] > 0]
    audit["removed_missing_product_or_price"] = int(before - len(df))

    # discount + brand/category standardisation
    df["market_price"] = df["market_price"].fillna(df["sale_price"])
    df["discount_pct"] = ((df["market_price"] - df["sale_price"]) /
                          df["market_price"].replace(0, np.nan) * 100).clip(lower=0)
    df["brand_clean"] = df["brand"].map(normalise_brand)
    df["analytical_category"] = df["category"].map(config.BB_TO_ANALYTICAL)

    # de-duplicate
    before = len(df)
    df = df.drop_duplicates(subset=["product", "brand", "sale_price"])
    audit["removed_duplicates"] = int(before - len(df))

    df = df.reset_index(drop=True)
    keep = ["product", "brand_clean", "category", "sub_category", "analytical_category",
            "sale_price", "market_price", "discount_pct", "rating"]
    df[keep].to_csv(config.BB_CLEAN, index=False)
    audit["cleaned_rows"] = int(len(df))
    audit["cleaned_cols"] = int(len(keep))
    audit["n_food_categories"] = int(df["category"].nunique())
    audit["n_sub_categories"] = int(df["sub_category"].nunique())
    audit["n_brands"] = int(df["brand_clean"].nunique())
    audit["median_price_inr"] = round(float(df["sale_price"].median()), 2)
    _log(f"saved cleaned BigBasket: {len(df):,} rows -> {config.BB_CLEAN.name}")
    return audit


def main() -> None:
    metrics = {}
    if config.METRICS_JSON.exists():
        metrics = json.loads(config.METRICS_JSON.read_text())
    metrics["cleaning_off"] = clean_off()
    metrics["cleaning_bigbasket"] = clean_bigbasket()
    config.METRICS_JSON.write_text(json.dumps(metrics, indent=2))
    print(f"\nAudit metrics written to {config.METRICS_JSON}")


if __name__ == "__main__":
    main()
