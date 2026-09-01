# Methodology
### India Packaged Food Label Impact & Market Analytics

This document explains how every result was produced and — just as important —
what each result can and cannot support. The guiding principle of the project is
that **all empirical numbers come from real public data; nothing is fabricated.**
Where a value is an assumption, it is labelled as one.

---

## 1. Data sources (real, public)

| Dataset | Role | Size (raw) | Key fields | Licence / provenance |
|---|---|---|---|---|
| **Open Food Facts** branded export | Nutrition engine | 257,387 products | product name, brands, nutrients/100 g, official Nutri-Score | Open Database License (ODbL); openfoodfacts.org |
| **BigBasket** catalogue | Indian market structure + price | 27,555 SKUs | product, brand, category, sub-category, price (INR) | Public product catalogue |

Full provenance and download URLs are in `docs/sources.md` and are reproduced by
`src/ingestion/download_data.py`.

### Why two datasets

No single reachable public dataset contains Indian branded products *with*
nutrition values at scale. Open Food Facts has rich nutrition and the official
Nutri-Score but is globally skewed (mostly EU/US products; very few India-tagged
items). BigBasket has real Indian brands, categories and prices but **no
nutrition**. We therefore integrate the two **at category level**: Open Food
Facts answers "how nutritionally exposed is this *category*", BigBasket grounds
that in the real Indian assortment and price. This design, and its limitations,
are stated openly rather than hidden.

## 2. The nutrition rating

### Nutri-Score (the scale we use)
The A–E rating is the **official 2017 Nutri-Score**, developed by the French
public-health authority (Santé publique France) from the FSA/Ofcom nutrient
profiling model. Points are assigned from *negative* nutrients (energy, sugars,
saturated fat, sodium) and *positive* components (fruit/veg/legume/nut %, fibre,
protein); the net score maps to a letter A–E. The published point tables are
reproduced in `src/config.py` and cited there.

- **Authoritative grade.** We use the Nutri-Score grade **already computed by
  Open Food Facts** from the full nutrient panel. This is the grade behind every
  headline number.
- **Re-implementation (validation).** We also implement the algorithm from
  scratch (`src/scoring/nutrition_score.py`). Because this particular export
  omits **saturated fat** and **fibre**, our re-implementation runs on the
  available subset (energy, sugars, sodium, protein). It reproduces the official
  grade **exactly in 48.9%** of cases and **within one grade in 92.5%**
  (Spearman ρ = 0.78 between our score and the official ordinal grade). The
  imperfect exact-match rate is expected and is documented as **Limitation L2**;
  it is a validation exercise, not the rating used downstream.

### India context (why this is a *scenario*)
Nutri-Score is a **European** front-of-pack scheme and is **not** an official
Indian rating. India's own proposal (FSSAI, Draft Labelling & Display
Regulations, 2022) is the **Indian Nutrition Rating (INR)** — a *star*-based
system (more stars = healthier). Applying Nutri-Score to products sold in India
is therefore an **analytical scenario** used to quantify *relative* exposure and
category structure; it should not be read as predicting the exact grade the INR
would assign. The A–E colour banding (Green A/B, Amber C, Red D/E) is used
purely as an intuitive exposure lens.

## 3. Cleaning (raw → cleaned)

The Open Food Facts cleaner (`src/cleaning/clean_data.py`) runs eleven steps:
load, schema-validate, standardise column names, coerce numerics, standardise
units (derive **sodium = salt ÷ 2.5**, i.e. `sodium_mg = salt_g × 400`), handle
missing values, de-duplicate, derive categories, normalise brands, flag/remove
impossible values, and save. Headline effects (full audit in
`data_quality_report.md`): 6,797 exact-duplicate rows and 10,256
duplicate name+brand rows removed; 699 rows with physically impossible nutrient
values removed; 804 statistical energy outliers *flagged but kept*. BigBasket is
filtered to genuine food categories (14,732 non-food SKUs removed) and price/
brand fields standardised.

