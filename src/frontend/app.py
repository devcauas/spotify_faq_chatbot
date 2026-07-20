# src/frontend/app.py

"""
Aplicação Streamlit para o Spotify FAQ Chatbot
"""

import streamlit as st
import sys
from pathlib import Path

# Adiciona src ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.frontend.utils.api_client import APIClient
from src.frontend.components.chat import display_message, handle_user_input
from src.frontend.components.sidebar import render_sidebar

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================

st.set_page_config(
    page_title="🎵 Spotify FAQ Chatbot",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO
# ============================================

st.markdown("""
<style>
    /* Título principal */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1DB954;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Chat messages */
    .stChatMessage {
        padding: 0.5rem 1rem;
    }
    
    /* Botões */
    .stButton button {
        background-color: #1DB954;
        color: white;
        font-weight: 600;
    }
    
    .stButton button:hover {
        background-color: #1ed760;
        color: white;
    }
    
    /* Métricas */
    [data-testid="metric-container"] {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INICIALIZAÇÃO
# ============================================

# Inicializa o cliente da API
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()

# Inicializa o histórico de mensagens
if "messages" not in st.session_state:
    # Mensagem de boas-vindas
    st.session_state.messages = [{
        "role": "assistant",
        "content": """👋 Olá! Sou o assistente do Spotify.

Posso ajudar com perguntas sobre:
- 🎵 Como criar playlists
- 💰 Spotify Premium e preços
- 🔗 Compartilhar músicas e playlists
- 📱 Funcionalidades do app

**O que você gostaria de saber?**""",
        "sources": [],
        "similarity": 1.0,
        "response_time": 0,
        "fallback": False
    }]

# ============================================
# HEADER
# ============================================

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<p class="main-title" style="text-align: center;">🎵 Spotify FAQ Chatbot</p>', 
                unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle" style="text-align: center;">Pergunte sobre o Spotify e receba respostas baseadas em FAQs oficiais</p>', 
                unsafe_allow_html=True)

st.markdown("---")

# ============================================
# SIDEBAR
# ============================================

config = render_sidebar(st.session_state.api_client)

# ============================================
# ÁREA PRINCIPAL - CHAT
# ============================================

# Container para mensagens
chat_container = st.container()

# Exibe mensagens existentes
with chat_container:
    for message in st.session_state.messages:
        display_message(message)

# ============================================
# INPUT DO USUÁRIO
# ============================================

# Input no final da página
prompt = st.chat_input(
    "Digite sua pergunta sobre o Spotify...",
    key="chat_input",
    disabled=not st.session_state.api_client.health_check()[0]
)

# Processa a entrada
if prompt:
    st.session_state.messages = handle_user_input(
        prompt,
        st.session_state.api_client,
        st.session_state.messages
    )
    st.rerun()

# ============================================
# RODAPÉ
# ============================================

st.markdown("---")
st.caption("🔒 Todas as perguntas são processadas localmente usando Ollama • Dados não são enviados para a nuvem")