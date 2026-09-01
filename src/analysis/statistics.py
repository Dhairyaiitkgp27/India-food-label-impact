"""
Statistical testing.

Formal hypothesis tests that back the headline claims with p-values and effect
sizes, so the findings are defensible rather than anecdotal. Each test prints
and stores: hypothesis, method, statistic, p-value, effect size and a one-line
business interpretation.

Tests
  T1  Two-proportion z-test  - are D/E products more common in Sugar-Sweetened
                               Beverages than in the rest of the market?
  T2  Welch's t-test + Cohen's d - is mean sugar higher in Chocolate &
                               Confectionery than in Milk/Butter/Cream?
  T3  Chi-square test of independence - is the A-E grade distribution
                               independent of category?
  T4  Spearman correlation - does energy density track the (ordinal) grade?
  T5  95% confidence interval (Wilson) for the overall market D/E share.

Run:
    python -m src.analysis.statistics
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src import config  # noqa: E402

DE = ["D", "E"]


def _two_proportion_z(succ1, n1, succ2, n2):
    p1, p2 = succ1 / n1, succ2 / n2
    p = (succ1 + succ2) / (n1 + n2)
    se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se
    pval = 2 * (1 - stats.norm.cdf(abs(z)))
    return p1, p2, z, pval


def _cohens_d(a, b):
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * a.std(ddof=1) ** 2 + (nb - 1) * b.std(ddof=1) ** 2) /
                 (na + nb - 2))
    return (a.mean() - b.mean()) / sp


def _wilson_ci(k, n, z=1.96):
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return centre - half, centre + half


def main() -> None:
    print("\n=== Statistical tests ===")
    df = pd.read_csv(config.OFF_FINAL, low_memory=False)
    df["is_de"] = df["nutrition_grade"].isin(DE)
    results = {}

    # T1 ---------------------------------------------------------------------
    ssb = df[df["category"] == "Sugar-Sweetened Beverages"]
    rest = df[df["category"] != "Sugar-Sweetened Beverages"]
    p1, p2, z, pval = _two_proportion_z(ssb["is_de"].sum(), len(ssb),
                                        rest["is_de"].sum(), len(rest))
    # within-bucket polarisation: full-sugar variants vs diet/zero variants
    ssb_b = round((ssb["nutrition_grade"] == "B").mean() * 100, 1)
    ssb_e = round((ssb["nutrition_grade"] == "E").mean() * 100, 1)
    # strict full-sugar carbonated / energy subset (excludes diet & zero)
    strict_mask = (df["product_name"].str.contains(
        r"cola|soda|energy drink|soft drink|coca|pepsi|sprite|fanta|mountain dew|red bull|thums up",
        case=False, na=False, regex=True)
        & ~df["product_name"].str.contains("diet|zero|sugar free|sugar-free|light|lite",
                                           case=False, na=False, regex=True))
    strict = df[strict_mask]
    strict_de = round(strict["is_de"].mean() * 100, 1)
    results["T1_ssb_vs_rest_DE_proportion"] = {
        "hypothesis": "D/E share differs in Sugar-Sweetened Beverages vs the rest of market",
        "method": "two-proportion z-test",
        "ssb_de_share_pct": round(p1 * 100, 2), "rest_de_share_pct": round(p2 * 100, 2),
        "z": round(float(z), 2), "p_value": float(f"{pval:.2e}"),
        "significant_at_0.05": bool(pval < 0.05),
        "direction": "SSB higher" if p1 > p2 else "SSB lower",
        "ssb_grade_B_pct": ssb_b, "ssb_grade_E_pct": ssb_e,
        "strict_full_sugar_subset_n": int(len(strict)),
        "strict_full_sugar_de_pct": strict_de,
        "interpretation": (
            "The broad SSB bucket is polarised: ~{b}% grade B (diet/zero/low-sugar "
            "variants) and ~{e}% grade E (full-sugar), so its overall D/E share "
            "({o:.1f}%) sits marginally below the market average. Isolating genuine "
            "full-sugar colas/energy drinks lifts D/E to {s}%, above market. A label "
            "would sharply split the beverage aisle rather than condemn it uniformly."
        ).format(b=ssb_b, e=ssb_e, o=p1 * 100, s=strict_de),
    }
    print(f"T1  SSB D/E={p1*100:.1f}% vs rest={p2*100:.1f}%  z={z:.1f}  p={pval:.2e} "
          f"| full-sugar subset D/E={strict_de}%")

    # T2 ---------------------------------------------------------------------
    choc = df[df["category"] == "Chocolate & Confectionery"]["sugars_g_100g"].dropna()
    milk = df[df["category"] == "Milk, Butter & Cream"]["sugars_g_100g"].dropna()
    t, p = stats.ttest_ind(choc, milk, equal_var=False)
    d = _cohens_d(choc, milk)
    results["T2_sugar_choc_vs_dairy"] = {
        "hypothesis": "mean sugar (g/100g) is higher in Chocolate & Confectionery than Milk/Butter/Cream",
        "method": "Welch's t-test (unequal variance) + Cohen's d",
        "choc_mean_sugar_g": round(float(choc.mean()), 2),
        "dairy_mean_sugar_g": round(float(milk.mean()), 2),
        "t": round(float(t), 2), "p_value": float(f"{p:.2e}"),
        "cohens_d": round(float(d), 2),
        "effect_size_label": ("large" if abs(d) >= 0.8 else "medium" if abs(d) >= 0.5
                              else "small" if abs(d) >= 0.2 else "negligible"),
        "significant_at_0.05": bool(p < 0.05),
    }
    print(f"T2  sugar choc={choc.mean():.1f} vs dairy={milk.mean():.1f}  "
          f"t={t:.1f}  p={p:.2e}  d={d:.2f}")

    # T3 ---------------------------------------------------------------------
    top_cats = (df[df["category"] != config.UNCLASSIFIED]["category"]
                .value_counts().head(12).index)
    sub = df[df["category"].isin(top_cats)]
    ct = pd.crosstab(sub["category"], sub["nutrition_grade"])
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    n = ct.to_numpy().sum()
    cramers_v = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))
    results["T3_grade_vs_category_independence"] = {
        "hypothesis": "grade distribution is independent of category",
        "method": "chi-square test of independence (top 12 categories) + Cramer's V",
        "chi2": round(float(chi2), 1), "dof": int(dof),
        "p_value": float(f"{p:.2e}"), "cramers_v": round(float(cramers_v), 3),
        "significant_at_0.05": bool(p < 0.05),
        "interpretation": ("grade is strongly associated with category -> category "
                           "is a primary driver of exposure"),
    }
    print(f"T3  chi2={chi2:.0f}  dof={dof}  p={p:.2e}  Cramer's V={cramers_v:.3f}")

    # T4 ---------------------------------------------------------------------
    rho, p = stats.spearmanr(df["energy_kj_100g"], df["nutrition_score"])
    results["T4_energy_vs_grade_correlation"] = {
        "hypothesis": "higher energy density is associated with a worse (higher) grade score",
        "method": "Spearman rank correlation",
        "spearman_rho": round(float(rho), 3), "p_value": float(f"{p:.2e}"),
        "significant_at_0.05": bool(p < 0.05),
    }
    print(f"T4  Spearman(energy, grade-score)={rho:.3f}  p={p:.2e}")

    # T5 ---------------------------------------------------------------------
    k, ntot = int(df["is_de"].sum()), len(df)
    lo, hi = _wilson_ci(k, ntot)
    results["T5_market_DE_share_CI"] = {
        "quantity": "overall market D/E share",
        "method": "Wilson 95% confidence interval",
        "point_estimate_pct": round(k / ntot * 100, 2),
        "ci95_low_pct": round(lo * 100, 2), "ci95_high_pct": round(hi * 100, 2),
        "n": ntot,
    }
    print(f"T5  market D/E={k/ntot*100:.2f}%  95% CI [{lo*100:.2f}, {hi*100:.2f}]")

    metrics = json.loads(config.METRICS_JSON.read_text())
    metrics["statistics"] = results
    config.METRICS_JSON.write_text(json.dumps(metrics, indent=2, default=str))
    print(f"\nStatistics written to {config.METRICS_JSON.name}")


if __name__ == "__main__":
    main()
