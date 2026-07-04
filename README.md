# Spotify FAQ Chatbot (RAG Local)

Este é um chatbot inteligente de FAQ projetado para responder a dúvidas de usuários do Spotify sobre pagamentos, cobranças e funcionalidades do plano Premium. O sistema utiliza a técnica de **RAG (Retrieval-Augmented Generation)** com modelos de IA executados de forma **100% local**, garantindo custo zero e independência de APIs pagas.

---

## Funcionalidades

* **Interface de Chat Amigável:** Tela construída em Streamlit com histórico de conversa, campo de pergunta e indicador de carregamento.
* **Busca Semântica Avançada:** Utilização de banco vetorial para encontrar os trechos mais relevantes do FAQ com base no contexto da pergunta.
* **Geração de Resposta Confiável:** Integração com LLM local (via Ollama) configurada para evitar alucinações, respondendo estritamente com base nos documentos fornecidos.
* **Transparência (Respostas com Fontes):** O chatbot exibe quais arquivos e trechos específicos foram utilizados para gerar a resposta.
* **Ingestão de Documentos:** Suporte automático para múltiplos arquivos nos formatos PDF e Markdown.

---

## Arquitetura & Pipeline do Sistema

O fluxo da informação segue o pipeline padrão de RAG:
1. O usuário envia uma pergunta pela interface (Streamlit).
2. O sistema gera o embedding da pergunta através do framework LangChain.
3. O banco vetorial (ChromaDB) busca os documentos e trechos mais semanticamente alinhados à dúvida.
4. O contexto extraído é enviado junto com a pergunta para a LLM local (Ollama).
5. A LLM gera a resposta final baseada estritamente no contexto.
6. O sistema retorna a resposta na tela acompanhada das fontes utilizadas.

---

## Stack Tecnológica

* **Backend:** Python 3.10+ & FastAPI
* **Frontend:** Streamlit
* **Orquestração de IA:** LangChain
* **Banco Vetorial:** ChromaDB
* **LLM & Embeddings Locais:** Ollama (`llama3` ou `mistral`)

---

## Estrutura do Projeto

```text
spotify-faq-chatbot/
├── data/                  # Pasta para armazenar os PDFs e Markdowns do FAQ
├── src/
│   ├── backend/
│   │   ├── main.py        # API FastAPI
│   │   └── rag_engine.py  # Lógica de indexação e busca do LangChain
│   └── frontend/
│       └── app.py         # Interface Streamlit
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
