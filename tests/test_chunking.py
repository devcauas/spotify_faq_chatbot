import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.core.vector_store import VectorStoreManager
import pytest
import shutil
import time
import uuid
import gc

class TestChunking:
    """Testa o sistema de chunking"""
    
    @pytest.fixture
    def manager(self):
        """Cria um manager para testes"""
        # Usa um ID único para evitar conflitos
        test_id = uuid.uuid4().hex[:8]
        test_dir = f"data/test_chroma_{test_id}"
        
        manager = VectorStoreManager(
            persist_directory=test_dir,
            chunk_size=100,
            chunk_overlap=10
        )
        
        yield manager
        
        # Limpeza robusta após o teste
        self._cleanup_test_dir(test_dir)
    
    def _cleanup_test_dir(self, test_dir):
        """Limpa o diretório de teste com retry"""
        if not Path(test_dir).exists():
            return
        
        for attempt in range(5):
            try:
                # Força coleta de lixo
                gc.collect()
                
                # Pequena pausa
                time.sleep(0.2)
                
                # Tenta deletar
                shutil.rmtree(test_dir, ignore_errors=True)
                
                # Verifica se foi deletado
                if not Path(test_dir).exists():
                    return
            except PermissionError:
                # Espera e tenta novamente
                time.sleep(0.5)
                continue
        
        # Se chegou aqui, não conseguiu deletar
        print(f"⚠️ Não foi possível deletar {test_dir} - arquivo será ignorado")
    
    def test_chunk_creation(self, manager):
        """Testa se os chunks são criados corretamente"""
        docs = manager.load_documents_from_directory("data/faq_documents")
        chunks = manager.process_documents(docs)
        
        assert len(chunks) > 0
        
        for chunk in chunks:
            assert len(chunk.page_content) <= manager.chunk_size + 50
            assert "source" in chunk.metadata
            assert "chunk_id" in chunk.metadata
    
    def test_search_relevance(self, manager):
        """Testa se a busca retorna resultados relevantes"""
        docs = manager.load_documents_from_directory("data/faq_documents")
        chunks = manager.process_documents(docs)
        manager.create_vector_store(chunks)
        
        query = "Como criar uma playlist?"
        results = manager.search(query, k=2)
        
        assert len(results) > 0
        found = any("playlist" in r.page_content.lower() for r in results)
        assert found, "Resultado não contém 'playlist'"
    
    def test_similarity_threshold(self, manager):
        """Testa se a similaridade está em um nível aceitável"""
        docs = manager.load_documents_from_directory("data/faq_documents")
        chunks = manager.process_documents(docs)
        vector_store = manager.create_vector_store(chunks)
        
        query = "Como criar uma playlist?"
        results = vector_store.similarity_search_with_score(query, k=1)
        
        if results:
            doc, score = results[0]
            similarity = 1 / (1 + score)
            assert similarity > 0.7, f"Similaridade muito baixa: {similarity}"
    
    def test_duplicate_results(self, manager):
        """Testa se os resultados não são duplicados"""
        docs = manager.load_documents_from_directory("data/faq_documents")
        chunks = manager.process_documents(docs)
        vector_store = manager.create_vector_store(chunks)
        
        query = "Como criar uma playlist?"
        results = vector_store.similarity_search_with_score(query, k=3)
        
        texts = [r[0].page_content for r in results]
        unique_texts = set(texts)
        
        if len(chunks) >= 3:
            assert len(unique_texts) == len(texts), f"Duplicatas: {len(unique_texts)} vs {len(texts)}"
        else:
            pytest.skip(f"Apenas {len(chunks)} chunks disponíveis para teste")