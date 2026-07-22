# scripts/scraper/extract_links.py
"""
Etapa 1: extrai título + URL de cada artigo da categoria escolhida.
"""

import json
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from config import CATEGORY_URL, LINKS_FILE, HEADLESS, WAIT_TIME


def slugify(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def extract_links():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()

        print(f"Abrindo categoria: {CATEGORY_URL}")
        page.goto(CATEGORY_URL, timeout=60000)
        page.wait_for_timeout(WAIT_TIME)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    artigos, seen = [], set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        texto = a.get_text(" ", strip=True)

        if "/article/" not in href:
            continue
        if href.startswith("/"):
            href = "https://support.spotify.com" + href
        if href in seen:
            continue
        seen.add(href)

        artigos.append({"title": texto, "url": href, "slug": slugify(href)})

    print(f"{len(artigos)} artigos encontrados")

    Path(LINKS_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(artigos, f, ensure_ascii=False, indent=2)

    print(f"Links salvos em: {LINKS_FILE}")
    return artigos


if __name__ == "__main__":
    extract_links()