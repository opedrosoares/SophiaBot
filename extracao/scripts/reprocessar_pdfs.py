#!/usr/bin/env python3
"""
Script para reprocessar PDFs que falharam na extração
Usa estratégias mais robustas e melhor tratamento de erros
"""

import pandas as pd
import requests
import time
import logging
from urllib.parse import urljoin, urlparse
import os
from Scrap import PDFExtractor, SophiaANTAQScraper

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analisar_pdfs_falhados(arquivo):
    """
    Analisa PDFs que falharam na extração
    """
    print(f"🔍 ANÁLISE DE PDFs FALHADOS")
    print("=" * 35)
    
    df = pd.read_parquet(arquivo)
    
    # Identifica PDFs falhados
    falhados = df[
        (df['link_pdf'].notna()) & 
        (df['conteudo_pdf'].str.len().eq(0) | df['conteudo_pdf'].isna())
    ]
    
    print(f"📋 Total de normas: {len(df)}")
    print(f"📄 Com link PDF: {df['link_pdf'].notna().sum()}")
    print(f"❌ PDFs falhados: {len(falhados)}")
    
    # Analisa tipos de erro
    if 'erro_extracao' in df.columns:
        erros = falhados['erro_extracao'].value_counts()
        print(f"\n📊 TIPOS DE ERRO:")
        for erro, count in erros.head(10).items():
            print(f"   • {erro}: {count}")
    
    return falhados

