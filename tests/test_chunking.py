"""
Testes automatizados para o sistema de chunking.

Para rodar: pytest tests/
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.core.vector_store import VectorStoreManager
import pytest

class TestChunking:
    """Testa o sistema de chunking"""
    
    @pytest.fixture
    def manager(self):
        """Cria um manager para testes"""
        return VectorStoreManager(
            persist_directory="data/test_chroma",
            chunk_size=100,
            chunk_overlap=10
        )
    
    def test_chunk_creation(self, manager):
        """Testa se os chunks são criados corretamente"""
        docs = manager.load_documents_from_directory("data/faq_documents")
        chunks = manager.process_documents(docs)
        
        # Verifica se criou chunks
        assert len(chunks) > 0
        
        # Verifica se cada chunk tem tamanho apropriado
        for chunk in chunks:
            assert len(chunk.page_content) <= manager.chunk_size + 50  # margem
        
        # Verifica metadata
        for chunk in chunks:
            assert "source" in chunk.metadata
            assert "chunk_id" in chunk.metadata
    
    def test_search_relevance(self, manager):
        """Testa se a busca retorna resultados relevantes"""
        # Processa documentos
        docs = manager.load_documents_from_directory("data/faq_documents")
        chunks = manager.process_documents(docs)
        manager.create_vector_store(chunks)
        
        # Testa busca
        query = "Como criar uma playlist?"
        results = manager.search(query, k=2)
        
        # Verifica resultados
        assert len(results) > 0
        
        # Verifica se o resultado contém palavras-chave
        found = any("playlist" in r.page_content.lower() for r in results)
        assert found, "Resultado não contém 'playlist'"
    
    def test_similarity_threshold(self, manager):
        """Testa se a similaridade está em um nível aceitável"""
        # Processa documentos
        docs = manager.load_documents_from_directory("data/faq_documents")
        chunks = manager.process_documents(docs)
        vector_store = manager.create_vector_store(chunks)
        
        # Testa com pergunta existente
        query = "Como criar uma playlist?"
        results = vector_store.similarity_search_with_score(query, k=1)
        
        if results:
            doc, score = results[0]
            similarity = 1 / (1 + score)
            # Espera similaridade > 0.7 (boa)
            assert similarity > 0.7, f"Similaridade muito baixa: {similarity}"
    
    def test_duplicate_results(self, manager):
        """Testa se os resultados não são duplicados"""
        # Processa documentos
        docs = manager.load_documents_from_directory("data/faq_documents")
        chunks = manager.process_documents(docs)
        vector_store = manager.create_vector_store(chunks)
        
        # Busca
        query = "Como criar uma playlist?"
        results = vector_store.similarity_search_with_score(query, k=3)
        
        # Verifica se há duplicatas
        texts = [r[0].page_content for r in results]
        unique_texts = set(texts)
        assert len(unique_texts) == len(texts), "Encontradas duplicatas nos resultados"