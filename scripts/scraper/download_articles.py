# scripts/scraper/download_articles.py
"""
Etapa 2: lê cada artigo (do cache da etapa 1, ou da web), limpa
(clean_article.py) e grava o .md (save_markdown.py).
"""

import json
import shutil
from pathlib import Path

from config import LINKS_FILE, MARKDOWN_DIR
from clean_article import clean_html
from http_client import fetch
from save_markdown import save_article_as_markdown


def download_and_process():
    with open(LINKS_FILE, encoding="utf-8") as f:
        artigos = json.load(f)

    print(f"{len(artigos)} artigos para processar")

    # Recria a pasta para não sobrar .md de uma coleta anterior
    shutil.rmtree(MARKDOWN_DIR, ignore_errors=True)
    Path(MARKDOWN_DIR).mkdir(parents=True)

    salvos = 0
    for artigo in artigos:
        url = artigo["url"]
        try:
            html = fetch(url, cache_name=artigo["slug"])
            data = clean_html(html, url=url, fallback_title=artigo["title"])
            if not data["content"]:
                print(f"  sem conteúdo, pulando: {url}")
                continue

            save_article_as_markdown(data, slug=artigo["slug"])
            salvos += 1
        except Exception as e:
            print(f"  erro em {url}: {e}")
            continue

    print(f"Finalizado: {salvos} artigos salvos em {MARKDOWN_DIR}")


if __name__ == "__main__":
    download_and_process()
