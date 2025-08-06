#!/usr/bin/env python3
import sys
sys.path.append('.')
from executar_completo_historico import main as main_historico
from executar_completo_historico import SophiaANTAQScraper
import os
import time

# Modifica os anos para retomar de onde parou
anos_restantes = list(range(2010, 2025))
print(f"🔄 RETOMANDO EXTRAÇÃO HISTÓRICA")
print(f"📅 Anos restantes: {len(anos_restantes)} ({anos_restantes[0]}-{anos_restantes[-1]})")
print(f"⏱️  Estimativa: {len(anos_restantes) * 0.5:.1f} horas")

# Executa a extração
if __name__ == "__main__":
    from Scrap import SophiaANTAQScraper
    import pandas as pd
    from datetime import datetime
    
    scraper = SophiaANTAQScraper(
        delay=1.5,
        verify_ssl=False,
        extract_pdf_content=True
    )
    
    arquivo_principal = "shared/data/normas_antaq_completo.parquet"
    
    # Carrega IDs existentes
    if os.path.exists(arquivo_principal):
        existing_ids_global = scraper.load_existing_ids(arquivo_principal)
        print(f"🔑 {len(existing_ids_global)} IDs já existentes no banco")
    else:
        existing_ids_global = set()
    
    try:
        for i, ano in enumerate(anos_restantes, 1):
            # Verifica comando de controle
            if os.path.exists('controle_extracao.json'):
                import json
                try:
                    with open('controle_extracao.json', 'r') as f:
                        cmd = json.load(f)
                    if cmd.get('acao') in ['pausar', 'parar']:
                        print(f"\n🛑 Comando '{cmd['acao']}' recebido - parando graciosamente")
                        break
                except:
                    pass
            
            print(f"\n📅 PROCESSANDO ANO {ano} ({i}/{len(anos_restantes)})")
            
            # Salva estado atual
            with open('estado_extracao.json', 'w') as f:
                import json
                json.dump({
                    'ano_atual': ano,
                    'progresso': (i-1)/len(anos_restantes)*100,
                    'total_normas': len(existing_ids_global),
                    'status': 'executando',
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            
            try:
                scraper.get_initial_guid()
                dados_ano = scraper.scrape_all_pages(max_pages=None, ano=ano)
                
                if dados_ano:
                    dados_novos = scraper.filter_duplicates(dados_ano, existing_ids_global)
                    if dados_novos:
                        scraper.save_to_parquet(dados_novos, arquivo_principal, merge_with_existing=True)
                        for item in dados_novos:
                            if item.get('codigo_registro'):
                                existing_ids_global.add(str(item['codigo_registro']))
                        print(f"💾 {len(dados_novos)} normas salvas para {ano}")
                    else:
                        print(f"📋 Todas as normas de {ano} já existiam")
                else:
                    print(f"📭 Nenhuma norma encontrada para {ano}")
                
                time.sleep(3)  # Pausa entre anos
                
            except Exception as e:
                print(f"❌ Erro no ano {ano}: {e}")
                continue
        
        # Salva estado final
        with open('estado_extracao.json', 'w') as f:
            json.dump({
                'ano_atual': anos_restantes[-1] if anos_restantes else 2024,
                'progresso': 100,
                'total_normas': len(existing_ids_global),
                'status': 'completo',
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        print("\n🎉 EXTRAÇÃO HISTÓRICA FINALIZADA!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Extração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
