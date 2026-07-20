import sys
from pathlib import Path
# Garante que o Python encontre a pasta src
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.core.vector_store import VectorStoreManager

def detailed_search_test():
    print("🤖 Inicializando gerenciador do banco...")
    manager = VectorStoreManager()
    manager.load_vector_store()
    
    # Verifica se o banco carregou de verdade
    if not manager.vector_store:
        print("❌ ERRO: O Banco Vetorial não pôde ser carregado na memória.")
        print("Verifique se a pasta 'data/chroma_db' contém os arquivos do banco.")
        return

    test_queries = [
        "Como criar uma playlist?",
        "Como faço uma playlist nova?",
        "Como compartilhar música no Spotify?",
        "O que é Spotify Premium?",
        "Quanto custa o Spotify Premium?",
        "Como funciona o Spotify Duo?", 
    ]

    print("=" * 80)
    print("🔬 TESTE DE QUALIDADE DE BUSCA")
    print("=" * 80)

    for query in test_queries:
        print(f"\n🔍 PERGUNTA: {query}")
        print("-" * 40)
        
        # Realiza a busca trazendo a distância (score)
        results = manager.vector_store.similarity_search_with_score(query, k=3)
        
        if not results:
            print("⚠️ Nenhum resultado retornado para esta pergunta.")
            continue

        for i, (doc, score) in enumerate(results):
            # Converte a distância em um índice de similaridade (0 a 1)
            similarity = 1 / (1 + score)
            
            print(f"\n📊 Resultado {i + 1} (Similaridade: {similarity:.3f})")
            print(f"📝 {doc.page_content[:150]}...")
            print(f"📁 Fonte: {doc.metadata.get('source', 'unknown')}")
            
            if similarity > 0.7:
                print("✅ ALTA RELEVÂNCIA")
            elif similarity > 0.5:
                print("⚠️ RELEVÂNCIA MÉDIA")
            else:
                print("❌ BAIXA RELEVÂNCIA")
        print("=" * 80)

if __name__ == "__main__":
    # Esta linha garante a execução da função
    detailed_search_test()