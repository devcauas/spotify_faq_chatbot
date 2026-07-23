# src/backend/core/vector_store.py

"""
Vector Store Manager com LangChain
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# ✅ IMPORTS CORRETOS DO LANGCHAIN
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Gerencia o ChromaDB usando LangChain
    """

    def __init__(
        self,
        persist_directory: str = "data/chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 700,
        chunk_overlap: int = 70,
        reset_on_init: bool = False
    ):
        self.persist_directory = persist_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # ✅ Embeddings via LangChain
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # ✅ Text Splitter via LangChain
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n==================================================\n",
                "\n# ",
                "\n## ",
                "\n\n",
                "\n",
                ". ",
                " "
            ]
        )

        # ✅ Vector Store via LangChain
        self.vector_store = None

        # Carrega ou cria vector store
        if reset_on_init:
            self.reset()
        else:
            self.load_vector_store()

        logger.info(f"VectorStoreManager inicializado em {persist_directory}")

    def load_documents_from_directory(self, directory_path: str) -> List[Document]:
        """
        Carrega documentos usando LangChain TextLoader
        """
        doc_path = Path(directory_path)

        if not doc_path.exists():
            raise FileNotFoundError(f"Diretório {directory_path} não encontrado")

        documents = []
        for file_path in doc_path.glob("*.txt"):
            logger.info(f"Carregando: {file_path}")
            loader = TextLoader(str(file_path), encoding='utf-8')
            documents.extend(loader.load())

        if not documents:
            raise ValueError(f"Nenhum documento encontrado em {directory_path}")

        logger.info(f"Carregados {len(documents)} documentos")
        return documents

    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Processa documentos usando LangChain TextSplitter.

        IMPORTANTE: preserva a metadata original do documento (title/url/category
        vindos do frontmatter em build_vector_db.py). Antes, este método
        recalculava title/url a partir do texto de cada chunk isolado, o que
        quebrava chunks do meio do artigo que não continham a URL nem o título.
        """
        chunks = self.text_splitter.split_documents(documents)

        for i, chunk in enumerate(chunks):
            # Não sobrescreve metadata já existente (title/url/category/source
            # vindos do frontmatter). Só adiciona o que ainda não existe.
            chunk.metadata["chunk_id"] = i
            chunk.metadata.setdefault("title", chunk.metadata.get("source", ""))
            chunk.metadata.setdefault("url", "")
            chunk.metadata.setdefault("category", "")
            chunk.metadata.setdefault("source", "")

        logger.info(f"Divididos {len(documents)} documentos em {len(chunks)} chunks")
        return chunks

    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """
        Cria vector store usando LangChain Chroma.

        Define explicitamente o espaço métrico como cosseno (hnsw:space).
        Sem isso, o Chroma usa distância L2 por padrão, o que quebra a
        conta `similaridade = 1 - distancia` usada no rag_engine.py.
        """
        logger.info("Criando vector store...")

        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_metadata={"hnsw:space": "cosine"}
        )

        self.vector_store.persist()
        logger.info(f"Vector store salvo em {self.persist_directory}")

        return self.vector_store

    def load_vector_store(self) -> Optional[Chroma]:
        """
        Carrega vector store existente
        """
        if Path(self.persist_directory).exists():
            logger.info(f"Carregando vector store de {self.persist_directory}")
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            return self.vector_store

        logger.warning(f"Vector store não encontrado em {self.persist_directory}")
        return None

    def search(self, query: str, k: int = 3) -> List[Document]:
        """
        Busca documentos similares
        """
        if not self.vector_store:
            raise ValueError("Vector store não inicializado")

        results = self.vector_store.similarity_search(query, k=k)
        logger.info(f"Encontrados {len(results)} resultados para: {query[:50]}...")
        return results

    def search_with_score(self, query: str, k: int = 3) -> List[tuple]:
        """
        Busca com scores de similaridade.

        Retorna tuplas (Document, distancia). Com collection_metadata
        {"hnsw:space": "cosine"} e embeddings normalizados, a distância
        está no intervalo [0, 2] e a similaridade real é `1 - distancia`.
        """
        if not self.vector_store:
            raise ValueError("Vector store não inicializado")

        results = self.vector_store.similarity_search_with_score(query, k=k)
        logger.info(f"Encontrados {len(results)} resultados com score")
        return results

    def get_retriever(self, k: int = 3, use_mmr: bool = True):
        """
        Retorna um retriever para uso em chains.

        use_mmr=True usa Maximal Marginal Relevance: busca um conjunto maior
        de candidatos (fetch_k) e seleciona os k mais relevantes E diversos
        entre si. Isso evita que perguntas amplas (ex: "quais as
        funcionalidades do Spotify?") recebam k chunks quase idênticos vindos
        do mesmo artigo, cobrindo mais tópicos diferentes na resposta.
        """
        if not self.vector_store:
            raise ValueError("Vector store não inicializado")

        if use_mmr:
            return self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": k, "fetch_k": max(k * 4, 20), "lambda_mult": 0.5}
            )

        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

    def reset(self):
        """
        Reseta o vector store
        """
        import shutil

        if Path(self.persist_directory).exists():
            logger.warning(f"Removendo vector store em {self.persist_directory}")
            shutil.rmtree(self.persist_directory)
            self.vector_store = None

        # Cria novo diretório
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas
        """
        try:
            if self.vector_store:
                collection = self.vector_store._collection
                count = collection.count()
            else:
                count = 0
        except Exception:
            count = 0

        return {
            "status": "active" if self.vector_store else "empty",
            "total_documents": count,
            "persist_directory": self.persist_directory,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "vector_store_type": "Chroma (LangChain)"
        }