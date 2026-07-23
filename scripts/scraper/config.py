# scripts/scraper/config.py

CATEGORY_URLS = [
    "https://support.spotify.com/br-pt/category/payment-help/",
]

RAW_DIR = "data/raw"
LINKS_FILE = f"{RAW_DIR}/links.json"

MARKDOWN_DIR = "data/faq_documents"

HEADLESS = True
WAIT_TIME = 4000