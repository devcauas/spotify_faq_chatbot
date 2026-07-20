# scripts/compare_chunk_sizes.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.core.vector_store import VectorStoreManager
import shutil
import time

def test_chunk_configuration(chunk_size, chunk_overlap, test_query):
    """Testa uma configuração específica de chunk"""
    
    print(f"\n{'='*60}")
    print(f"Testando: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    print('='*60)
    
    # Diretório temporário para teste
    test_dir = f"data/test_chroma_{chunk_size}"
    
    # Limpa diretório anterior
    if Path(test_dir).exists():
        shutil.rmtree(test_dir)
    
    # Cria manager com configuração específica
    manager = VectorStoreManager(
        persist_directory=test_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # Processa documentos
    start = time.time()
    docs = manager.load_documents_from_directory("data/faq_documents")
    chunks = manager.process_documents(docs)
    manager.create_vector_store(chunks)
    process_time = time.time() - start
    
    # Testa busca
    results = manager.vector_store.similarity_search_with_score(test_query, k=3)
    
    # Estatísticas
    print(f"\n📊 Estatísticas:")
    print(f"- Tempo de processamento: {process_time:.2f}s")
    print(f"- Número de chunks: {len(chunks)}")
    print(f"- Tamanho médio: {sum(len(c.page_content) for c in chunks) / len(chunks):.0f} caracteres")
    
    print(f"\n🔍 Resultados para: '{test_query}'")
    for i, (doc, score) in enumerate(results):
        similarity = 1 / (1 + score)
        print(f"\nResultado {i+1} (similaridade: {similarity:.3f}):")
        print(f"{doc.page_content[:100]}...")
    
    return manager

def main():
    test_query = "Como criar uma playlist?"
    
    # Testa diferentes configurações
    configs = [
        (200, 20),   # Pequeno
        (500, 50),   # Médio (atual)
        (1000, 100), # Grande
    ]
    
    for chunk_size, chunk_overlap in configs:
        test_chunk_configuration(chunk_size, chunk_overlap, test_query)

if __name__ == "__main__":
    main()