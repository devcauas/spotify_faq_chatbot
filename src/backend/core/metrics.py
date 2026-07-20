from dataclasses import dataclass
from typing import List, Dict
import time
import json

@dataclass
class RAGMetrics:
    """Métricas do sistema RAG"""
    
    # Métricas de performance
    total_queries: int = 0
    avg_response_time: float = 0.0
    avg_retrieval_time: float = 0.0
    avg_generation_time: float = 0.0
    
    # Métricas de qualidade
    avg_similarity: float = 0.0
    high_similarity_count: int = 0  # > 0.7
    medium_similarity_count: int = 0  # 0.5 - 0.7
    low_similarity_count: int = 0  # < 0.5
    
    # Métricas de resposta
    response_count: int = 0
    fallback_count: int = 0  # Quando usou resposta padrão
    error_count: int = 0
    
    # Histórico para análise
    queries_history: List[Dict] = None
    
    def __post_init__(self):
        self.queries_history = []
    
    def record_query(self, query: str, result: Dict):
        """Registra uma consulta e suas métricas"""
        self.total_queries += 1
        self.response_count += 1
        
        # Performance
        self.avg_response_time = (
            (self.avg_response_time * (self.total_queries - 1) + 
             result.get('response_time', 0)) / self.total_queries
        )
        
        # Similaridade
        similarity = result.get('max_similarity', 0)
        self.avg_similarity = (
            (self.avg_similarity * (self.total_queries - 1) + 
             similarity) / self.total_queries
        )
        
        if similarity > 0.7:
            self.high_similarity_count += 1
        elif similarity > 0.5:
            self.medium_similarity_count += 1
        else:
            self.low_similarity_count += 1
        
        # Fallbacks
        if result.get('is_fallback', False):
            self.fallback_count += 1
        
        # Histórico
        self.queries_history.append({
            'query': query,
            'similarity': similarity,
            'response_time': result.get('response_time', 0),
            'sources_used': result.get('sources', []),
            'was_fallback': result.get('is_fallback', False)
        })
        
        # Mantém apenas últimos 1000
        if len(self.queries_history) > 1000:
            self.queries_history = self.queries_history[-1000:]
    
    def get_report(self) -> Dict:
        """Gera relatório detalhado das métricas"""
        total = self.total_queries or 1  # Evita divisão por zero
        
        return {
            'resumo': {
                'total_consultas': self.total_queries,
                'tempo_resposta_medio': f"{self.avg_response_time:.2f}s",
                'similaridade_media': f"{self.avg_similarity:.2%}",
            },
            'qualidade': {
                'alta_similaridade': f"{self.high_similarity_count/total:.1%}",
                'media_similaridade': f"{self.medium_similarity_count/total:.1%}",
                'baixa_similaridade': f"{self.low_similarity_count/total:.1%}",
                'fallbacks': f"{self.fallback_count/total:.1%}",
            },
            'performance': {
                'media_busca': f"{self.avg_retrieval_time:.2f}s",
                'media_geracao': f"{self.avg_generation_time:.2f}s",
            }
        }
    
    def save_report(self, filename: str = "metrics_report.json"):
        """Salva relatório em arquivo"""
        report = self.get_report()
        report['historico'] = self.queries_history[-20:]  # Últimas 20
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)