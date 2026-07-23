# src/backend/core/rag_engine.py

"""
RAG Engine com LangChain - Versão Corrigida (v2)

Principais mudanças em relação à versão anterior:
- Abandona o RetrievalQA chain para o fluxo principal, pois ele não expõe
  o score de similaridade retornado pelo Chroma (doc.metadata['score']
  nunca existiu de fato — o código antigo sempre caía no valor fixo 0.7).
- Calcula similaridade real via similarity_search_with_score e aplica o
  threshold ANTES de chamar o LLM, evitando gastar tempo/tokens em
  perguntas fora do escopo da base de conhecimento.
- Mantém _is_fallback_response como segunda camada de segurança (caso o
  LLM decida recusar mesmo com documentos relevantes recuperados).
"""

from typing import Dict, List, Optional, Any
import time
import logging

from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

from .vector_store import VectorStoreManager
from .prompts import RAG_PROMPT_TEMPLATE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Motor RAG completo usando LangChain
    """

    _FALLBACK_SENTENCE = (
        "Não encontrei essa informação nos documentos oficiais do Spotify. "
        "Por favor, reformule sua pergunta ou entre em contato com o suporte."
    )

    def _strip_trailing_fallback(self, answer: str) -> str:
        idx = answer.find(self._FALLBACK_SENTENCE)
        if idx > 80:  # só corta se veio DEPOIS de conteúdo real
            return answer[:idx].strip()
        return answer.strip()

    def __init__(
        self,
        model_name: str = "llama3.2",
        temperature: float = 0.3,
        top_k: int = 5,
        similarity_threshold: float = 0.4,
        verbose: bool = False
    ):
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.verbose = verbose

        logger.info("Inicializando Vector Store...")
        self.vector_store = VectorStoreManager()

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

        logger.info("RAG Engine inicializado com sucesso!")

    def _fallback_result(self, response_time: float) -> Dict[str, Any]:
        return {
            'answer': (
                "Não encontrei essa informação nos documentos oficiais do "
                "Spotify. Por favor, reformule sua pergunta ou entre em "
                "contato com o suporte."
            ),
            'sources': [],
            'source_contents': [],
            'similarity': 0.0,
            'response_time': response_time,
            'is_fallback': True,
            'num_sources': 0
        }

    def ask(self, question: str) -> Dict[str, Any]:
        """
        Processa uma pergunta e retorna resposta + fontes.

        Fluxo:
        1. Busca top_k*3 candidatos (mais do que precisa) já com score real.
        2. Converte distância -> similaridade (1 - distância, espaço cosseno).
        3. Filtra pelo threshold, corta no máx. 2 chunks por artigo (diversidade),
           e mantém só os top_k finais.
        4. Se nada sobrar, fallback SEM chamar o LLM.
        5. Caso contrário, monta o contexto e gera a resposta com o Llama.
        """
        start_time = time.time()

        try:
            logger.info(f"Processando pergunta: {question[:50]}...")

            raw_results = self.vector_store.vector_store.similarity_search_with_score(
                question, k=self.top_k * 3
            )

            # Chroma retorna DISTÂNCIA (quanto menor, mais similar).
            # Com collection_metadata={"hnsw:space": "cosine"} e embeddings
            # normalizados, a similaridade real é 1 - distância.
            docs_with_sim = [(doc, 1 - dist) for doc, dist in raw_results]

            # Filtra pelo threshold antes de aplicar o cap de diversidade
            docs_with_sim = [d for d in docs_with_sim if d[1] >= self.similarity_threshold]

            if not docs_with_sim:
                logger.info(
                    f"Nenhum chunk acima do threshold {self.similarity_threshold} — "
                    "fallback sem chamar o LLM."
                )
                return self._fallback_result(time.time() - start_time)

            # Limita no máx. 2 chunks por fonte (artigo), preservando ordem por similaridade,
            # para evitar que um único artigo domine todo o contexto enviado ao LLM.
            from collections import defaultdict
            capped, seen_count = [], defaultdict(int)
            for doc, sim in sorted(docs_with_sim, key=lambda x: -x[1]):
                src = doc.metadata.get('source')
                if seen_count[src] >= 2:
                    continue
                seen_count[src] += 1
                capped.append((doc, sim))
                if len(capped) >= self.top_k:
                    break
            docs_with_sim = capped

            max_similarity = max(sim for _, sim in docs_with_sim)

            context = "\n\n".join(doc.page_content for doc, _ in docs_with_sim)
            prompt = self.prompt_template.format(context=context, question=question)

            answer = self.llm.invoke(prompt)

            answer = self._strip_trailing_fallback(answer)

            is_fallback = self._is_fallback_response(answer)
            response_time = time.time() - start_time

            # Dedup de fontes, preservando ordem (mesmo artigo pode ter entrado
            # 2x na lista de chunks, mas só deve aparecer 1x na citação final).
            sources_raw = [doc.metadata.get('source', 'FAQ') for doc, _ in docs_with_sim]
            sources = list(dict.fromkeys(sources_raw))

            return {
                'answer': answer,
                'sources': sources,
                'source_contents': [doc.page_content for doc, _ in docs_with_sim],
                'similarity': max_similarity,
                'response_time': response_time,
                'is_fallback': is_fallback,
                'num_sources': len(docs_with_sim)
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
        """
        Só considera fallback se a frase canônica de recusa DOMINAR a resposta
        (ou seja, o modelo não respondeu nada de fato) — não quando ela aparece
        colada ao final de uma resposta que já contém conteúdo substancial.
        """
        canonical = "não encontrei essa informação nos documentos oficiais do spotify"
        answer_lower = answer.lower().strip()
        if canonical not in answer_lower:
            return False
        # Se a frase canônica representa a maior parte do texto, é fallback de verdade.
        # Se veio DEPOIS de bastante conteúdo, o modelo só "hedgeou" no final.
        idx = answer_lower.find(canonical)
        return idx < 80  # a recusa apareceu logo no início = fallback real

    def get_stats(self) -> Dict:
        """Retorna estatísticas do sistema"""
        return self.vector_store.get_stats()