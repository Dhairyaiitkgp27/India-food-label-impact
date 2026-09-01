-- ============================================================================
-- brand_analysis.sql  |  Brand-level exposure intelligence.
-- CTEs, window ranking, NTILE deciles, HAVING thresholds, self-join comparison.
-- ============================================================================

-- 1. Most-exposed major brands (>=80 products), ranked by D/E share ----------
WITH b AS (
    SELECT
        brand_clean,
        COUNT(*)                                                          AS products,
        ROUND(100.0*SUM(CASE WHEN nutrition_grade IN ('D','E') THEN 1 END)/COUNT(*),1) AS de_pct,
        ROUND(100.0*SUM(CASE WHEN nutrition_grade IN ('A','B') THEN 1 END)/COUNT(*),1) AS ab_pct,
        ROUND(AVG(nutrition_score),2)                                     AS avg_score
    FROM products
    WHERE brand_clean <> 'Unknown'
    GROUP BY brand_clean
    HAVING COUNT(*) >= 80
)
SELECT
    RANK() OVER (ORDER BY de_pct DESC, products DESC) AS exposure_rank,
    brand_clean, products, de_pct, ab_pct, avg_score,
    NTILE(10) OVER (ORDER BY de_pct DESC)             AS exposure_decile
FROM b
ORDER BY de_pct DESC, products DESC
LIMIT 25;

-- 2. Best-positioned major brands (highest A/B share) ------------------------
WITH b AS (
    SELECT brand_clean, COUNT(*) AS products,
        ROUND(100.0*SUM(CASE WHEN nutrition_grade IN ('A','B') THEN 1 END)/COUNT(*),1) AS ab_pct
    FROM products
    WHERE brand_clean <> 'Unknown'
    GROUP BY brand_clean
    HAVING COUNT(*) >= 80
)
SELECT RANK() OVER (ORDER BY ab_pct DESC) AS health_rank,
       brand_clean, products, ab_pct
FROM b
ORDER BY ab_pct DESC
LIMIT 25;

-- 3. Portfolio breadth vs exposure: do brands with more SKUs skew worse? -----
--    bucket brands into SKU-count quartiles and compare mean D/E share.
WITH b AS (
    SELECT brand_clean, COUNT(*) AS products,
        100.0*SUM(CASE WHEN nutrition_grade IN ('D','E') THEN 1 END)/COUNT(*) AS de_pct
    FROM products
    WHERE brand_clean <> 'Unknown'
    GROUP BY brand_clean
    HAVING COUNT(*) >= 80
),
q AS (SELECT brand_clean, products, de_pct,
             NTILE(4) OVER (ORDER BY products) AS sku_quartile FROM b)
SELECT sku_quartile,
       COUNT(*)                AS brands,
       MIN(products)           AS min_skus,
       MAX(products)           AS max_skus,
       ROUND(AVG(de_pct),1)    AS avg_de_pct
FROM q
GROUP BY sku_quartile
ORDER BY sku_quartile;

-- 4. Brand exposure vs its category norm -------------------------------------
--    for each brand's dominant category, compare brand D/E to category D/E.
WITH brand_cat AS (
    SELECT brand_clean, category, COUNT(*) AS n,
           ROW_NUMBER() OVER (PARTITION BY brand_clean ORDER BY COUNT(*) DESC) AS rn
    FROM products
    WHERE brand_clean <> 'Unknown' AND category <> 'Other / Unclassified'
    GROUP BY brand_clean, category
),
brand_de AS (
    SELECT brand_clean,
           100.0*SUM(CASE WHEN nutrition_grade IN ('D','E') THEN 1 END)/COUNT(*) AS brand_de,
           COUNT(*) AS products
    FROM products WHERE brand_clean <> 'Unknown' GROUP BY brand_clean
),
cat_de AS (
    SELECT category,
           100.0*SUM(CASE WHEN nutrition_grade IN ('D','E') THEN 1 END)/COUNT(*) AS cat_de
    FROM products GROUP BY category
)
SELECT bc.brand_clean, bc.category AS main_category, bd.products,
       ROUND(bd.brand_de,1) AS brand_de_pct,
       ROUND(cd.cat_de,1)   AS category_de_pct,
       ROUND(bd.brand_de - cd.cat_de,1) AS gap_vs_category
FROM brand_cat bc
JOIN brand_de bd ON bd.brand_clean = bc.brand_clean
JOIN cat_de  cd ON cd.category    = bc.category
WHERE bc.rn = 1 AND bd.products >= 80
ORDER BY gap_vs_category DESC
LIMIT 20;
