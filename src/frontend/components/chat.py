# src/frontend/components/chat.py

"""
Componente de chat do Streamlit
"""

import streamlit as st
import time
from typing import Dict, List


def display_message(message: Dict):
    """
    Exibe uma mensagem no chat
    
    Args:
        message: Dicionário com role e content
    """
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Se for do assistente e tiver fontes
        if message["role"] == "assistant" and "sources" in message:
            if message["sources"]:
                with st.expander("📁 Ver fontes utilizadas"):
                    for source in message["sources"]:
                        st.text(f"📄 {source}")
            
            # Mostra métricas
            col1, col2, col3 = st.columns(3)
            if "similarity" in message:
                col1.metric("Similaridade", f"{message['similarity']:.1%}")
            if "response_time" in message:
                col2.metric("Tempo", f"{message['response_time']:.1f}s")
            if "fallback" in message:
                status = "⚠️ Fallback" if message["fallback"] else "✅ Normal"
                col3.metric("Status", status)


def handle_user_input(
    prompt: str,
    api_client,
    messages: List[Dict]
) -> List[Dict]:
    """
    Processa a entrada do usuário e obtém resposta
    
    Args:
        prompt: Pergunta do usuário
        api_client: Cliente da API
        messages: Lista de mensagens
        
    Returns:
        Lista atualizada de mensagens
    """
    # Adiciona mensagem do usuário
    messages.append({"role": "user", "content": prompt})
    
    # Mostra mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Obtém resposta da API
    with st.chat_message("assistant"):
        with st.spinner("🤔 Pensando..."):
            response = api_client.ask_question(prompt)
        
        # Mostra resposta
        if "error" in response:
            st.error(response["answer"])
            response_display = response["answer"]
            sources = []
            similarity = 0.0
            fallback = True
            response_time = response.get("response_time", 0)
        else:
            st.markdown(response["answer"])
            response_display = response["answer"]
            sources = response.get("sources", [])
            similarity = response.get("similarity", 0.0)
            fallback = response.get("fallback", False)
            response_time = response.get("response_time", 0)
            
            # Mostra métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Similaridade", f"{similarity:.1%}")
            col2.metric("Tempo", f"{response_time:.1f}s")
            col3.metric("Status", "⚠️ Fallback" if fallback else "✅ OK")
            
            # Mostra fontes
            if sources:
                with st.expander("📁 Ver fontes utilizadas"):
                    for source in sources:
                        st.text(f"📄 {source}")
    
    # Adiciona resposta ao histórico
    messages.append({
        "role": "assistant",
        "content": response_display,
        "sources": sources if not response.get("error") else [],
        "similarity": similarity,
        "response_time": response_time,
        "fallback": fallback
    })
    
    return messages