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
        st.title("🎵 Spotify FAQ")
        st.markdown("---")
        
        # Status da API
        st.subheader("🔌 Conexão")
        is_healthy, health_data = api_client.health_check()
        
        if is_healthy:
            st.success("✅ API conectada")
        else:
            st.error("❌ API desconectada")
            st.caption(health_data.get("error", "Erro desconhecido"))
        
        # Estatísticas
        st.subheader("📊 Estatísticas")
        stats = api_client.get_stats()
        
        if "error" not in stats:
            col1, col2 = st.columns(2)
            col1.metric("Chunks", stats.get("total_documents", 0))
            col2.metric("Tamanho", f"{stats.get('chunk_size', 0)} chars")
            
            st.caption(f"📁 {stats.get('persist_directory', 'N/A')}")
            st.caption(f"🔧 {stats.get('vector_store_type', 'N/A')}")
        else:
            st.warning("Não foi possível obter estatísticas")
        
        st.markdown("---")
        
        # Configurações
        st.subheader("⚙️ Configurações")
        
        top_k = st.slider(
            "Número de fontes (top_k)",
            min_value=1,
            max_value=5,
            value=3,
            help="Quantos documentos usar para responder"
        )
        
        st.caption("🧠 Modelo: llama3.2")
        st.caption("📚 Banco: ChromaDB")
        
        # Botões
        st.markdown("---")
        
        if st.button("🗑️ Limpar conversa", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("🔄 Reiniciar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        # Rodapé
        st.markdown("---")
        st.caption("💡 Dica: Seja específico nas perguntas")
        st.caption(f"v1.0.0 • LangChain + Ollama")
    
    return {"top_k": top_k}