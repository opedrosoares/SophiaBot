#!/usr/bin/env python3
"""
Análise detalhada das normas ANTAQ extraídas
Gera relatório completo dos dados
"""

import pandas as pd
import os
from datetime import datetime
import re

def carregar_dados_completos():
    """Carrega o arquivo de dados completos mais recente"""
    data_dir = 'shared/data'
    arquivos = [f for f in os.listdir(data_dir) if f.endswith('.parquet') and 'completo' in f]
    
    if not arquivos:
        print("❌ Nenhum arquivo completo encontrado")
        return None
    
    arquivo = max(arquivos, key=lambda x: os.path.getctime(os.path.join(data_dir, x)))
    print(f"📂 Carregando: {arquivo}")
    return pd.read_parquet(os.path.join(data_dir, arquivo))

def analisar_tipos_normas(df):
    """Analisa os tipos de normas por título"""
    print("\n📋 TIPOS DE NORMAS IDENTIFICADAS:")
    print("-" * 50)
    
    tipos = {}
    for titulo in df['titulo']:
        if pd.isna(titulo):
            continue
            
        # Identifica tipo da norma pelo título
        titulo_upper = titulo.upper()
        if 'RESOLUÇÃO' in titulo_upper:
            tipo = 'Resolução'
        elif 'PORTARIA' in titulo_upper:
            tipo = 'Portaria'
        elif 'TERMO DE AUTORIZAÇÃO' in titulo_upper:
            tipo = 'Termo de Autorização'
        elif 'INSTRUÇÃO NORMATIVA' in titulo_upper:
            tipo = 'Instrução Normativa'
        elif 'DELIBERAÇÃO' in titulo_upper:
            tipo = 'Deliberação'
        elif 'ACÓRDÃO' in titulo_upper:
            tipo = 'Acórdão'
        else:
            tipo = 'Outros'
        
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    # Ordena por quantidade
    for tipo, quantidade in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
        percentual = (quantidade / len(df)) * 100
        print(f"{tipo:20} {quantidade:3d} normas ({percentual:5.1f}%)")
    
    return tipos

def analisar_por_ano(df):
    """Análise temporal das normas"""
    print("\n📅 DISTRIBUIÇÃO POR ANO:")
    print("-" * 30)
    
    # Converte datas
    df['data_assinatura'] = pd.to_datetime(df['assinatura'], format='%d/%m/%Y', errors='coerce')
    df['ano'] = df['data_assinatura'].dt.year
    
    # Conta por ano
    anos = df['ano'].value_counts().sort_index()
    
    total = len(df[df['ano'].notna()])
    for ano, quantidade in anos.items():
        if pd.notna(ano):
            percentual = (quantidade / total) * 100
            print(f"{int(ano):4d}: {quantidade:3d} normas ({percentual:5.1f}%)")
    
    # Estatísticas
    print(f"\n📊 Período: {int(anos.index.min())} - {int(anos.index.max())}")
    print(f"📈 Ano com mais normas: {int(anos.idxmax())} ({anos.max()} normas)")
    
    return anos

def analisar_situacoes(df):
    """Análise das situações das normas"""
    print("\n⚖️  SITUAÇÃO DAS NORMAS:")
    print("-" * 25)
    
    situacoes = df['situacao'].value_counts()
    total = len(df)
    
    for situacao, quantidade in situacoes.items():
        percentual = (quantidade / total) * 100
        status = "🟢" if situacao == "Em vigor" else "🔴" if situacao == "Revogado" else "⚪"
        print(f"{status} {situacao:15} {quantidade:3d} ({percentual:5.1f}%)")

