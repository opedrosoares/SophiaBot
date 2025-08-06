#!/usr/bin/env python3
"""
Script para monitorar o progresso da extração histórica em tempo real
"""

import os
import time
import pandas as pd
from datetime import datetime
import subprocess

def verificar_processo_ativo():
    """Verifica se o processo de extração está executando"""
    try:
        result = subprocess.run(['pgrep', '-f', 'executar_completo_historico'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def analisar_arquivo_principal():
    """Analisa o arquivo principal de dados"""
    arquivo = "normas_antaq_completo.parquet"
    
    if not os.path.exists(arquivo):
        return None
    
    try:
        df = pd.read_parquet(arquivo)
        
        # Análise básica
        total = len(df)
        
        # Análise por ano (tentativa de extrair ano da data)
        anos_dados = {}
        if 'publicacao' in df.columns:
            for _, row in df.iterrows():
                pub = str(row.get('publicacao', '')).strip()
                # Tenta extrair ano da publicação
                for ano in range(2002, 2026):
                    if str(ano) in pub:
                        anos_dados[ano] = anos_dados.get(ano, 0) + 1
                        break
        
        # PDFs extraídos
        pdfs_com_conteudo = 0
        metodos = {}
        if 'conteudo_pdf' in df.columns:
            pdfs_com_conteudo = (df['conteudo_pdf'].str.len() > 0).sum()
            
            if 'metodo_extracao' in df.columns:
                metodos_count = df[df['metodo_extracao'] != '']['metodo_extracao'].value_counts()
                metodos = dict(metodos_count)
        
        return {
            'total': total,
            'pdfs_extraidos': pdfs_com_conteudo,
            'anos_dados': anos_dados,
            'metodos': metodos,
            'tamanho_mb': os.path.getsize(arquivo) / (1024*1024)
        }
    except Exception as e:
        return {'erro': str(e)}

def main():
    print("🔍 MONITOR - EXTRAÇÃO HISTÓRICA ANTAQ")
    print("=" * 50)
    print("⚡ Monitoramento em tempo real da extração completa")
    print("📅 Anos: 2002-2025 (24 anos)")
    print("⏹️  Pressione Ctrl+C para parar o monitoramento")
    print("")
    
    contador = 0
    ultimo_total = 0
    
    while True:
        try:
            contador += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"\n🕐 {timestamp} - Update #{contador}")
            print("-" * 40)
            
            # Verifica processo
            processo_ativo = verificar_processo_ativo()
            status_icon = "🔄" if processo_ativo else "⏸️"
            status_text = "EXECUTANDO" if processo_ativo else "PARADO/FINALIZADO"
            print(f"{status_icon} Status: {status_text}")
            
            # Analisa dados
            dados = analisar_arquivo_principal()
            
            if dados is None:
                print("📁 Arquivo principal ainda não criado")
            elif 'erro' in dados:
                print(f"❌ Erro ao ler arquivo: {dados['erro']}")
            else:
                total = dados['total']
                pdfs = dados['pdfs_extraidos']
                tamanho = dados['tamanho_mb']
                
                print(f"📊 Total de normas: {total}")
                print(f"📄 PDFs extraídos: {pdfs} ({pdfs/total*100:.1f}%)")
                print(f"💾 Tamanho arquivo: {tamanho:.1f}MB")
                
                # Mostra progresso
                if total > ultimo_total:
                    novas = total - ultimo_total
                    print(f"🆕 Novas desde último check: +{novas}")
                    ultimo_total = total
                
                # Mostra anos com dados
                if dados['anos_dados']:
                    anos_ordenados = sorted(dados['anos_dados'].items())
                    print(f"📅 Anos com dados: {len(anos_ordenados)}/24")
                    
                    # Mostra últimos 5 anos processados
                    if len(anos_ordenados) > 5:
                        print(f"   Últimos: {dict(anos_ordenados[-5:])}")
                    else:
                        print(f"   Todos: {dict(anos_ordenados)}")
                
                # Mostra métodos de extração
                if dados['metodos']:
                    print(f"🔧 Métodos: {dados['metodos']}")
            
            # Verifica backups
            backups = [f for f in os.listdir('.') if f.startswith('backup_historico_') and f.endswith('.parquet')]
            if backups:
                backup_mais_recente = max(backups, key=lambda f: os.path.getctime(f))
                print(f"💾 Último backup: {backup_mais_recente}")
            
            # Estimativa de progresso
            if dados and dados.get('anos_dados'):
                anos_processados = len(dados['anos_dados'])
                progresso_pct = (anos_processados / 24) * 100
                print(f"📈 Progresso estimado: {progresso_pct:.1f}% ({anos_processados}/24 anos)")
                
                if anos_processados > 0 and processo_ativo:
                    # Estimativa de tempo restante (muito aproximada)
                    tempo_decorrido = contador * 30  # segundos
                    tempo_por_ano = tempo_decorrido / anos_processados
                    anos_restantes = 24 - anos_processados
                    tempo_restante_horas = (anos_restantes * tempo_por_ano) / 3600
                    print(f"⏰ Tempo restante estimado: {tempo_restante_horas:.1f}h")
            
            if not processo_ativo and dados and dados.get('total', 0) > 0:
                print(f"\n🎉 EXTRAÇÃO POSSIVELMENTE FINALIZADA!")
                print(f"📊 Total final: {dados['total']} normas")
                break
            
            print(f"\n⏸️  Próximo update em 30 segundos...")
            time.sleep(30)
            
        except KeyboardInterrupt:
            print(f"\n👋 Monitoramento interrompido pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro no monitoramento: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()