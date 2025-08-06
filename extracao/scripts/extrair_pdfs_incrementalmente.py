#!/usr/bin/env python3
"""
Script para extração incremental de conteúdo de PDFs
Permite extrair PDFs apenas das normas que ainda não possuem conteúdo extraído
"""

from Scrap import SophiaANTAQScraper, PDFExtractor
import pandas as pd
import os
import time

def encontrar_base_dados():
    """
    Encontra a base de dados principal de normas
    """
    # Procura por arquivos parquet de normas
    candidatos = [
        "normas_antaq_completo.parquet",
        "normas_antaq.parquet"
    ]
    
    # Adiciona outros arquivos encontrados
    for arquivo in os.listdir('.'):
        if arquivo.endswith('.parquet') and 'normas' in arquivo.lower():
            if arquivo not in candidatos:
                candidatos.append(arquivo)
    
    # Encontra o arquivo mais recente
    arquivos_existentes = [f for f in candidatos if os.path.exists(f)]
    
    if not arquivos_existentes:
        return None
    
    arquivo_principal = max(arquivos_existentes, key=os.path.getctime)
    return arquivo_principal

def analisar_situacao_pdfs(arquivo):
    """
    Analisa quantos PDFs já foram extraídos
    """
    print(f"📊 ANÁLISE DA SITUAÇÃO ATUAL")
    print("=" * 35)
    
    df = pd.read_parquet(arquivo)
    
    total = len(df)
    com_link_pdf = df['link_pdf'].notna().sum()
    
    # Verifica se já tem coluna de conteúdo PDF
    if 'conteudo_pdf' in df.columns:
        com_conteudo = df['conteudo_pdf'].str.len().gt(0).sum()
        sem_conteudo = com_link_pdf - com_conteudo
        
        print(f"📋 Total de normas: {total}")
        print(f"📄 Com link PDF: {com_link_pdf} ({com_link_pdf/total*100:.1f}%)")
        print(f"✅ PDFs já extraídos: {com_conteudo} ({com_conteudo/com_link_pdf*100:.1f}%)")
        print(f"⏳ PDFs pendentes: {sem_conteudo} ({sem_conteudo/com_link_pdf*100:.1f}%)")
        
        return {
            'total': total,
            'com_link': com_link_pdf,
            'extraidos': com_conteudo,
            'pendentes': sem_conteudo,
            'tem_coluna_pdf': True
        }
    else:
        print(f"📋 Total de normas: {total}")
        print(f"📄 Com link PDF: {com_link_pdf} ({com_link_pdf/total*100:.1f}%)")
        print(f"⚠️  Nenhum PDF foi extraído ainda (coluna conteudo_pdf não existe)")
        
        return {
            'total': total,
            'com_link': com_link_pdf,
            'extraidos': 0,
            'pendentes': com_link_pdf,
            'tem_coluna_pdf': False
        }

def extrair_pdfs_pendentes(arquivo, max_pdfs=None):
    """
    Extrai conteúdo dos PDFs que ainda não foram processados
    """
    print(f"\n🔄 EXTRAÇÃO INCREMENTAL DE PDFs")
    print("=" * 40)
    
    df = pd.read_parquet(arquivo)
    
    # Identifica normas com PDF pendente
    if 'conteudo_pdf' in df.columns:
        # Normas com link PDF mas sem conteúdo extraído
        pendentes = df[
            (df['link_pdf'].notna()) & 
            (df['conteudo_pdf'].str.len().eq(0) | df['conteudo_pdf'].isna())
        ]
    else:
        # Todas as normas com link PDF são pendentes
        pendentes = df[df['link_pdf'].notna()]
    
    if len(pendentes) == 0:
        print("✅ Todos os PDFs já foram extraídos!")
        return df
    
    # Limita quantidade se especificado
    if max_pdfs and len(pendentes) > max_pdfs:
        pendentes = pendentes.head(max_pdfs)
        print(f"🎯 Processando apenas {max_pdfs} PDFs (de {len(df[df['link_pdf'].notna()])} pendentes)")
    else:
        print(f"🎯 Processando {len(pendentes)} PDFs pendentes")
    
    # Cria extrator de PDF
    scraper = SophiaANTAQScraper(delay=1.0, extract_pdf_content=False)
    pdf_extractor = PDFExtractor(scraper.session, timeout=30)
    
    # Adiciona colunas de PDF se não existirem
    if 'conteudo_pdf' not in df.columns:
        df['conteudo_pdf'] = ''
        df['metodo_extracao'] = ''
        df['tamanho_pdf'] = 0
        df['paginas_extraidas'] = 0
        df['erro_extracao'] = ''
    
    # Processa cada PDF pendente
    sucessos = 0
    erros = 0
    
    print(f"\n📥 Iniciando extração de PDFs...")
    start_time = time.time()
    
    for idx, (index, row) in enumerate(pendentes.iterrows(), 1):
        codigo = row['codigo_registro']
        titulo = row['titulo'][:40] + "..."
        pdf_url = row['link_pdf']
        
        print(f"📄 [{idx}/{len(pendentes)}] ID {codigo}: {titulo}")
        
        try:
            # Extrai conteúdo do PDF
            resultado = pdf_extractor.extract_pdf_content(pdf_url)
            
            # Atualiza o DataFrame
            df.loc[index, 'conteudo_pdf'] = resultado.get('conteudo_pdf', '')
            df.loc[index, 'metodo_extracao'] = resultado.get('metodo_extracao', '')
            df.loc[index, 'tamanho_pdf'] = resultado.get('tamanho_pdf', 0)
            df.loc[index, 'paginas_extraidas'] = resultado.get('paginas_extraidas', 0)
            df.loc[index, 'erro_extracao'] = resultado.get('erro_extracao', '')
            
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
        time.sleep(0.5)
        
        # Salva progresso a cada 10 PDFs
        if idx % 10 == 0:
            backup_file = f"backup_progresso_{int(time.time())}.parquet"
            df.to_parquet(backup_file, index=False)
            print(f"   💾 Progresso salvo em: {backup_file}")
    
    # Estatísticas finais
    elapsed_time = time.time() - start_time
    
    print(f"\n📊 EXTRAÇÃO CONCLUÍDA:")
    print(f"   ⏱️  Tempo total: {elapsed_time/60:.1f} minutos")
    print(f"   ✅ Sucessos: {sucessos}")
    print(f"   ❌ Erros: {erros}")
    print(f"   📈 Taxa de sucesso: {sucessos/(sucessos+erros)*100:.1f}%")
    print(f"   🚀 Velocidade: {len(pendentes)/(elapsed_time/60):.1f} PDFs/min")
    
    return df

