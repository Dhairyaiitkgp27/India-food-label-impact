-- ============================================================================
-- market_exposure.sql  |  Market rollups, price-vs-nutrition, scenario & risk.
-- Cross-source joins (OFF x BigBasket), CTEs, window functions.
-- ============================================================================

-- 1. Whole-market exposure headline ------------------------------------------
SELECT
    COUNT(*)                                                        AS products,
    ROUND(100.0*SUM(CASE WHEN nutrition_grade IN ('D','E') THEN 1 END)/COUNT(*),2) AS de_pct,
    ROUND(100.0*SUM(CASE WHEN nutrition_grade IN ('A','B') THEN 1 END)/COUNT(*),2) AS ab_pct,
    ROUND(100.0*SUM(CASE WHEN nutrition_grade = 'C'        THEN 1 END)/COUNT(*),2) AS c_pct
FROM products;

-- 2. Price vs nutrition by category (cross-source, category-level) -----------
--    Indian median price (BigBasket) alongside nutrition exposure (OFF).
--    A positive correlation of price with avg_score (1=A..5=E) => pricier
--    categories are LESS healthy.
SELECT
    category,
    off_products,
    de_pct,
    avg_score            AS nutrition_badness_1to5,
    bb_skus,
    median_price_inr
FROM price_vs_nutrition
ORDER BY median_price_inr DESC;

-- 3. Price tiers: split matched categories into price terciles and compare ---
--    average nutrition badness across Budget / Mid / Premium tiers.
WITH tiers AS (
    SELECT category, median_price_inr, avg_score,
           NTILE(3) OVER (ORDER BY median_price_inr) AS price_tier
    FROM price_vs_nutrition
)
SELECT
    CASE price_tier WHEN 1 THEN '1 Budget' WHEN 2 THEN '2 Mid' ELSE '3 Premium' END AS price_tier,
    COUNT(*)                        AS categories,
    ROUND(AVG(median_price_inr),0)  AS avg_median_price_inr,
    ROUND(AVG(avg_score),2)         AS avg_nutrition_badness
FROM tiers
GROUP BY price_tier
ORDER BY price_tier;

-- 4. Business-risk league table (Q6 framework) -------------------------------
SELECT
    RANK() OVER (ORDER BY business_risk DESC) AS risk_rank,
    category, de_pct, nutrition_exposure, consumer_sensitivity,
    commercial_importance, business_risk, business_risk_alt
FROM category_business_risk
ORDER BY business_risk DESC;

-- 5. Scenario impact: at-risk D/E SKUs by scenario ---------------------------
SELECT
    scenario,
    COUNT(*)                          AS categories,
    SUM(de_products)                  AS de_skus_in_scope,
    ROUND(SUM(at_risk_de_skus),0)     AS total_at_risk_skus,
    ROUND(AVG(effective_switch_rate),3) AS avg_effective_switch_rate
FROM scenario_results
GROUP BY scenario
ORDER BY total_at_risk_skus;

-- 6. Reformulation priority leaders under the Moderate scenario --------------
SELECT
    category,
    ROUND(de_share,3)                     AS de_share,
    ROUND(commercial_importance,3)        AS commercial_importance,
    ROUND(reformulation_priority_0_100,1) AS reformulation_priority_0_100
FROM scenario_results
WHERE scenario = 'Moderate'
ORDER BY reformulation_priority_0_100 DESC
LIMIT 10;

-- 7. Brands most exposed within the single highest-risk category -------------
--    (join the risk table's top category back to product-level brand detail).
WITH top_cat AS (
    SELECT category FROM category_business_risk ORDER BY business_risk DESC LIMIT 1
)
SELECT p.brand_clean,
       COUNT(*)                                                          AS products,
       ROUND(100.0*SUM(CASE WHEN p.nutrition_grade IN ('D','E') THEN 1 END)/COUNT(*),1) AS de_pct
FROM products p
JOIN top_cat t ON p.category = t.category
WHERE p.brand_clean <> 'Unknown'
GROUP BY p.brand_clean
HAVING COUNT(*) >= 20
ORDER BY de_pct DESC, products DESC
LIMIT 15;
