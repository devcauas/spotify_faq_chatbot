# scripts/scraper/clean_article.py
"""
Recebe o HTML bruto de um artigo e devolve título + conteúdo limpo.

O corpo do artigo vem logo depois do <h1>. Tudo o que vem a partir de
"Artigos relacionados" (lista de links e o menu da categoria) é navegação
do site, não conteúdo: antes isso entrava no .md e vazava para as
respostas do chatbot como uma lista de títulos solta.
"""

import re

from bs4 import BeautifulSoup

# Seções que marcam o fim do conteúdo do artigo
END_MARKERS = ("artigos relacionados", "assuntos recomendados")

# Frases de boilerplate do próprio site do Spotify que não são conteúdo de FAQ
NOISE_PHRASES = (
    "você está usando uma ferramenta baseada em ia",
    "isso foi útil",
)


def normalize(texto: str) -> str:
    # get_text(" ") separa o texto de links com espaço ("Acesse Gerenciar
    # seu plano ."), então colamos de volta a pontuação.
    texto = re.sub(r"\s+", " ", texto).strip()
    return re.sub(r"\s+([.,;:!?)])", r"\1", texto)


def is_container(li) -> bool:
    """
    <li> que embrulha um bloco inteiro (as abas "Celulares e tablets" /
    "Computador", com título e lista própria). O texto dele já sai pelos
    elementos de dentro; usá-lo também juntava a aba toda numa linha só e
    duplicava o conteúdo.
    """
    return li.find(["ul", "ol", "h2", "h3", "h4"]) is not None or len(li.find_all("p")) > 1


def clean_html(html: str, url: str, fallback_title: str = "", category: str = "") -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # Os passos usam ícones no lugar do nome do botão ("Clique em <ícone>
    # para baixar"); sem o alt, o texto ficava "Clique em para baixar" e o
    # modelo inventava um nome.
    for img in soup.find_all("img", alt=True):
        if img["alt"].strip():
            img.replace_with(f'"{img["alt"].strip()}"')

    titulo_tag = soup.find("h1")
    titulo = normalize(titulo_tag.get_text(" ")) if titulo_tag else fallback_title
    if not titulo_tag:
        return {"title": titulo, "url": url, "category": category, "content": ""}

    partes = []
    for tag in titulo_tag.find_all_next(["h2", "h3", "h4", "p", "li", "tr"]):
        # <p> dentro de <li> ou de célula de tabela já entra pelo elemento pai
        if tag.name != "tr" and tag.find_parent("tr"):
            continue
        if tag.name == "li" and is_container(tag):
            continue
        if tag.name == "p" and tag.find_parent("li") and not is_container(tag.find_parent("li")):
            continue

        if tag.name == "tr":
            # Cada linha da tabela vira "coluna 1 | coluna 2", para o par
            # situação/solução não se perder em linhas soltas
            celulas = [normalize(c.get_text(" ")) for c in tag.find_all(["th", "td"])]
            texto = " | ".join(c for c in celulas if c)
        else:
            texto = normalize(tag.get_text(" "))
        lower = texto.lower()

        if lower in END_MARKERS:
            break
        if not texto or any(frase in lower for frase in NOISE_PHRASES):
            continue

        if tag.name == "tr":
            partes.append(f"- {texto}")
        elif tag.name in ("h2", "h3", "h4"):
            # O ## é o separador que o text_splitter usa para respeitar
            # fronteiras semânticas no chunking.
            partes.append(f"\n## {texto}\n")
        elif tag.name == "li" and tag.parent.name == "ol":
            # Passo a passo do artigo: numerado, para o modelo distinguir
            # os passos das listas de regras e observações
            numero = tag.parent.find_all("li", recursive=False).index(tag) + 1
            partes.append(f"{numero}. {texto}")
        elif tag.name == "li":
            partes.append(f"- {texto}")
        else:
            partes.append(texto)

    return {
        "title": titulo,
        "url": url,
        "category": category,
        "content": "\n".join(partes).strip(),
    }
