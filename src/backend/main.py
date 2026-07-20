# src/backend/main.py

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.backend.core.rag_engine import RAGEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rag_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_engine

    logger.info("Inicializando RAG Engine...")

    rag_engine = RAGEngine()

    logger.info("RAG Engine inicializado.")

    yield

    logger.info("Encerrando aplicação...")


app = FastAPI(
    title="Spotify FAQ Chatbot API",
    description="API para chatbot FAQ utilizando LangChain + Ollama + ChromaDB",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    similarity: float
    response_time: float
    fallback: bool


@app.get("/")
def root():
    return {
        "message": "Spotify FAQ Chatbot API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/stats")
def stats():
    if rag_engine is None:
        raise HTTPException(
            status_code=503,
            detail="RAG Engine não inicializado"
        )

    return rag_engine.get_stats()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    if rag_engine is None:
        raise HTTPException(
            status_code=503,
            detail="RAG Engine não inicializado"
        )

    result = rag_engine.ask(request.question)

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        similarity=result["similarity"],
        response_time=result["response_time"],
        fallback=result["is_fallback"]
    )