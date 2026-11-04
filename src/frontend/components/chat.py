# src/frontend/components/chat.py

"""
Componente de chat do Streamlit
"""

import html
from typing import Dict, List, Optional

import streamlit as st

ROTULOS = {"user": "Você", "assistant": "Assistente"}


def _render_role(role: str):
    # A classe msg-user / msg-assistant é usada no CSS (app.py) para dar
    # fundo diferente a cada lado da conversa.
    st.markdown(
        f'<div class="msg-role msg-{role}">{ROTULOS[role]}</div>',
        unsafe_allow_html=True,
    )


def _render_details(message: Dict):
    """Fontes e metadados abaixo da resposta do assistente."""
    sources = message.get("sources") or []
    titles = message.get("source_titles") or sources

    if sources:
        itens = "".join(
            f'<li><a href="{html.escape(url)}" target="_blank">{html.escape(titulo)}</a></li>'
            for titulo, url in zip(titles, sources)
        )
        st.markdown(
            f'<div class="msg-sources">Fontes<ol>{itens}</ol></div>',
            unsafe_allow_html=True,
        )

    if "response_time" in message:
        partes = []
        if message.get("fallback"):
            partes.append("Sem resposta na base")
        elif message.get("similarity"):
            partes.append(f"Similaridade {message['similarity']:.0%}")
        partes.append(f"{message['response_time']:.1f} s".replace(".", ","))
        st.markdown(
            f'<div class="msg-meta">{" · ".join(partes)}</div>',
            unsafe_allow_html=True,
        )


def display_message(message: Dict):
    """
    Exibe uma mensagem no chat

    Args:
        message: Dicionário com role e content
    """
    with st.chat_message(message["role"]):
        _render_role(message["role"])
        st.markdown(message["content"])
        if message["role"] == "assistant":
            _render_details(message)


def handle_user_input(
    prompt: str,
    api_client,
    messages: List[Dict],
    top_k: Optional[int] = None,
) -> List[Dict]:
    """
    Processa a entrada do usuário e obtém resposta

    Args:
        prompt: Pergunta do usuário
        api_client: Cliente da API
        messages: Lista de mensagens
        top_k: número de trechos a buscar (slider da sidebar)

    Returns:
        Lista atualizada de mensagens
    """
    user_message = {"role": "user", "content": prompt}
    messages.append(user_message)
    display_message(user_message)

    with st.chat_message("assistant"):
        _render_role("assistant")
        with st.spinner("Buscando nos artigos e escrevendo a resposta..."):
            response = api_client.ask_question(prompt, top_k=top_k)

    erro = "error" in response
    messages.append({
        "role": "assistant",
        "content": response["answer"],
        "sources": [] if erro else response.get("sources", []),
        "source_titles": [] if erro else response.get("source_titles", []),
        "similarity": response.get("similarity", 0.0),
        "response_time": response.get("response_time", 0),
        "fallback": response.get("fallback", erro),
    })

    return messages
