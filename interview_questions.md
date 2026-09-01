# Interview Questions & Answers

Practice questions for defending the **India Packaged Food Label Impact & Market
Analytics** project. Each item has an **answer**, a likely **follow-up**, and an
answer to that follow-up. Questions are grouped by theme. Numbers cited are the
real project outputs (`reports/computed_metrics.json`).

---

## A. Project framing & business sense

**1. In one sentence, what does this project do?**
It scores 220K+ real packaged-food products on the official A–E Nutri-Score scale
and maps that exposure onto the real Indian grocery market to estimate which
FMCG categories and brands are most exposed to a front-of-pack nutrition label,
how demand might shift, and what companies should do.
- *Follow-up: Why is that a business problem and not just a public-health one?*
  Because a label re-prices attention across the shelf overnight: ~48% of
  products would get a Red flag, concentrated in high-margin indulgence
  categories, directly affecting volumes, portfolio strategy and reformulation
  spend. It changes what sells.

**2. Why did you treat this as business analytics rather than machine learning?**
The question is "which categories/brands are exposed, by how much, and what
should we do" — a descriptive, diagnostic and prescriptive problem. The value is
in a defensible score, transparent segmentation and a decision framework, not in
predicting an unknown label. Forcing an ML model would add opacity without
answering the actual question.
- *Follow-up: Where could ML add value later?*
  Predicting a product's likely grade from its name/ingredients where nutrient
  data is missing, or clustering reformulation archetypes. Both are extensions,
  not the core deliverable.

**3. Who is the audience and what decision does this inform?**
FMCG manufacturers and retailers (and, secondarily, policymakers). It informs
reformulation prioritisation, portfolio strategy, private-label range decisions
and shelf navigation ahead of a labelling regulation.

**4. What's the single most important finding?**
That the exposure is both large (~48% D/E) and *concentrated* — a handful of
categories drive it — which means it is addressable through targeted
reformulation rather than being a diffuse, unfixable problem.

**5. What surprised you most?**
That price offers no nutritional protection: across 25 categories the price–
badness correlation is positive (ρ = +0.34), and budget categories scored the
*healthiest*. It contradicts the intuitive "premium = healthier" assumption.

**6. If you had one more week, what would you add?**
India-specific nutrient data (even a few hundred verified products) to calibrate
the category patterns, and a proper INR (star) re-implementation alongside
Nutri-Score to compare grade distributions.

---

## B. Data sourcing & honesty

**7. Walk me through your data sources.**
Two real public datasets: Open Food Facts (257K branded products with nutrients
per 100 g and the official Nutri-Score, ODbL) as the nutrition engine, and the
BigBasket catalogue (27.5K Indian SKUs with brand, category, price) for Indian
market structure and price.

**8. The obvious criticism: Open Food Facts is mostly not Indian. How do you
defend that?**
I don't hide it — it's Limitation L1. No reachable public dataset has Indian
branded products *with* nutrition values at scale. My design response is to
analyse nutrition patterns at **category level** (which are near-universal —
chocolate is sugar-and-fat-dense everywhere) and ground them in the *real* Indian
assortment and prices via BigBasket. I state clearly that the nutrition values
are not India-specific.
- *Follow-up: Doesn't that undermine the whole project?*
  It bounds the claims, not invalidates them. The project answers "relative
  category/brand exposure and market structure," which category-level nutrition
  supports well. It does not claim to predict the exact grade of a specific
  Indian SKU, and says so.

**9. How do the two datasets actually join?**
At category level. I run the *same* keyword classifier on both Open Food Facts
and BigBasket product names, so both share one 28-bucket taxonomy. That lets me
put category nutrition exposure (OFF) next to category Indian price and
assortment weight (BigBasket).

