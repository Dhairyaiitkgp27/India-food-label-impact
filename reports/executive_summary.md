# Executive Summary
### India Packaged Food Label Impact & Market Analytics

**The question.** If India rolls out an A–E front-of-pack (FOP) nutrition label,
which packaged-food categories and brands are most exposed, how might consumer
demand shift, and what should manufacturers and retailers do about it?

**The approach.** We scored **220,315 real packaged-food products** on the
official Nutri-Score (A–E) scale and mapped the exposure onto the **real Indian
grocery assortment and prices** of **12,207 BigBasket SKUs**. Nutri-Score is a
European scheme, so applying it to India is an explicit *analytical scenario*,
not a regulatory forecast — India's own proposal is the star-based Indian
Nutrition Rating (INR). Every figure below is computed from public data and is
reproducible from `reports/computed_metrics.json`.

---

## What an FMCG executive needs to know

1. **Nearly half the shelf would carry a "Red" label.** **48.1%** of products are
   grade **D or E**; only **31.1%** are A or B. A colour-coded label makes a
   problem that is currently invisible on-pack suddenly obvious to shoppers.

2. **The exposure is concentrated, not uniform.** Sweet and fatty indulgence
   categories dominate: **Chocolate & Confectionery (85.8% D/E)**, **Biscuits &
   Wafers (81.6%)**, **Cheese (74.6%)**, **Edible Oils & Fats (73.9%)** and
   **Cakes & Sweet Bakery (70.3%)**. Staples are barely touched — **Flour/Rice/
   Pulses sit at 10.0% D/E**. The problem is addressable because it is
   category-specific.

3. **The beverage aisle would split in two.** The broad sugary-drinks bucket
   looks average (44% D/E) only because it mixes diet/zero variants (≈39% grade
   B) with full-sugar drinks (≈30% grade E). Isolate genuine full-sugar colas and
   energy drinks and D/E exposure jumps to **85.3%**. A label rewards the
   reformulated variants and punishes the rest — within the same brand.

4. **Paying more does not buy health.** Across 25 categories matched to Indian
   prices, the correlation between price and nutritional "badness" is **positive**
   (Spearman **ρ = +0.34**), i.e. pricier categories are, if anything, *slightly
   less* healthy — the premium is paying for indulgence, not nutrition. Budget
   categories average the *best* nutrition score.

5. **A label moves demand at the margin, and that margin is quantifiable.** Under
   a central ("Moderate", 10% base switch) scenario, roughly **6,100 D/E SKUs**
   worth of demand in scope is exposed to switching; under a strong-response
   scenario, **~12,200**. Confectionery, biscuits and salty snacks carry the
   greatest revenue-exposure index in every scenario.

6. **The highest-value response is reformulation, not resistance.** The single
   highest-risk category — Chocolate & Confectionery (risk score **0.95/1.0**) —
   is also where the most grade-D products sit just below the C boundary, i.e.
   the most "fixable" via modest sugar/energy reduction. Risk rankings are stable
   whether the three risk drivers are weighted equally or nutrition-first
   (rank correlation **ρ = 0.94**), so the priority list is robust.

---

## The one-slide takeaway

> An A–E label would place a Red flag on **~48%** of packaged foods, with the
> damage concentrated in **confectionery, biscuits, cheese, oils and full-sugar
> drinks**. Price offers consumers no nutritional protection. The winning move
> for a manufacturer is to **reformulate the fixable D-grade lines and grow the
> A/B range**, especially in high-commercial-importance indulgence categories,
> rather than to treat the label as a threat to be resisted.

See `findings.md` for the full evidence, `recommendations.md` for the
stakeholder playbook, and `methodology.md` for how every number was produced and
what it can and cannot support.
