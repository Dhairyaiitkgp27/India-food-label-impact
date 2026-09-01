-- ============================================================================
-- schema.sql  |  India Packaged Food Label Impact & Market Analytics
-- Reference schema for database/food_market.db (built by database/build_database.py).
-- SQLite dialect.
-- ============================================================================

-- Product-level nutrition and authoritative Nutri-Score grade (Open Food Facts).
-- ~220k graded packaged-food products.
CREATE TABLE IF NOT EXISTS products (
    product_name           TEXT,
    brand_clean            TEXT,      -- normalised brand
    category               TEXT,      -- engineered from product name (28-bucket taxonomy)
    nutrition_grade        TEXT,      -- authoritative official Nutri-Score A..E
    rating_category        TEXT,      -- Green/Favourable | Amber/Intermediate | Red/Exposed
    nutrition_score        INTEGER,   -- 1=A(best) .. 5=E(worst)
    nutrition_score_computed INTEGER, -- from-scratch re-implementation (validation only)
    energy_kj_100g         REAL,
    fat_g_100g             REAL,
    carbohydrates_g_100g   REAL,
    sugars_g_100g          REAL,
    proteins_g_100g        REAL,
    salt_g_100g            REAL,
    sodium_mg_100g         REAL,      -- derived: salt_g * 400
    energy_outlier_flag    INTEGER    -- 1 if energy above IQR upper fence (kept, flagged)
);

-- Indian grocery catalogue (BigBasket): brand, category, price. No nutrition.
CREATE TABLE IF NOT EXISTS bigbasket (
    product              TEXT,
    brand_clean          TEXT,
    category             TEXT,
    sub_category         TEXT,
    analytical_category  TEXT,
    sale_price           REAL,        -- INR
    market_price         REAL,        -- INR (list price)
    discount_pct         REAL,
    rating               REAL
);

-- Pre-aggregated analytical outputs (materialised from the Python pipeline).
CREATE TABLE IF NOT EXISTS category_exposure (
    category TEXT, products INTEGER, de_pct REAL, ab_pct REAL,
    avg_score REAL, avg_sugar_g REAL, avg_sodium_mg REAL,
    avg_satfat_proxy_fat_g REAL, avg_energy_kj REAL
);

CREATE TABLE IF NOT EXISTS brand_exposure (
    brand_clean TEXT, products INTEGER, ab_pct REAL, c_pct REAL,
    de_pct REAL, avg_score REAL
);

CREATE TABLE IF NOT EXISTS price_vs_nutrition (
    category TEXT, off_products INTEGER, de_pct REAL, avg_score REAL,
    avg_sugar_g REAL, bb_skus INTEGER, median_price_inr REAL, mean_price_inr REAL
);

CREATE TABLE IF NOT EXISTS category_business_risk (
    category TEXT, de_pct REAL, nutrition_exposure REAL, consumer_sensitivity REAL,
    commercial_importance REAL, business_risk REAL, business_risk_alt REAL
);

CREATE TABLE IF NOT EXISTS scenario_results (
    category TEXT, off_products INTEGER, de_products INTEGER, de_share REAL,
    d_products INTEGER, e_products INTEGER, commercial_importance REAL,
    consumer_sensitivity REAL, effective_switch_rate REAL, at_risk_de_skus REAL,
    revenue_exposure_index REAL, fixable_share_of_de REAL, reformulation_priority REAL,
    scenario TEXT, revenue_exposure_index_0_100 REAL, reformulation_priority_0_100 REAL
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_products_cat   ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_grade ON products(nutrition_grade);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand_clean);
CREATE INDEX IF NOT EXISTS idx_bb_cat         ON bigbasket(category);
CREATE INDEX IF NOT EXISTS idx_bb_brand       ON bigbasket(brand_clean);