**10. Did you fabricate or estimate any numbers?**
No empirical number is fabricated. Every count, share, mean, correlation, p-value
and effect size is computed from the real data and stored in a metrics JSON. The
only non-observed inputs are clearly-labelled *assumptions* (scenario switch
rates, consumer-sensitivity weights), documented in `docs/assumptions.md`.

**11. Why didn't you just invent plausible revenue figures to make it punchier?**
Because SKU-level Indian sales/volume data isn't public, any revenue number would
be fiction — and a single fabricated figure would make an interviewer distrust
the entire project. Instead I built a unit-less Revenue Exposure Index and used
SKU counts as a transparent volume proxy.

**12. What licence governs the data and why does it matter?**
Open Food Facts is under the Open Database License (ODbL), which permits reuse
with attribution — so the project is legally reproducible and shareable.
BigBasket is a public catalogue used for non-commercial educational analysis.

---

## C. Nutri-Score & scoring

**13. What is Nutri-Score and why did you choose it?**
It's a validated European front-of-pack scheme (Santé publique France, from the
FSA/Ofcom nutrient profiling model) that maps a product to A–E from negative
nutrients (energy, sugars, saturated fat, sodium) and positive components
(fruit/veg/nuts, fibre, protein). I chose it because it's published, widely
validated, and the Open Food Facts data already carries official grades.

**14. But India isn't adopting Nutri-Score. Isn't that a fatal flaw?**
It's why the whole thing is framed as a *scenario*. India's proposal is the
star-based Indian Nutrition Rating (INR). I use the A–E scheme as an intuitive,
validated lens for *relative* exposure and state explicitly (L5) that results
describe relative exposure, not the exact grade the INR would issue.
- *Follow-up: Would your conclusions change under a star system?*
  The *ordering* almost certainly holds — confectionery and sugary drinks are
  nutritionally worst under any sane profiling model. The exact thresholds and
  percentages would shift. That's why I emphasise the ranking and structure, not
  the precise cut-offs.

**15. You "re-implemented" Nutri-Score. Why, if the grade was already there?**
To prove I understand the algorithm and to validate the authoritative grade
rather than trusting it blindly. I coded the 2017 point tables from scratch and
compared.

**16. Your re-implementation only matched exactly 48.9% of the time. Isn't that
bad?**
It's expected and honestly reported. This export omits **saturated fat and
fibre**, two scoring inputs, so my from-scratch score runs on a subset. Despite
that, it agrees within one grade 92.5% of the time with Spearman ρ = 0.78 — good
convergent validity given missing inputs. Crucially, the *authoritative* OFF
grade (computed with the full panel) is what every downstream number uses; the
re-implementation is validation only.
- *Follow-up: So which grade did you actually analyse with?*
  The official Open Food Facts Nutri-Score, always. The re-implementation never
  feeds the analysis.

**17. How did you handle the missing saturated fat and fibre?**
In the re-implementation they score zero (documented, A3). For the real analysis
it doesn't matter because I use the official grade. I flag the gap as Limitation
L2 rather than papering over it.

**18. What do the A/B/C/D/E bands mean in your reports?**
Green/Favourable (A/B), Amber/Intermediate (C), Red/Exposed (D/E). "D/E exposure"
is my headline metric because those two grades would get the red-flag colour on
pack.

---

## D. Cleaning & feature engineering

**19. Walk me through your cleaning pipeline.**
Eleven steps for Open Food Facts: load, schema-validate, standardise columns,
coerce numerics, standardise units (derive sodium from salt), handle missing
values, de-duplicate, engineer category, normalise brand, flag/remove impossible
values, save. BigBasket is filtered to food, prices coerced and validated,
brands normalised.

**20. How much data did you remove and how do you justify it?**
~17.8K Open Food Facts rows: 6,797 exact duplicates, 10,256 duplicate
name+brand, and 699 physically impossible rows (e.g. sugars > carbohydrates,
energy out of range). For BigBasket, 14,732 non-food SKUs. Each rule is
principled and logged in the data-quality report.
- *Follow-up: How did you decide a row was "impossible"?*
  Hard physical bounds (sugar/salt 0–100 g/100 g, energy 0–3,900 kJ/100 g) and a
  logical rule (sugars can't exceed carbohydrates, with a 0.5 g tolerance for
  rounding).

