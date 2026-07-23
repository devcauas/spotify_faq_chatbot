# scripts/scraper/clean_article.py
"""
Recebe o HTML bruto de um artigo e devolve título + conteúdo limpo.
"""

from bs4 import BeautifulSoup

NOISE_SELECTORS = [
    "nav", "footer", "header", "script", "style",
    "[class*='cookie']", "[class*='banner']", "[class*='breadcrumb']",
]

# Frases de boilerplate do próprio site do Spotify que não são conteúdo de FAQ
NOISE_PHRASES = [
    "você está usando uma ferramenta baseada em ia",
    "isso foi útil",
    "artigos relacionados",
]


def is_noise(texto: str) -> bool:
    texto_lower = texto.lower().strip()
    return any(frase in texto_lower for frase in NOISE_PHRASES)

def clean_html(html: str, url: str, fallback_title: str = "", category: str = "") -> dict:
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

        if is_noise(texto):
            continue

        if tag.name in ("h2", "h3"):
            # Headers de seção não devem ser descartados por serem curtos
            # (ex: "Wi-Fi", "Login", "Premium" são headers válidos com < 20 chars).
            # O ## é o separador que o text_splitter usa para respeitar
            # fronteiras semânticas no chunking, então precisa sobreviver.
            if not texto:
                continue
            partes.append(f"\n## {texto}\n")
        else:
            # Para parágrafos e itens de lista, texto curto costuma ser
            # ruído (ex: "Compartilhar", "Saiba mais"), então o filtro
            # de tamanho continua fazendo sentido aqui.
            if len(texto) < 20:
                continue
            if tag.name == "li":
                partes.append(f"- {texto}")
            else:
                partes.append(texto)

    return {
        "title": titulo,
        "url": url,
        "category": category,
        "content": "\n".join(partes).strip(),
    }