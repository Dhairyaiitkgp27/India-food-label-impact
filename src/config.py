"""
Central configuration for the India Packaged Food Label Impact project.

Everything that multiple pipeline stages need lives here: filesystem paths,
the official Nutri-Score (2017) point tables, nutrient plausibility bounds used
in cleaning, and the keyword taxonomy used to derive food categories from
Open Food Facts product names.

No numbers in this project are invented. This file only contains (a) paths and
(b) the *published* Nutri-Score algorithm constants, which are sourced from
Santé publique France's official method (see reports/methodology.md for the
citation). All empirical results are computed from the real datasets at runtime.
"""
from __future__ import annotations
from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data"
RAW = DATA / "raw"
CLEANED = DATA / "cleaned"
FINAL = DATA / "final"
CONSUMER = DATA / "consumer_evidence"

DATABASE = ROOT / "database" / "food_market.db"
REPORTS = ROOT / "reports"
POWERBI = ROOT / "powerbi"
DOCS = ROOT / "docs"

# Raw inputs (real, publicly sourced -- see docs/sources.md)
OFF_RAW = RAW / "openfoodfacts_products_raw.csv"
BB_RAW = RAW / "bigbasket_products_raw.csv"

# Cleaned outputs
OFF_CLEAN = CLEANED / "cleaned_food_products.csv"
BB_CLEAN = CLEANED / "cleaned_bigbasket_products.csv"

# Final analytical outputs
OFF_FINAL = FINAL / "food_market_analytics.csv"
CATEGORY_FINAL = FINAL / "category_exposure.csv"
BRAND_FINAL = FINAL / "brand_exposure.csv"
SCENARIO_FINAL = FINAL / "scenario_results.csv"

# Machine-readable metrics store (every figure quoted in the reports is written
# here by the pipeline so the reports can be regenerated / audited).
METRICS_JSON = REPORTS / "computed_metrics.json"

for _d in (RAW, CLEANED, FINAL, CONSUMER, REPORTS, POWERBI, DOCS, DATABASE.parent):
    _d.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# Nutrient plausibility bounds (per 100 g / 100 ml)
# Used to flag physically impossible values in the raw Open Food Facts export.
# Bounds are deliberately generous -- they only catch data-entry errors, not
# legitimately extreme (but possible) products.
# --------------------------------------------------------------------------- #
NUTRIENT_BOUNDS = {
    # column: (min_allowed, max_allowed)
    "energy_100g": (0, 3900),        # kJ. Pure fat ~3700 kJ/100g; >3900 is impossible.
    "fat_100g": (0, 100),            # g per 100 g cannot exceed 100
    "carbohydrates_100g": (0, 100),
    "sugars_100g": (0, 100),
    "proteins_100g": (0, 100),
    "salt_100g": (0, 100),           # g per 100 g cannot exceed 100
}
# Sugars cannot exceed carbohydrates; used as an additional consistency rule.

# --------------------------------------------------------------------------- #
# Nutri-Score 2017 official point tables (general foods)
# Source: Santé publique France, "Nutri-Score: Frequently Asked Questions"
# and the scientific method note. Reproduced in reports/methodology.md.
#
# Negative ("N") points come from energy, sugars, saturated fat and sodium.
# Positive ("P") points come from fruit/veg/legumes/nuts %, fibre and protein.
# Final score = N - P, then mapped to a letter grade A-E.
# --------------------------------------------------------------------------- #

# Each list is a set of upper thresholds; the index (0..10) is the points awarded.
# A value strictly greater than threshold[i] scores at least i+1 points.
NUTRISCORE_NEGATIVE = {
    # energy in kJ/100g
    "energy_kj": [335, 670, 1005, 1340, 1675, 2010, 2345, 2680, 3015, 3350],
    # sugars in g/100g
    "sugars_g": [4.5, 9, 13.5, 18, 22.5, 27, 31, 36, 40, 45],
    # saturated fat in g/100g
    "sat_fat_g": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    # sodium in mg/100g
    "sodium_mg": [90, 180, 270, 360, 450, 540, 630, 720, 810, 900],
}

NUTRISCORE_POSITIVE = {
    # fruit/veg/legume/nut % -> 0,1,2,5 points at 40/60/80 cutoffs (special rule)
    "fvln_pct": [40, 60, 80],  # >40 ->1, >60 ->2, >80 ->5
    # fibre in g/100g (AOAC)
    "fibre_g": [0.9, 1.9, 2.8, 3.7, 4.7],
    # protein in g/100g
    "protein_g": [1.6, 3.2, 4.8, 6.4, 8.0],
}

# Grade cut-offs for general foods (score = N - P), official 2017 thresholds
NUTRISCORE_GRADE_BOUNDS = [
    ("A", -float("inf"), -1),  # score <= -1
    ("B", 0, 2),               # 0..2
    ("C", 3, 10),              # 3..10
    ("D", 11, 18),             # 11..18
    ("E", 19, float("inf")),   # >= 19
]