**21. You *flagged* energy outliers instead of deleting them. Why the different
treatment?**
Because a high energy value is often legitimate (oils, nuts). Deleting them would
bias the analysis against energy-dense-but-real foods. So I added an
`energy_outlier_flag` (804 rows) and kept them — outlier ≠ error.

**22. How did you create the category feature, and how good is it?**
Open Food Facts has no usable category in this export, so I built a
priority-ordered, multilingual (English + French, since ~28% of names are French)
keyword classifier into 28 buckets. It classifies 75.5% of products; the rest
stay in an explicit *Other / Unclassified* bucket and are excluded from category
rankings.
- *Follow-up: Keyword classification is crude — what's the risk?*
  Mis-bucketing and language gaps. I mitigated with priority ordering (so
  "chocolate milk" resolves sensibly), accent-stripping for French, and by never
  force-fitting the unclassified 24.5%. A supervised classifier is the obvious
  upgrade, but a transparent rule base is more auditable for a portfolio.

**23. Why normalise brands, and how?**
The same brand appears many ways (case, accents, "Brand A, Brand B" strings). I
lower-case, strip accents, take the first brand, and alias major owners, giving
34.7K clean brands. Without this, brand-level exposure would be fragmented and
wrong.

**24. Why the ≥300-product (category) and ≥80 (brand) thresholds?**
So reported percentages are stable rather than driven by a handful of items. A
category at 90% D/E from 12 products is noise; from 300+ it's a signal.

---

## E. SQL & database

**25. Why put the data in SQLite at all?**
To demonstrate a proper analytical data layer and let the analysis be re-run in
SQL independently of Python. It also mirrors how a real BI stack would query the
data.

**26. What SQL techniques did you use?**
CTEs, conditional aggregation, window functions (RANK, ROW_NUMBER, NTILE),
running totals, HAVING filters, correlated subqueries and cross-source joins —
across six query files (27 queries), all verified to run against the DB.

**27. Give an example of a non-trivial query.**
A Pareto in `category_analysis.sql`: a CTE aggregates D/E counts per category,
then a window `SUM() OVER (ORDER BY … DESC)` produces a cumulative share, showing
how few categories account for most of the D/E problem.
- *Follow-up: How would you optimise it on a much larger table?*
  Index the filter/join columns (I index category, grade and brand), pre-
  aggregate into summary tables (which I do for the dashboard), and avoid
  correlated subqueries in favour of window functions on big scans.

**28. How do you know the database matches your Python results?**
A pytest test and an in-build check both recompute the D/E share in SQL (48.07%)
and assert it matches the pipeline. The data-quality SQL re-verifies integrity
directly against the DB.

---

## F. Statistics

**29. Which statistical tests did you run and why those?**
Five, each tied to a claim: a two-proportion z-test (are drinks more exposed?),
Welch's t-test with Cohen's d (is confectionery sugar higher than dairy?), a χ²
test with Cramér's V (does grade depend on category?), Spearman (does energy
track grade?), and a Wilson CI (how precise is the 48% estimate?).

**30. Your beverage z-test came out the "wrong" way — explain.**
The broad sugary-drinks bucket is 44.2% D/E, *below* the 48.1% market average,
which looks counterintuitive. The reason is genuine polarisation: the bucket
mixes ~39% grade-B diet/zero variants with ~30% grade-E full-sugar drinks. When I
isolate genuine full-sugar colas/energy drinks, D/E jumps to 85.3%. So the
honest finding is more interesting than the naïve one — a label would split the
aisle, not condemn it uniformly.
- *Follow-up: Isn't reporting a result that contradicts your hypothesis a
  weakness?*
  The opposite — it shows I follow the data and investigate anomalies rather than
  cherry-picking. The polarisation insight is one of the project's best points.

