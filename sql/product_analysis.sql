-- ============================================================================
-- product_analysis.sql  |  Product-level deep dives.
-- Window functions, percentile buckets, CASE segmentation, subqueries.
-- ============================================================================

-- 1. Top-20 highest-sugar products (with their grade and brand) --------------
SELECT
    ROW_NUMBER() OVER (ORDER BY sugars_g_100g DESC) AS rnk,
    product_name, brand_clean, category, nutrition_grade,
    sugars_g_100g, energy_kj_100g
FROM products
WHERE sugars_g_100g IS NOT NULL
ORDER BY sugars_g_100g DESC
LIMIT 20;

-- 2. Top-20 highest-sodium products ------------------------------------------
SELECT
    ROW_NUMBER() OVER (ORDER BY sodium_mg_100g DESC) AS rnk,
    product_name, brand_clean, category, nutrition_grade, sodium_mg_100g
FROM products
WHERE sodium_mg_100g IS NOT NULL
ORDER BY sodium_mg_100g DESC
LIMIT 20;

-- 3. "Health halo" check: A/B products that still carry high sugar -----------
--    products rated favourably but sitting in the top sugar decile.
WITH decile AS (
    SELECT product_name, brand_clean, category, nutrition_grade, sugars_g_100g,
           NTILE(10) OVER (ORDER BY sugars_g_100g) AS sugar_decile
    FROM products WHERE sugars_g_100g IS NOT NULL
)
SELECT category, COUNT(*) AS favourable_but_high_sugar
FROM decile
WHERE sugar_decile = 10 AND nutrition_grade IN ('A','B')
GROUP BY category
ORDER BY favourable_but_high_sugar DESC
LIMIT 15;

-- 4. Nutrient profile by grade (does the grade behave as expected?) ----------
SELECT
    nutrition_grade,
    COUNT(*)                     AS products,
    ROUND(AVG(energy_kj_100g),0) AS avg_energy_kj,
    ROUND(AVG(sugars_g_100g),1)  AS avg_sugar_g,
    ROUND(AVG(sodium_mg_100g),0) AS avg_sodium_mg,
    ROUND(AVG(proteins_g_100g),1) AS avg_protein_g
FROM products
GROUP BY nutrition_grade
ORDER BY nutrition_grade;

-- 5. Reformulation shortlist: grade-D products closest to the C boundary ------
--    (grade D with relatively modest sugar - "quick wins" for reformulation).
SELECT product_name, brand_clean, category, sugars_g_100g, sodium_mg_100g, energy_kj_100g
FROM products
WHERE nutrition_grade = 'D'
  AND sugars_g_100g < (SELECT AVG(sugars_g_100g) FROM products WHERE nutrition_grade='D')
  AND sodium_mg_100g < (SELECT AVG(sodium_mg_100g) FROM products WHERE nutrition_grade='D')
ORDER BY energy_kj_100g ASC
LIMIT 20;

-- 6. Segmentation: label every product Green/Amber/Red and count ------------
SELECT
    CASE WHEN nutrition_grade IN ('A','B') THEN 'Green / Favourable'
         WHEN nutrition_grade = 'C'        THEN 'Amber / Intermediate'
         ELSE 'Red / Exposed' END          AS rating_band,
    COUNT(*)                               AS products,
    ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM products),1) AS pct
FROM products
GROUP BY rating_band
ORDER BY products DESC;
