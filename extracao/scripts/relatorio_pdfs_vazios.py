#!/usr/bin/env python3
"""
Script para gerar relatório detalhado dos PDFs vazios
Categoriza os problemas encontrados
"""

import pandas as pd
import os
from urllib.parse import urlparse

def analisar_pdfs_vazios(arquivo):
    """
    Analisa e categoriza PDFs que ainda estão vazios
    """
    print(f"📋 RELATÓRIO DETALHADO DE PDFs VAZIOS")
    print("=" * 50)
    
    df = pd.read_parquet(arquivo)
    
    # Identifica PDFs vazios
    vazios = df[
        (df['link_pdf'].notna()) & 
        (df['conteudo_pdf'].str.len().eq(0) | df['conteudo_pdf'].isna())
    ]
    
    print(f"📊 ESTATÍSTICAS GERAIS:")
    print(f"   📋 Total de normas: {len(df):,}")
    print(f"   📄 Com link PDF: {df['link_pdf'].notna().sum():,}")
    print(f"   ✅ PDFs extraídos: {df['conteudo_pdf'].str.len().gt(0).sum():,}")
    print(f"   ❌ PDFs vazios: {len(vazios):,}")
    print(f"   📈 Cobertura atual: {df['conteudo_pdf'].str.len().gt(0).sum()/len(df)*100:.1f}%")
    
    # Categoriza problemas
    categorias = {
        'url_vazia': [],
        'url_html': [],
        'url_octet_stream': [],
        'erro_download': [],
        'erro_extracao': [],
        'outros': []
    }
    
    for idx, row in vazios.iterrows():
        link_pdf = row['link_pdf']
        erro = row.get('erro_extracao', '')
        
        if pd.isna(link_pdf) or link_pdf == '':
            categorias['url_vazia'].append(row)
        elif 'Retorna HTML' in erro or 'erro 404' in erro.lower():
            categorias['url_html'].append(row)
        elif 'application/octet-stream' in erro or 'Content-Type desconhecido' in erro:
            categorias['url_octet_stream'].append(row)
        elif 'Erro no download' in erro:
            categorias['erro_download'].append(row)
        elif 'Não foi possível extrair' in erro:
            categorias['erro_extracao'].append(row)
        else:
            categorias['outros'].append(row)
    
    print(f"\n🔍 CATEGORIZAÇÃO DOS PROBLEMAS:")
    for categoria, registros in categorias.items():
        if registros:
            print(f"   • {categoria.replace('_', ' ').title()}: {len(registros)} PDFs")
    
    return vazios, categorias

def gerar_relatorio_detalhado(vazios, categorias):
    """
    Gera relatório detalhado por categoria
    """
    print(f"\n📄 RELATÓRIO DETALHADO POR CATEGORIA")
    print("=" * 50)
    
    for categoria, registros in categorias.items():
        if not registros:
            continue
            
        print(f"\n🔸 {categoria.replace('_', ' ').upper()}: {len(registros)} PDFs")
        print("-" * 40)
        
        # Mostra primeiros 5 exemplos
        for i, row in enumerate(registros[:5]):
            codigo = row['codigo_registro']
            titulo = row['titulo'][:60] + "..." if len(row['titulo']) > 60 else row['titulo']
            link = row['link_pdf'] if pd.notna(row['link_pdf']) else "VAZIO"
            erro = row.get('erro_extracao', 'Sem erro registrado')
            
            print(f"   {i+1}. ID {codigo}: {titulo}")
            print(f"      Link: {link}")
            print(f"      Erro: {erro}")
            print()
        
        if len(registros) > 5:
            print(f"   ... e mais {len(registros) - 5} registros similares")

def analisar_por_ano(vazios):
    """
    Analisa PDFs vazios por ano
    """
    print(f"\n📅 ANÁLISE POR ANO")
    print("=" * 30)
    
    # Extrai ano do título ou data
    anos = []
    for _, row in vazios.iterrows():
        titulo = row['titulo']
        ano = None
        
        # Tenta extrair ano do título
        import re
        match = re.search(r'(\d{4})', titulo)
        if match:
            ano = int(match.group(1))
        else:
            # Tenta extrair da data se disponível
            if 'data_publicacao' in row and pd.notna(row['data_publicacao']):
                try:
                    ano = pd.to_datetime(row['data_publicacao']).year
                except:
                    pass
        
        anos.append(ano)
    
    # Conta por ano
    from collections import Counter
    contador_anos = Counter([a for a in anos if a is not None])
    
    print("📊 PDFs vazios por ano:")
    for ano in sorted(contador_anos.keys()):
        print(f"   {ano}: {contador_anos[ano]} PDFs")

