# scripts/scraper/http_client.py
"""
GET com cache em disco: extract_links.py já baixa cada artigo para descobrir
novos links, então download_articles.py reaproveita o mesmo HTML em vez de
pedir a página de novo.
"""

import time
from pathlib import Path

import requests

from config import HTML_CACHE_DIR, USER_AGENT, REQUEST_DELAY, TIMEOUT, MAX_RETRIES

_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "pt-BR"})


def fetch(url: str, cache_name: str | None = None) -> str:
    cache_path = Path(HTML_CACHE_DIR) / f"{cache_name}.html" if cache_name else None
    if cache_path and cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    for tentativa in range(MAX_RETRIES):
        response = _session.get(url, timeout=TIMEOUT)
        if response.status_code != 429:
            break
        # O site limita a taxa de requisições: espera e tenta de novo
        espera = int(response.headers.get("Retry-After", 0)) or 60 * (tentativa + 1)
        print(f"  429, aguardando {espera}s")
        time.sleep(espera)
    response.raise_for_status()
    response.encoding = "utf-8"
    time.sleep(REQUEST_DELAY)

    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(response.text, encoding="utf-8")
    return response.text
