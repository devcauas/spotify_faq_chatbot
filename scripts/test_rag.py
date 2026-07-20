# scripts/test_rag.py

"""
Teste do RAG Engine com LangChain
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.core.rag_engine import RAGEngine
import time

def test_rag():
    print("=" * 60)
    print("🧪 TESTE RAG COM LANGCHAIN")
    print("=" * 60)
    
    print("\n📦 Inicializando RAG Engine...")
    rag = RAGEngine(verbose=True)
    
    print(f"📊 Estatísticas: {rag.get_stats()}")
    
    questions = [
        "Como criar uma playlist no Spotify?",
        "O que é Spotify Premium?",
        "Como compartilhar uma música?",
        "Como criar um podcast no Spotify?"  # Deve gerar fallback
    ]
    
    for question in questions:
        print(f"\n📝 Pergunta: {question}")
        print("-" * 40)
        
        start = time.time()
        result = rag.ask(question)
        elapsed = time.time() - start
        
        print(f"\n✅ Resposta ({elapsed:.2f}s):")
        print(result['answer'])
        print(f"\n📊 Similaridade: {result['similarity']:.2%}")
        print(f"📁 Fontes: {result['sources']}")
        print(f"🔄 Fallback: {'Sim' if result['is_fallback'] else 'Não'}")
        print(f"📄 Número de fontes: {result['num_sources']}")

if __name__ == "__main__":
    test_rag()