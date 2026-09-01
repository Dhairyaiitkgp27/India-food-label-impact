"""
Nutrition rating.

This module does two things:

1. Implements the *published* Nutri-Score (2017) algorithm from first principles
   (Santé publique France method; point tables live in src/config.py and are
   cited in reports/methodology.md). This demonstrates the scoring logic.

2. Adopts the Open Food Facts *official* Nutri-Score grade as the authoritative
   A-E rating for every product, because it was computed upstream from the full
   nutrient panel (including saturated fat and fibre, which are NOT present in
   this particular export). The re-implementation is then validated against the
   official grade on the nutrient subset that IS available, and the agreement /
   rank-correlation is reported honestly.

IMPORTANT SCOPE NOTE (kept in every report): applying Nutri-Score to products
sold in India is an *analytical scenario*. Nutri-Score is a European front-of-
pack scheme; it is NOT an official Indian government rating. India's own
framework is the Indian Nutrition Rating (INR), a star-based system proposed by
FSSAI. See reports/methodology.md.

Run:
    python -m src.scoring.nutrition_score
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src import config  # noqa: E402


# --------------------------------------------------------------------------- #
# Official Nutri-Score 2017 point tables (vectorised)
# --------------------------------------------------------------------------- #
def _points(values: pd.Series, thresholds: list[float]) -> pd.Series:
    """Award 0..len(thresholds) points: 1 point per threshold strictly exceeded."""
    v = values.fillna(0).to_numpy()
    pts = np.zeros(len(v), dtype=int)
    for t in thresholds:
        pts += (v > t).astype(int)
    return pd.Series(pts, index=values.index)


def _fvln_points(pct: pd.Series) -> pd.Series:
    v = pct.fillna(0).to_numpy()
    pts = np.zeros(len(v), dtype=int)
    pts = np.where(v > 40, 1, pts)
    pts = np.where(v > 60, 2, pts)
    pts = np.where(v > 80, 5, pts)
    return pd.Series(pts, index=pct.index)


def compute_nutriscore(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Nutri-Score points and final score from available nutrients.

    Available in this export : energy (kJ), sugars, sodium (from salt), protein.
    NOT available             : saturated fat, fibre, fruit/veg/legume/nut %.

    Missing components score 0 points, which is stated as Limitation L2. The
    result is therefore a partial re-implementation used for validation, not the
    authoritative grade.
    """
    n = config.NUTRISCORE_NEGATIVE
    p = config.NUTRISCORE_POSITIVE

    energy_pts = _points(df["energy_kj_100g"], n["energy_kj"])
    sugar_pts = _points(df["sugars_g_100g"], n["sugars_g"])
    sodium_pts = _points(df["sodium_mg_100g"], n["sodium_mg"])
    # saturated fat unavailable -> 0 points (documented limitation)
    satfat_pts = pd.Series(0, index=df.index)

    negative = energy_pts + sugar_pts + satfat_pts + sodium_pts

    protein_pts = _points(df["proteins_g_100g"], p["protein_g"])
    # fibre + fvln unavailable -> 0 points
    fibre_pts = pd.Series(0, index=df.index)
    fvln_pts = pd.Series(0, index=df.index)

    positive_wo_protein = fibre_pts + fvln_pts
    # Official special rule: if N>=11 and FVLN points<5, protein is NOT counted.
    count_protein = ~((negative >= 11) & (fvln_pts < 5))
    positive = positive_wo_protein + protein_pts.where(count_protein, 0)

    score = negative - positive

    out = df.copy()
    out["ns_neg_points"] = negative
    out["ns_pos_points"] = positive
    out["nutrition_score_computed"] = score
    out["computed_grade"] = score.map(_grade_from_score)
    return out


def _grade_from_score(score: float) -> str:
    for grade, lo, hi in config.NUTRISCORE_GRADE_BOUNDS:
        if lo <= score <= hi:
            return grade
    return "E"


# --------------------------------------------------------------------------- #
# Authoritative grade + rating band
# --------------------------------------------------------------------------- #
RATING_BAND = {"A": "Green / Favourable", "B": "Green / Favourable",
               "C": "Amber / Intermediate",
               "D": "Red / Exposed", "E": "Red / Exposed"}


def main() -> None:
    print("\n=== Nutrition scoring ===")
    df = pd.read_csv(config.OFF_CLEAN, low_memory=False)

    # 1. re-implementation (validation) --------------------------------------
    df = compute_nutriscore(df)

    # 2. authoritative grade = official OFF Nutri-Score ----------------------
    df["nutrition_grade"] = df["official_grade"]
    graded = df[df["nutrition_grade"].isin(config.GRADE_ORDER)].copy()
    graded["rating_category"] = graded["nutrition_grade"].map(RATING_BAND)
    # a numeric score aligned with the authoritative grade (A=1 best .. E=5 worst)
    graded["nutrition_score"] = graded["nutrition_grade"].map(
        {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5})

    # 3. validate re-implementation vs official ------------------------------
    both = graded.dropna(subset=["computed_grade", "nutrition_grade"])
    exact = float((both["computed_grade"] == both["nutrition_grade"]).mean() * 100)
    within1 = float((both["computed_grade"].map(lambda g: config.GRADE_ORDER.index(g))
                     .sub(both["nutrition_grade"].map(lambda g: config.GRADE_ORDER.index(g)))
                     .abs() <= 1).mean() * 100)
    # rank correlation between computed score and official ordinal grade
    from scipy.stats import spearmanr
    rho, _ = spearmanr(both["nutrition_score_computed"],
                       both["nutrition_grade"].map(lambda g: config.GRADE_ORDER.index(g)))

    print(f"  authoritative graded products: {len(graded):,}")
    print(f"  re-implementation exact-grade agreement : {exact:.1f}%")
    print(f"  re-implementation within-one-grade      : {within1:.1f}%")
    print(f"  Spearman(computed score, official grade): {rho:.3f}")

    # 4. save scored dataset -------------------------------------------------
    graded.to_csv(config.FINAL / "food_scored.csv", index=False)
    print(f"  saved scored dataset: {len(graded):,} rows -> data/final/food_scored.csv")

    # 5. persist metrics -----------------------------------------------------
    metrics = json.loads(config.METRICS_JSON.read_text()) if config.METRICS_JSON.exists() else {}
    metrics["scoring"] = {
        "graded_products": int(len(graded)),
        "reimpl_exact_agreement_pct": round(exact, 2),
        "reimpl_within_one_grade_pct": round(within1, 2),
        "reimpl_spearman_rho": round(float(rho), 3),
        "grade_distribution": {k: int(v) for k, v in
                               graded["nutrition_grade"].value_counts().sort_index().items()},
        "note": ("Authoritative grade = official Open Food Facts Nutri-Score. "
                 "Re-implementation excludes saturated fat and fibre (absent in "
                 "this export) and is reported for validation only."),
    }
    config.METRICS_JSON.write_text(json.dumps(metrics, indent=2))
    print(f"  metrics updated -> {config.METRICS_JSON.name}")


if __name__ == "__main__":
    main()