def extrair_numeros_normas(df):
    """Extrai e analisa numeração das normas"""
    print("\n🔢 ANÁLISE DE NUMERAÇÃO:")
    print("-" * 25)
    
    numeros = []
    anos_numeracao = []
    
    for titulo in df['titulo']:
        if pd.isna(titulo):
            continue
        
        # Busca padrões de numeração
        match_numero = re.search(r'(\d+)', titulo)
        match_ano = re.search(r'/(\d{4})', titulo)
        
        if match_numero:
            numeros.append(int(match_numero.group(1)))
        
        if match_ano:
            anos_numeracao.append(int(match_ano.group(1)))
    
    if numeros:
        print(f"📊 Numeração mínima: {min(numeros)}")
        print(f"📊 Numeração máxima: {max(numeros)}")
        print(f"📊 Média de numeração: {sum(numeros)/len(numeros):.0f}")
    
    if anos_numeracao:
        anos_unicos = set(anos_numeracao)
        print(f"📅 Anos na numeração: {', '.join(map(str, sorted(anos_unicos)))}")

def gerar_relatorio_pdf_links(df):
    """Verifica e analisa links de PDF"""
    print("\n📄 ANÁLISE DOS LINKS PDF:")
    print("-" * 30)
    
    # Links válidos
    links_validos = df['link_pdf'].notna().sum()
    print(f"✅ Links válidos: {links_validos}/{len(df)} ({links_validos/len(df)*100:.1f}%)")
    
    # Análise dos códigos de arquivo
    codigos = []
    for link in df['link_pdf'].dropna():
        match = re.search(r'codigoArquivo=(\d+)', link)
        if match:
            codigos.append(int(match.group(1)))
    
    if codigos:
        print(f"📊 Códigos de arquivo: {min(codigos)} - {max(codigos)}")
        print(f"📊 Total de arquivos únicos: {len(set(codigos))}")

def exportar_resumo_excel(df):
    """Exporta resumo para Excel (se possível)"""
    try:
        # Cria resumo
        resumo = df[['titulo', 'situacao', 'assinatura', 'autor', 'link_pdf']].copy()
        resumo['ano'] = pd.to_datetime(df['assinatura'], format='%d/%m/%Y', errors='coerce').dt.year
        
        # Adiciona tipo de norma
        resumo['tipo'] = resumo['titulo'].apply(lambda x: 
            'Resolução' if 'Resolução' in str(x) else
            'Portaria' if 'Portaria' in str(x) else
            'Termo de Autorização' if 'Termo de Autorização' in str(x) else
            'Outros'
        )
        
        # Salva
        exports_dir = 'shared/exports'
        arquivo_excel = os.path.join(exports_dir, "resumo_normas_antaq.xlsx")
        resumo.to_excel(arquivo_excel, index=False)
        print(f"\n💾 Resumo exportado para: {arquivo_excel}")
        
    except ImportError:
        print("\n⚠️  Para exportar Excel, instale: pip install openpyxl")
    except Exception as e:
        print(f"\n❌ Erro ao exportar Excel: {e}")

def main():
    """Função principal de análise"""
    print("🔍 ANÁLISE DETALHADA - NORMAS ANTAQ")
    print("=" * 60)
    
    # Carrega dados
    df = carregar_dados_completos()
    if df is None:
        return
    
    print(f"\n📊 DADOS GERAIS:")
    print(f"Total de registros: {len(df)}")
    print(f"Período de extração: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Análises detalhadas
    tipos = analisar_tipos_normas(df)
    anos = analisar_por_ano(df)
    analisar_situacoes(df)
    extrair_numeros_normas(df)
    gerar_relatorio_pdf_links(df)
    
    # Estatísticas adicionais
    print(f"\n📈 ESTATÍSTICAS ADICIONAIS:")
    print("-" * 30)
    print(f"📝 Normas com assunto definido: {df['assunto'].notna().sum()}")
    print(f"🏛️  Autores únicos: {df['autor'].nunique()}")
    print(f"🌍 Esferas únicas: {df['esfera'].nunique()}")
    
    # Lista esferas
    if df['esfera'].nunique() > 1:
        print(f"\n🌍 ESFERAS IDENTIFICADAS:")
        for esfera, count in df['esfera'].value_counts().items():
            print(f"   {esfera}: {count} normas")
    
    # Tenta exportar Excel
    exportar_resumo_excel(df)
    
    print(f"\n✅ Análise completa finalizada!")
    print(f"💡 Dados disponíveis em formato Parquet para análises adicionais")

if __name__ == "__main__":
    main()