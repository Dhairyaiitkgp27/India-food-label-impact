"""
Streamlit dashboard — India Packaged Food Label Impact & Market Analytics.

Run:
    pip install -r requirements.txt
    streamlit run dashboard/app.py

Reads the final CSVs in data/final/ and the metrics in
reports/computed_metrics.json. All numbers shown are computed by the pipeline.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
FINAL = ROOT / "data" / "final"
METRICS = ROOT / "reports" / "computed_metrics.json"

st.set_page_config(page_title="India Food Label Impact", layout="wide")

GREEN, AMBER, RED = "#27AE60", "#E67E22", "#C0392B"


@st.cache_data
def load():
    prod = pd.read_csv(FINAL / "food_market_analytics.csv", low_memory=False)
    cat = pd.read_csv(FINAL / "category_exposure.csv")
    brand = pd.read_csv(FINAL / "brand_exposure.csv")
    price = pd.read_csv(FINAL / "price_vs_nutrition_category.csv")
    risk = pd.read_csv(FINAL / "category_business_risk.csv")
    scen = pd.read_csv(FINAL / "scenario_results.csv")
    metrics = json.loads(METRICS.read_text()) if METRICS.exists() else {}
    return prod, cat, brand, price, risk, scen, metrics


prod, cat, brand, price, risk, scen, metrics = load()

st.title("🇮🇳 India Packaged Food Label Impact & Market Analytics")
st.caption("Scoring 220k+ real products on the A–E Nutri-Score scale and mapping "
           "exposure onto the Indian grocery market. Nutri-Score applied to India "
           "is an analytical scenario, not a regulatory forecast.")

page = st.sidebar.radio("Page", ["Market overview", "Category intelligence",
                                 "Brand exposure", "Price vs nutrition",
                                 "Scenario & risk"])

# --------------------------------------------------------------------------- #
if page == "Market overview":
    de = prod["nutrition_grade"].isin(["D", "E"]).mean() * 100
    ab = prod["nutrition_grade"].isin(["A", "B"]).mean() * 100
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Products", f"{len(prod):,}")
    c2.metric("D/E (Red) exposure", f"{de:.1f}%")
    c3.metric("A/B (Green) favourable", f"{ab:.1f}%")
    c4.metric("Avg score (1=A..5=E)", f"{prod['nutrition_score'].mean():.2f}")
    st.subheader("Grade distribution")
    dist = (prod["nutrition_grade"].value_counts(normalize=True)
            .reindex(list("ABCDE")).mul(100).round(1))
    st.bar_chart(dist)
    st.subheader("Rating bands")
    band = prod["rating_category"].value_counts()
    st.dataframe(band.rename("products"))

elif page == "Category intelligence":
    st.subheader("Category exposure league table")
    show = cat.sort_values("de_pct", ascending=False)
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.subheader("D/E exposure by category")
    st.bar_chart(show.set_index("category")["de_pct"])
    st.subheader("Sugar vs exposure")
    st.scatter_chart(cat, x="avg_sugar_g", y="de_pct", size="products")

elif page == "Brand exposure":
    st.subheader("Brand exposure (≥80 products)")
    min_n = st.slider("Minimum products", 80, int(brand["products"].max()), 80, 10)
    b = brand[brand["products"] >= min_n]
    left, right = st.columns(2)
    left.markdown("**Most exposed (D/E %)**")
    left.dataframe(b.sort_values("de_pct", ascending=False)
                   .head(15)[["brand_clean", "products", "de_pct"]],
                   hide_index=True, use_container_width=True)
    right.markdown("**Best positioned (A/B %)**")
    right.dataframe(b.sort_values("ab_pct", ascending=False)
                    .head(15)[["brand_clean", "products", "ab_pct"]],
                    hide_index=True, use_container_width=True)

elif page == "Price vs nutrition":
    st.subheader("Does paying more buy nutrition? (category-level, Indian prices)")
    q5 = metrics.get("q5_price_nutrition", {})
    c1, c2 = st.columns(2)
    c1.metric("Spearman(price, badness)", q5.get("spearman_price_vs_badness", "—"))
    c2.metric("p-value", q5.get("spearman_p_value", "—"))
    st.caption("nutrition badness: 1=A (best) .. 5=E (worst). A positive "
               "correlation means pricier categories are LESS healthy.")
    st.scatter_chart(price, x="median_price_inr", y="avg_score", size="bb_skus")
    st.dataframe(price.sort_values("median_price_inr", ascending=False),
                 hide_index=True, use_container_width=True)

elif page == "Scenario & risk":
    st.subheader("Consumer-response scenario")
    which = st.radio("Scenario", ["Low", "Moderate", "High"], horizontal=True, index=1)
    s = scen[scen["scenario"] == which].sort_values("at_risk_de_skus", ascending=False)
    st.metric("Total at-risk D/E SKUs (in scope)",
              f"{s['at_risk_de_skus'].sum():,.0f}")
    st.bar_chart(s.set_index("category")["at_risk_de_skus"])
    st.subheader("Category business-risk ranking")
    st.dataframe(risk.sort_values("business_risk", ascending=False),
                 hide_index=True, use_container_width=True)
    st.caption("Business risk = equal-weight blend of nutrition exposure, "
               "consumer sensitivity and commercial importance. Indices are "
               "unit-less exposure, not rupee revenue.")

st.sidebar.markdown("---")
st.sidebar.caption("Data: Open Food Facts (ODbL) + BigBasket catalogue. "
                   "Grades = official Nutri-Score. See reports/ for methodology.")
