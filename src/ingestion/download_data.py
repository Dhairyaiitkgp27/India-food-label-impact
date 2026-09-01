"""
Reproducible download of the two REAL public datasets used in this project.

Both are mirrored on public GitHub repositories, which makes the download
deterministic and firewall-friendly (no scraping, no API keys). Provenance and
licensing are documented in docs/sources.md.

    Dataset 1  Open Food Facts branded-product export (nutrition + official
               Nutri-Score). ~257k products.
               Upstream: https://world.openfoodfacts.org  (Open Database License)
               Mirror  : github.com/adadntla/OpenFoodFacts-Nutrition-Analysis

    Dataset 2  BigBasket product catalogue (Indian grocery: brand, category,
               sub-category, price). ~27.5k SKUs.
               Upstream: BigBasket.com product listing (public catalogue)
               Mirror  : github.com/Sumaiyyaustad/MarketMetrics-...-FMCG-Pricing-Trends

Run:
    python -m src.ingestion.download_data
"""
from __future__ import annotations
import sys
import urllib.request
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src import config  # noqa: E402

SOURCES = [
    (
        "Open Food Facts (nutrition + Nutri-Score)",
        "https://raw.githubusercontent.com/adadntla/OpenFoodFacts-Nutrition-Analysis/"
        "main/Final_OpenFoodFacts_Clean.csv",
        config.OFF_RAW,
    ),
    (
        "BigBasket Indian product catalogue (brand/category/price)",
        "https://raw.githubusercontent.com/Sumaiyyaustad/"
        "MarketMetrics-Analyzing-Grocery-FMCG-Pricing-Trends/main/"
        "Data/BigBasket%20Products.csv",
        config.BB_RAW,
    ),
]


def download(name: str, url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"[skip] {name}: already present ({dest.stat().st_size/1e6:.1f} MB)")
        return
    print(f"[get ] {name}\n       {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "india-food-label-impact"})
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
        f.write(r.read())
    print(f"       -> {dest}  ({dest.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    for name, url, dest in SOURCES:
        download(name, url, dest)
    print("\nDone. Raw data in", config.RAW)
