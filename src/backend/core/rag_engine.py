# src/backend/core/rag_engine.py

"""
RAG Engine com LangChain - Versão Corrigida
"""

from typing import Dict, List, Optional, Any
import time
import logging

# ✅ IMPORTS CORRETOS
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.documents import Document

# ✅ TRY/EXCEPT para compatibilidade
try:
    from langchain.chains import RetrievalQA
except ImportError:
    try:
        from langchain.chains.retrieval_qa.base import RetrievalQA
    except ImportError:
        raise ImportError(
            "Não foi possível importar RetrievalQA. "
            "Verifique a versão do langchain: pip install langchain==0.1.20"
        )

from .vector_store import VectorStoreManager
from .prompts import RAG_PROMPT_TEMPLATE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Motor RAG completo usando LangChain
    """
    
    def __init__(
        self,
        model_name: str = "llama3.2",
        temperature: float = 0.3,
        top_k: int = 3,
        similarity_threshold: float = 0.6,
        verbose: bool = False
    ):
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.verbose = verbose
        
        logger.info("Inicializando Vector Store...")
        self.vector_store = VectorStoreManager()
        self.vector_store.load_vector_store()
        
        logger.info("Criando Retriever...")
        self.retriever = self.vector_store.get_retriever(k=top_k)
        
        logger.info(f"Inicializando LLM com modelo {model_name}...")
        self.llm = OllamaLLM(
            model=model_name,
            temperature=temperature,
            num_predict=500,
            top_k=10,
            top_p=0.9
        )
        
        logger.info("Configurando Prompt...")
        self.prompt_template = PromptTemplate(
            template=RAG_PROMPT_TEMPLATE,
            input_variables=["context", "question"]
        )
        
        logger.info("Criando QA Chain...")
        try:
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True,
                chain_type_kwargs={
                    "prompt": self.prompt_template,
                }
            )
        except Exception as e:
            logger.error(f"Erro ao criar QA Chain: {e}")
            # Fallback: tenta sem chain_type_kwargs
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True
            )
        
        logger.info("RAG Engine inicializado com sucesso!")
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Processa uma pergunta e retorna resposta + fontes
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processando pergunta: {question[:50]}...")
            
            # ✅ Executa a chain
            result = self.qa_chain.invoke({"query": question})
            
            # Extrai resposta e fontes
            answer = result['result']
            source_documents = result.get('source_documents', [])
            
            # Extrai similaridade (se disponível)
            similarities = []
            for doc in source_documents:
                if hasattr(doc, 'metadata') and 'score' in doc.metadata:
                    similarities.append(doc.metadata['score'])
            
            max_similarity = max(similarities) if similarities else 0.7
            
            # Verifica fallback
            is_fallback = self._is_fallback_response(answer)
            
            response_time = time.time() - start_time
            
            return {
                'answer': answer,
                'sources': [doc.metadata.get('source', 'FAQ') for doc in source_documents],
                'source_contents': [doc.page_content for doc in source_documents],
                'similarity': max_similarity,
                'response_time': response_time,
                'is_fallback': is_fallback,
                'num_sources': len(source_documents)
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {e}")
            return {
                'answer': f"❌ Erro ao processar pergunta: {str(e)}",
                'sources': [],
                'source_contents': [],
                'similarity': 0.0,
                'response_time': time.time() - start_time,
                'is_fallback': True,
                'error': str(e)
            }
    
    def _is_fallback_response(self, answer: str) -> bool:
        """Verifica se a resposta é um fallback"""
        fallback_indicators = [
            "não encontrei",
            "não tenho informações",
            "não sei",
            "não está nos documentos",
            "não encontrado"
        ]
        answer_lower = answer.lower()
        return any(indicator in answer_lower for indicator in fallback_indicators)
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do sistema"""
        return self.vector_store.get_stats()