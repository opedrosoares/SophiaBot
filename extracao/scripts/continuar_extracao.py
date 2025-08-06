#!/usr/bin/env python3
"""
Script simplificado para continuar extração de 2004 a 2024
"""

from Scrap import SophiaANTAQScraper
import time
import os
import pandas as pd
from datetime import datetime

def main():
    print("🚀 CONTINUANDO EXTRAÇÃO HISTÓRICA - ANOS 2004 a 2024")
    print("=" * 60)
    
    # Anos a processar
    anos = list(range(2004, 2025))  # 2004 a 2024
    print(f"📅 Processando {len(anos)} anos: {anos[0]}-{anos[-1]}")
    print(f"⏱️  Tempo estimado: {len(anos) * 0.5:.1f} horas")
    
    # Configuração do scraper
    scraper = SophiaANTAQScraper(
        delay=1.5,
        verify_ssl=False,
        extract_pdf_content=True
    )
    
    arquivo_principal = "shared/data/normas_antaq_completo.parquet"
    
    # Carrega IDs existentes
    if os.path.exists(arquivo_principal):
        existing_ids_global = scraper.load_existing_ids(arquivo_principal)
        print(f"🔑 {len(existing_ids_global)} IDs já existentes")
    else:
        existing_ids_global = set()
        print("🆕 Criando nova base")
    
    start_time = time.time()
    
    try:
        for i, ano in enumerate(anos, 1):
            print(f"\n{'='*50}")
            print(f"📅 PROCESSANDO ANO {ano} ({i}/{len(anos)})")
            print(f"📈 Progresso geral: {((i-1)/len(anos))*100:.1f}%")
            print('='*50)
            
            start_ano = time.time()
            
            try:
                # Obtém GUID e processa ano
                scraper.get_initial_guid()
                dados_ano = scraper.scrape_all_pages(max_pages=None, ano=ano)
                
                if dados_ano:
                    print(f"🔍 {len(dados_ano)} normas encontradas para {ano}")
                    
                    # Filtra duplicatas
                    dados_novos = scraper.filter_duplicates(dados_ano, existing_ids_global)
                    
                    if dados_novos:
                        print(f"🆕 {len(dados_novos)} normas NOVAS para {ano}")
                        
                        # Conta PDFs extraídos
                        pdfs_extraidos = sum(1 for item in dados_novos 
                                           if item.get('conteudo_pdf', '').strip())
                        
                        # Salva dados
                        scraper.save_to_parquet(dados_novos, arquivo_principal, merge_with_existing=True)
                        
                        # Atualiza IDs existentes
                        for item in dados_novos:
                            if item.get('codigo_registro'):
                                existing_ids_global.add(str(item['codigo_registro']))
                        
                        print(f"💾 {len(dados_novos)} normas salvas")
                        if pdfs_extraidos > 0:
                            print(f"📄 {pdfs_extraidos} PDFs extraídos")
                        
                        # Estatísticas do arquivo
                        if os.path.exists(arquivo_principal):
                            df_atual = pd.read_parquet(arquivo_principal)
                            total_atual = len(df_atual)
                            pdfs_total = (df_atual['conteudo_pdf'].str.len() > 0).sum()
                            tamanho_mb = os.path.getsize(arquivo_principal) / (1024*1024)
                            
                            print(f"📊 Total no arquivo: {total_atual} normas")
                            print(f"📄 Total PDFs: {pdfs_total} ({pdfs_total/total_atual*100:.1f}%)")
                            print(f"💾 Tamanho: {tamanho_mb:.1f}MB")
                    else:
                        print(f"📋 Todas as {len(dados_ano)} normas de {ano} já existiam")
                        
                else:
                    print(f"📭 Nenhuma norma encontrada para {ano}")
                
                # Tempo do ano
                elapsed_ano = time.time() - start_ano
                print(f"⏱️  Tempo para {ano}: {elapsed_ano/60:.1f} minutos")
                
                # Backup a cada 5 anos
                if i % 5 == 0:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"backup_continuo_{ano}_{timestamp}.parquet"
                    
                    if os.path.exists(arquivo_principal):
                        df_backup = pd.read_parquet(arquivo_principal)
                        df_backup.to_parquet(backup_name, engine='pyarrow', index=True)
                        print(f"💾 Backup criado: {backup_name}")
                
                # Pausa entre anos
                if i < len(anos):
                    print("⏸️  Pausa de 3 segundos...")
                    time.sleep(3)
                    
            except KeyboardInterrupt:
                print(f"\n⚠️  Extração interrompida no ano {ano}")
                raise
            except Exception as e:
                print(f"❌ Erro no ano {ano}: {e}")
                print("➡️  Continuando para próximo ano...")
                continue
        
        # Estatísticas finais
        elapsed_total = time.time() - start_time
        
        print(f"\n{'='*60}")
        print("🎉 EXTRAÇÃO HISTÓRICA FINALIZADA!")
        print('='*60)
        print(f"⏱️  Tempo total: {elapsed_total/3600:.1f} horas")
        print(f"📅 Anos processados: {len(anos)}")
        
        if os.path.exists(arquivo_principal):
            df_final = pd.read_parquet(arquivo_principal)
            print(f"📊 Total final: {len(df_final)} normas")
            print(f"📄 PDFs extraídos: {(df_final['conteudo_pdf'].str.len() > 0).sum()}")
            print(f"💾 Arquivo final: {arquivo_principal}")
        
        print(f"📈 Velocidade média: {len(anos)/(elapsed_total/3600):.1f} anos/hora")
        
    except KeyboardInterrupt:
        elapsed_parcial = time.time() - start_time
        print(f"\n⚠️  Extração interrompida após {elapsed_parcial/3600:.1f} horas")
        print(f"💾 Progresso salvo em: {arquivo_principal}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()