GRADE_ORDER = ["A", "B", "C", "D", "E"]

# --------------------------------------------------------------------------- #
# Category taxonomy derived from product names (Open Food Facts has no usable
# category column in this export, so categories are engineered from the product
# name text). Order matters: the first matching bucket wins, so more specific /
# higher-signal buckets are listed before generic ones. This is a transparent,
# rule-based classifier (documented in docs/methodology). % classified is
# reported in the data-quality report.
# --------------------------------------------------------------------------- #
CATEGORY_KEYWORDS = [
    ("Chocolate & Confectionery",
     ["chocolate", "chocolat", "choco ", "cocoa", "candy", "candies", "gummy",
      "gummies", "lollipop", "toffee", "fudge", "marshmallow", "nougat",
      "praline", "truffle", "caramel", "licorice", "liquorice", "mint ",
      "mints", "bonbon", "kitkat", "kit kat", "snickers", "twix", "m&m",
      "hershey", "reese", "milka", "ferrero", "dairy milk", "gems", "eclair",
      "confiserie", "dragee"]),
    ("Biscuits, Cookies & Wafers",
     ["biscuit", "cookie", "cookies", "wafer", "gaufrette", "cracker",
      "crackers", "shortbread", "digestive", "rusk", "graham", "oreo",
      "bourbon", "marie ", "cream biscuit", "petit beurre", "sable"]),
    ("Cakes, Pastries & Sweet Bakery",
     ["cake", "gateau", "brownie", "muffin", "donut", "doughnut", "croissant",
      "pastry", "patisserie", "pie ", " pie", "tarte", "tart", "cupcake",
      "waffle", "gaufre", "pancake", "danish", "cinnamon roll", "swiss roll",
      "madeleine", "brioche"]),
    ("Chips, Crisps & Salty Snacks",
     ["chips", "crisps", "popcorn", "pretzel", "nachos", "tortilla",
      "namkeen", "bhujia", "sev ", "mixture", "snack mix", "puffs",
      "kurkure", "lays", "pringles", "doritos", "cheetos", "papad",
      "murukku", "chakli", "mathri", "potato snack", "aperitif", "apero",
      "souffle sale"]),
    ("Sugar-Sweetened Beverages",
     ["soda", "cola", "soft drink", "energy drink", "sports drink",
      "lemonade", "limonade", "fruit drink", "squash", "cordial",
      "coca-cola", "pepsi", "sprite", "fanta", "mountain dew", "red bull",
      "gatorade", "frooti", "maaza", "thums up", "tonic water", "iced tea",
      "soft-drink", "boisson gazeuse", "boisson sucree"]),
    ("Juices & Nectars",
     ["juice", "jus ", "nectar", "smoothie", "fruit punch", "compote"]),
    ("Water & Unsweetened Drinks",
     ["water", "eau ", "sparkling water", "mineral water", "seltzer",
      "black coffee", "unsweetened tea", "green tea"]),
    ("Breakfast Cereals & Muesli",
     ["cereal", "cereale", "corn flakes", "cornflakes", "muesli", "granola",
      "oats", "oatmeal", "porridge", "wheat flakes", "chocos", "weetabix",
      "breakfast bar", "flocons"]),
    ("Instant Noodles, Pasta & Soups",
     ["noodle", "noodles", "pasta", "pate ", "spaghetti", "macaroni",
      "vermicelli", "ramen", "maggi", "soup", "soupe", "potage", "instant soup",
      "cup noodle", "penne", "lasagne", "lasagna", "fusilli", "tagliatelle"]),
    ("Sauces, Ketchup & Condiments",
     ["ketchup", "sauce", "mayonnaise", "mayo", "mustard", "moutarde",
      "dressing", "vinegar", "vinaigre", "chutney", "relish", "salsa",
      "gravy", "marinade", "seasoning", "assaisonnement", "passata",
      "sriracha", "soy sauce", "coulis"]),
    ("Spreads, Jam, Honey & Syrups",
     ["jam ", "jelly", "marmalade", "marmelade", "confiture", "honey", "miel",
      "syrup", "sirop", "peanut butter", "nut butter", "hazelnut spread",
      "nutella", "spread", "pate a tartiner", "preserve"]),
    ("Ice Cream & Frozen Desserts",
     ["ice cream", "ice-cream", "glace ", "gelato", "sorbet", "frozen dessert",
      "kulfi", "popsicle", "frozen yogurt", "frozen yoghurt", "creme glacee"]),
    ("Cheese",
     ["cheese", "fromage", "cheddar", "mozzarella", "parmesan", "gouda",
      "brie", "paneer", "feta", "ricotta", "cream cheese", "camembert",
      "emmental", "chevre"]),
    ("Yogurt & Dairy Drinks",
     ["yogurt", "yoghurt", "yaourt", "curd", "lassi", "buttermilk", "dahi",
      "milkshake", "flavoured milk", "flavored milk", "dairy drink",
      "drinkable yogurt", "fromage blanc", "petit suisse"]),
    ("Milk, Butter & Cream",
     ["milk", "lait", "butter", "beurre", "cream", "creme", "ghee",
      "condensed milk", "milk powder", "khoya", "dairy whitener"]),
    ("Bread & Savoury Bakery",
     ["bread", "pain ", "bun ", "buns", "bagel", "baguette", "roll ", "rolls",
      "pita", "naan", "tortilla wrap", "flatbread", "loaf", "biscotte"]),
    ("Ready Meals & Frozen Foods",
     ["ready meal", "plat cuisine", "frozen", "surgele", "microwave", "pizza",
      "burger", "nugget", "nuggets", "cutlet", "samosa", "spring roll",
      "paratha", "tikka", "curry", "biryani", "instant meal", "heat and eat",
      "ready to eat", "ready-to-eat", "fries", "frites", "patty", "patties",
      "quiche", "raviolis"]),
    ("Processed Meat & Seafood",
     ["sausage", "saucisse", "saucisson", "bacon", "ham ", "jambon", "salami",
      "pepperoni", "hot dog", "meat", "viande", "chicken", "poulet", "mutton",
      "beef", "boeuf", "poultry", "dinde", "canard", "fish", "poisson",
      "tuna", "thon", "prawn", "shrimp", "crevette", "kebab", "jerky",
      "cold cut", "charcuterie", "canned fish", "sardine", "lardons"]),
    ("Nuts, Seeds & Dried Fruit",
     ["almond", "amande", "cashew", "walnut", "noix", "pistachio", "pistache",
      "peanut", "cacahuete", "raisin", "trail mix", "dried fruit",
      "fruits secs", "dates", "seeds", "graines", "makhana", "mixed nuts",
      "roasted nuts", "noisette"]),
    ("Fruits & Vegetables (packaged/plain)",
     ["pomme", "apple", "orange", "banana", "banane", "tomato", "tomate",
      "legume", "vegetable", "carrot", "carotte", "potato", "pea ", "peas",
      "petits pois", "spinach", "epinard", "onion", "oignon", "mango",
      "grape", "raisin sec", "berry", "salad", "salade", "haricot vert",
      "champignon", "mushroom", "courgette", "poivron", "fruit "]),
    ("Sugar, Sweeteners & Baking",
     ["sugar", "jaggery", "gur ", "sweetener", "baking", "icing",
      "cocoa powder", "custard powder", "dessert mix", "jelly crystals"]),
    ("Edible Oils & Fats",
     ["olive oil", "sunflower oil", "vegetable oil", "cooking oil",
      "mustard oil", "coconut oil", "refined oil", "canola", "margarine"]),
    ("Staples: Flour, Rice, Pulses & Grains",
     ["flour", "atta", "maida", "besan", "rice", "wheat", "dal ", "lentil",
      "pulses", "quinoa", "millet", "semolina", "suji", "rava", "poha",
      "chickpea", "kidney bean", "grain"]),
    ("Protein, Diet & Nutrition Bars",
     ["protein bar", "energy bar", "granola bar", "nutrition bar",
      "meal replacement", "protein powder", "whey", "dietary supplement",
      "protein shake"]),
    ("Tea, Coffee & Hot Drink Mixes",
     ["tea ", "coffee", "cappuccino", "latte", "hot chocolate",
      "drinking chocolate", "malt drink", "health drink", "horlicks",
      "bournvita", "boost"]),
    ("Baby & Infant Food",
     ["baby food", "infant", "cerelac", "formula milk", "baby cereal",
      "toddler"]),
    ("Pickles & Preserved Vegetables",
     ["pickle", "achar", "olives", "gherkin", "preserved vegetable",
      "canned vegetable", "canned bean"]),
]

# BigBasket top-level categories that are actually FOOD (used to filter out
# non-food SKUs such as cleaning products, beauty, kitchenware, pet care).
BB_FOOD_CATEGORIES = {
    "Snacks & Branded Foods",
    "Foodgrains, Oil & Masala",
    "Bakery, Cakes & Dairy",
    "Beverages",
    "Gourmet & World Food",
    "Eggs, Meat & Fish",
    "Fruits & Vegetables",
}

# Map BigBasket food categories -> the OFF-style analytical categories so the
# two sources can be harmonised at category level. This is a coarse, documented
# mapping (many-to-one); see reports/methodology.md.
BB_TO_ANALYTICAL = {
    "Snacks & Branded Foods": "Packaged Snacks & Confectionery (composite)",
    "Beverages": "Beverages (composite)",
    "Bakery, Cakes & Dairy": "Bakery & Dairy (composite)",
    "Foodgrains, Oil & Masala": "Staples, Oil & Masala (composite)",
    "Gourmet & World Food": "Gourmet & World Food (composite)",
    "Eggs, Meat & Fish": "Eggs, Meat & Fish (composite)",
    "Fruits & Vegetables": "Fruits & Vegetables (composite)",
}

UNCLASSIFIED = "Other / Unclassified"
