# Power BI — DAX Measures

Paste these into the `_Measures` table. They are grouped by dashboard page.
Column references match the exported CSVs.

## Core exposure

```DAX
Total Products = COUNTROWS ( fact_products )

D/E Products =
CALCULATE ( [Total Products], fact_products[nutrition_grade] IN { "D", "E" } )

A/B Products =
CALCULATE ( [Total Products], fact_products[nutrition_grade] IN { "A", "B" } )

D/E Exposure % =
DIVIDE ( [D/E Products], [Total Products] )

A/B Favourable % =
DIVIDE ( [A/B Products], [Total Products] )

Avg Nutrition Score =            -- 1 = A (best) .. 5 = E (worst)
AVERAGE ( fact_products[nutrition_score] )
```

## Nutrient measures

```DAX
Avg Sugar (g/100g)  = AVERAGE ( fact_products[sugars_g_100g] )
Avg Sodium (mg/100g)= AVERAGE ( fact_products[sodium_mg_100g] )
Avg Energy (kJ/100g)= AVERAGE ( fact_products[energy_kj_100g] )

High-Sugar Products =            -- top-decile threshold is data-driven
VAR Cutoff =
    PERCENTILEX.INC ( ALL ( fact_products ), fact_products[sugars_g_100g], 0.9 )
RETURN
    CALCULATE ( [Total Products], fact_products[sugars_g_100g] >= Cutoff )
```

## Category / brand ranking

```DAX
Category D/E Rank =
IF (
    HASONEVALUE ( dim_category[category] ),
    RANKX ( ALL ( dim_category[category] ), [D/E Exposure %],, DESC )
)

Brand D/E Rank =
IF (
    HASONEVALUE ( dim_brand[brand_clean] ),
    RANKX ( ALL ( dim_brand[brand_clean] ), [D/E Exposure %],, DESC )
)

-- Only rank brands above a minimum size (mirrors the analysis threshold)
Brand D/E % (min 80) =
IF ( [Total Products] >= 80, [D/E Exposure %] )
```

## Business-risk page (pre-computed in `dim_category`)

```DAX
Business Risk = AVERAGE ( dim_category[business_risk] )

Nutrition Exposure = AVERAGE ( dim_category[nutrition_exposure] )
Consumer Sensitivity = AVERAGE ( dim_category[consumer_sensitivity] )
Commercial Importance = AVERAGE ( dim_category[commercial_importance] )

Risk Rank =
RANKX ( ALL ( dim_category[category] ), [Business Risk],, DESC )
```

## Scenario page (with a what-if parameter)

Create a numeric what-if parameter **Switch Rate** (0.00–0.30, step 0.02), then:

```DAX
At-Risk D/E SKUs =
SUM ( fact_scenario[at_risk_de_skus] )        -- pre-computed per scenario

Revenue Exposure Index (0-100) =
AVERAGE ( fact_scenario[revenue_exposure_index_0_100] )

Reformulation Priority (0-100) =
AVERAGE ( fact_scenario[reformulation_priority_0_100] )

-- Live recompute driven by the slider instead of the stored scenario:
At-Risk SKUs (live) =
SUMX (
    VALUES ( dim_category[category] ),
    VAR de   = CALCULATE ( [D/E Products] )
    VAR sens = CALCULATE ( AVERAGE ( dim_category[consumer_sensitivity] ) )
    RETURN de * sens * [Switch Rate Value]
)
```

## Price-vs-nutrition page

```DAX
Median Price (INR) = AVERAGE ( price_vs_nutrition[median_price_inr] )
Nutrition Badness (1-5) = AVERAGE ( price_vs_nutrition[avg_score] )

Price-Nutrition Correlation =    -- Pearson r across categories
VAR t = SUMMARIZE ( price_vs_nutrition, price_vs_nutrition[category],
        "x", [Median Price (INR)], "y", [Nutrition Badness (1-5)] )
VAR n = COUNTROWS ( t )
VAR sx = SUMX ( t, [x] )  VAR sy = SUMX ( t, [y] )
VAR sxy = SUMX ( t, [x] * [y] )
VAR sx2 = SUMX ( t, [x] ^ 2 )  VAR sy2 = SUMX ( t, [y] ^ 2 )
RETURN DIVIDE ( n * sxy - sx * sy,
        SQRT ( ( n * sx2 - sx ^ 2 ) * ( n * sy2 - sy ^ 2 ) ) )
```

## Formatting helpers

```DAX
Exposure Colour =                -- for conditional formatting
SWITCH ( TRUE (),
    [D/E Exposure %] >= 0.6, "#C0392B",   -- red
    [D/E Exposure %] >= 0.4, "#E67E22",   -- amber
    "#27AE60" )                            -- green
```