def testar_url_pdf(url, session):
    """
    Testa se a URL realmente retorna um PDF
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = session.get(url, headers=headers, timeout=30, allow_redirects=True)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            
            if 'pdf' in content_type:
                return True, 'PDF válido'
            elif 'html' in content_type:
                return False, 'Retorna HTML (possível erro 404)'
            else:
                return False, f'Content-Type desconhecido: {content_type}'
        else:
            return False, f'HTTP {response.status_code}'
            
    except Exception as e:
        return False, f'Erro de conexão: {str(e)}'

def tentar_urls_alternativas(url_original):
    """
    Tenta variações da URL original
    """
    urls_alternativas = [url_original]
    
    # Remove parâmetros de query
    parsed = urlparse(url_original)
    if parsed.query:
        url_sem_query = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        urls_alternativas.append(url_sem_query)
    
    # Tenta com/sem www
    if 'www.' in parsed.netloc:
        url_sem_www = url_original.replace('www.', '')
        urls_alternativas.append(url_sem_www)
    else:
        url_com_www = url_original.replace('://', '://www.')
        urls_alternativas.append(url_com_www)
    
    # Tenta variações de extensão
    if url_original.endswith('.pdf'):
        url_sem_ext = url_original[:-4]
        urls_alternativas.extend([url_sem_ext, url_sem_ext + '.PDF'])
    
    return list(set(urls_alternativas))  # Remove duplicatas

def reprocessar_pdf_robusto(pdf_url, session, pdf_extractor):
    """
    Tenta extrair PDF com estratégias mais robustas
    """
    print(f"🔧 Testando URL: {pdf_url}")
    
    # Testa URL original
    is_valid, status = testar_url_pdf(pdf_url, session)
    if is_valid:
        print(f"   ✅ URL válida: {status}")
        resultado = pdf_extractor.extract_pdf_content(pdf_url)
        if resultado.get('conteudo_pdf'):
            return resultado, pdf_url
    
    print(f"   ❌ URL inválida: {status}")
    
    # Tenta URLs alternativas
    urls_alternativas = tentar_urls_alternativas(pdf_url)
    print(f"   🔄 Tentando {len(urls_alternativas)-1} URLs alternativas...")
    
    for url_alt in urls_alternativas[1:]:  # Pula a original
        print(f"      Testando: {url_alt}")
        is_valid, status = testar_url_pdf(url_alt, session)
        
        if is_valid:
            print(f"      ✅ URL alternativa válida: {status}")
            resultado = pdf_extractor.extract_pdf_content(url_alt)
            if resultado.get('conteudo_pdf'):
                return resultado, url_alt
        else:
            print(f"      ❌ URL alternativa inválida: {status}")
    
    # Nenhuma URL funcionou
    return {
        'conteudo_pdf': '',
        'metodo_extracao': '',
        'tamanho_pdf': 0,
        'paginas_extraidas': 0,
        'erro_extracao': 'Todas as URLs testadas falharam'
    }, None

def reprocessar_pdfs_falhados(arquivo, max_pdfs=None):
    """
    Reprocessa PDFs que falharam com estratégias mais robustas
    """
    print(f"\n🔄 REPROCESSAMENTO ROBUSTO DE PDFs FALHADOS")
    print("=" * 50)
    
    df = pd.read_parquet(arquivo)
    
    # Identifica PDFs falhados
    falhados = df[
        (df['link_pdf'].notna()) & 
        (df['conteudo_pdf'].str.len().eq(0) | df['conteudo_pdf'].isna())
    ]
    
    if len(falhados) == 0:
        print("✅ Nenhum PDF falhado encontrado!")
        return df
    
    # Limita quantidade se especificado
    if max_pdfs and len(falhados) > max_pdfs:
        falhados = falhados.head(max_pdfs)
        print(f"🎯 Processando apenas {max_pdfs} PDFs (de {len(df[df['link_pdf'].notna()])} falhados)")
    else:
        print(f"🎯 Processando {len(falhados)} PDFs falhados")
    
    # Cria sessão e extrator
    scraper = SophiaANTAQScraper(delay=1.0, extract_pdf_content=False)
    pdf_extractor = PDFExtractor(scraper.session, timeout=60)  # Timeout maior
    
    # Processa cada PDF falhado
    sucessos = 0
    erros = 0
    urls_corrigidas = 0
    
    print(f"\n📥 Iniciando reprocessamento...")
    start_time = time.time()
    
    for idx, (index, row) in enumerate(falhados.iterrows(), 1):
        codigo = row['codigo_registro']
        titulo = row['titulo'][:40] + "..."
        pdf_url = row['link_pdf']
        
        print(f"\n📄 [{idx}/{len(falhados)}] ID {codigo}: {titulo}")
        
        try:
            # Tenta reprocessar com estratégias robustas
            resultado, url_corrigida = reprocessar_pdf_robusto(pdf_url, scraper.session, pdf_extractor)
            
            # Atualiza o DataFrame
            df.loc[index, 'conteudo_pdf'] = resultado.get('conteudo_pdf', '')
            df.loc[index, 'metodo_extracao'] = resultado.get('metodo_extracao', '')
            df.loc[index, 'tamanho_pdf'] = resultado.get('tamanho_pdf', 0)
            df.loc[index, 'paginas_extraidas'] = resultado.get('paginas_extraidas', 0)
            df.loc[index, 'erro_extracao'] = resultado.get('erro_extracao', '')
            
            # Se usou URL corrigida, atualiza o link
            if url_corrigida and url_corrigida != pdf_url:
                df.loc[index, 'link_pdf'] = url_corrigida
                urls_corrigidas += 1
                print(f"   🔗 URL corrigida: {url_corrigida}")
            
            if resultado.get('conteudo_pdf'):
                chars = len(resultado['conteudo_pdf'])
                metodo = resultado['metodo_extracao']
                print(f"   ✅ Extraído: {chars} chars via {metodo}")
                sucessos += 1
            else:
                erro = resultado.get('erro_extracao', 'Erro desconhecido')
                print(f"   ❌ Erro: {erro}")
                erros += 1
            
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
            df.loc[index, 'erro_extracao'] = f"Exceção: {str(e)}"
            erros += 1
        
        # Pausa entre PDFs
        time.sleep(1.0)  # Pausa maior para não sobrecarregar
        
        # Salva progresso a cada 5 PDFs
        if idx % 5 == 0:
            backup_file = f"backups/backup_reprocessamento_{int(time.time())}.parquet"
            df.to_parquet(backup_file, index=False)
            print(f"   💾 Progresso salvo em: {backup_file}")
    
    # Estatísticas finais
    elapsed_time = time.time() - start_time
    
    print(f"\n📊 REPROCESSAMENTO CONCLUÍDO:")
    print(f"   ⏱️  Tempo total: {elapsed_time/60:.1f} minutos")
    print(f"   ✅ Sucessos: {sucessos}")
    print(f"   ❌ Erros: {erros}")
    print(f"   🔗 URLs corrigidas: {urls_corrigidas}")
    print(f"   📈 Taxa de sucesso: {sucessos/(sucessos+erros)*100:.1f}%")
    
    return df

def main():
    """
    Função principal
    """
    print("🔄 REPROCESSAMENTO DE PDFs FALHADOS - NORMAS ANTAQ")
    print("=" * 60)
    
    try:
        # Encontra base de dados
        arquivo = "data/normas_antaq_completo.parquet"
        
        if not os.path.exists(arquivo):
            print("❌ Arquivo normas_antaq_completo.parquet não encontrado")
            return
        
        print(f"📂 Base de dados: {arquivo}")
        
        # Analisa PDFs falhados
        falhados = analisar_pdfs_falhados(arquivo)
        
        if len(falhados) == 0:
            print(f"\n✅ Nenhum PDF falhado encontrado! Nada a fazer.")
            return
        
        # Pergunta se deve continuar
        print(f"\n❓ Deseja reprocessar os {len(falhados)} PDFs falhados?")
        print(f"⚠️  Isso pode demorar ~{len(falhados)*2/60:.0f} minutos")
        
        resposta = input("Continuar? (s/N): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("❌ Reprocessamento cancelado pelo usuário")
            return
        
        # Pergunta sobre limite
        limite_str = input(f"Limite de PDFs (Enter para todos os {len(falhados)}): ").strip()
        max_pdfs = None
        if limite_str:
            try:
                max_pdfs = int(limite_str)
                print(f"🎯 Limitando a {max_pdfs} PDFs")
            except ValueError:
                print("⚠️ Limite inválido, processando todos")
        
        # Reprocessa PDFs
        df_atualizado = reprocessar_pdfs_falhados(arquivo, max_pdfs)
        
        # Salva dados atualizados
        timestamp = int(time.time())
        backup_original = f"backups/backup_antes_reprocessamento_{timestamp}.parquet"
        
        if os.path.exists(arquivo):
            os.rename(arquivo, backup_original)
            print(f"📦 Backup do original: {backup_original}")
        
        df_atualizado.to_parquet(arquivo, index=False)
        print(f"💾 Dados atualizados salvos em: {arquivo}")
        
        # Estatísticas finais
        total = len(df_atualizado)
        com_conteudo = df_atualizado['conteudo_pdf'].str.len().gt(0).sum()
        
        print(f"\n📊 ESTATÍSTICAS FINAIS:")
        print(f"   📋 Total de normas: {total}")
        print(f"   📄 PDFs com conteúdo: {com_conteudo}")
        print(f"   📊 Cobertura: {com_conteudo/total*100:.1f}%")
        
        print(f"\n🎉 REPROCESSAMENTO CONCLUÍDO!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Reprocessamento interrompido pelo usuário")
        print(f"💡 Progresso pode ter sido salvo automaticamente")
    except Exception as e:
        print(f"❌ Erro durante reprocessamento: {e}")

if __name__ == "__main__":
    main() 