### Category derivation (engineered feature)
Open Food Facts has no usable category column in this export, so categories are
derived from the **product name** using a transparent, priority-ordered keyword
classifier (28 buckets, multilingual EN + FR because ~28% of products are
French). The classifier assigns **75.5%** of products to a named category; the
remaining ~24.5% stay in an explicit *Other / Unclassified* bucket and are
**excluded** from category rankings rather than force-fitted. The same classifier
is applied to BigBasket product names so both sources share one taxonomy — this
is the mechanism that makes the cross-source category join valid.

## 4. Analysis (cleaned → final)

`src/analysis/business_analysis.py` computes Q1–Q6. Category rankings require
**≥300 graded products**; brand rankings require **≥80** — thresholds chosen so
that reported percentages are stable rather than driven by a handful of items.
Statistical tests (`src/analysis/statistics.py`) attach p-values and effect
sizes to the headline claims (two-proportion z, Welch's t + Cohen's d, Spearman,
Wilson CI, χ² + Cramér's V).

## 5. Scenario model (assumptions, clearly labelled)

`src/modelling/scenario_model.py` models three consumer responses. The **base
switch rates (Low 4%, Moderate 10%, High 20%)** are **ASSUMPTIONS** anchored to
the range of effects seen in published front-of-pack studies (see
`data/consumer_evidence/`), not empirical predictions for India. Each rate is
scaled by a **documented consumer-sensitivity** ordinal (impulse/indulgence
categories move more than staples; justification below).

**No invented revenue.** SKU-level Indian sales/volume data is not public, so the
model outputs a **unit-less Revenue Exposure Index** (exposure × switch × Indian
commercial weight, normalised 0–100) and a **Reformulation Priority** score —
never rupees. SKU counts proxy volume and this is stated wherever the index
appears.

## 6. Justifying the weights (no arbitrary numbers)

Two places use weights, and both are defended:

- **Consumer sensitivity (per category).** An ordinal 0.3–1.0 reflecting how much
  a front-of-pack colour plausibly moves purchases: highest for discretionary,
  impulse and indulgence buys (sugary drinks, confectionery, salty snacks =
  1.0), lowest for staples bought regardless of a colour (flour, rice, oil,
  water = 0.3). This mirrors the evidence that labels bite hardest on
  discretionary purchases.
- **Business-risk weights.** The base case weights the three drivers **equally
  (1/3 each)** — the honest default when no evidence justifies preferring one.
  We then re-run with a nutrition-first weighting (0.5 / 0.3 / 0.2) as a
  sensitivity check; the category ranking barely moves (Spearman ρ = 0.94), so
  conclusions do not hinge on the weighting.

## 7. Reproducibility

`python -m src.ingestion.download_data` → `src.cleaning.clean_data` →
`src.scoring.nutrition_score` → `src.analysis.business_analysis` →
`src.modelling.scenario_model` → `src.analysis.statistics` →
`database.build_database` → `powerbi.export_powerbi_data` regenerates every
artifact and the metrics file end-to-end.

## 8. Limitations (stated plainly)

- **L1 — India coverage.** Open Food Facts is globally skewed; category nutrition
  patterns are near-universal and are mapped onto the *real* Indian assortment
  via BigBasket, but the nutrition values themselves are not India-specific.
- **L2 — Missing nutrients.** This Open Food Facts export lacks saturated fat and
  fibre, so our *re-implemented* score is partial (the authoritative OFF grade is
  unaffected).
- **L3 — Category-level price join.** Price (BigBasket) and nutrition (OFF) meet
  at category level, not product level, so Q5 is a category-level signal with
  limited statistical power (25 points).
- **L4 — Scenario assumptions.** Switch rates are assumptions within the
  evidence range, not forecasts.
- **L5 — Nutri-Score ≠ INR.** The Indian scheme is star-based; results describe
  relative exposure, not the exact grade the INR would issue.
