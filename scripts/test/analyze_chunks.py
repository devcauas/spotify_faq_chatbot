import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.core.vector_store import VectorStoreManager

def analyze_chunks():
    manager = VectorStoreManager()
    manager.load_vector_store()
    
    if manager.vector_store:
        all_docs = manager.vector_store.get()
        
        print("=" * 80)
        print("ANÁLISE DOS CHUNKS CRIADOS")
        print("=" * 80)
        
        for i, (doc_id, doc, metadata) in enumerate(zip(
            all_docs['ids'], 
            all_docs['documents'], 
            all_docs['metadatas']
        )):
            print(f"\n📄 CHUNK {i+1} (ID: {doc_id})")
            print("-" * 40)
            print(f"Tamanho: {len(doc)} caracteres")
            print(f"Fonte: {metadata.get('source', 'unknown')}")
            print(f"Posição: {metadata.get('chunk_id', 'N/A')}")
            print("\n📝 CONTEÚDO:")
            print(doc)
            print("\n" + "=" * 80)

if __name__ == "__main__":
    analyze_chunks()