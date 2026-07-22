# Spotify FAQ Chatbot

Chatbot inteligente para responder dúvidas sobre o Spotify utilizando **Retrieval-Augmented Generation (RAG)** e modelos de linguagem executados localmente.

O sistema realiza automaticamente a coleta de artigos da Central de Ajuda do Spotify, transforma esses documentos em embeddings utilizando **Sentence Transformers**, armazena-os em um banco vetorial **ChromaDB** e utiliza um modelo **Llama 3.2**, executado via **Ollama**, para responder perguntas fundamentadas exclusivamente na documentação oficial.

Todo o processamento ocorre localmente, sem utilização de APIs pagas.

---

# Demonstração

## Pipeline de Indexação

1. O scraper acessa a Central de Ajuda do Spotify.
2. Os artigos são convertidos para Markdown.
3. Os documentos são divididos em chunks.
4. Os chunks são transformados em embeddings.
5. Os embeddings são armazenados no ChromaDB.

## Pipeline de Consulta

1. O usuário envia uma pergunta.
2. A pergunta é convertida em embedding.
3. O ChromaDB realiza a busca semântica.
4. Os documentos mais relevantes são recuperados.
5. O contexto é enviado ao Llama 3.2.
6. A resposta é gerada utilizando exclusivamente as informações encontradas.
7. O sistema retorna a resposta juntamente com as fontes consultadas.

---

# Funcionalidades

- Busca semântica baseada em embeddings
- Pipeline completo de Retrieval-Augmented Generation (RAG)
- Coleta automática de FAQs oficiais do Spotify
- Conversão automática dos artigos para Markdown
- Chunking inteligente utilizando LangChain
- Banco vetorial ChromaDB
- Recuperação de documentos por similaridade
- Respostas fundamentadas exclusivamente na documentação oficial
- Exibição das fontes utilizadas
- API REST utilizando FastAPI
- Interface Web construída com Streamlit
- Execução totalmente local utilizando Ollama
- Docker Compose para facilitar a execução

---

# Tecnologias

## Backend

- Python 3.10
- FastAPI
- LangChain
- ChromaDB
- Ollama
- Sentence Transformers
- BeautifulSoup
- Requests

## Frontend

- Streamlit

## Inteligência Artificial

- llama3.2
- sentence-transformers/all-MiniLM-L6-v2

---

# Estrutura do Projeto

```text
spotify_faq_chatbot
│
├── data/
│   ├── chroma_db/
│   ├── faq_documents/
│   └── raw/
│
├── scripts/
│   ├── scraper/
│   │   ├── extract_links.py
│   │   ├── download_articles.py
│   │   ├── build_vector_db.py
│   │   ├── clean_article.py
│   │   ├── save_markdows.py
│   │   └── config.py
│   │
│   ├── analyze_chunks.py
│   ├── inspect_vector_store.py
│   └── test_search.py
│
├── src/
│   ├── backend/
│   │   ├── core/
│   │   │   ├── rag_engine.py
│   │   │   ├── vector_store.py
│   │   │   ├── prompts.py
│   │   │   ├── config.py
│   │   │   ├── metrics.py
│   │   │   └── error_handling.py
│   │   │
│   │   └── main.py
│   │
│   └── frontend/
│       ├── components/
│       │   ├── chat.py
│       │   └── sidebar.py
│       │
│       ├── utils/
│       │   └── api_client.py
│       │
│       └── app.py
│
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Como executar

## 1. Clone o projeto

```bash
git clone https://github.com/SEU-USUARIO/spotify_faq_chatbot.git

