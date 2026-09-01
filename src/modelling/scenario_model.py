"""
Scenario model: how might an A-E front-of-pack label change exposure?

The brief is explicit: DO NOT invent revenue. Market-share and volume data for
individual Indian SKUs are not available in the public sources used here, so we
do NOT output rupee revenue. Instead we build a transparent, unit-less
**Revenue Exposure Index (REI)** from quantities we can defend, and a
**Reformulation Priority** score. Every quantity is labelled ASSUMPTION, INPUT,
CALCULATION or OUTPUT.

Three consumer-response scenarios are modelled. The switch rates are ASSUMPTIONS
anchored to the range reported in published front-of-pack-label studies (see
data/consumer_evidence/ and reports/methodology.md) - they are scenario inputs,
not empirical predictions for India.

    Scenario        base switch rate (fraction of demand for D/E items that
                    moves away from those items, before category scaling)
    ------------    ------------------------------------------------------
    Low              0.04   (~lower bound of observed FOP effects)
    Moderate         0.10   (~central estimate)
    High             0.20   (~upper bound / strong-response case)

The base rate is scaled by each category's documented consumer sensitivity, so a
label moves impulse/indulgence categories more than staples.

Run:
    python -m src.modelling.scenario_model
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src import config  # noqa: E402
from src.analysis.business_analysis import CONSUMER_SENSITIVITY, DE

# ASSUMPTION: base switch rates per scenario (anchored to FOP evidence range)
SWITCH_RATES = {"Low": 0.04, "Moderate": 0.10, "High": 0.20}


def build_category_frame() -> pd.DataFrame:
    """INPUT: per-category exposure (OFF) + Indian commercial weight (BigBasket)."""
    off = pd.read_csv(config.OFF_FINAL, low_memory=False)
    off = off[off["category"] != config.UNCLASSIFIED]
    g = off.groupby("category")
    frame = pd.DataFrame({
        "off_products": g.size(),
        "de_products": g["nutrition_grade"].apply(lambda s: s.isin(DE).sum()),
        "de_share": g["nutrition_grade"].apply(lambda s: s.isin(DE).mean()),
        "d_products": g["nutrition_grade"].apply(lambda s: (s == "D").sum()),
        "e_products": g["nutrition_grade"].apply(lambda s: (s == "E").sum()),
    })
    frame = frame[frame["off_products"] >= 300]

    # commercial importance from real Indian assortment (BigBasket SKU share)
    risk = pd.read_csv(config.FINAL / "category_business_risk.csv", index_col=0)
    frame = frame.join(risk[["commercial_importance"]], how="left")
    frame["commercial_importance"] = frame["commercial_importance"].fillna(
        frame["commercial_importance"].min())
    frame["consumer_sensitivity"] = frame.index.map(CONSUMER_SENSITIVITY).astype(float)
    frame["consumer_sensitivity"] = frame["consumer_sensitivity"].fillna(
        frame["consumer_sensitivity"].median())
    return frame


def run() -> dict:
    print("\n=== Scenario model ===")
    frame = build_category_frame()
    rows = []
    for scen, base in SWITCH_RATES.items():
        f = frame.copy()
        # CALCULATION: effective switch rate = base * consumer sensitivity
        f["effective_switch_rate"] = (base * f["consumer_sensitivity"]).clip(0, 1)
        # OUTPUT: SKUs whose demand is at risk = D/E SKUs * switch rate
        f["at_risk_de_skus"] = (f["de_products"] * f["effective_switch_rate"]).round(1)
        # Revenue Exposure Index (unit-less 0-1): exposure x sensitivity x commercial weight
        f["revenue_exposure_index"] = (
            f["de_share"] * f["effective_switch_rate"] * f["commercial_importance"])
        # Reformulation priority: prioritise big, exposed, commercially important
        # categories where many D/E items are grade D (closer to C -> easier to fix)
        f["fixable_share_of_de"] = (f["d_products"] /
                                    f["de_products"].replace(0, np.nan)).fillna(0)
        f["reformulation_priority"] = (
            f["de_share"] * f["commercial_importance"] * f["fixable_share_of_de"])
        f["scenario"] = scen
        rows.append(f.reset_index())
    out = pd.concat(rows, ignore_index=True)
    # normalise the two indices to 0-100 within each scenario for readability
    for scen in SWITCH_RATES:
        m = out["scenario"] == scen
        for col in ["revenue_exposure_index", "reformulation_priority"]:
            v = out.loc[m, col]
            out.loc[m, col + "_0_100"] = (100 * (v - v.min()) /
                                          (v.max() - v.min() + 1e-9)).round(1)
    out = out.round(4)
    out.to_csv(config.SCENARIO_FINAL, index=False)
    print(f"  saved {len(out):,} category x scenario rows -> {config.SCENARIO_FINAL.name}")

    # market-level rollups per scenario
    summary = {}
    for scen in SWITCH_RATES:
        s = out[out["scenario"] == scen]
        summary[scen] = {
            "base_switch_rate": SWITCH_RATES[scen],
            "total_de_skus_in_scope": int(s["de_products"].sum()),
            "total_at_risk_de_skus": round(float(s["at_risk_de_skus"].sum()), 1),
            "mean_effective_switch_rate": round(float(s["effective_switch_rate"].mean()), 4),
            "top3_revenue_exposure_categories": (
                s.sort_values("revenue_exposure_index", ascending=False)
                 .head(3)["category"].tolist()),
            "top3_reformulation_priority_categories": (
                s.sort_values("reformulation_priority", ascending=False)
                 .head(3)["category"].tolist()),
        }
        print(f"  {scen:9s} at-risk D/E SKUs (scope) = "
              f"{summary[scen]['total_at_risk_de_skus']:,.0f}")

    res = {
        "assumptions": {"switch_rates_by_scenario": SWITCH_RATES,
                        "note": ("REI and reformulation priority are unit-less "
                                 "indices, NOT rupee revenue; SKU counts proxy "
                                 "volume because SKU-level sales are unavailable.")},
        "scenario_summary": summary,
        "reformulation_leaders_moderate": (
            out[out["scenario"] == "Moderate"]
            .sort_values("reformulation_priority", ascending=False)
            .head(6)[["category", "de_share", "commercial_importance",
                      "reformulation_priority_0_100"]].round(3).to_dict("records")),
    }
    metrics = json.loads(config.METRICS_JSON.read_text())
    metrics["scenarios"] = res
    config.METRICS_JSON.write_text(json.dumps(metrics, indent=2, default=str))
    print(f"  metrics updated -> {config.METRICS_JSON.name}")
    return res


if __name__ == "__main__":
    run()
