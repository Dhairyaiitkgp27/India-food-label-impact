-- ============================================================================
-- category_analysis.sql  |  Category-level exposure intelligence.
-- Demonstrates CTEs, conditional aggregation, window functions (RANK, NTILE,
-- running totals) and HAVING filters.
-- ============================================================================

-- 1. Category exposure league table -----------------------------------------
--    D/E %, A/B %, mean sugar/sodium/energy, ranked worst-first.
WITH cat AS (
    SELECT
        category,
        COUNT(*)                                                         AS products,
        ROUND(100.0*SUM(CASE WHEN nutrition_grade IN ('D','E') THEN 1 END)/COUNT(*),2) AS de_pct,
        ROUND(100.0*SUM(CASE WHEN nutrition_grade IN ('A','B') THEN 1 END)/COUNT(*),2) AS ab_pct,
        ROUND(AVG(sugars_g_100g),1)                                      AS avg_sugar_g,
        ROUND(AVG(sodium_mg_100g),0)                                     AS avg_sodium_mg,
        ROUND(AVG(energy_kj_100g),0)                                     AS avg_energy_kj
    FROM products
    WHERE category <> 'Other / Unclassified'
    GROUP BY category
    HAVING COUNT(*) >= 300
)
SELECT
    RANK() OVER (ORDER BY de_pct DESC)         AS exposure_rank,
    category, products, de_pct, ab_pct,
    avg_sugar_g, avg_sodium_mg, avg_energy_kj,
    NTILE(4)   OVER (ORDER BY de_pct DESC)     AS exposure_quartile
FROM cat
ORDER BY de_pct DESC;

-- 2. Grade mix per category as a pivot (share of each grade) -----------------
SELECT
    category,
    COUNT(*)                                                    AS products,
    ROUND(100.0*SUM(CASE WHEN nutrition_grade='A' THEN 1 END)/COUNT(*),1) AS a_pct,
    ROUND(100.0*SUM(CASE WHEN nutrition_grade='B' THEN 1 END)/COUNT(*),1) AS b_pct,
    ROUND(100.0*SUM(CASE WHEN nutrition_grade='C' THEN 1 END)/COUNT(*),1) AS c_pct,
    ROUND(100.0*SUM(CASE WHEN nutrition_grade='D' THEN 1 END)/COUNT(*),1) AS d_pct,
    ROUND(100.0*SUM(CASE WHEN nutrition_grade='E' THEN 1 END)/COUNT(*),1) AS e_pct
FROM products
WHERE category <> 'Other / Unclassified'
GROUP BY category
HAVING COUNT(*) >= 300
ORDER BY e_pct DESC;

-- 3. Each category's share of all D/E products, with a running cumulative %----
--    (which categories account for the bulk of the exposure problem?)
WITH de AS (
    SELECT category, COUNT(*) AS de_products
    FROM products
    WHERE nutrition_grade IN ('D','E') AND category <> 'Other / Unclassified'
    GROUP BY category
),
tot AS (SELECT SUM(de_products) AS all_de FROM de)
SELECT
    d.category,
    d.de_products,
    ROUND(100.0*d.de_products/t.all_de,2)                               AS pct_of_all_de,
    ROUND(100.0*SUM(d.de_products) OVER (ORDER BY d.de_products DESC)
          / t.all_de, 2)                                                AS cumulative_pct
FROM de d CROSS JOIN tot t
ORDER BY d.de_products DESC;

-- 4. Categories where mean sugar exceeds the overall product mean ------------
--    (correlated subquery against the global average)
SELECT category,
       ROUND(AVG(sugars_g_100g),1) AS avg_sugar_g
FROM products p
WHERE category <> 'Other / Unclassified'
GROUP BY category
HAVING AVG(sugars_g_100g) > (SELECT AVG(sugars_g_100g) FROM products)
ORDER BY avg_sugar_g DESC;
