import sys
from pathlib import Path

# Adiciona a raiz do projeto ao PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.core.vector_store import VectorStoreManager


def main():
    manager = VectorStoreManager()

    perguntas = [
        "Como cancelar meu Premium?",
        "Quais formas de pagamento são aceitas?",
        "Como mudar meu cartão de crédito?",
        "O que acontece se meu pagamento falhar?"
    ]

    for pergunta in perguntas:
        print("=" * 80)
        print(f"PERGUNTA: {pergunta}")

        resultados = manager.search(pergunta, k=3)

        for i, doc in enumerate(resultados, start=1):
            print(f"\nResultado {i}")
            print("Metadata:", doc.metadata)
            print(doc.page_content[:500])
            print("-" * 80)


if __name__ == "__main__":
    main()