# scripts/scraper/save_markdown.py
"""
Salva um artigo já limpo como .md, com metadata (title/url/category) em frontmatter.
"""

from pathlib import Path
from config import MARKDOWN_DIR


def save_article_as_markdown(article: dict, slug: str) -> Path:
    Path(MARKDOWN_DIR).mkdir(parents=True, exist_ok=True)
    output_path = Path(MARKDOWN_DIR) / f"{slug}.md"

    frontmatter = (
        "---\n"
        f"title: {article['title']}\n"
        f"url: {article['url']}\n"
        f"category: {article.get('category', '')}\n"
        "---\n\n"
    )
    body = f"# {article['title']}\n\n{article['content']}\n"

    output_path.write_text(frontmatter + body, encoding="utf-8")
    print(f"  💾 salvo: {output_path}")
    return output_path