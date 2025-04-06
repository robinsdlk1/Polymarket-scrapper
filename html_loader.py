from playwright.sync_api import sync_playwright
import sys
import os

# Vérification des arguments
if len(sys.argv) < 2:
    print("Usage: python3 scrape_polymarket_body.py <market_slug>")
    sys.exit(1)

slug = sys.argv[1]
url = f"https://polymarket.com/market/{slug}"

base_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(base_dir, "db/html/polymarket_loaded_source.html")

with sync_playwright() as p:
    browser = p.chromium.launch(headless = True)
    page = browser.new_page()
    page.goto(url, wait_until = "networkidle")
    body_content = page.inner_html("body")
    with open(output_file, "w", encoding = "utf-8") as f:
        f.write(body_content)
    browser.close()
