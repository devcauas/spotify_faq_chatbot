# src/frontend/components/sidebar.py

"""
Componente da barra lateral do Streamlit
"""

import streamlit as st
from typing import Dict


def render_sidebar(api_client) -> Dict:
    """
    Renderiza a barra lateral com informações do sistema

    Args:
        api_client: Cliente da API

    Returns:
        Dicionário com configurações
    """
    with st.sidebar:
        st.markdown("**Sobre este assistente**")
        st.caption(
            "Busca os trechos mais parecidos com a pergunta nos artigos da "
            "Central de Ajuda e gera a resposta com um modelo de linguagem "
            "que roda no próprio computador."
        )

        is_healthy, health_data = api_client.health_check()
        stats = api_client.get_stats() if is_healthy else {"error": True}

        linhas = [
            f"Servidor: {'conectado' if is_healthy else 'desconectado'}",
            "Modelo: Llama 3.2, via Ollama",
            "Busca: ChromaDB",
        ]
        if "error" not in stats:
            linhas.insert(1, f"Base: {stats.get('total_documents', 0)} trechos de artigos")
        st.caption("  \n".join(linhas))

        if not is_healthy:
            st.caption(health_data.get("error", "Erro desconhecido"))

        st.divider()

        top_k = st.slider(
            "Trechos consultados por pergunta",
            min_value=1,
            max_value=6,
            value=4,
            help="Quantos trechos de artigos o modelo recebe para responder",
        )

        if st.button("Limpar conversa", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.caption(
            "Tudo é processado localmente: as perguntas não são enviadas "
            "para serviços na nuvem."
        )

    return {"top_k": top_k}