def analisar_por_tipo(vazios):
    """
    Analisa PDFs vazios por tipo de documento
    """
    print(f"\n📋 ANÁLISE POR TIPO DE DOCUMENTO")
    print("=" * 40)
    
    tipos = []
    for _, row in vazios.iterrows():
        titulo = row['titulo']
        
        # Identifica tipo baseado no título
        tipo = "Outros"
        if "Resolução" in titulo:
            tipo = "Resolução"
        elif "Portaria" in titulo:
            tipo = "Portaria"
        elif "Acórdão" in titulo:
            tipo = "Acórdão"
        elif "Deliberação" in titulo:
            tipo = "Deliberação"
        elif "Termo de Autorização" in titulo:
            tipo = "Termo de Autorização"
        elif "Despacho" in titulo:
            tipo = "Despacho"
        elif "Ementa" in titulo:
            tipo = "Ementa"
        
        tipos.append(tipo)
    
    # Conta por tipo
    from collections import Counter
    contador_tipos = Counter(tipos)
    
    print("📊 PDFs vazios por tipo:")
    for tipo, count in contador_tipos.most_common():
        print(f"   {tipo}: {count} PDFs")

def salvar_relatorio_csv(vazios, categorias):
    """
    Salva relatório em CSV
    """
    # Adiciona categoria a cada registro
    vazios_com_categoria = vazios.copy()
    vazios_com_categoria['categoria_problema'] = 'outros'
    
    for categoria, registros in categorias.items():
        indices = [r.name for r in registros]
        vazios_com_categoria.loc[indices, 'categoria_problema'] = categoria
    
    # Salva CSV
    arquivo_csv = "relatorio_pdfs_vazios.csv"
    vazios_com_categoria.to_csv(arquivo_csv, index=False)
    print(f"\n💾 Relatório salvo em: {arquivo_csv}")
    
    return arquivo_csv

def main():
    """
    Função principal
    """
    print("📋 RELATÓRIO DE PDFs VAZIOS - NORMAS ANTAQ")
    print("=" * 60)
    
    try:
        arquivo = "normas_antaq_completo.parquet"
        
        if not os.path.exists(arquivo):
            print("❌ Arquivo normas_antaq_completo.parquet não encontrado")
            return
        
        # Analisa PDFs vazios
        vazios, categorias = analisar_pdfs_vazios(arquivo)
        
        if len(vazios) == 0:
            print("✅ Nenhum PDF vazio encontrado!")
            return
        
        # Gera relatórios
        gerar_relatorio_detalhado(vazios, categorias)
        analisar_por_ano(vazios)
        analisar_por_tipo(vazios)
        
        # Salva relatório
        arquivo_csv = salvar_relatorio_csv(vazios, categorias)
        
        print(f"\n🎯 RECOMENDAÇÕES:")
        print(f"   📄 URLs vazias ({len(categorias['url_vazia'])}): Verificar se os links foram extraídos corretamente")
        print(f"   🌐 URLs HTML ({len(categorias['url_html'])}): Links quebrados ou arquivos removidos")
        print(f"   📦 Octet-stream ({len(categorias['url_octet_stream'])}): Arquivos corrompidos ou não-PDF")
        print(f"   ⬇️  Erros de download ({len(categorias['erro_download'])}): Problemas de rede/conexão")
        print(f"   🔧 Erros de extração ({len(categorias['erro_extracao'])}): PDFs com proteção ou formato especial")
        
        print(f"\n💡 PRÓXIMOS PASSOS:")
        print(f"   🔍 Verificar manualmente alguns exemplos de cada categoria")
        print(f"   🔄 Tentar reprocessar com diferentes estratégias")
        print(f"   📞 Contatar ANTAQ sobre links quebrados")
        print(f"   📊 Usar o relatório CSV para análise detalhada")
        
    except Exception as e:
        print(f"❌ Erro durante análise: {e}")

if __name__ == "__main__":
    main() 