#!/usr/bin/env python3
"""
Script para monitorar o progresso da extração em execução
"""

import os
import time
import pandas as pd
from datetime import datetime

def monitorar_progresso():
    """
    Monitora o progresso da extração verificando arquivos gerados
    """
    print("🔍 MONITORAMENTO DE PROGRESSO - EXTRAÇÃO ANTAQ")
    print("=" * 50)
    
    # Arquivos esperados
    arquivos_principais = [
        "normas_antaq_completo.parquet",
        "normas_antaq.parquet"
    ]
    
    backups_pattern = "backup_normas_antaq_"
    
    while True:
        try:
            print(f"\n📊 Status em {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 30)
            
            # Verifica arquivos principais
            arquivo_encontrado = None
            for arquivo in arquivos_principais:
                if os.path.exists(arquivo):
                    arquivo_encontrado = arquivo
                    break
            
            # Verifica backups
            backups = [f for f in os.listdir('.') if f.startswith(backups_pattern) and f.endswith('.parquet')]
            
            if arquivo_encontrado:
                try:
                    df = pd.read_parquet(arquivo_encontrado)
                    total = len(df)
                    
                    print(f"📁 Arquivo: {arquivo_encontrado}")
                    print(f"📊 Normas extraídas: {total}")
                    
                    # Verifica se tem PDFs
                    if 'conteudo_pdf' in df.columns:
                        com_pdf = df['conteudo_pdf'].str.len().gt(0).sum()
                        print(f"📄 PDFs extraídos: {com_pdf}/{total} ({com_pdf/total*100:.1f}%)")
                        
                        if 'metodo_extracao' in df.columns:
                            metodos = df[df['metodo_extracao'] != '']['metodo_extracao'].value_counts()
                            print(f"🔧 Métodos: {dict(metodos)}")
                    
                    # Verifica situações
                    if 'situacao' in df.columns:
                        vigentes = (df['situacao'] == 'Em vigor').sum()
                        print(f"⚖️  Em vigor: {vigentes}/{total}")
                    
                    # Tamanho do arquivo
                    tamanho = os.path.getsize(arquivo_encontrado) / (1024*1024)  # MB
                    print(f"💾 Tamanho: {tamanho:.1f}MB")
                    
                except Exception as e:
                    print(f"⚠️ Erro ao ler arquivo: {e}")
            
            elif backups:
                backup_recente = max(backups, key=lambda f: os.path.getctime(f))
                print(f"📦 Backup encontrado: {backup_recente}")
                
                try:
                    df = pd.read_parquet(backup_recente)
                    print(f"📊 Registros no backup: {len(df)}")
                except:
                    print(f"⚠️ Não foi possível ler o backup")
            
            else:
                print("⏳ Nenhum arquivo de dados encontrado ainda...")
                print("💡 A extração pode estar na fase inicial")
            
            # Verifica processos Python executando
            try:
                import subprocess
                result = subprocess.run(['pgrep', '-f', 'python.*executar_completo'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("🔄 Processo de extração ativo")
                else:
                    print("⚠️ Processo de extração não detectado")
            except:
                pass
            
            print("\n⌨️  Pressione Ctrl+C para parar o monitoramento")
            time.sleep(30)  # Atualiza a cada 30 segundos
            
        except KeyboardInterrupt:
            print(f"\n👋 Monitoramento interrompido")
            break
        except Exception as e:
            print(f"\n❌ Erro no monitoramento: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitorar_progresso()