def salvar_dados_atualizados(df, arquivo_original):
    """
    Salva os dados atualizados
    """
    print(f"\n💾 SALVANDO DADOS ATUALIZADOS")
    print("=" * 35)
    
    # Cria backup do arquivo original
    timestamp = int(time.time())
    backup_original = f"backup_original_{timestamp}.parquet"
    
    if os.path.exists(arquivo_original):
        os.rename(arquivo_original, backup_original)
        print(f"📦 Backup do original: {backup_original}")
    
    # Salva dados atualizados
    df.to_parquet(arquivo_original, index=False)
    print(f"💾 Dados atualizados salvos em: {arquivo_original}")
    
    # Cria também versão com timestamp
    arquivo_timestamped = f"normas_com_pdfs_{timestamp}.parquet"
    df.to_parquet(arquivo_timestamped, index=False)
    print(f"📄 Cópia timestamped: {arquivo_timestamped}")
    
    # Estatísticas finais
    total = len(df)
    com_conteudo = df['conteudo_pdf'].str.len().gt(0).sum()
    tamanho_medio = df[df['conteudo_pdf'].str.len() > 0]['conteudo_pdf'].str.len().mean()
    
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   📋 Total de normas: {total}")
    print(f"   📄 PDFs com conteúdo: {com_conteudo}")
    print(f"   📊 Cobertura: {com_conteudo/total*100:.1f}%")
    print(f"   📏 Tamanho médio: {tamanho_medio:.0f} chars")

def main():
    """
    Função principal
    """
    print("🔄 EXTRAÇÃO INCREMENTAL DE PDFs - NORMAS ANTAQ")
    print("=" * 55)
    
    try:
        # Encontra base de dados
        arquivo = encontrar_base_dados()
        
        if not arquivo:
            print("❌ Nenhuma base de dados de normas encontrada")
            print("💡 Execute primeiro: python3 Scrap.py ou python3 executar_completo.py")
            return
        
        print(f"📂 Base de dados encontrada: {arquivo}")
        
        # Analisa situação atual
        situacao = analisar_situacao_pdfs(arquivo)
        
        if situacao['pendentes'] == 0:
            print(f"\n✅ Todos os PDFs já foram extraídos! Nada a fazer.")
            return
        
        # Pergunta se deve continuar
        print(f"\n❓ Deseja extrair conteúdo dos {situacao['pendentes']} PDFs pendentes?")
        print(f"⚠️  Isso pode demorar ~{situacao['pendentes']*2/60:.0f} minutos")
        
        resposta = input("Continuar? (s/N): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("❌ Extração cancelada pelo usuário")
            return
        
        # Pergunta sobre limite
        limite_str = input(f"Limite de PDFs (Enter para todos os {situacao['pendentes']}): ").strip()
        max_pdfs = None
        if limite_str:
            try:
                max_pdfs = int(limite_str)
                print(f"🎯 Limitando a {max_pdfs} PDFs")
            except ValueError:
                print("⚠️ Limite inválido, processando todos")
        
        # Extrai PDFs
        df_atualizado = extrair_pdfs_pendentes(arquivo, max_pdfs)
        
        # Salva dados atualizados
        salvar_dados_atualizados(df_atualizado, arquivo)
        
        print(f"\n🎉 EXTRAÇÃO INCREMENTAL CONCLUÍDA!")
        print(f"💡 Agora você pode:")
        print(f"   🔍 Usar pandas para buscar por conteúdo")
        print(f"   📊 Fazer análises estatísticas do texto")
        print(f"   🔄 Executar novamente para processar mais PDFs")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Extração interrompida pelo usuário")
        print(f"💡 Progresso pode ter sido salvo automaticamente")
    except Exception as e:
        print(f"❌ Erro durante extração: {e}")

if __name__ == "__main__":
    main()