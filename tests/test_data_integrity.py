"""
Data-integrity and sanity tests for the analytical outputs.

These are intentionally *data* tests (not unit tests of internal functions):
they assert that the shipped final datasets and database obey the invariants the
analysis relies on. Run:

    pytest -q
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "data" / "final"
DB = ROOT / "database" / "food_market.db"
METRICS = ROOT / "reports" / "computed_metrics.json"

VALID_GRADES = set("ABCDE")


@pytest.fixture(scope="module")
def products() -> pd.DataFrame:
    return pd.read_csv(FINAL / "food_market_analytics.csv", low_memory=False)


@pytest.fixture(scope="module")
def metrics() -> dict:
    return json.loads(METRICS.read_text())


# --- grade integrity ------------------------------------------------------- #
def test_grades_are_valid(products):
    assert set(products["nutrition_grade"].dropna().unique()).issubset(VALID_GRADES)


def test_grade_score_mapping(products):
    # nutrition_score must be 1..5 and monotonically aligned with grade order
    m = (products.dropna(subset=["nutrition_grade", "nutrition_score"])
         .groupby("nutrition_grade")["nutrition_score"].mean())
    assert m["A"] < m["C"] < m["E"]
    assert products["nutrition_score"].dropna().between(1, 5).all()


def test_rating_band_consistency(products):
    de = products[products["nutrition_grade"].isin(["D", "E"])]
    assert (de["rating_category"] == "Red / Exposed").all()


# --- nutrient plausibility ------------------------------------------------- #
def test_no_impossible_nutrients(products):
    assert products["sugars_g_100g"].dropna().between(0, 100).all()
    assert products["salt_g_100g"].dropna().between(0, 100).all()
    assert products["energy_kj_100g"].dropna().between(0, 3900).all()


def test_sugars_not_exceeding_carbs(products):
    d = products.dropna(subset=["sugars_g_100g", "carbohydrates_g_100g"])
    # allow a small tolerance used in cleaning
    assert (d["sugars_g_100g"] <= d["carbohydrates_g_100g"] + 0.5).all()


def test_sodium_derivation(products):
    d = products.dropna(subset=["salt_g_100g", "sodium_mg_100g"]).head(5000)
    approx = (d["salt_g_100g"] * 400)
    assert ((d["sodium_mg_100g"] - approx).abs() < 1.0).all()


# --- distribution sanity --------------------------------------------------- #
def test_de_share_in_expected_range(products):
    de = products["nutrition_grade"].isin(["D", "E"]).mean()
    assert 0.40 < de < 0.55  # ~48% observed


def test_metrics_de_matches_data(products, metrics):
    data_de = round(products["nutrition_grade"].isin(["D", "E"]).mean() * 100, 2)
    metric_de = metrics["q1_market"]["de_share_pct"]
    assert abs(data_de - metric_de) < 0.5


# --- category & scenario outputs ------------------------------------------- #
def test_category_exposure_bounds():
    cat = pd.read_csv(FINAL / "category_exposure.csv")
    assert cat["de_pct"].between(0, 100).all()
    assert cat["ab_pct"].between(0, 100).all()
    assert (cat["products"] >= 300).all()  # min threshold honoured


def test_scenario_monotonic():
    scen = pd.read_csv(FINAL / "scenario_results.csv")
    totals = scen.groupby("scenario")["at_risk_de_skus"].sum()
    assert totals["Low"] < totals["Moderate"] < totals["High"]


def test_scenario_indices_normalised():
    scen = pd.read_csv(FINAL / "scenario_results.csv")
    assert scen["revenue_exposure_index_0_100"].between(0, 100).all()
    assert scen["reformulation_priority_0_100"].between(0, 100).all()


# --- database integrity ---------------------------------------------------- #
@pytest.mark.skipif(not DB.exists(), reason="database not built")
def test_database_row_count():
    con = sqlite3.connect(DB)
    n = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    con.close()
    assert n > 200_000


@pytest.mark.skipif(not DB.exists(), reason="database not built")
def test_database_matches_metrics(metrics):
    con = sqlite3.connect(DB)
    de = con.execute(
        "SELECT 100.0*SUM(CASE WHEN nutrition_grade IN ('D','E') THEN 1 END)"
        "/COUNT(*) FROM products").fetchone()[0]
    con.close()
    assert abs(de - metrics["q1_market"]["de_share_pct"]) < 0.5
