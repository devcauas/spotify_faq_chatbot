"""
Módulo responsável pelo gerenciamento do banco vetorial ChromaDB.

Este módulo encapsula toda a lógica de:
- Criação do vector store a partir de documentos
- Persistência dos embeddings
- Busca por similaridade

Data: 06/07/2026
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Gerencia o banco vetorial ChromaDB.
    
    Responsabilidades:
    1. Carregar documentos do disco
    2. Dividir documentos em chunks
    3. Gerar embeddings
    4. Persistir no ChromaDB
    5. Buscar documentos similares
    
    Attributes:
        persist_directory (str): Diretório onde o ChromaDB será salvo
        embedding_model (str): Nome do modelo de embeddings
        chunk_size (int): Tamanho máximo de cada chunk
        chunk_overlap (int): Overlap entre chunks
        vector_store (Chroma): Instância do ChromaDB
    """
    
    def __init__(
        self,
        persist_directory: str = "data/chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        Inicializa o gerenciador do vector store.
        
        Args:
            persist_directory: Onde salvar o banco vetorial
            embedding_model: Modelo para gerar embeddings
            chunk_size: Tamanho dos chunks em caracteres
            chunk_overlap: Sobreposição entre chunks (para manter contexto)
        """
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Inicializa o modelo de embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},  # Use 'cuda' se tiver GPU
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Inicializa o splitter de documentos
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        self.vector_store = None
        logger.info(f"VectorStoreManager inicializado com modelo {embedding_model}")
    
    def load_documents_from_directory(self, directory_path: str) -> List[Document]:
        """
        Carrega todos os documentos de um diretório.
        
        Args:
            directory_path: Caminho para o diretório com os documentos
            
        Returns:
            Lista de objetos Document do LangChain
            
        Raises:
            FileNotFoundError: Se o diretório não existir
            ValueError: Se nenhum documento for encontrado
        """
        doc_path = Path(directory_path)
        
        if not doc_path.exists():
            raise FileNotFoundError(f"Diretório {directory_path} não encontrado")
        
        documents = []
        
        # Suporta vários formatos de arquivo
        for file_path in doc_path.glob("*"):
            if file_path.suffix in ['.txt', '.md']:
                logger.info(f"Carregando documento: {file_path}")
                loader = TextLoader(str(file_path), encoding='utf-8')
                documents.extend(loader.load())
        
        if not documents:
            raise ValueError(f"Nenhum documento encontrado em {directory_path}")
        
        logger.info(f"Carregados {len(documents)} documentos")
        return documents
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Processa documentos: divide em chunks.
        
        Args:
            documents: Lista de documentos para processar
            
        Returns:
            Lista de chunks (Document)
        """
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Divididos {len(documents)} documentos em {len(chunks)} chunks")
        
        # Adiciona metadata para rastreabilidade
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["source"] = chunk.metadata.get("source", "unknown")
        
        return chunks
    
    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """
        Cria um novo vector store com os documentos fornecidos.
        
        Args:
            documents: Lista de documentos (já chunkados)
            
        Returns:
            Instância do ChromaDB
            
        Nota:
            Se já existir um vector store no diretório, ele será sobrescrito.
        """
        logger.info("Criando vector store...")

        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        
        # Cria o vector store
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        # Persiste no disco
        self.vector_store.persist()
        logger.info(f"Vector store salvo em {self.persist_directory}")
        
        return self.vector_store
    
    def load_vector_store(self) -> Optional[Chroma]:
        """
        Carrega um vector store existente do disco.
        
        Returns:
            Instância do ChromaDB ou None se não existir
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
        Busca documentos similares a uma query.
        
        Args:
            query: Texto para busca
            k: Número de resultados
            
        Returns:
            Lista de documentos similares
        """
        if not self.vector_store:
            raise ValueError("Vector store não inicializado. Use create_vector_store() ou load_vector_store()")
        
        results = self.vector_store.similarity_search(query, k=k)
        logger.info(f"Encontrados {len(results)} resultados para: {query[:50]}...")
        
        return results
    
    def reset(self) -> None:
        """
        Reseta o vector store (remove todos os dados).
        
        Útil para reindexar documentos do zero.
        """
        import shutil
        
        if Path(self.persist_directory).exists():
            logger.warning(f"Removendo vector store em {self.persist_directory}")
            shutil.rmtree(self.persist_directory)
            self.vector_store = None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do vector store.
        
        Returns:
            Dicionário com informações do banco
        """
        if not self.vector_store:
            return {"status": "empty", "message": "Vector store não inicializado"}
        
        # Obtém o número de documentos
        try:
            # ChromaDB não tem uma API direta para contar docs
            # Mas podemos fazer um search vazio e contar
            count = len(self.vector_store.get()["ids"])
        except:
            count = 0
        
        return {
            "status": "active",
            "total_documents": count,
            "persist_directory": self.persist_directory,
            "embedding_model": self.embedding_model,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }