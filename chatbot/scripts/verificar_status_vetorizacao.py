#!/usr/bin/env python3
"""
Script para verificar o status atual da vetorização
"""

import pandas as pd
import os
from datetime import datetime

def verificar_status_vetorizacao():
    """
    Verifica o status atual da vetorização das normas
    """
    
    arquivo_parquet = "shared/data/normas_antaq_completo.parquet"
    
    if not os.path.exists(arquivo_parquet):
        print(f"❌ Arquivo {arquivo_parquet} não encontrado!")
        return False
    
    print(f"📖 Carregando arquivo: {arquivo_parquet}")
    
    # Carregar dados
    df = pd.read_parquet(arquivo_parquet)
    
    print(f"📊 Shape: {df.shape}")
    print(f"📋 Colunas: {df.columns.tolist()}")
    
    # Verificar se coluna vetorizado existe
    if 'vetorizado' not in df.columns:
        print("❌ Coluna 'vetorizado' não encontrada!")
        return False
    
    # Estatísticas básicas
    total_normas = len(df)
    normas_vetorizadas = df['vetorizado'].sum()
    normas_nao_vetorizadas = total_normas - normas_vetorizadas
    
    print(f"\n📊 ESTATÍSTICAS GERAIS:")
    print(f"   Total de normas: {total_normas:,}")
    print(f"   Normas vetorizadas: {normas_vetorizadas:,}")
    print(f"   Normas não vetorizadas: {normas_nao_vetorizadas:,}")
    print(f"   Percentual vetorizado: {normas_vetorizadas/total_normas*100:.1f}%")
    
    # Normas em vigor com conteúdo
    normas_em_vigor = df[
        (df['situacao'] == 'Em vigor') & 
        (df['conteudo_pdf'].notna()) & 
        (df['conteudo_pdf'].str.len() > 100)
    ]
    
    normas_em_vigor_vetorizadas = normas_em_vigor['vetorizado'].sum()
    normas_em_vigor_nao_vetorizadas = len(normas_em_vigor) - normas_em_vigor_vetorizadas
    
    print(f"\n📋 NORMAS EM VIGOR COM CONTEÚDO:")
    print(f"   Total: {len(normas_em_vigor):,}")
    print(f"   Vetorizadas: {normas_em_vigor_vetorizadas:,}")
    print(f"   Não vetorizadas: {normas_em_vigor_nao_vetorizadas:,}")
    print(f"   Percentual vetorizado: {normas_em_vigor_vetorizadas/len(normas_em_vigor)*100:.1f}%")
    
    # Verificar coluna de última verificação
    if 'ultima_verificacao_vetorizacao' in df.columns:
        ultima_verificacao = df['ultima_verificacao_vetorizacao'].max()
        if pd.notna(ultima_verificacao):
            print(f"\n⏰ Última verificação: {ultima_verificacao}")
        else:
            print(f"\n⏰ Última verificação: Nenhuma")
    else:
        print(f"\n⚠️  Coluna 'ultima_verificacao_vetorizacao' não encontrada")
    
    # Estatísticas por situação
    print(f"\n📊 ESTATÍSTICAS POR SITUAÇÃO:")
    for situacao in df['situacao'].value_counts().head(5).index:
        subset = df[df['situacao'] == situacao]
        vetorizadas = subset['vetorizado'].sum()
        total = len(subset)
        percentual = vetorizadas/total*100 if total > 0 else 0
        print(f"   {situacao}: {vetorizadas:,}/{total:,} ({percentual:.1f}%)")
    
    # Estatísticas por tipo de material
    print(f"\n📊 ESTATÍSTICAS POR TIPO DE MATERIAL:")
    for tipo in df['tipo_material'].value_counts().head(5).index:
        subset = df[df['tipo_material'] == tipo]
        vetorizadas = subset['vetorizado'].sum()
        total = len(subset)
        percentual = vetorizadas/total*100 if total > 0 else 0
        print(f"   {tipo}: {vetorizadas:,}/{total:,} ({percentual:.1f}%)")
    
    # Mostrar algumas normas não vetorizadas
    normas_nao_vetorizadas_df = df[~df['vetorizado']].head(10)
    print(f"\n📝 EXEMPLOS DE NORMAS NÃO VETORIZADAS:")
    for idx, row in normas_nao_vetorizadas_df.iterrows():
        print(f"   - {row['codigo_registro']}: {row['titulo'][:60]}...")
    
    # Mostrar algumas normas vetorizadas
    normas_vetorizadas_df = df[df['vetorizado']].head(5)
    print(f"\n✅ EXEMPLOS DE NORMAS VETORIZADAS:")
    for idx, row in normas_vetorizadas_df.iterrows():
        print(f"   - {row['codigo_registro']}: {row['titulo'][:60]}...")
    
    # Progresso visual
    print(f"\n📈 PROGRESSO VISUAL:")
    progresso = normas_em_vigor_vetorizadas / len(normas_em_vigor) * 100
    barras = int(progresso / 2)  # 50 caracteres = 100%
    barra_progresso = "█" * barras + "░" * (50 - barras)
    print(f"   [{barra_progresso}] {progresso:.1f}%")
    print(f"   {normas_em_vigor_vetorizadas:,} / {len(normas_em_vigor):,} normas")
    
    return True

if __name__ == "__main__":
    print("📊 VERIFICAÇÃO DE STATUS DA VETORIZAÇÃO")
    print("=" * 50)
    
    success = verificar_status_vetorizacao()
    
    if success:
        print("\n✅ Verificação concluída!")
    else:
        print("\n❌ Verificação falhou!") 