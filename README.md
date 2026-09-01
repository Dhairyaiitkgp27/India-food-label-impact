# 🇮🇳 India Packaged Food Label Impact & Market Analytics

**Assessing the potential FMCG impact of an A–E front-of-pack nutrition label
using product-level nutrition data, SQL analytics, statistical testing and
Power BI.**

> If India introduced a front-of-pack A–E nutrition label, which packaged-food
> categories and brands are most exposed, how might consumer demand shift, and
> what should manufacturers and retailers do about it?

This is an end-to-end **business-analytics / market-intelligence** project (not a
machine-learning project): real public data → cleaning → an official nutrition
score → SQL + statistical analysis → a scenario model → Power BI + a Streamlit
dashboard → written business reports.

---

## 🔑 Key findings (all computed from real data)

| # | Finding | Number |
|---|---|---|
| 1 | Share of the packaged-food market that would carry a **Red (D/E)** label | **48.1%** |
| 2 | Most-exposed category — **Chocolate & Confectionery** | **85.8% D/E** |
| 3 | Least-exposed category — **Staples (Flour/Rice/Pulses)** | **10.0% D/E** |
| 4 | Genuine **full-sugar** colas/energy drinks (strict subset) | **85.3% D/E** |
| 5 | Price vs nutrition across 25 categories (Spearman) | **ρ = +0.34** → pricier ≠ healthier |
| 6 | Highest-risk category (business-risk framework) | **Chocolate & Confectionery, 0.95/1.0** |
| 7 | D/E SKUs exposed to switching under the **Moderate** scenario | **~6,100** (High: ~12,200) |

Full evidence with tables: [`reports/findings.md`](reports/findings.md).

---

## 📊 Data (real, public)

| Dataset | Role | Raw size | Licence |
|---|---|---|---|
| **Open Food Facts** branded export | Nutrition engine + official Nutri-Score | 257,387 products | Open Database License (ODbL) |
| **BigBasket** catalogue | Indian market structure + price (INR) | 27,555 SKUs | Public catalogue |

After cleaning: **220,315** graded products across **28** engineered categories,
and **12,207** Indian food SKUs. The two sources are integrated **at category
level** — a deliberate, documented design choice, because no single reachable
public dataset has Indian branded products *with* nutrition values at scale. See
[`docs/sources.md`](docs/sources.md) and the honest limitations below.

> **The repository intentionally ships `data/raw`, `data/cleaned` and
> `data/final`** so the full transformation is inspectable.

---

## 🧠 Methodology (in brief)

1. **Nutrition rating — Nutri-Score (A–E).** The authoritative grade is Open Food
   Facts' own official Nutri-Score (Santé publique France methodology). We also
   **re-implement** the 2017 algorithm from scratch and validate it against the
   official grade (48.9% exact, 92.5% within one grade, Spearman ρ = 0.78). This
   export lacks saturated fat and fibre, so the re-implementation is used for
   validation only.
2. **Applying it to India is a *scenario*.** India's own proposal is the
   star-based **Indian Nutrition Rating (INR)**, not Nutri-Score. Results
   describe *relative* exposure and category structure, not the exact grade the
   INR would assign.
3. **Cleaning.** De-duplication, unit standardisation (sodium derived from salt),
   impossible-value removal, IQR outlier flagging, brand normalisation, and a
   priority-ordered multilingual keyword classifier for category (75.5%
   coverage; remainder kept as *Other / Unclassified*).
4. **Analysis.** Category/brand exposure, nutrient profiles, a cross-source
   price-vs-nutrition study, and a category **business-risk** framework, all with
   documented thresholds and weights.
5. **Statistics.** Two-proportion z-test, Welch's t-test with Cohen's d, Spearman
   correlation, Wilson confidence interval, and a χ² test with Cramér's V.
6. **Scenario model.** Three evidence-anchored consumer-response scenarios; the
   output is a **unit-less Revenue Exposure Index** and a **Reformulation
   Priority** score — **never invented rupee revenue**.

Full detail, weighting justifications and reproducibility chain:
[`reports/methodology.md`](reports/methodology.md).

