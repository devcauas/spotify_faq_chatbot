import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.core.vector_store import VectorStoreManager

def test_search_quality():
    manager = VectorStoreManager()
    manager.load_vector_store()
    
    test_queries = [
        "Como faço para criar uma playlist?",  # Variação da pergunta original
        "Quais são os benefícios do premium?",  # Pergunta diferente
        "Como compartilho uma música com amigos?",  # Reformulação
        "O que é o Spotify Duo?",  # Pergunta sobre tópico não coberto
    ]
    
    for query in test_queries:
        print(f"\n--- Pergunta: {query} ---")
        results = manager.search(query, k=2)
        
        for i, doc in enumerate(results):
            score = doc.metadata.get('score', 'N/A')
            print(f"Resultado {i+1}:")
            print(f"Texto: {doc.page_content[:150]}...")
            print(f"Fonte: {doc.metadata.get('source', 'unknown')}")
            print(f"Score: {score}")
            print("-" * 50)

if __name__ == "__main__":
    test_search_quality()