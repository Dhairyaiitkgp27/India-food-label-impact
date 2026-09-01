-- ============================================================================
-- data_quality.sql  |  Data-quality checks run directly in SQL.
-- These mirror the Python cleaning audit and let a reviewer re-verify integrity
-- straight from the database.
-- ============================================================================

-- 1. Row counts per table -----------------------------------------------------
SELECT 'products'        AS table_name, COUNT(*) AS rows FROM products
UNION ALL SELECT 'bigbasket',        COUNT(*) FROM bigbasket
UNION ALL SELECT 'category_exposure', COUNT(*) FROM category_exposure
UNION ALL SELECT 'brand_exposure',    COUNT(*) FROM brand_exposure;

-- 2. Grade completeness: every product must carry a valid A-E grade ----------
SELECT
    COUNT(*)                                                        AS total,
    SUM(CASE WHEN nutrition_grade IN ('A','B','C','D','E') THEN 1 END) AS valid_grade,
    SUM(CASE WHEN nutrition_grade NOT IN ('A','B','C','D','E')
             OR nutrition_grade IS NULL THEN 1 END)                AS invalid_grade
FROM products;

-- 3. Nutrient plausibility: nothing outside physical bounds should remain -----
SELECT
    SUM(CASE WHEN sugars_g_100g  < 0 OR sugars_g_100g  > 100  THEN 1 ELSE 0 END) AS bad_sugar,
    SUM(CASE WHEN salt_g_100g    < 0 OR salt_g_100g    > 100  THEN 1 ELSE 0 END) AS bad_salt,
    SUM(CASE WHEN energy_kj_100g < 0 OR energy_kj_100g > 3900 THEN 1 ELSE 0 END) AS bad_energy,
    SUM(CASE WHEN sugars_g_100g > carbohydrates_g_100g + 0.5  THEN 1 ELSE 0 END) AS sugar_gt_carbs
FROM products;

-- 4. Category coverage: share of products that were classified ----------------
SELECT
    ROUND(100.0 * SUM(CASE WHEN category <> 'Other / Unclassified' THEN 1 END)
          / COUNT(*), 2)                                          AS pct_classified,
    COUNT(DISTINCT category)                                      AS n_categories
FROM products;

-- 5. Duplicate guard: (product_name, brand) should be unique post-clean -------
SELECT COUNT(*) AS duplicate_key_groups
FROM (
    SELECT product_name, brand_clean, COUNT(*) AS c
    FROM products
    GROUP BY product_name, brand_clean
    HAVING c > 1
);

-- 6. BigBasket price sanity: sale price must be positive and <= market price ---
SELECT
    SUM(CASE WHEN sale_price <= 0 THEN 1 ELSE 0 END)                 AS non_positive_price,
    SUM(CASE WHEN sale_price > market_price + 0.01 THEN 1 ELSE 0 END) AS sale_gt_market
FROM bigbasket;
