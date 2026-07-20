# scripts/process_documents.py

"""
Processa documentos e popula o ChromaDB
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.core.vector_store import VectorStoreManager
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reseta o banco")
    parser.add_argument("--doc-dir", default="data/faq_documents", help="Diretório dos documentos")
    args = parser.parse_args()
    
    print("=" * 60)
    print("PROCESSANDO DOCUMENTOS")
    print("=" * 60)
    
    # Inicializa
    manager = VectorStoreManager()
    
    if args.reset:
        print("🔄 Resetando banco...")
        manager.reset()
    
    # Carrega
    print(f"📂 Carregando documentos de {args.doc_dir}...")
    documents = manager.load_documents_from_directory(args.doc_dir)
    
    # Processa
    print("✂️ Dividindo em chunks...")
    chunks = manager.process_documents(documents)
    
    # Adiciona ao banco
    print("💾 Salvando no ChromaDB...")
    manager.create_vector_store(chunks)
    
    # Estatísticas
    stats = manager.get_stats()
    print(f"\n📊 Estatísticas:")
    print(f"   Total de chunks: {stats['total_documents']}")
    print(f"   Diretório: {stats['persist_directory']}")
    
    print("\n✅ PROCESSAMENTO CONCLUÍDO!")

if __name__ == "__main__":
    main()