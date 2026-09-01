# Findings
### India Packaged Food Label Impact & Market Analytics

All figures are computed from the cleaned datasets and stored in
`reports/computed_metrics.json`. Nutrition grade = **official Open Food Facts
Nutri-Score** (A best … E worst). "D/E" = the two grades that would receive a
Red front-of-pack flag.

---

## Q1 — How exposed is the market overall?

| Metric | Value |
|---|---|
| Graded products analysed | **220,315** |
| Grade A / B / C / D / E share | 16.0% / 15.1% / 20.9% / 28.4% / 19.7% |
| **D/E (Red) exposure** | **48.1%** |
| A/B (Green) favourable | 31.1% |
| Mean nutrition score (1=A … 5=E) | ~3.2 |

Nutrient averages rise monotonically with worse grades — grade A products
average 732 kJ and 3.5 g sugar / 100 g, grade E products 1,779 kJ and 26.0 g
sugar — confirming the grade behaves as a sensible nutritional summary. Sodium
peaks in the C–D band (salty processed foods), not at E.

## Q2 — Which categories are most / least exposed?

**Most exposed (share D/E):**

| Rank | Category | D/E % |
|---|---|---|
| 1 | Chocolate & Confectionery | **85.8%** |
| 2 | Biscuits, Cookies & Wafers | 81.6% |
| 3 | Cheese | 74.6% |
| 4 | Edible Oils & Fats | 73.9% |
| 5 | Cakes, Pastries & Sweet Bakery | 70.3% |

**Least exposed:**

| Category | D/E % |
|---|---|
| Staples: Flour, Rice, Pulses & Grains | **10.0%** |
| Bread & Savoury Bakery | 15.5% |
| Yogurt & Dairy Drinks | 16.0% |
| Instant Noodles, Pasta & Soups | 19.0% |
| Fruits & Vegetables (packaged/plain) | 20.0% |

Two nuances worth flagging to a business audience: **cheese and edible oils
score poorly** not because they are "junk" but because Nutri-Score penalises
saturated-fat and energy density — a reminder that the label measures nutrient
profile, not culinary category. Highest mean sugar sits in *Sugar/Sweeteners &
Baking* (47.8 g/100 g); highest mean sodium in *Sauces, Ketchup & Condiments*
(1,331 mg/100 g).

## Q3 — Which brands are most / least exposed?

365 brands have ≥80 graded products and are ranked. The most-exposed brands are
premium **chocolate** houses whose entire catalogue is D/E — **Lindt, Milka,
Frey, Ritter Sport (all 100% D/E)** — illustrating that exposure tracks category
mix. The best-positioned large brands are dairy, produce and canned-vegetable
players (e.g. Chobani ~97% A/B, Bonduelle ~96% A/B, Dannon ~96% A/B). The
strategic point: a brand's exposure is largely a function of the categories it
competes in, so portfolio mix is the primary lever.

## Q4 — Product-level detail

- **43,311** products carry grade **E**; **35,166** carry grade **A**.
- Worst-by-sugar, worst-by-sodium and worst-by-energy league tables are exported
  to `data/final/` and reproduced by `sql/product_analysis.sql`.
- A "health-halo" scan (A/B products that nonetheless fall in the top sugar
  decile) highlights categories where a favourable grade can still hide high
  sugar — useful for reformulation QA.

## Q5 — Does price buy nutrition? (cross-source, Indian prices)

Matching **25 categories** to real BigBasket Indian prices and correlating median
price against nutritional badness (1–5):

- Spearman **ρ = +0.34** (p = 0.098), Pearson **r** similar and positive.
- Price-tercile view: **Budget** categories average the *best* badness score
  (2.72), **Mid** the worst (3.55), **Premium** in between (3.25).

**Interpretation:** there is no evidence that more expensive categories are
healthier; the weak signal points the other way. The correlation is not
statistically significant at 5% (only 25 category points), so we state it as a
*directional* finding, not a proven law. Practically: consumers cannot price-
shop their way to a Green basket.

## Q6 — Category business-risk framework

Business risk combines three equally-weighted, documented drivers — **nutrition
exposure** (D/E share), **consumer sensitivity** (how much a label moves that
category) and **commercial importance** (Indian assortment share from BigBasket):

| Rank | Category | Risk (0–1) |
|---|---|---|
| 1 | Chocolate & Confectionery | **0.95** |
| 2 | Biscuits, Cookies & Wafers | 0.72 |
| 3 | Chips, Crisps & Salty Snacks | 0.67 |
| 4 | Spreads, Jam, Honey & Syrups | 0.60 |
| 5 | Cakes, Pastries & Sweet Bakery | 0.58 |

Re-running with a nutrition-first weighting (0.5 / 0.3 / 0.2) barely changes the
order — rank correlation **ρ = 0.94** — so the priority list is robust to the
weighting choice (a common interview challenge).

---

## Scenario model — how much demand is exposed?

Three consumer-response scenarios apply an evidence-anchored base switch rate to
the D/E assortment, scaled by category consumer sensitivity. Outputs are
**unit-less exposure indices and SKU counts, never rupee revenue** (SKU-level
Indian sales data is not public).

| Scenario | Base switch | D/E SKUs at risk (in scope) |
|---|---|---|
| Low | 4% | ~2,440 |
| Moderate | 10% | ~6,100 |
| High | 20% | ~12,200 |

Confectionery, biscuits and salty snacks top the Revenue Exposure Index in every
scenario. **Reformulation Priority** (which categories combine high exposure,
high commercial weight and a high share of *fixable* grade-D products) is led by
Chocolate & Confectionery (100/100), then nuts/spreads, sauces and salty snacks.

## Statistical tests (defensibility)

| Test | Result | Meaning |
|---|---|---|
| Full-sugar drinks vs market D/E (two-prop z) | strict subset **85.3% D/E**; broad SSB 44.2% vs market 48.1%, z=−3.2, p=0.001 | beverage bucket is polarised (diet B vs full-sugar E) |
| Sugar: confectionery vs dairy (Welch t) | 39.2 vs 11.8 g, t=120, p<10⁻³, **Cohen's d=1.45** | very large, significant gap |
| Energy vs grade (Spearman) | **ρ=0.57**, p<10⁻³, n≈220k | energy density tracks worse grades |
| Market D/E share (Wilson 95% CI) | **48.07%**, CI 47.86–48.28% | tight, precise estimate |
| Category × grade independence (χ²) | χ²≈45,270, p<10⁻³, Cramér's V=0.30 | grade depends strongly on category |

See `methodology.md` for assumptions and limitations, and `recommendations.md`
for what to do with these findings.