cd spotify_faq_chatbot
```

---

## 2. Crie um ambiente virtual

Windows

```bash
python -m venv .venv
```

Ative o ambiente

PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

---

## 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## 4. Instale o Ollama

Faça o download:

https://ollama.com/download

Depois instale o modelo utilizado:

```bash
ollama pull llama3.2
```

Verifique se o Ollama está em execução:

```bash
ollama list
```

---

# Construção da Base Vetorial

## 1. Extrair os links das FAQs

```bash
python scripts/scraper/extract_links.py
```

Este script acessa a categoria da Central de Ajuda do Spotify e gera uma lista contendo os artigos que serão utilizados.

---

## 2. Baixar os artigos

```bash
python scripts/scraper/download_articles.py
```

Os artigos serão convertidos automaticamente para Markdown e armazenados em:

```text
data/faq_documents/
```

---

## 3. Construir o banco vetorial

```bash
python scripts/scraper/build_vector_db.py
```

Durante esta etapa o sistema:

- lê todos os arquivos Markdown;
- divide os documentos em chunks;
- gera embeddings utilizando Sentence Transformers;
- cria o banco vetorial ChromaDB.

O banco será salvo em:

```text
data/chroma_db/
```

---

## 4. Testar a busca semântica

```bash
python scripts/test_search.py
```

Este script verifica se o ChromaDB está recuperando corretamente os documentos mais relevantes para perguntas de teste.

---

## 5. Executar a API

```bash
uvicorn src.backend.main:app --reload
```

API disponível em:

```text
http://127.0.0.1:8000
```

Documentação Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## 6. Executar o Streamlit

Em outro terminal:

```bash
streamlit run src/frontend/app.py
```

Interface disponível em:

```text
http://localhost:8501
```

---

# Arquitetura

```text
                    Spotify Support
                           │
                           ▼
                    Web Scraper
                           │
                           ▼
                 Markdown Documents
                           │
                           ▼
           RecursiveCharacterTextSplitter
                           │
                           ▼
             Sentence Transformers
                           │
                           ▼
                     ChromaDB
                           ▲
                           │
                 Busca Semântica
                           ▲
                           │
                   Pergunta do Usuário
                           │
                           ▼
                 Documentos Relevantes
                           │
                           ▼
               Construção do Contexto
                           │
                           ▼
                     Ollama (Llama 3.2)
                           │
                           ▼
                Resposta + Fontes Utilizadas
```

---

# Coleta dos Documentos

As FAQs utilizadas pelo chatbot são obtidas automaticamente a partir da Central de Ajuda do Spotify.

O scraper realiza as seguintes etapas:

- navega pelas categorias desejadas;
- extrai os links dos artigos;
- converte cada página para Markdown;
- preserva títulos e estrutura dos documentos;
- prepara os arquivos para indexação no banco vetorial.

Isso facilita futuras atualizações da base de conhecimento, bastando executar novamente os scripts de scraping e reconstrução da base vetorial.

---

# Estratégia RAG

O pipeline de Retrieval-Augmented Generation segue as etapas abaixo:

1. Divisão dos documentos utilizando `RecursiveCharacterTextSplitter`;
2. Geração de embeddings com `all-MiniLM-L6-v2`;
3. Armazenamento dos vetores no ChromaDB;
4. Busca semântica por similaridade;
5. Recuperação dos documentos mais relevantes (Top-K);
6. Construção do contexto enviado ao modelo;
7. Geração da resposta utilizando o Llama 3.2.

Todo o conhecimento utilizado pelo modelo provém exclusivamente dos documentos indexados.

---

# Exemplo de Consulta

### Pergunta

```text
Como criar uma playlist?
```

### Resposta

```text
Para criar uma playlist no Spotify:

1. Abra o aplicativo do Spotify.
2. Clique em "Sua Biblioteca".
3. Selecione "Criar Playlist".
4. Informe um nome para a playlist.
5. Adicione músicas pesquisando artistas, álbuns ou faixas.

Fonte:
Criar e editar playlists
https://support.spotify.com/
```

---

# Diferenciais do Projeto

- Pipeline completo de RAG desenvolvido do zero.
- Execução totalmente local utilizando Ollama.
- Construção automática do banco vetorial.
- Scraping automático da Central de Ajuda do Spotify.
- Busca semântica baseada em embeddings.
- Separação entre Backend (FastAPI) e Frontend (Streamlit).
- Banco vetorial persistente utilizando ChromaDB.
- Código organizado em módulos para facilitar manutenção e expansão.

---

# Próximas Melhorias

- Reranking utilizando Cross Encoder
- Hybrid Search (BM25 + Embeddings)
- Streaming das respostas
- Cache de embeddings
- Atualização incremental da base vetorial
- Suporte a múltiplas categorias da Central de Ajuda do Spotify
- Avaliação automática do RAG com Ragas
- Observabilidade utilizando LangSmith
- Testes unitários e de integração
- Deploy completo utilizando Docker Compose

---

# Autor

**Cauã Souza Almeida**

Projeto desenvolvido como desafio técnico para demonstrar conhecimentos em:

- Retrieval-Augmented Generation (RAG)
- Engenharia de Dados
- Processamento de Linguagem Natural (NLP)
- Busca Semântica
- LangChain
- ChromaDB
- FastAPI
- Streamlit
- Ollama
- Modelos Open Source executados localmente