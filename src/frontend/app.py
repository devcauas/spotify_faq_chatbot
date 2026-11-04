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
    page_title="Central de Ajuda do Spotify | Assistente",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO
# ============================================

# As cores do tema ficam em .streamlit/config.toml; aqui só o que o tema
# não cobre: faixa do título, avatares, cores das mensagens e das fontes.
st.markdown("""
<style>
    /* Faixa em degradê que o Streamlit põe no topo da página */
    [data-testid="stDecoration"] {
        display: none;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        padding-top: 2.5rem;
        max-width: 760px;
    }

    /* Faixa do título em verde escuro: a cor da marca sem o neon */
    .app-header {
        background: #1F6B4F;
        color: #FAF8F3;
        border-radius: 10px;
        padding: 1.3rem 1.5rem 1.1rem 1.5rem;
        margin-bottom: 1.5rem;
    }

    .app-title {
        font-size: 1.5rem;
        font-weight: 650;
        letter-spacing: -0.01em;
        margin: 0 0 0.3rem 0;
        color: #FAF8F3;
    }

    .app-subtitle {
        color: #CFE3D8;
        font-size: 0.93rem;
        margin: 0;
    }

    /* Sem avatares de robô: quem fala é indicado pelo rótulo */
    [data-testid="chatAvatarIcon-user"],
    [data-testid="chatAvatarIcon-assistant"],
    [data-testid="stChatMessage"] > img {
        display: none;
    }

    [data-testid="stChatMessage"] {
        padding: 0.9rem 1.1rem;
        border-radius: 10px;
        gap: 0;
    }

    [data-testid="stChatMessage"]:has(.msg-user) {
        background: #E3EEE7;
        margin-left: 3rem;
    }

    [data-testid="stChatMessage"]:has(.msg-assistant) {
        background: #FFFFFF;
        border: 1px solid #DCE6DF;
        border-left: 4px solid #1F6B4F;
    }

    .msg-role {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 0.35rem;
    }

    .msg-role.msg-user {
        color: #1F6B4F;
    }

    .msg-role.msg-assistant {
        color: #B5651D;
    }

    .msg-sources {
        border-top: 1px solid #DCE6DF;
        margin-top: 0.8rem;
        padding-top: 0.6rem;
        font-size: 0.85rem;
        color: #4A5550;
    }

    .msg-sources ol {
        margin: 0.2rem 0 0 1.1rem;
        padding: 0;
    }

    .msg-sources a {
        color: #1F6B4F;
        font-weight: 500;
    }

    .msg-meta {
        color: #7A847F;
        font-size: 0.78rem;
        margin-top: 0.5rem;
    }

    .stButton button {
        border-radius: 8px;
        border: 1px solid #BFD5C7;
        background: #FFFFFF;
        color: #1F6B4F;
        font-weight: 500;
    }

    .stButton button:hover {
        background: #E3EEE7;
        border-color: #1F6B4F;
        color: #174F3B;
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
    st.session_state.messages = []

EXEMPLOS = [
    "Como cancelo o Premium?",
    "Como baixo músicas para ouvir offline?",
    "Como mudo meu endereço de e-mail?",
]

# ============================================
# HEADER
# ============================================

st.markdown(
    '<div class="app-header">'
    '<p class="app-title">Assistente da Central de Ajuda do Spotify</p>'
    '<p class="app-subtitle">Responde com base apenas nos artigos oficiais da '
    'Central de Ajuda e mostra de quais artigos tirou cada resposta.</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ============================================
# SIDEBAR
# ============================================

config = render_sidebar(st.session_state.api_client)

# ============================================
# ÁREA PRINCIPAL - CHAT
# ============================================

for message in st.session_state.messages:
    display_message(message)

# Perguntas de exemplo enquanto a conversa está vazia
pergunta_exemplo = None
if not st.session_state.messages:
    st.caption("Exemplos de perguntas")
    for exemplo in EXEMPLOS:
        if st.button(exemplo, use_container_width=True):
            pergunta_exemplo = exemplo

# ============================================
# INPUT DO USUÁRIO
# ============================================

prompt = st.chat_input(
    "Escreva sua pergunta sobre o Spotify",
    key="chat_input",
    disabled=not st.session_state.api_client.health_check()[0]
)

prompt = prompt or pergunta_exemplo
if prompt:
    st.session_state.messages = handle_user_input(
        prompt,
        st.session_state.api_client,
        st.session_state.messages,
        top_k=config["top_k"],
    )
    st.rerun()