**31. Why Welch's t-test rather than Student's?**
Because the two groups (confectionery vs dairy sugar) have very different
variances and sizes; Welch's doesn't assume equal variance, so it's the safer
default.

**32. Cohen's d was 1.45 — interpret that.**
It's a very large effect: the mean sugar difference between confectionery and
dairy is about 1.45 pooled standard deviations. Combined with p < 10⁻³, the
difference is both statistically and practically significant.

**33. Your price–nutrition correlation wasn't significant (p = 0.098). Why report
it?**
Honesty and power. With only 25 category points, significance is hard, so I state
it as a *directional* finding, not a proven law. The direction (positive, i.e.
pricier ≠ healthier) is consistent across the tercile view too, which strengthens
the qualitative read even without significance.
- *Follow-up: How would you get significance?*
  More matched categories or a product-level price join (not available here), or
  a bootstrap on the category estimates. I chose not to overclaim instead.

**34. What does Cramér's V = 0.30 tell you beyond the χ²?**
χ² only says "not independent" (trivially true at this sample size). Cramér's V
(0.30) quantifies the *strength* — a moderate association between category and
grade — which is the business-relevant part.

**35. Why a Wilson confidence interval rather than a normal approximation?**
Wilson behaves better for proportions and large n, giving a tight, reliable
interval (47.86–48.28%) around the 48.07% D/E estimate. It's the more defensible
choice.

---

## G. Business analysis, risk & scenario

**36. How is your business-risk score constructed?**
Equal-weight (1/3 each) blend of nutrition exposure (D/E share), consumer
sensitivity (how much a label moves that category) and commercial importance
(Indian assortment share from BigBasket), per category.

**37. Equal weights feel arbitrary. Defend that.**
Equal weighting is the neutral default when no evidence justifies preferring a
driver. More importantly, I ran a sensitivity check with a nutrition-first
weighting (0.5/0.3/0.2) and the category ranking barely moved (Spearman ρ =
0.94), so the conclusion doesn't hinge on the weights.
- *Follow-up: What if a stakeholder insisted commercial importance should
  dominate?*
  The framework takes any weights; I'd re-run and show the new ranking plus its
  correlation to the base case. The robustness check is exactly there to handle
  that conversation.

**38. Where does "consumer sensitivity" come from — did you make it up?**
It's a documented ordinal (0.3–1.0): high for discretionary/impulse/indulgence
categories, low for staples bought regardless of a colour. It's an assumption
(A6), justified by the FOP-label evidence that labels bite hardest on
discretionary purchases — and it's transparent, not hidden inside a black box.

**39. Explain your scenario model in plain terms.**
Three consumer responses (Low/Moderate/High) apply a base switch rate (4/10/20%)
to the D/E assortment, scaled by category sensitivity, to estimate how many D/E
SKUs' worth of demand is exposed to switching — ~2,440 / ~6,100 / ~12,200.

**40. Those switch rates — where's the evidence?**
They're assumptions anchored to the *range* seen in published FOP studies (Chile
warning labels, Nutri-Score experiments, meta-analyses) in
`data/consumer_evidence/`. I label them as assumptions (A7), not predictions, and
the model is explicitly a what-if.
- *Follow-up: Chile saw ~24% — why is your "High" only 20%?*
  Chile used mandatory *warning* labels (stronger than a graded A–E scheme) and
  measured specific flagged drinks. A general A–E label across all categories
  should move demand less on average, so a 4–20% band is conservative and
  defensible.

**41. What's the "Revenue Exposure Index" and why not real revenue?**
A unit-less 0–100 index = exposure × switch × Indian commercial weight, used
because SKU-level Indian sales aren't public. It ranks where revenue is *most
exposed* without pretending to know the rupee value.

