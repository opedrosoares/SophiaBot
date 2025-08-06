#!/usr/bin/env python3
"""
Script para visualizar dados extraídos do Sistema Sophia ANTAQ
"""

import pandas as pd
import os

def visualizar_dados():
    """Carrega e mostra dados do arquivo Parquet"""
    
    # Procura arquivos Parquet
    data_dir = 'shared/data'
    arquivos = [f for f in os.listdir(data_dir) if f.endswith('.parquet')]
    
    if not arquivos:
        print("❌ Nenhum arquivo .parquet encontrado")
        return
    
    # Usa o arquivo mais recente
    arquivo = max(arquivos, key=lambda x: os.path.getctime(os.path.join(data_dir, x)))
    print(f"📊 Analisando: {arquivo}")
    print("=" * 60)
    
    # Carrega dados
    df = pd.read_parquet(os.path.join(data_dir, arquivo))
    
    print(f"🔢 Total de registros: {len(df)}")
    print(f"📋 Colunas: {', '.join(df.columns)}")
    print()
    
    # Mostra primeiros registros
    print("🔍 PRIMEIROS 3 REGISTROS:")
    print("-" * 60)
    for i, row in df.head(3).iterrows():
        print(f"{i+1}. {row['titulo']}")
        print(f"   📅 Assinatura: {row['assinatura']}")
        print(f"   ⚖️  Situação: {row['situacao']}")
        print(f"   🏛️  Autor: {row['autor']}")
        if row['link_pdf']:
            print(f"   📄 PDF: {row['link_pdf'][:60]}...")
        print()
    
    # Estatísticas
    print("📊 ESTATÍSTICAS:")
    print("-" * 30)
    print(f"Situações:")
    print(df['situacao'].value_counts())
    print()
    
    # Verifica se há links de PDF
    pdfs_validos = df['link_pdf'].notna().sum()
    print(f"📄 Links PDF válidos: {pdfs_validos}/{len(df)} ({pdfs_validos/len(df)*100:.1f}%)")
    
    # Mostra anos mais comuns
    df['ano'] = pd.to_datetime(df['assinatura'], format='%d/%m/%Y', errors='coerce').dt.year
    print(f"\n📅 Anos mais comuns:")
    print(df['ano'].value_counts().head())
    
    print("\n✅ Dados carregados com sucesso!")

if __name__ == "__main__":
    visualizar_dados()