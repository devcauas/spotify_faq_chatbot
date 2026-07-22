# scripts/scraper/build_vector_db.py
"""
Lê os .md, extrai o frontmatter (title/url) como metadata e popula o ChromaDB.
"""

import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))  # raiz do projeto

from langchain_core.documents import Document
from src.backend.core.vector_store import VectorStoreManager
from config import MARKDOWN_DIR

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n\n(.*)$", re.DOTALL)


def parse_markdown_file(path: Path) -> Document:
    raw = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)

    metadata = {"file": path.name, "source": path.name}
    content = raw

    if match:
        frontmatter_block, content = match.groups()
        for line in frontmatter_block.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

    if "url" in metadata:
        metadata["source"] = metadata["url"]  # a "fonte" citada vira a URL real

    return Document(page_content=content.strip(), metadata=metadata)


def load_markdown_documents(directory: str):
    return [parse_markdown_file(p) for p in sorted(Path(directory).glob("*.md"))]


def main():
    print("=" * 60)
    print("CONSTRUINDO VECTOR DB A PARTIR DOS MARKDOWNS")
    print("=" * 60)

    manager = VectorStoreManager(reset_on_init=True)  # evita o lock que você teve antes

    print(f"📂 Carregando .md de {MARKDOWN_DIR}...")
    documents = load_markdown_documents(MARKDOWN_DIR)
    print(f"   {len(documents)} artigos carregados")

    print("✂️ Dividindo em chunks...")
    chunks = manager.process_documents(documents)

    print("💾 Salvando no ChromaDB...")
    manager.create_vector_store(chunks)

    stats = manager.get_stats()
    print(f"\n📊 Total de chunks: {stats['total_documents']}")
    print("\n✅ CONCLUÍDO!")


if __name__ == "__main__":
    main()