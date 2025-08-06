#!/usr/bin/env python3
"""
Script para executar extração completa HISTÓRICA de todas as normas ANTAQ
Processa todos os anos desde 2002 até 2025
ATENÇÃO: Este processo pode demorar 12-24 horas ou mais
"""

from Scrap import SophiaANTAQScraper
import time
import os
from datetime import datetime

def main():
    print("🚀 EXTRAÇÃO HISTÓRICA COMPLETA - NORMAS ANTAQ (2002-2025)")
    print("⚠️  ATENÇÃO: Este processo pode demorar 12-24 horas ou mais!")
    print("📅 Será executado para TODOS os anos de 2002 a 2025")
    print("💾 Os dados serão salvos após cada ano processado")
    print("💡 Pressione Ctrl+C para interromper a qualquer momento")
    print("=" * 70)
    
    # Confirmação do usuário
    resposta = input("Deseja continuar com a extração histórica completa? (s/N): ").strip().lower()
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("❌ Extração cancelada pelo usuário")
        return
    
    # Configuração dos anos (de 2002 a 2025)
    anos = list(range(2024, 2025))  # 2002 a 2025 inclusive
    
    print(f"\n🔄 Iniciando extração histórica para {len(anos)} anos...")
    print(f"📅 Anos a processar: {anos[0]} - {anos[-1]}")
    
    start_time_total = time.time()
    
    # Configurações para extração completa
    scraper = SophiaANTAQScraper(
        delay=1.5,  # 1.5 segundos entre requisições (uso responsável)
        verify_ssl=False,
        extract_pdf_content=True  # Extrair conteúdo dos PDFs
    )
    
    # Nome do arquivo principal (sempre o mesmo para updates incrementais)
    arquivo_principal = "shared/data/normas_antaq_completo.parquet"
    
    # Carrega IDs existentes uma única vez (para controle global de duplicatas)
    if os.path.exists(arquivo_principal):
        print(f"📂 Arquivo existente encontrado: {arquivo_principal}")
        existing_ids_global = scraper.load_existing_ids(arquivo_principal)
        print(f"🔑 {len(existing_ids_global)} IDs já existentes no banco")
    else:
        print("📂 Iniciando nova base de dados histórica completa")
        existing_ids_global = set()
    
    # Estatísticas globais
    estatisticas = {
        'anos_processados': 0,
        'anos_com_dados': 0,
        'total_normas_encontradas': 0,
        'total_normas_novas': 0,
        'total_pdfs_extraidos': 0,
        'anos_vazios': []
    }
    
    try:
        for i, ano in enumerate(anos, 1):
            print(f"\n" + "="*60)
            print(f"📅 PROCESSANDO ANO {ano} ({i}/{len(anos)})")
            print(f"⏱️  Progresso total: {((i-1)/len(anos))*100:.1f}%")
            print("="*60)
            
            start_time_ano = time.time()
            
            try:
                # Obtém GUID inicial para este ano
                scraper.get_initial_guid()
                
                # Extrai TODAS as páginas para o ano específico
                print(f"📥 Extraindo todas as normas do ano {ano}...")
                dados_ano = scraper.scrape_all_pages(max_pages=None, ano=ano)
                
                estatisticas['anos_processados'] += 1
                
                if dados_ano:
                    print(f"🔍 {len(dados_ano)} normas encontradas para {ano}")
                    estatisticas['total_normas_encontradas'] += len(dados_ano)
                    
                    # Filtra duplicatas baseado nos IDs globais
                    dados_novos = scraper.filter_duplicates(dados_ano, existing_ids_global)
                    
                    if dados_novos:
                        print(f"🆕 {len(dados_novos)} normas NOVAS para adicionar do ano {ano}")
                        estatisticas['total_normas_novas'] += len(dados_novos)
                        estatisticas['anos_com_dados'] += 1
                        
                        # Conta PDFs extraídos
                        pdfs_extraidos = sum(1 for item in dados_novos 
                                           if item.get('conteudo_pdf', '').strip())
                        estatisticas['total_pdfs_extraidos'] += pdfs_extraidos
                        
                        # Salva dados (mescla com existentes)
                        scraper.save_to_parquet(dados_novos, arquivo_principal, merge_with_existing=True)
                        
                        # Atualiza conjunto de IDs existentes para próximas iterações
                        for item in dados_novos:
                            if item.get('codigo_registro'):
                                existing_ids_global.add(str(item['codigo_registro']))
                        
                        print(f"💾 {len(dados_novos)} normas salvas para o ano {ano}")
                        if pdfs_extraidos > 0:
                            print(f"📄 {pdfs_extraidos} PDFs com conteúdo extraído")
                    else:
                        print(f"📋 Todas as {len(dados_ano)} normas de {ano} já existiam no banco")
                        
                else:
                    print(f"📭 Nenhuma norma encontrada para o ano {ano}")
                    estatisticas['anos_vazios'].append(ano)
                
                # Tempo do ano atual
                elapsed_ano = time.time() - start_time_ano
                
                print(f"⏱️  Tempo para ano {ano}: {elapsed_ano/60:.1f} minutos")
                
                # Cria backup periódico a cada 5 anos processados
                if i % 5 == 0 or ano == anos[-1]:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"shared/backups/backup_historico_{ano}_{timestamp}.parquet"
                    
                    # Recarrega todos os dados para o backup
                    if os.path.exists(arquivo_principal):
                        import pandas as pd
                        df_backup = pd.read_parquet(arquivo_principal)
                        df_backup.to_parquet(backup_name, engine='pyarrow', index=True)
                        print(f"💾 Backup criado: {backup_name} ({len(df_backup)} normas)")
                
                # Aguarda um pouco antes do próximo ano (para não sobrecarregar servidor)
                if i < len(anos):  # Não aguarda no último ano
                    print("⏸️  Aguardando 3 segundos antes do próximo ano...")
                    time.sleep(3)
                    
            except KeyboardInterrupt:
                print(f"\n⚠️  Extração interrompida pelo usuário no ano {ano}")
                raise
            except Exception as e:
                print(f"❌ Erro ao processar ano {ano}: {e}")
                print("➡️  Continuando para o próximo ano...")
                continue
        
        # Estatísticas finais
        elapsed_total = time.time() - start_time_total
        
        print(f"\n" + "="*70)
        print("🎉 EXTRAÇÃO HISTÓRICA COMPLETA FINALIZADA!")
        print("="*70)
        print(f"⏱️  Tempo total: {elapsed_total/3600:.1f} horas")
        print(f"📅 Anos processados: {estatisticas['anos_processados']}/{len(anos)}")
        print(f"📊 Anos com dados: {estatisticas['anos_com_dados']}")
        print(f"📈 Total de normas encontradas: {estatisticas['total_normas_encontradas']}")
        print(f"🆕 Total de normas NOVAS adicionadas: {estatisticas['total_normas_novas']}")
        print(f"📄 Total de PDFs extraídos: {estatisticas['total_pdfs_extraidos']}")
        print(f"🗃️  Total final no arquivo: {len(existing_ids_global)} normas únicas")
        print(f"💾 Arquivo principal: {arquivo_principal}")
        
        if estatisticas['anos_vazios']:
            print(f"📭 Anos sem dados: {estatisticas['anos_vazios']}")
        
        if estatisticas['total_normas_encontradas'] > 0:
            velocidade = estatisticas['total_normas_encontradas'] / (elapsed_total / 3600)
            print(f"📈 Velocidade média: {velocidade:.0f} normas/hora")
        
        # Backup final
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_final = f"shared/backups/backup_historico_completo_{timestamp}.parquet"
        
        if os.path.exists(arquivo_principal):
            import pandas as pd
            df_final = pd.read_parquet(arquivo_principal)
            df_final.to_parquet(backup_final, engine='pyarrow', index=True)
            print(f"💾 Backup final criado: {backup_final}")
            
            # Análise por décadas
            print(f"\n📊 ANÁLISE POR DÉCADAS:")
            if 'ano_norma' in df_final.columns:
                decadas = df_final['ano_norma'].value_counts().sort_index()
                for decada_inicio in range(2000, 2030, 10):
                    decada_fim = decada_inicio + 9
                    count = decadas[(decadas.index >= decada_inicio) & (decadas.index <= decada_fim)].sum()
                    if count > 0:
                        print(f"   {decada_inicio}-{decada_fim}: {count} normas")
    
    except KeyboardInterrupt:
        elapsed_parcial = time.time() - start_time_total
        print(f"\n⚠️  Extração interrompida após {elapsed_parcial/3600:.1f} horas")
        print(f"📊 Progresso: {estatisticas['anos_processados']}/{len(anos)} anos processados")
        print(f"💾 Dados parciais salvos em: {arquivo_principal}")
        
    except Exception as e:
        print(f"❌ Erro geral durante extração histórica: {e}")

if __name__ == "__main__":
    main()