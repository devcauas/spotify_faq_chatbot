# scripts/scraper/extract_links.py
"""
Etapa 1: extrai título + URL de cada artigo de TODAS as categorias configuradas.
"""

import json
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from config import CATEGORY_URLS, LINKS_FILE, HEADLESS, WAIT_TIME


def slugify(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def extract_links_from_category(page, category_url: str):
    print(f"Abrindo categoria: {category_url}")
    page.goto(category_url, timeout=60000)
    page.wait_for_timeout(WAIT_TIME)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    category_slug = category_url.rstrip("/").split("/")[-1]

    artigos = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        texto = a.get_text(" ", strip=True)

        if "/article/" not in href:
            continue
        if href.startswith("/"):
            href = "https://support.spotify.com" + href

        artigos.append({
            "title": texto,
            "url": href,
            "slug": slugify(href),
            "category": category_slug,
        })

    return artigos


def extract_links():
    todos_artigos, seen = [], set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()

        for category_url in CATEGORY_URLS:
            artigos = extract_links_from_category(page, category_url)
            novos = 0
            for artigo in artigos:
                if artigo["url"] in seen:
                    continue
                seen.add(artigo["url"])
                todos_artigos.append(artigo)
                novos += 1
            print(f"  → {novos} artigos novos ({len(artigos) - novos} duplicados ignorados)")

        browser.close()

    print(f"\nTotal: {len(todos_artigos)} artigos únicos encontrados")

    Path(LINKS_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(todos_artigos, f, ensure_ascii=False, indent=2)

    print(f"Links salvos em: {LINKS_FILE}")
    return todos_artigos


if __name__ == "__main__":
    extract_links()