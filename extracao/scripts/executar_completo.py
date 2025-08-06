#!/usr/bin/env python3
"""
Script para executar extração completa de todas as normas ANTAQ
ATENÇÃO: Este processo pode demorar várias horas
"""

from Scrap import SophiaANTAQScraper
import time
import os

def main():
    print("🚀 EXTRAÇÃO COMPLETA - NORMAS ANTAQ")
    print("⚠️  ATENÇÃO: Este processo pode demorar várias horas!")
    print("💡 Pressione Ctrl+C para interromper a qualquer momento")
    print("=" * 60)
    
    # Confirmação do usuário
    resposta = input("Deseja continuar com a extração completa? (s/N): ").strip().lower()
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("❌ Extração cancelada pelo usuário")
        return
    
    print("\n🔄 Iniciando extração completa...")
    start_time = time.time()
    
    # Configurações para extração completa
    scraper = SophiaANTAQScraper(
        delay=1.5,  # 1.5 segundos entre requisições (uso responsável)
        verify_ssl=False
    )
    
    # Nome do arquivo principal (sempre o mesmo para updates incrementais)
    arquivo_principal = "shared/data/normas_antaq_completo.parquet"
    
    try:
        # Verifica se já existe arquivo com dados
        if os.path.exists(arquivo_principal):
            print(f"📂 Arquivo existente encontrado: {arquivo_principal}")
            existing_ids = scraper.load_existing_ids(arquivo_principal)
            print(f"🔑 {len(existing_ids)} IDs já existentes no banco")
            print(f"💡 Modo INCREMENTAL: apenas normas novas serão adicionadas")
        else:
            print("📂 Iniciando nova base de dados completa")
            existing_ids = set()
        
        # Obtém GUID inicial
        scraper.get_initial_guid()
        
        # Extrai TODAS as páginas (sem limite)
        print("📥 Extraindo todas as páginas disponíveis...")
        todos_dados = scraper.scrape_all_pages()  # SEM max_pages
        
        if todos_dados:
            print(f"🔍 Filtrando duplicatas de {len(todos_dados)} registros extraídos...")
            
            # Filtra duplicatas se há dados existentes
            if existing_ids:
                dados_novos = scraper.filter_duplicates(todos_dados, existing_ids)
            else:
                dados_novos = todos_dados
                print(f"📋 Primeira execução: todos os {len(dados_novos)} registros são novos")
            
            if dados_novos:
                # Salva dados (mescla com existentes)
                scraper.save_to_parquet(dados_novos, arquivo_principal, merge_with_existing=True)
                
                # Estatísticas finais
                elapsed_time = time.time() - start_time
                print(f"\n🎉 EXTRAÇÃO COMPLETA FINALIZADA!")
                print(f"⏱️  Tempo total: {elapsed_time/3600:.1f} horas")
                print(f"📊 Registros extraídos: {len(todos_dados)} total")
                print(f"🆕 Registros NOVOS adicionados: {len(dados_novos)}")
                print(f"🗃️  Total no arquivo: {len(existing_ids) + len(dados_novos)} normas")
                print(f"💾 Arquivo salvo: {arquivo_principal}")
                print(f"📈 Velocidade média: {len(todos_dados)/(elapsed_time/3600):.0f} normas/hora")
                
                # Cria backup com timestamp se houve mudanças significativas
                if len(dados_novos) > 10:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    backup_name = f"shared/backups/backup_normas_antaq_{timestamp}.parquet"
                    scraper.save_to_parquet(todos_dados, backup_name, merge_with_existing=False)
                    print(f"💾 Backup criado: {backup_name}")
            else:
                elapsed_time = time.time() - start_time
                print(f"\n📋 BASE DE DADOS JÁ ATUALIZADA!")
                print(f"⏱️  Tempo de verificação: {elapsed_time/60:.1f} minutos")
                print(f"🗃️  Total de normas no arquivo: {len(existing_ids)}")
                print(f"✅ Nenhuma norma nova encontrada")
            
        else:
            print("❌ Nenhum dado foi extraído")
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Extração interrompida pelo usuário após {(time.time()-start_time)/60:.1f} minutos")
        print("💡 Dados parciais podem ter sido salvos")
    except Exception as e:
        print(f"❌ Erro durante extração: {e}")

if __name__ == "__main__":
    main()