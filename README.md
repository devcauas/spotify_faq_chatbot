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

- Python 3.11
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
- sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

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
│   │   ├── save_markdown.py
│   │   └── config.py
│   │
│   └── tests/
│       ├── analyze_chunks.py
│       ├── inspect_vector_store.py
│       └── test_search.py
│
├── src/
│   ├── backend/
│   │   ├── core/
│   │   │   ├── rag_engine.py
│   │   │   ├── vector_store.py
│   │   │   └── prompts.py
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
├── requirements-backend.txt
├── requirements-frontend.txt
├── requirements.txt
├── requirements_scraper.txt
└── README.md
```

---

# Executando com Docker (recomendado)

Esta é a forma mais simples de rodar o projeto: o Docker Compose sobe o Ollama, baixa o modelo, constrói a base vetorial e inicia a API e a interface, sem precisar instalar Python ou Ollama na máquina.

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) em execução
- Cerca de 15 GB livres em disco (imagens + modelo llama3.2)
- Pelo menos 6 GB de RAM disponíveis para o Docker

> **Windows (WSL 2):** por padrão o Docker pode ficar com pouca memória. Para aumentar, crie o arquivo `C:\Users\<seu-usuario>\.wslconfig` com:
>
> ```ini
> [wsl2]
> memory=8GB
> ```
>
> Depois execute `wsl --shutdown` e reinicie o Docker Desktop.

## 1. Clone o projeto e suba os containers

```bash
git clone https://github.com/SEU-USUARIO/spotify_faq_chatbot.git

cd spotify_faq_chatbot

docker compose up --build
```

Na primeira execução o processo é mais demorado, pois as imagens são construídas e o modelo llama3.2 (~2 GB) é baixado. Os serviços sobem nesta ordem:

| Serviço | Função |
|---|---|
| `ollama` | Servidor do Ollama que executa o Llama 3.2 |
| `ollama-pull` | Baixa o modelo llama3.2 e encerra (o modelo fica salvo no volume `ollama_data`) |
| `backend` | API FastAPI com o motor RAG; a base vetorial é construída durante o build da imagem |
| `frontend` | Interface Streamlit |

## 2. Acesse a aplicação

- Interface: http://localhost:8501
- API: http://localhost:8000
- Documentação Swagger: http://localhost:8000/docs

> A primeira pergunta pode demorar alguns minutos, pois o modelo é carregado na memória. As perguntas seguintes são mais rápidas. Como o Ollama roda em CPU, cada resposta leva em média de 20 a 60 segundos, dependendo da máquina.

## Comandos úteis

```bash
# Subir em segundo plano
docker compose up -d

# Acompanhar os logs
docker compose logs -f backend

# Parar os containers
docker compose down

# Parar e apagar também o modelo baixado (volume ollama_data)
docker compose down -v
```

Se os documentos em `data/faq_documents/` forem alterados, reconstrua a imagem do backend para recriar a base vetorial:

```bash
docker compose up --build backend
```

---

# Executando localmente (sem Docker)

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

> **Atenção:** os artigos já coletados estão versionados em `data/faq_documents/`, então os passos 1 e 2 só são necessários para atualizar ou ampliar a base de conhecimento. O passo 3 é **obrigatório** na primeira execução local, pois o banco vetorial (`data/chroma_db/`) não é versionado.

Os scripts de scraping usam dependências próprias, que não fazem parte do `requirements.txt`:

```bash
pip install -r requirements_scraper.txt
```

## 1. Extrair os links das FAQs

```bash
python scripts/scraper/extract_links.py
```

Este script parte da página inicial da Central de Ajuda do Spotify e segue os links entre artigos até reunir `MAX_ARTICLES` (300) artigos de todas as categorias. O HTML de cada página fica em cache em `data/raw/html/`, para a etapa seguinte não precisar baixar de novo. Há uma pausa de 3 segundos entre as requisições: com intervalos menores, o site devolve erro 429 e bloqueia o IP por alguns minutos.

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
python scripts/tests/test_search.py
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

- parte da página inicial e segue os links entre artigos;
- baixa cada página com uma requisição HTTP simples (a Central de Ajuda é renderizada no servidor);
- guarda só o corpo do artigo, descartando "Artigos relacionados" e o menu da categoria;
- converte listas de passos e tabelas para Markdown;
- preserva títulos e estrutura dos documentos;
- prepara os arquivos para indexação no banco vetorial.

Isso facilita futuras atualizações da base de conhecimento, bastando executar novamente os scripts de scraping e reconstrução da base vetorial.

---

# Estratégia RAG

O pipeline de Retrieval-Augmented Generation segue as etapas abaixo:

1. Divisão dos documentos utilizando `RecursiveCharacterTextSplitter` (chunks de 500 caracteres, cada um com o título do artigo);
2. Geração de embeddings com `paraphrase-multilingual-MiniLM-L12-v2`, que entende português;
3. Armazenamento dos vetores no ChromaDB;
4. Busca semântica por similaridade; abaixo de 0,4 o sistema responde que não encontrou, sem chamar o modelo;
5. Os chunks encontrados indicam os artigos mais relevantes (no máximo 2);
6. O contexto enviado ao modelo é o texto completo desses artigos, não fragmentos soltos;
7. Geração da resposta utilizando o Llama 3.2, com temperatura 0,1 e um prompt que proíbe passos e nomes de menu que não estejam no artigo.

Todo o conhecimento utilizado pelo modelo provém exclusivamente dos documentos indexados.

---

# Exemplo de Consulta

### Pergunta

```text
Como cancelar meu Premium?
```

### Resposta

```text
Para cancelar seu plano Premium, acesse Gerenciar seu plano e selecione
Cancelar assinatura. Sua conta continuará no Premium até a próxima data de
cobrança. Depois disso, ela passará para a versão grátis. Você não vai perder
suas playlists e músicas salvas quando passar para o Free. Você ainda vai poder
entrar e curtir seu som, mas com anúncios.

Fonte:
https://support.spotify.com/br-pt/article/cancel-premium/
```

> A base de conhecimento atual tem **211 artigos** da Central de Ajuda, de todas as categorias que a coleta alcança a partir da página inicial (conta e login, planos, pagamentos, download offline, dispositivos, privacidade etc.). Perguntas fora desse escopo recebem uma resposta de fallback informando que a informação não foi encontrada.

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
- Avaliação automática do RAG com Ragas
- Observabilidade utilizando LangSmith
- Testes unitários e de integração
- Suporte a GPU no Docker Compose para acelerar o Ollama

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
