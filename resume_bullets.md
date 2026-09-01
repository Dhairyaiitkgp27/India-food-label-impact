# Résumé Bullets

Ready-to-paste bullets for the **India Packaged Food Label Impact & Market
Analytics** project. Every number is real and reproducible from
`reports/computed_metrics.json`. Three versions are provided — pick the one that
matches the role you are applying for. Each bullet follows
**Action → Tech → Scale → Quantified finding → Impact**.

> Tip: keep 4–5 bullets. Lead with the bullet closest to the job description.

---

## Version A — Data Analyst (analysis / SQL / BI emphasis)

- **Engineered an end-to-end analytics pipeline** in **Python (pandas, NumPy)**
  that cleaned and integrated **257K+ Open Food Facts products** with **27K
  BigBasket Indian SKUs**, removing ~18K duplicate/invalid records and
  classifying **220K+ products** into 28 categories via a rule-based
  multilingual keyword classifier (75.5% coverage).
- **Built a SQLite analytical database and 27 SQL queries** (CTEs, window
  functions, cross-source joins) to quantify nutrition exposure, revealing that
  **48.1% of packaged foods would carry a "Red" (D/E) front-of-pack label**,
  concentrated in confectionery (85.8%), biscuits (81.6%) and edible oils
  (73.9%).
- **Re-implemented the official Nutri-Score algorithm** from scratch and
  **validated it against 220K+ authoritative grades** (92.5% within-one-grade
  agreement, Spearman ρ = 0.78), establishing the scoring as defensible rather
  than a black box.
- **Ran a statistical test suite** (two-proportion z, Welch's t with Cohen's
  d = 1.45, χ² with Cramér's V, Wilson CI) that isolated a **polarised beverage
  aisle** — a broad sugary-drink bucket at 44% D/E but genuine full-sugar
  colas/energy drinks at **85.3% D/E**.
- **Designed a 5-page Power BI report** (star schema, DAX, what-if parameter) and
  a **Streamlit dashboard**, translating 220K-row analysis into an
  executive-ready view of category and brand exposure.

## Version B — Business / Market-Intelligence Analyst (insight / decision emphasis)

- **Framed and answered a live FMCG policy question** — the market impact of an
  A–E front-of-pack nutrition label in India — by scoring **220K+ real products**
  and mapping exposure onto the Indian grocery assortment and prices.
- **Quantified category and brand risk** with a documented, weight-justified
  business-risk framework, identifying **Chocolate & Confectionery as the
  highest-risk category (0.95/1.0)** and showing the ranking is robust to the
  weighting choice (ρ = 0.94).
- **Overturned a common pricing assumption** through a cross-source price-vs-
  nutrition analysis of 25 categories, showing **price does not buy nutrition**
  (Spearman ρ = +0.34; budget categories scored *healthiest*) — a direct input
  to retailer range and messaging strategy.
- **Modelled three evidence-anchored demand scenarios**, estimating **~6,100 D/E
  SKUs exposed to switching under a moderate response (~12,200 under a strong
  response)** using a transparent, unit-less Revenue Exposure Index rather than
  fabricated revenue.
- **Authored a full decision pack** (executive summary, findings, stakeholder
  playbook and four qualitatively-scored strategic options), converting the
  analysis into a "reformulate the fixable D-lines, grow the A/B range"
  recommendation for manufacturers and retailers.

## Version C — Data + Business Analyst (balanced, technical + commercial)

- **Delivered an end-to-end market-intelligence study** (Python, SQL, Power BI,
  Streamlit) on the FMCG impact of an A–E nutrition label, integrating **257K+
  Open Food Facts products** with **27K BigBasket Indian SKUs** into a single
  category-level analytical model.
- **Cleaned and scored 220K+ products** on the official Nutri-Score scale
  (validated re-implementation, ρ = 0.78) and quantified that **48.1% of the
  market would carry a Red D/E label**, with exposure concentrated in a handful
  of indulgence categories.
- **Wrote 27 SQL analytical queries** and a **statistical test suite** (z-test,
  Welch's t, Cohen's d = 1.45, χ², Wilson CI) to make every headline claim
  defensible, surfacing an **85.3% D/E rate among genuine full-sugar drinks**
  hidden inside an average-looking beverage bucket.
- **Built a category business-risk framework and a 3-scenario demand model**
  (unit-less exposure indices, no invented revenue), identifying reformulation
  priorities led by confectionery, biscuits and salty snacks.
- **Packaged the results for decision-makers** via a 5-page Power BI report,
  a Streamlit dashboard and a written stakeholder playbook, recommending a
  reformulation-and-portfolio-shift strategy over resistance to the label.

---

### Skills demonstrated (for a skills section)
Data cleaning & integration · feature engineering · SQL (CTEs, window functions)
· statistical hypothesis testing & effect sizes · scenario/what-if modelling ·
data visualisation (Power BI, DAX, Streamlit) · business framing & stakeholder
communication · reproducible pipelines · analytical honesty (documented
assumptions & limitations).
