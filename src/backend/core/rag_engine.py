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
import os
import time
import logging

from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

from .vector_store import VectorStoreManager
from .prompts import RAG_PROMPT_TEMPLATE, REFUSAL_SENTENCE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Motor RAG completo usando LangChain
    """

    def __init__(
        self,
        model_name: str = "llama3.2",
        temperature: float = 0.1,
        top_k: int = 4,
        similarity_threshold: float = 0.4,
        # Só entram no contexto os chunks a no máximo esta distância do
        # melhor resultado. Antes, todos os top_k iam sempre, mesmo os de
        # artigos sem relação, e o modelo misturava os assuntos.
        relevance_margin: float = 0.12,
        max_articles: int = 2,
        max_article_chars: int = 2500,
        verbose: bool = False
    ):
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.relevance_margin = relevance_margin
        self.max_articles = max_articles
        self.max_article_chars = max_article_chars
        self.verbose = verbose

        logger.info("Inicializando Vector Store...")
        # VectorStoreManager já carrega o vector store existente no seu
        # próprio __init__ (reset_on_init=False por padrão), então chamar
        # load_vector_store() de novo aqui era redundante. Além disso,
        # load_vector_store agora é strict por padrão: se o banco não
        # existir ou estiver vazio, falha aqui com uma mensagem clara,
        # em vez de deixar o FastAPI subir "saudável" e só quebrar na
        # primeira pergunta do usuário.
        self.vector_store = VectorStoreManager()

        logger.info(f"Inicializando LLM com modelo {model_name}...")
        # Em Docker Compose, "localhost" dentro do container do backend NÃO
        # é o container do Ollama — cada serviço tem sua própria rede
        # loopback. Por isso a URL vem de uma env var (setada no
        # docker-compose.yml como http://ollama:11434), com fallback para
        # localhost:11434 para quem roda tudo fora de container (dev local).
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.llm = OllamaLLM(
            model=model_name,
            base_url=ollama_base_url,
            temperature=temperature,
            num_predict=300,
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
            'answer': REFUSAL_SENTENCE,
            'sources': [],
            'source_titles': [],
            'source_contents': [],
            'similarity': 0.0,
            'response_time': response_time,
            'is_fallback': True,
            'num_sources': 0
        }

    def ask(self, question: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        Processa uma pergunta e retorna resposta + fontes.

        Args:
            question: pergunta do usuário.
            top_k: sobrescreve, só para esta chamada, o número de chunks
                buscados (ex: vindo do slider da sidebar no Streamlit).
                Se None, usa o self.top_k definido no __init__.

        Fluxo:
        1. Busca os top_k chunks mais similares, com score real (distância).
        2. Converte distância -> similaridade (1 - distância, espaço cosseno).
        3. Se a maior similaridade encontrada for menor que o threshold,
           retorna fallback SEM chamar o LLM (mais rápido e mais confiável
           do que depender do modelo se autopoliciar).
        4. Caso contrário, monta o contexto e gera a resposta com o Llama.
        """
        start_time = time.time()
        k = top_k or self.top_k

        try:
            logger.info(f"Processando pergunta: {question[:50]}...")

            raw_results = self.vector_store.vector_store.similarity_search_with_score(
                question, k=k
            )

            # Chroma retorna DISTÂNCIA (quanto menor, mais similar).
            # Com collection_metadata={"hnsw:space": "cosine"} e embeddings
            # normalizados, a similaridade real é 1 - distância.
            docs_with_sim = [(doc, 1 - dist) for doc, dist in raw_results]

            max_similarity = max((sim for _, sim in docs_with_sim), default=0.0)

            if not docs_with_sim or max_similarity < self.similarity_threshold:
                logger.info(
                    f"Similaridade máxima {max_similarity:.2f} abaixo do "
                    f"threshold {self.similarity_threshold} — fallback sem chamar o LLM."
                )
                return self._fallback_result(time.time() - start_time)

            # Os chunks servem para ACHAR o artigo; para responder, o modelo
            # recebe o artigo inteiro. Com fragmentos soltos de 3 artigos, o
            # Llama 3.2 misturava o fim de um com o começo de outro e perdia
            # os passos (ex: "Gerenciar seu plano > Cancelar assinatura").
            # Artigos com o mesmo título (ex: "Plano Família" geral e o de
            # iOS) ocupariam as duas vagas com quase o mesmo texto; a segunda
            # vaga fica para um artigo diferente.
            sources, source_titles = [], []
            for doc, sim in docs_with_sim:
                url = doc.metadata.get('source', 'FAQ')
                title = doc.metadata.get('title', url)
                if (sim >= max_similarity - self.relevance_margin
                        and url not in sources and title not in source_titles):
                    sources.append(url)
                    source_titles.append(title)
            sources = sources[:self.max_articles]
            source_titles = source_titles[:self.max_articles]

            source_contents = [self._full_article(url) for url in sources]
            context = "\n\n---\n\n".join(source_contents)
            prompt = self.prompt_template.format(context=context, question=question)

            answer = self._strip_refusal(self.llm.invoke(prompt).strip())

            is_fallback = self._is_fallback_response(answer)
            response_time = time.time() - start_time

            return {
                'answer': answer,
                'sources': sources,
                'source_titles': source_titles,
                'source_contents': source_contents,
                'similarity': max_similarity,
                'response_time': response_time,
                'is_fallback': is_fallback,
                'num_sources': len(sources)
            }

        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {e}")
            return {
                'answer': f"Erro ao processar pergunta: {str(e)}",
                'sources': [],
                'source_titles': [],
                'source_contents': [],
                'similarity': 0.0,
                'response_time': time.time() - start_time,
                'is_fallback': True,
                'error': str(e)
            }

    def _full_article(self, url: str) -> str:
        """
        Remonta o artigo a partir dos seus chunks no Chroma, na ordem
        original, tirando o título repetido em cada chunk e o overlap do
        text splitter.
        """
        data = self.vector_store.vector_store.get(
            where={"source": url}, include=["documents", "metadatas"]
        )
        chunks = sorted(
            zip(data["documents"], data["metadatas"]),
            key=lambda item: item[1].get("chunk_id", 0)
        )
        if not chunks:
            return ""

        title = chunks[0][1].get("title", "")
        prefix = f"# {title}\n"
        texto = ""
        for content, _ in chunks:
            # O 1º chunk já traz o título do próprio .md; os outros, o que o
            # VectorStoreManager acrescentou
            while content.lstrip().startswith(prefix):
                content = content.lstrip()[len(prefix):]
            # O fim do chunk anterior se repete no começo deste (overlap)
            for n in range(min(len(texto), len(content), 80), 10, -1):
                if texto.endswith(content[:n]):
                    content = content[n:]
                    break
            texto += ("" if not texto or content[:1].isspace() else "\n") + content

        return f"{prefix}{texto.strip()}"[:self.max_article_chars]

    def _strip_refusal(self, answer: str) -> str:
        """
        O Llama 3.2 às vezes responde e, no fim, ainda cola a frase de
        recusa. Se há resposta antes dela, a frase sai; se a resposta é só
        a recusa, fica como está.
        """
        idx = answer.find(REFUSAL_SENTENCE)
        if idx > 0 and answer[:idx].strip():
            return answer[:idx].strip()
        return answer

    def _is_fallback_response(self, answer: str) -> bool:
        """Verifica se a resposta é um fallback (segunda camada de segurança)"""
        # Uma resposta com passos que só menciona "não encontrei" no meio
        # não é recusa: só conta quando a resposta é curta.
        if len(answer) > 200:
            return False
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