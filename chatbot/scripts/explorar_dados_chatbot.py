#!/usr/bin/env python3
"""
Script para explorar a estrutura dos dados das normas ANTAQ
para planejamento do chatbot
"""

import pandas as pd
import numpy as np
from pathlib import Path

def explorar_dados_normas():
    """
    Explora a estrutura e conteúdo do arquivo de normas para entender
    que informações temos disponíveis para o chatbot
    """
    
    caminho_dados = Path("shared/data/normas_antaq_completo.parquet")
    
    if not caminho_dados.exists():
        print("❌ Arquivo de dados não encontrado!")
        return
    
    print("🔍 Explorando dados das normas ANTAQ...")
    print("=" * 50)
    
    try:
        # Carregar dados
        df = pd.read_parquet(caminho_dados)
        
        # Informações básicas
        print(f"📊 INFORMAÇÕES GERAIS:")
        print(f"   • Total de registros: {len(df):,}")
        print(f"   • Total de colunas: {df.shape[1]}")
        print(f"   • Tamanho do arquivo: {caminho_dados.stat().st_size / (1024*1024):.1f} MB")
        print()
        
        # Estrutura das colunas
        print("📋 COLUNAS DISPONÍVEIS:")
        for i, col in enumerate(df.columns, 1):
            tipo = str(df[col].dtype)
            nulos = df[col].isnull().sum()
            print(f"   {i:2d}. {col:<25} [{tipo}] - {nulos:,} nulos")
        print()
        
        # Amostra de dados
        print("📖 AMOSTRA DE DADOS (primeiros 3 registros):")
        print("-" * 80)
        for idx in range(min(3, len(df))):
            print(f"\n🔸 REGISTRO {idx + 1}:")
            for col in df.columns:
                valor = df.iloc[idx][col]
                if pd.isna(valor):
                    valor_str = "N/A"
                elif isinstance(valor, str) and len(valor) > 100:
                    valor_str = valor[:100] + "..."
                else:
                    valor_str = str(valor)
                print(f"   {col}: {valor_str}")
        
        # Análise de conteúdo textual
        print("\n" + "="*50)
        print("📝 ANÁLISE DE CONTEÚDO TEXTUAL:")
        
        # Identificar colunas com texto longo
        colunas_texto = []
        for col in df.columns:
            if df[col].dtype == 'object':
                media_tamanho = df[col].astype(str).str.len().mean()
                if media_tamanho > 50:  # Considerar como texto longo
                    colunas_texto.append((col, media_tamanho))
        
        if colunas_texto:
            print("   Colunas com texto extenso (potenciais para embedding):")
            for col, media in sorted(colunas_texto, key=lambda x: x[1], reverse=True):
                print(f"   • {col}: {media:.0f} caracteres em média")
        
        # Análise temporal
        colunas_data = [col for col in df.columns if 'data' in col.lower() or 'ano' in col.lower()]
        if colunas_data:
            print(f"\n   📅 Colunas temporais encontradas: {colunas_data}")
            for col in colunas_data:
                try:
                    valores_unicos = df[col].nunique()
                    print(f"   • {col}: {valores_unicos} valores únicos")
                    if valores_unicos < 50:
                        print(f"     Valores: {sorted(df[col].dropna().unique())}")
                except:
                    pass
        
        # Análise de categorias
        print(f"\n   📊 DISTRIBUIÇÃO POR CATEGORIAS:")
        colunas_categoria = [col for col in df.columns if df[col].dtype == 'object' and df[col].nunique() < 50]
        
        for col in colunas_categoria[:5]:  # Mostrar até 5 colunas categóricas
            try:
                contagem = df[col].value_counts().head(10)
                if len(contagem) > 0:
                    print(f"\n   🏷️  {col}:")
                    for valor, count in contagem.items():
                        print(f"      • {valor}: {count:,} ({count/len(df)*100:.1f}%)")
            except:
                pass
        
        # Verificar qualidade dos dados
        print(f"\n" + "="*50)
        print("🔍 QUALIDADE DOS DADOS:")
        
        total_nulos = df.isnull().sum().sum()
        print(f"   • Total de valores nulos: {total_nulos:,}")
        
        if total_nulos > 0:
            print("   • Colunas com mais valores nulos:")
            nulos_por_coluna = df.isnull().sum().sort_values(ascending=False)
            for col, nulos in nulos_por_coluna.head(5).items():
                if nulos > 0:
                    percent = (nulos / len(df)) * 100
                    print(f"     - {col}: {nulos:,} ({percent:.1f}%)")
        
        # Sugestões para o chatbot
        print(f"\n" + "="*50)
        print("💡 SUGESTÕES PARA O CHATBOT:")
        
        # Identificar campos chave para busca
        campos_busca = []
        for col in df.columns:
            if any(termo in col.lower() for termo in ['titulo', 'nome', 'assunto', 'ementa', 'texto', 'conteudo']):
                campos_busca.append(col)
        
        if campos_busca:
            print("   🔍 Campos recomendados para busca semântica:")
            for campo in campos_busca:
                print(f"     • {campo}")
        
        # Identificar campos de metadados
        campos_metadata = []
        for col in df.columns:
            if any(termo in col.lower() for termo in ['data', 'ano', 'numero', 'tipo', 'orgao', 'status']):
                campos_metadata.append(col)
        
        if campos_metadata:
            print("   📋 Campos para filtros e metadados:")
            for campo in campos_metadata:
                print(f"     • {campo}")
        
        print("\n✅ Exploração concluída!")
        
    except Exception as e:
        print(f"❌ Erro ao explorar dados: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    explorar_dados_normas()