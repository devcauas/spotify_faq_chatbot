# scripts/scraper/download_articles.py
"""
Etapa 2: baixa cada artigo (via extract_links.py), limpa (clean_article.py)
e grava o .md (save_markdown.py).
"""

import json
from playwright.sync_api import sync_playwright

from config import LINKS_FILE, HEADLESS
from clean_article import clean_html
from save_markdown import save_article_as_markdown


def download_and_process():
    with open(LINKS_FILE, encoding="utf-8") as f:
        artigos = json.load(f)

    print(f"{len(artigos)} artigos para baixar")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()

        for i, artigo in enumerate(artigos):
            url = artigo["url"]
            print(f"[{i+1}/{len(artigos)}] {url}")
            try:
                page.goto(url, timeout=60000)
                page.wait_for_timeout(3000)
                html = page.content()

                data = clean_html(html, url=url, fallback_title=artigo["title"])
                if not data["content"]:
                    print(f"  ⚠️ sem conteúdo, pulando: {url}")
                    continue

                save_article_as_markdown(data, slug=artigo["slug"])
            except Exception as e:
                print(f"  ❌ erro em {url}: {e}")
                continue

        browser.close()

    print("Finalizado")


if __name__ == "__main__":
    download_and_process()