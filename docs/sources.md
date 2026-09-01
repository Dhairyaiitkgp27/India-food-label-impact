# Data Sources & Provenance

All data used in this project is **publicly available**. This file documents
where each dataset came from, its licence, and how to reproduce the download.

## 1. Open Food Facts — branded product nutrition

- **What:** ~257k branded packaged-food products with nutrient values per 100 g
  and the official Nutri-Score grade.
- **Upstream project:** Open Food Facts (openfoodfacts.org), a collaborative,
  free food-products database.
- **Licence:** **Open Database License (ODbL)**. Product data is available under
  ODbL; individual contents may be under Database Contents License. Attribution
  to Open Food Facts and the ODbL is required for reuse.
- **Access used here:** a public CSV export mirrored on GitHub
  (`adadntla/OpenFoodFacts-Nutrition-Analysis`,
  `Final_OpenFoodFacts_Clean.csv`), chosen for a deterministic, scriptable
  download. Reproduced by `src/ingestion/download_data.py`.
- **Note on coverage:** the export is globally skewed (predominantly EU/US
  products; very few India-tagged items). This is why nutrition patterns are
  analysed at category level and grounded in the Indian assortment via
  BigBasket. See Limitation L1 in `reports/methodology.md`.

## 2. BigBasket — Indian grocery catalogue

- **What:** ~27.5k SKUs from a large Indian online grocer, with product, brand,
  category, sub-category and price (INR).
- **Upstream:** BigBasket.com public product catalogue.
- **Licence / terms:** public catalogue data; used here for non-commercial,
  educational analysis. No personal or transactional data is involved.
- **Access used here:** a public CSV mirrored on GitHub
  (`Sumaiyyaustad/MarketMetrics-Analyzing-Grocery-FMCG-Pricing-Trends`,
  `Data/BigBasket Products.csv`). Reproduced by
  `src/ingestion/download_data.py`.

## 3. Nutri-Score methodology (not a dataset — an algorithm)

- **What:** the 2017 Nutri-Score point tables and grade thresholds.
- **Source:** Santé publique France (the French public-health authority), based
  on the FSA/Ofcom nutrient profiling model.
- **Use:** reproduced in `src/config.py` and applied in
  `src/scoring/nutrition_score.py`; the authoritative grades come from Open Food
  Facts' own Nutri-Score computation.

## 4. Indian policy context

- **What:** the Indian Nutrition Rating (INR), a proposed star-based front-of-
  pack scheme.
- **Source:** FSSAI (Food Safety and Standards Authority of India), Draft
  Labelling & Display Regulations, 2022.
- **Use:** establishes that a front-of-pack label in India is a live policy
  scenario and that India's own scheme differs from Nutri-Score.

## 5. Consumer-evidence literature

Summarised in `data/consumer_evidence/fop_label_studies.csv` with per-study
attribution (Taillie et al. 2020; Shangguan et al. 2019; Egnell et al.; Cecchini
& Warin 2016; Crosetto et al.; FSSAI INR proposal; Global Food Monitoring
Group). These motivate the scenario assumptions and are indexed, not
reproduced — confirm specific figures against the primary papers before external
citation.

---

### Attribution statement
This project reuses Open Food Facts data under the **ODbL**; Open Food Facts and
its contributors are gratefully acknowledged. BigBasket catalogue data is used
for educational, non-commercial analysis. Nutri-Score is a scheme of Santé
publique France. This project is an independent academic/portfolio analysis and
is not affiliated with, or endorsed by, any of these organisations.
