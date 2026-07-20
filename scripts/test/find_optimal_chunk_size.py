"""
Teste abrangente de configurações de chunk com diferentes tipos de pergunta
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.core.vector_store import VectorStoreManager
import shutil
import json
from typing import Dict, List
import time

class ComprehensiveChunkTester:
    """Testa configurações de chunk em diferentes cenários"""
    
    def __init__(self):
        self.results = []
        
        # Categorias de perguntas para testar
        self.test_cases = {
            "perguntas_diretas": [
                "Como criar uma playlist?",
                "O que é Spotify Premium?",
                "Como compartilhar uma música?",
            ],
            "perguntas_similares": [
                "Como fazer uma playlist nova?",
                "Me explique o Spotify Premium",
                "Como enviar uma música para alguém?",
            ],
            "perguntas_abertas": [
                "Fale sobre playlists",
                "O que você sabe sobre Spotify?",
                "Como funciona o compartilhamento?",
            ],
            "perguntas_inexistentes": [
                "Como fazer upload de músicas?",
                "O que é Spotify HiFi?",
                "Como criar um podcast?",
            ]
        }
        
    def test_configuration(self, chunk_size: int, chunk_overlap: int) -> Dict:
        """Testa uma configuração específica com todas as categorias"""
        
        test_dir = f"data/test_chunk_{chunk_size}_{chunk_overlap}"
        
        # Limpa diretório anterior
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)
        
        # Cria vector store
        start_time = time.time()
        manager = VectorStoreManager(
            persist_directory=test_dir,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        docs = manager.load_documents_from_directory("data/faq_documents")
        chunks = manager.process_documents(docs)
        manager.create_vector_store(chunks)
        process_time = time.time() - start_time
        
        # Testa cada categoria
        category_results = {}
        for category, queries in self.test_cases.items():
            query_results = []
            for query in queries:
                results = manager.vector_store.similarity_search_with_score(query, k=1)
                if results:
                    doc, score = results[0]
                    similarity = 1 / (1 + score)
                    query_results.append({
                        "query": query,
                        "similarity": similarity,
                        "preview": doc.page_content[:100]
                    })
            
            avg_sim = sum(r["similarity"] for r in query_results) / len(query_results)
            category_results[category] = {
                "avg_similarity": avg_sim,
                "queries": query_results
            }
        
        # Métricas gerais
        all_similarities = []
        for category in category_results.values():
            for query in category["queries"]:
                all_similarities.append(query["similarity"])
        
        return {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "num_chunks": len(chunks),
            "process_time": process_time,
            "overall_avg_similarity": sum(all_similarities) / len(all_similarities),
            "category_results": category_results,
            "chunk_examples": [
                {"id": i, "text": chunk.page_content[:150]} 
                for i, chunk in enumerate(chunks[:3])
            ]
        }
    
    def run_tests(self):
        """Executa testes com configurações variadas"""
        
        configs = [
            (50, 5),    # Muito pequeno
            (100, 10),  # Pequeno (seu vencedor)
            (150, 15),  # Pequeno-médio
            (200, 20),  # Médio
            (300, 30),  # Médio-grande
            (500, 50),  # Grande
        ]
        
        print("=" * 80)
        print("TESTE ABRANGENTE DE CONFIGURAÇÕES DE CHUNK")
        print("=" * 80)
        
        for chunk_size, chunk_overlap in configs:
            print(f"\n📊 Testando: chunk_size={chunk_size}, overlap={chunk_overlap}")
            result = self.test_configuration(chunk_size, chunk_overlap)
            self.results.append(result)
            
            print(f"   ✅ Chunks: {result['num_chunks']}")
            print(f"   ⏱️  Tempo: {result['process_time']:.2f}s")
            print(f"   📈 Similaridade geral: {result['overall_avg_similarity']:.4f}")
            
            # Mostra por categoria
            for category, cat_data in result["category_results"].items():
                print(f"      {category}: {cat_data['avg_similarity']:.4f}")
    
    def show_analysis(self):
        """Mostra análise detalhada dos resultados"""
        
        print("\n" + "=" * 80)
        print("ANÁLISE COMPARATIVA")
        print("=" * 80)
        
        # Encontra a melhor configuração geral
        best_overall = max(self.results, key=lambda x: x['overall_avg_similarity'])
        
        # Encontra a melhor por categoria
        best_by_category = {}
        for category in self.test_cases.keys():
            best = max(self.results, key=lambda x: x['category_results'][category]['avg_similarity'])
            best_by_category[category] = best
        
        # Mostra resultados
        print("\n🏆 MELHOR CONFIGURAÇÃO GERAL:")
        print(f"   chunk_size={best_overall['chunk_size']}, overlap={best_overall['chunk_overlap']}")
        print(f"   Similaridade: {best_overall['overall_avg_similarity']:.4f}")
        print(f"   Nº de chunks: {best_overall['num_chunks']}")
        
        print("\n📊 MELHOR POR CATEGORIA:")
        for category, config in best_by_category.items():
            print(f"   {category}: size={config['chunk_size']}, overlap={config['chunk_overlap']}")
            print(f"      Similaridade: {config['category_results'][category]['avg_similarity']:.4f}")
        
        # Tabela comparativa
        print("\n📋 TABELA COMPARATIVA:")
        print(f"{'Chunk Size':<10} {'Overlap':<10} {'Similarity':<12} {'Chunks':<8} {'Tempo':<8}")
        print("-" * 55)
        for r in sorted(self.results, key=lambda x: x['overall_avg_similarity'], reverse=True):
            print(f"{r['chunk_size']:<10} {r['chunk_overlap']:<10} {r['overall_avg_similarity']:.4f}     {r['num_chunks']:<8} {r['process_time']:.2f}s")
    
    def generate_recommendation(self):
        """Gera recomendação final com justificativa"""
        
        print("\n" + "=" * 80)
        print("💡 RECOMENDAÇÃO FINAL")
        print("=" * 80)
        
        # Encontra a melhor configuração
        best = max(self.results, key=lambda x: x['overall_avg_similarity'])
        
        print(f"\n✅ CONFIGURAÇÃO RECOMENDADA:")
        print(f"   chunk_size = {best['chunk_size']}")
        print(f"   chunk_overlap = {best['chunk_overlap']}")
        
        print(f"\n📊 JUSTIFICATIVA:")
        print(f"   • Similaridade média: {best['overall_avg_similarity']:.4f}")
        print(f"   • Número de chunks: {best['num_chunks']}")
        print(f"   • Tempo de processamento: {best['process_time']:.2f}s")
        
        print(f"\n📝 EXEMPLO DE CHUNK:")
        if best['chunk_examples']:
            example = best['chunk_examples'][0]
            print(f"   {example['text']}...")
        
        print(f"\n⚠️ CONSIDERAÇÕES:")
        if best['chunk_size'] < 100:
            print("   • Chunks muito pequenos podem perder contexto")
        if best['num_chunks'] > 50:
            print("   • Muitos chunks podem impactar performance")
        
        # Exporta resultados para arquivo
        report = {
            "recommended_config": {
                "chunk_size": best['chunk_size'],
                "chunk_overlap": best['chunk_overlap']
            },
            "all_results": self.results,
            "best_by_category": {}
        }
        
        for category in self.test_cases.keys():
            best_cat = max(self.results, key=lambda x: x['category_results'][category]['avg_similarity'])
            report["best_by_category"][category] = {
                "chunk_size": best_cat['chunk_size'],
                "chunk_overlap": best_cat['chunk_overlap'],
                "similarity": best_cat['category_results'][category]['avg_similarity']
            }
        
        with open("chunk_recommendation_report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: chunk_recommendation_report.json")

def main():
    tester = ComprehensiveChunkTester()
    tester.run_tests()
    tester.show_analysis()
    tester.generate_recommendation()

if __name__ == "__main__":
    main()