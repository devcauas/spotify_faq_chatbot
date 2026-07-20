class RAGErrorHandler:
    """Gerencia diferentes tipos de erros no sistema RAG"""
    
    def handle_no_documents(self, question: str) -> str:
        """
        Quando não encontra documentos relevantes.
        """
        return f"""
        Não encontrei informações sobre "{question}" nos documentos disponíveis.
        
        📝 Dicas:
        - Reformule sua pergunta usando palavras-chave diferentes
        - Seja mais específico sobre o que deseja saber
        - Verifique se o tópico é coberto pelas FAQs do Spotify
        
        Perguntas que posso ajudar:
        - Como criar uma playlist?
        - O que é Spotify Premium?
        - Como compartilhar músicas?
        """
    
    def handle_low_similarity(self, question: str, max_similarity: float) -> str:
        """
        Quando a similaridade é baixa (< 0.6).
        """
        return f"""
        Encontrei algumas informações, mas elas não são muito relevantes para sua pergunta.
        
        🔍 O que encontrei tem relevância de {max_similarity:.2%}.
        
        💡 Sugestão: Tente ser mais específico ou usar termos diferentes.
        
        Exemplo:
        - Em vez de "preços" → "Quanto custa o Spotify Premium?"
        - Em vez de "música" → "Como compartilhar uma música?"
        """
    
    def handle_llm_timeout(self) -> str:
        """
        Quando o Ollama não responde em tempo hábil.
        """
        return """
        ⏳ O modelo de IA está demorando para responder.
        
        🔄 Tentando reconectar...
        - Verifique se o Ollama está rodando
        - O modelo pode estar carregando pela primeira vez
        - Tente novamente em alguns segundos
        
        Se o problema persistir, reinicie o Ollama com:
        `ollama restart`
        """
    
    def handle_complex_question(self) -> str:
        """
        Quando a pergunta é muito longa ou complexa.
        """
        return """
        📚 Sua pergunta é bastante complexa.
        
        💡 Sugestão: Divida em perguntas menores:
        1. Faça perguntas específicas sobre um tópico de cada vez
        2. Use palavras-chave simples
        3. Seja direto sobre o que quer saber
        
        Exemplo:
        ❌ "Como funciona o Spotify Premium em relação a playlists e compartilhamento?"
        ✅ "Quais são os benefícios do Spotify Premium?"
        ✅ "Como compartilhar uma playlist?"
        """