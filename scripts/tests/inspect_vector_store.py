# scripts/inspect_vector_store.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.core.vector_store import VectorStoreManager

def inspect_store():
    manager = VectorStoreManager()
    manager.load_vector_store()
    
    if manager.vector_store:
        # Pega todos os documentos
        all_docs = manager.vector_store.get()
        
        print(f"Total de documentos: {len(all_docs['ids'])}")
        print("\n--- Documentos ---")
        
        for i, (doc_id, doc) in enumerate(zip(all_docs['ids'], all_docs['documents'])):
            print(f"\nChunk {i+1} (ID: {doc_id}):")
            print(f"Conteúdo: {doc[:200]}...")
            print(f"Metadata: {all_docs['metadatas'][i]}")

if __name__ == "__main__":
    inspect_store()