**42. What's "Reformulation Priority" and why is it useful?**
It combines D/E share, commercial importance and the share of D products that are
*fixable* (close to the C boundary). It points to where reformulation buys the
most grade improvement per unit effort — confectionery first, then snacks/
spreads/sauces.

---

## H. Recommendations, limitations & design

**43. What do you actually recommend a manufacturer do?**
Treat the label as a reformulation roadmap: fix the borderline grade-D lines in
high-commercial-importance indulgence categories and grow the A/B range, rather
than resist the label. "Do nothing" is only rational for already-Green portfolios
(staples/dairy/produce).

**44. Why present four strategic options instead of one answer?**
Because the right move depends on the portfolio and risk appetite. I scored
Reformulate / Reposition / Portfolio-shift / Do-nothing qualitatively
(Cost/Benefit/Risk/Feasibility) so a decision-maker can choose — that's decision
support, not a lecture.

**45. What are the biggest limitations, honestly?**
Five, all documented: India coverage (L1), missing sat-fat/fibre (L2), category-
level price join (L3), scenario assumptions (L4) and Nutri-Score ≠ INR (L5). I'd
rather state them than have an interviewer find them.
- *Follow-up: Which limitation worries you most?*
  L1 (India coverage), because it's the one a sharp reviewer hits first. My
  mitigation — category-level analysis grounded in the real Indian assortment,
  with explicit scoping of claims — is deliberate, but India-specific nutrient
  data would materially strengthen it.

**46. How is the whole project reproducible?**
A single documented chain: download → clean → score → analyse → model → stats →
build DB → export BI, regenerating every artifact and the metrics JSON.
`requirements.txt`, a pytest suite and executed notebooks back it up.

**47. How did you validate correctness beyond eyeballing?**
A 13-test pytest suite asserts valid grades, no impossible nutrients, correct
sodium derivation, monotonic scenario outputs, normalised indices and DB↔metrics
agreement. Nutrient means also rise monotonically by grade, a sanity check that
the score behaves.

**48. If this were going into production, what would you change?**
Add a supervised category classifier, ingest India-specific nutrition where
available, implement the INR star scheme alongside Nutri-Score, move from SQLite
to a warehouse, and schedule the pipeline. The current design is optimised for
transparency and reproducibility, which is right for a portfolio.

**49. What was the hardest technical decision?**
How to honestly connect Indian market data (no nutrition) with global nutrition
data (little India). Choosing a documented category-level join — and being
explicit about what it can and can't support — was harder and more valuable than
any single line of code.

**50. Sell me this project in 30 seconds.**
I took two messy public datasets, built a reproducible pipeline that scores 220K+
products on a validated nutrition scale, and answered a real FMCG question: ~48%
of the shelf would get a Red label, the damage is concentrated in a few
indulgence categories, price buys you no health, and the winning response is
targeted reformulation. Every number is real, every assumption is labelled, and
every limitation is stated — with SQL, statistics, Power BI and a written
decision pack to back it up.

---

## I. Rapid-fire

**51. Rows analysed?** 220,315 graded products.
**52. D/E share?** 48.1% (Wilson CI 47.86–48.28%).
**53. Most-exposed category?** Chocolate & Confectionery, 85.8% D/E.
**54. Least-exposed?** Staples (Flour/Rice/Pulses), 10.0% D/E.
**55. Full-sugar drinks D/E?** 85.3% (strict subset).
**56. Price–nutrition correlation?** Spearman ρ = +0.34 (pricier ≠ healthier).
**57. Highest-risk category?** Chocolate & Confectionery, 0.95/1.0.
**58. Moderate-scenario at-risk SKUs?** ~6,100 (High: ~12,200).
**59. Biggest effect size?** Cohen's d = 1.45 (confectionery vs dairy sugar).
**60. One-line honesty statement?** Every empirical number is real and
reproducible; every assumption and limitation is written down.