---

## 🛠️ Tech stack

**Python** (pandas, numpy, scipy) · **SQL** (SQLite; CTEs, window functions) ·
**Power BI** (star schema, DAX, 5-page report design) · **Streamlit** (interactive
dashboard) · **Jupyter** · **pytest** (data-integrity tests).

---

## 📁 Repository structure

```
india-food-label-impact/
├── data/
│   ├── raw/                 # the two source datasets, as downloaded
│   ├── cleaned/             # post-cleaning datasets
│   ├── final/               # analytical outputs (exposure, risk, scenario, ...)
│   └── consumer_evidence/   # published FOP-label studies (observed evidence)
├── src/
│   ├── config.py            # paths, Nutri-Score tables, category taxonomy
│   ├── ingestion/           # reproducible data download
│   ├── cleaning/            # cleaning + category/brand engineering
│   ├── scoring/             # Nutri-Score (official grade + re-implementation)
│   ├── analysis/            # Q1–Q6 business analysis + statistics
│   └── modelling/           # consumer-response scenario model
├── sql/                     # schema + 6 analysis query files (27 queries)
├── database/                # build script + SQLite DB
├── notebooks/               # 01 audit · 02 nutrition · 03 evidence · 04 impact
├── powerbi/                 # BI-ready data + data model + DAX + dashboard design
├── dashboard/               # Streamlit app
├── reports/                 # exec summary, findings, methodology, recs, DQ, metrics
├── docs/                    # data dictionary, assumptions register, sources
├── tests/                   # pytest data-integrity suite
├── requirements.txt
└── README.md
```

---

## ▶️ Reproduce it

```bash
pip install -r requirements.txt

# full pipeline (raw -> cleaned -> scored -> analysed -> modelled -> stats)
python -m src.ingestion.download_data
python -m src.cleaning.clean_data
python -m src.scoring.nutrition_score
python -m src.analysis.business_analysis
python -m src.modelling.scenario_model
python -m src.analysis.statistics

# build the database and Power BI extracts
python -m database.build_database
python -m powerbi.export_powerbi_data

# tests + dashboard
pytest -q
streamlit run dashboard/app.py
```

Every headline number is regenerated into
[`reports/computed_metrics.json`](reports/computed_metrics.json).

---

## 📈 Power BI

A five-page report (Executive Summary · Category Intelligence · Brand Exposure ·
Consumer & Market Impact · Management Action) built on a star schema with a
what-if switch-rate parameter. Data model, DAX measures and full page-by-page
design are in [`powerbi/`](powerbi/).

---

## ✅ Recommendations (headline)

Treat the label as a **reformulation roadmap, not a threat**: prioritise the
fixable grade-D lines in high-commercial-importance indulgence categories
(confectionery, biscuits, salty snacks) and grow the A/B range. Retailers should
build Green/Amber/Red navigation and expand healthier private label. Full
stakeholder playbook and strategic options (qualitatively scored, no invented
money): [`reports/recommendations.md`](reports/recommendations.md).

---

## ⚠️ Limitations (stated plainly)

- **India coverage** — Open Food Facts is globally skewed; nutrition patterns are
  mapped onto the real Indian assortment via BigBasket, but the nutrition values
  themselves are not India-specific.
- **Missing nutrients** — this export lacks saturated fat and fibre (re-
  implementation is partial; the authoritative OFF grade is unaffected).
- **Category-level price join** — price and nutrition meet at category, not
  product, level (25-point correlation, stated as directional).
- **Scenario assumptions** — switch rates are evidence-anchored assumptions, not
  forecasts.
- **Nutri-Score ≠ INR** — India's scheme is star-based; results are relative
  exposure, not the exact INR grade.

---

## 📚 Attribution

Open Food Facts data under **ODbL** — Open Food Facts and its contributors are
gratefully acknowledged. BigBasket catalogue used for educational, non-commercial
analysis. Nutri-Score is a scheme of Santé publique France. This is an
independent academic/portfolio project, not affiliated with or endorsed by any of
these organisations.
