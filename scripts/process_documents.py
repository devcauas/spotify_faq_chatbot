"""
Script para processar documentos e popular o ChromaDB.

Este script deve ser executado:
1. Na primeira vez que o sistema for configurado
2. Sempre que novos documentos forem adicionados
3. Quando o modelo de embeddings mudar

Uso:
    python scripts/process_documents.py

Ou com argumentos:
    python scripts/process_documents.py --dir data/faq_documents --reset
"""

import argparse
import logging
import sys
from pathlib import Path

# Adiciona o src ao path para importar os módulos
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.core.vector_store import VectorStoreManager

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(description="Processa documentos FAQ para o ChromaDB")
    parser.add_argument(
        "--doc-dir",
        type=str,
        default="data/faq_documents",
        help="Diretório com os documentos FAQ"
    )
    parser.add_argument(
        "--persist-dir",
        type=str,
        default="data/chroma_db",
        help="Diretório para persistir o ChromaDB"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reseta o banco antes de processar"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Tamanho dos chunks em caracteres"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="Overlap entre chunks"
    )
    
    args = parser.parse_args()
    
    logger.info("=== INICIANDO PROCESSAMENTO DE DOCUMENTOS ===")
    logger.info(f"Diretório de documentos: {args.doc_dir}")
    logger.info(f"Diretório de persistência: {args.persist_dir}")
    
    # 1. Inicializa o gerenciador
    manager = VectorStoreManager(
        persist_directory=args.persist_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    # 2. Reseta se solicitado
    if args.reset:
        logger.warning("Resetando banco existente...")
        manager.reset()
    
    # 3. Carrega documentos
    logger.info("Carregando documentos...")
    try:
        documents = manager.load_documents_from_directory(args.doc_dir)
    except Exception as e:
        logger.error(f"Erro ao carregar documentos: {e}")
        sys.exit(1)
    
    # 4. Processa (chunking)
    logger.info("Processando documentos (chunking)...")
    chunks = manager.process_documents(documents)
    
    # 5. Cria vector store
    logger.info("Criando vector store...")
    vector_store = manager.create_vector_store(chunks)
    
    # 6. Estatísticas
    stats = manager.get_stats()
    logger.info(f"Estatísticas do banco: {stats}")
    
    # 7. Teste rápido
    logger.info("Realizando teste de busca...")
    test_queries = [
        "Como criar uma playlist?",
        "O que é Spotify Premium?",
        "Como compartilhar uma música?"
    ]
    
    for query in test_queries:
        results = manager.search(query, k=2)
        logger.info(f"Pergunta: {query}")
        logger.info(f"Resultados: {len(results)} chunks encontrados")
        if results:
            logger.info(f"Primeiro resultado: {results[0].page_content[:100]}...")
    
    logger.info("=== PROCESSAMENTO CONCLUÍDO ===")


if __name__ == "__main__":
    main()