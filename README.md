# Spotify FAQ Chatbot

Chatbot de perguntas e respostas desenvolvido para responder dúvidas frequentes sobre o Spotify utilizando **Retrieval-Augmented Generation (RAG)** com modelos de linguagem executados localmente.

O projeto foi desenvolvido utilizando **FastAPI**, **LangChain**, **ChromaDB**, **Ollama** e **Streamlit**, sem utilizar APIs pagas.

---

# Demonstração

Fluxo da aplicação:

1. O usuário envia uma pergunta.
2. A pergunta é convertida em embeddings.
3. O ChromaDB realiza a busca semântica.
4. Os documentos relevantes são enviados para a LLM.
5. A LLM gera uma resposta baseada exclusivamente no FAQ.
6. O sistema retorna a resposta juntamente com as fontes utilizadas.

---

# Funcionalidades

- Chat baseado em documentos FAQ
- Busca semântica utilizando embeddings
- Banco vetorial ChromaDB
- Integração com Ollama
- Modelo LLM executando localmente
- Respostas fundamentadas nos documentos
- Exibição das fontes utilizadas
- API REST utilizando FastAPI
- Interface Web utilizando Streamlit
- Docker para facilitar a execução

---

# Tecnologias

## Backend

- Python 3.10
- FastAPI
- LangChain
- ChromaDB
- Sentence Transformers

## Frontend

- Streamlit

## Modelo de IA

- Ollama
- llama3.2

---

# Estrutura do Projeto

```text
spotify_faq_chatbot
│
├── data/
│   ├── chroma_db/
│   ├── faq_documents/
│   └── test_*/
│
├── scripts/
│   ├── process_documents.py
│   ├── analyze_chunks.py
│   ├── inspect_vector_store.py
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

https://ollama.com/download

Após instalar, baixe o modelo utilizado:

```bash
ollama pull llama3.2
```

Verifique se o Ollama está executando:

```bash
ollama list
```

---

## 5. Processar os documentos

Caso seja a primeira execução, gere o banco vetorial:

```bash
python scripts/process_documents.py
```

O ChromaDB será criado automaticamente em:

```
data/chroma_db/
```

---

## 6. Testar o motor RAG

```bash
python scripts/test_rag.py
```

Se tudo estiver correto, serão exibidas respostas para perguntas de teste.

---

## 7. Executar a API

```bash
uvicorn src.backend.main:app --reload
```

A API ficará disponível em:

```
http://127.0.0.1:8000
```

Documentação Swagger:

```
http://127.0.0.1:8000/docs
```

---

## 8. Executar o Streamlit

Em outro terminal:

```bash
streamlit run src/frontend/app.py
```

A interface será aberta em:

```
http://localhost:8501
```

---

# Arquitetura

```text
Usuário
      │
      ▼
 Streamlit
      │
      ▼
 FastAPI
      │
      ▼
RAG Engine
      │
      ▼
ChromaDB
      │
      ▼
Documentos FAQ
      │
      ▼
Ollama (llama3.2)
      │
      ▼
Resposta
```

---

# Exemplo de consulta

Pergunta

```
Como criar uma playlist?
```

Resposta

```
Para criar uma playlist:

1. Clique em "Sua Biblioteca";
2. Clique em "Criar Playlist";
3. Defina um nome;
4. Adicione músicas.

Fonte:
spotify_faq.txt
```

---

# Próximas melhorias

- Upload de novos documentos pela interface
- Suporte a PDF e Markdown
- Histórico persistente de conversas
- Streaming das respostas
- Deploy em nuvem
- Avaliação automática das respostas
- Testes unitários e integração
- Observabilidade e métricas

---

# Autor

Cauã Souza Almeida

Projeto desenvolvido como desafio técnico para construção de um chatbot FAQ utilizando RAG, LangChain e modelos open source executados localmente.