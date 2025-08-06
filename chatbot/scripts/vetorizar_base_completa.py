#!/usr/bin/env python3
"""
Script para vetorizar toda a base de normas ANTAQ
"""

import os
import sys
import time
from datetime import datetime

# Adicionar o diretório raiz ao path para importações corretas
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

def vetorizar_base_completa():
    """
    Vetoriza toda a base de normas ANTAQ
    """
    
    # Importar configurações do config
    try:
        from chatbot.config.config import OPENAI_API_KEY
        from chatbot.core.vector_store import VectorStoreANTAQ
    except ImportError as e:
        print(f"❌ Erro ao importar configurações do chatbot: {e}")
        print("   Verifique se o arquivo chatbot/config/config.py existe")
        return False
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY não encontrada no settings.py")
        return False
    
    # Inicializar vector store
    print("🚀 Inicializando VectorStore...")
    vs = VectorStoreANTAQ(OPENAI_API_KEY)
    
    # Caminho para o arquivo parquet
    parquet_path = "shared/data/normas_antaq_completo.parquet"
    
    if not os.path.exists(parquet_path):
        print(f"❌ Arquivo {parquet_path} não encontrado!")
        return False
    
    # Verificar estatísticas iniciais
    print("\n📊 ESTATÍSTICAS INICIAIS:")
    stats_inicial = vs.get_vetorizacao_stats(parquet_path)
    
    if 'error' in stats_inicial:
        print(f"❌ Erro: {stats_inicial['error']}")
        return False
    
    print(f"   Total de normas: {stats_inicial['total_normas']}")
    print(f"   Normas vetorizadas: {stats_inicial['normas_vetorizadas']}")
    print(f"   Normas não vetorizadas: {stats_inicial['normas_nao_vetorizadas']}")
    print(f"   Percentual vetorizado: {stats_inicial['percentual_vetorizado']:.1f}%")
    print(f"   Normas em vigor com conteúdo: {stats_inicial['normas_em_vigor_com_conteudo']}")
    print(f"   Normas em vigor vetorizadas: {stats_inicial['normas_em_vigor_vetorizadas']}")
    print(f"   Normas em vigor não vetorizadas: {stats_inicial['normas_em_vigor_nao_vetorizadas']}")
    print(f"   Percentual em vigor vetorizado: {stats_inicial['percentual_em_vigor_vetorizado']:.1f}%")
    
    # Verificar se já está tudo vetorizado
    if stats_inicial['normas_em_vigor_nao_vetorizadas'] == 0:
        print("\n✅ Todas as normas em vigor já estão vetorizadas!")
        return True
    
    # Confirmar com o usuário
    print(f"\n⚠️  ATENÇÃO: Este processo irá vetorizar {stats_inicial['normas_em_vigor_nao_vetorizadas']} normas.")
    print("   Isso pode levar várias horas dependendo da quantidade de dados.")
    print("   Certifique-se de que você tem tempo suficiente e conexão estável com a internet.")
    
    confirmacao = input("\nDeseja continuar? (s/N): ").strip().lower()
    if confirmacao not in ['s', 'sim', 'y', 'yes']:
        print("❌ Processo cancelado pelo usuário.")
        return False
    
    # Iniciar vetorização
    print(f"\n🔄 INICIANDO VETORIZAÇÃO COMPLETA...")
    print(f"   Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # Processar todas as normas não vetorizadas
    success = vs.load_and_process_data(
        parquet_path,
        incremental=True,  # Processar apenas não vetorizadas
        force_rebuild=False
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    if not success:
        print("❌ Erro durante a vetorização!")
        return False
    
    # Verificar estatísticas finais
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    stats_final = vs.get_vetorizacao_stats(parquet_path)
    
    print(f"   Total de normas: {stats_final['total_normas']}")
    print(f"   Normas vetorizadas: {stats_final['normas_vetorizadas']}")
    print(f"   Normas não vetorizadas: {stats_final['normas_nao_vetorizadas']}")
    print(f"   Percentual vetorizado: {stats_final['percentual_vetorizado']:.1f}%")
    print(f"   Normas em vigor com conteúdo: {stats_final['normas_em_vigor_com_conteudo']}")
    print(f"   Normas em vigor vetorizadas: {stats_final['normas_em_vigor_vetorizadas']}")
    print(f"   Normas em vigor não vetorizadas: {stats_final['normas_em_vigor_nao_vetorizadas']}")
    print(f"   Percentual em vigor vetorizado: {stats_final['percentual_em_vigor_vetorizado']:.1f}%")
    
    # Estatísticas da coleção
    collection_stats = vs.get_collection_stats()
    print(f"\n📊 ESTATÍSTICAS DA COLEÇÃO:")
    print(f"   Total chunks: {collection_stats.get('total_chunks', 0)}")
    
    # Informações de tempo
    print(f"\n⏱️  INFORMAÇÕES DE TEMPO:")
    print(f"   Início: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Fim: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Duração total: {duration/3600:.2f} horas ({duration/60:.1f} minutos)")
    
    # Calcular normas processadas
    normas_processadas = stats_final['normas_vetorizadas'] - stats_inicial['normas_vetorizadas']
    if normas_processadas > 0:
        tempo_medio = duration / normas_processadas
        print(f"   Normas processadas: {normas_processadas}")
        print(f"   Tempo médio por norma: {tempo_medio:.1f} segundos")
    
    print(f"\n✅ VETORIZAÇÃO COMPLETA FINALIZADA!")
    print(f"   Todas as {stats_final['normas_em_vigor_vetorizadas']} normas em vigor foram vetorizadas com sucesso!")
    
    return True

if __name__ == "__main__":
    print("🚀 VETORIZAÇÃO COMPLETA DA BASE ANTAQ")
    print("=" * 50)
    
    success = vetorizar_base_completa()
    
    if success:
        print("\n✅ Processo concluído com sucesso!")
        print("   A base está pronta para uso no chatbot.")
    else:
        print("\n❌ Processo falhou!")
        print("   Verifique os logs para mais detalhes.") 