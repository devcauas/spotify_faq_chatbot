# scripts/scraper/extract_links.py
"""
Etapa 1: descobre os artigos da Central de Ajuda.

Começa pelas SEED_URLS e segue, em largura, os links /article/ encontrados
em cada artigo, até MAX_ARTICLES. Cada página baixada fica em cache para a
etapa 2.
"""

import json
from collections import deque
from pathlib import Path

from bs4 import BeautifulSoup

from config import BASE_URL, ARTICLE_PREFIX, SEED_URLS, MAX_ARTICLES, LINKS_FILE
from http_client import fetch


def slugify(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def article_links(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].split("#")[0].split("?")[0]
        if href.startswith(BASE_URL):
            href = href[len(BASE_URL):]
        if href.startswith(ARTICLE_PREFIX):
            links.append(BASE_URL + href.rstrip("/") + "/")
    return links


def page_title(html: str) -> str:
    h1 = BeautifulSoup(html, "html.parser").find("h1")
    return h1.get_text(" ", strip=True) if h1 else ""


def extract_links():
    fila, vistos = deque(), set()

    for seed in SEED_URLS:
        print(f"Abrindo página inicial: {seed}")
        seed_cache = "_seed_" + (seed.rstrip("/").split("/")[-1] or "home")
        for url in article_links(fetch(seed, cache_name=seed_cache)):
            if url not in vistos:
                vistos.add(url)
                fila.append(url)

    artigos = []
    while fila and len(artigos) < MAX_ARTICLES:
        url = fila.popleft()
        slug = slugify(url)
        try:
            html = fetch(url, cache_name=slug)
        except Exception as e:
            print(f"  erro em {url}: {e}")
            continue

        artigos.append({"title": page_title(html), "url": url, "slug": slug})
        print(f"[{len(artigos)}] {slug}")

        for link in article_links(html):
            if link not in vistos:
                vistos.add(link)
                fila.append(link)

    print(f"\nTotal: {len(artigos)} artigos")

    Path(LINKS_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(artigos, f, ensure_ascii=False, indent=2)

    print(f"Links salvos em: {LINKS_FILE}")
    return artigos


if __name__ == "__main__":
    extract_links()
