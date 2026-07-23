# src/frontend/utils/api_client.py

"""
Cliente para comunicação com a API FastAPI
"""

import requests
import time
from typing import Dict, Optional, Tuple


class APIClient:
    """Cliente para a API do chatbot"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 180
    
    def health_check(self) -> Tuple[bool, Dict]:
        """Verifica se a API está saudável"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            if response.status_code == 200:
                return True, response.json()
            return False, {"error": f"Status: {response.status_code}"}
        except requests.exceptions.ConnectionError:
            return False, {"error": "Não foi possível conectar à API"}
        except requests.exceptions.Timeout:
            return False, {"error": "Timeout ao conectar à API"}
        except Exception as e:
            return False, {"error": str(e)}
    
    def get_stats(self) -> Dict:
        """Obtém estatísticas do sistema"""
        try:
            response = requests.get(
                f"{self.base_url}/stats",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return {"error": f"Status: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def ask_question(self, question: str) -> Dict:
        """
        Envia uma pergunta para a API
        
        Args:
            question: Pergunta do usuário
            
        Returns:
            Dicionário com resposta e metadados
        """
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={"question": question},
                timeout=self.timeout
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                data['api_response_time'] = elapsed
                return data
            else:
                return {
                    "error": f"Erro {response.status_code}",
                    "answer": f"❌ Erro ao processar pergunta: {response.status_code}",
                    "sources": [],
                    "similarity": 0.0,
                    "response_time": elapsed,
                    "fallback": True
                }
                
        except requests.exceptions.Timeout:
            return {
                "error": "Timeout",
                "answer": "⏳ O modelo está demorando para responder. Tente novamente.",
                "sources": [],
                "similarity": 0.0,
                "response_time": time.time() - start_time,
                "fallback": True
            }
        except requests.exceptions.ConnectionError:
            return {
                "error": "ConnectionError",
                "answer": "❌ Não foi possível conectar à API. Verifique se o servidor está rodando.",
                "sources": [],
                "similarity": 0.0,
                "response_time": time.time() - start_time,
                "fallback": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "answer": f"❌ Erro: {str(e)}",
                "sources": [],
                "similarity": 0.0,
                "response_time": time.time() - start_time,
                "fallback": True
            }