# scripts/scraper/config.py

BASE_URL = "https://support.spotify.com"
ARTICLE_PREFIX = "/br-pt/article/"

# Páginas de partida. A home lista os artigos mais acessados de todas as
# categorias; a partir deles, o crawler segue os links internos de cada
# artigo (menu da categoria + artigos relacionados) até MAX_ARTICLES.
SEED_URLS = [
    f"{BASE_URL}/br-pt/",
    f"{BASE_URL}/br-pt/category/payments-and-billing/",
]

MAX_ARTICLES = 300

RAW_DIR = "data/raw"
LINKS_FILE = f"{RAW_DIR}/links.json"
HTML_CACHE_DIR = f"{RAW_DIR}/html"

MARKDOWN_DIR = "data/faq_documents"

# A Central de Ajuda é renderizada no servidor: um GET simples já traz o
# artigo completo, sem precisar de navegador headless.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
# Segundos entre requisições. Com 0,5 s o site devolveu 429 depois de ~55
# páginas e bloqueou o IP por alguns minutos.
REQUEST_DELAY = 3
TIMEOUT = 30
MAX_RETRIES = 5
