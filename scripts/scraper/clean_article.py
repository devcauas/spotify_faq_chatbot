# scripts/scraper/clean_article.py
"""
Recebe o HTML bruto de um artigo e devolve título + conteúdo limpo.
"""

from bs4 import BeautifulSoup

NOISE_SELECTORS = [
    "nav", "footer", "header", "script", "style",
    "[class*='cookie']", "[class*='banner']", "[class*='breadcrumb']",
]


def clean_html(html: str, url: str, fallback_title: str = "") -> dict:
    soup = BeautifulSoup(html, "html.parser")

    for selector in NOISE_SELECTORS:
        for tag in soup.select(selector):
            tag.decompose()

    titulo_tag = soup.find("h1")
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else fallback_title

    container = soup.find("main") or soup.find("article") or soup

    partes = []
    for tag in container.find_all(["h2", "h3", "p", "li"]):
        texto = tag.get_text(" ", strip=True)
        if len(texto) < 20:
            continue
        if tag.name in ("h2", "h3"):
            partes.append(f"\n## {texto}\n")
        elif tag.name == "li":
            partes.append(f"- {texto}")
        else:
            partes.append(texto)

    return {"title": titulo, "url": url, "content": "\n".join(partes).strip()}