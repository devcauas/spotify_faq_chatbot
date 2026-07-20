"""
Limpa os diretórios de teste do ChromaDB.
"""

import shutil
from pathlib import Path

def cleanup_test_dirs():
    """Remove todos os diretórios de teste"""
    test_dirs = Path("data").glob("test_chroma_*")
    
    removed = 0
    for test_dir in test_dirs:
        try:
            shutil.rmtree(test_dir)
            print(f"✅ Removido: {test_dir}")
            removed += 1
        except PermissionError:
            print(f"⚠️ Não foi possível remover: {test_dir} (arquivo em uso)")
    
    print(f"\nTotal removido: {removed}")

if __name__ == "__main__":
    cleanup_test_dirs()