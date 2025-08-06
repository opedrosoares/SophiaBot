#!/usr/bin/env python3
"""
Script para extrair dados de registros com URLs vazias
Acessa diretamente as páginas individuais do Sophia ANTAQ
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import logging
import re
from urllib.parse import urljoin
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SophiaIndividualExtractor:
    """
    Extrator para páginas individuais do Sophia ANTAQ
    """
    
    def __init__(self, delay: float = 1.0):
        self.base_url = "https://sophia.antaq.gov.br"
        self.delay = delay
        
        # Configuração da sessão
        self.session = requests.Session()
        self.session.verify = False  # Desabilita verificação SSL
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extrair_dados_pagina(self, codigo_registro):
        """
        Extrai dados de uma página individual do Sophia
        """
        url = f"{self.base_url}/Terminal/acervo/detalhe/{codigo_registro}"
        
        try:
            logger.info(f"Acessando página: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrai dados básicos
            dados = {
                'codigo_registro': codigo_registro,
                'titulo': self._extrair_titulo(soup),
                'orgao': self._extrair_orgao(soup),
                'esfera': self._extrair_campo(soup, 'Esfera'),
                'situacao': self._extrair_campo(soup, 'Situação'),
                'data_assinatura': self._extrair_campo(soup, 'Data de assinatura'),
                'data_publicacao': self._extrair_campo(soup, 'Data de publicação'),
                'processos': self._extrair_processos(soup),
                'assuntos': self._extrair_assuntos(soup),
                'texto_integral': self._extrair_texto_integral(soup),
                'link_pdf': self._extrair_link_pdf(soup),
                'conteudo_pdf': '',  # Será preenchido se houver PDF
                'metodo_extracao': '',
                'tamanho_pdf': 0,
                'paginas_extraidas': 0,
                'erro_extracao': ''
            }
            
            # Se encontrou link PDF, tenta extrair o conteúdo
            if dados['link_pdf']:
                logger.info(f"Encontrou link PDF: {dados['link_pdf']}")
                dados.update(self._extrair_conteudo_pdf(dados['link_pdf']))
            
            return dados
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do registro {codigo_registro}: {e}")
            return {
                'codigo_registro': codigo_registro,
                'titulo': '',
                'orgao': '',
                'esfera': '',
                'situacao': '',
                'data_assinatura': '',
                'data_publicacao': '',
                'processos': '',
                'assuntos': '',
                'texto_integral': '',
                'link_pdf': '',
                'conteudo_pdf': '',
                'metodo_extracao': '',
                'tamanho_pdf': 0,
                'paginas_extraidas': 0,
                'erro_extracao': f'Erro ao acessar página: {str(e)}'
            }
    
    def _extrair_titulo(self, soup):
        """Extrai o título do documento"""
        try:
            titulo_elem = soup.find('h1', class_='titulo')
            if titulo_elem:
                return titulo_elem.get_text(strip=True)
        except:
            pass
        return ''
    
    def _extrair_orgao(self, soup):
        """Extrai o órgão responsável"""
        try:
            orgao_elem = soup.find('a', class_='OrgaoNome')
            if orgao_elem:
                return orgao_elem.get_text(strip=True)
        except:
            pass
        return ''
    
    def _extrair_campo(self, soup, label_text):
        """Extrai valor de um campo específico"""
        try:
            # Procura pelo label e pega o valor do próximo elemento p
            label = soup.find('label', string=lambda text: text and label_text in text)
            if label:
                # Procura o próximo elemento p
                valor_elem = label.find_next('p')
                if valor_elem:
                    return valor_elem.get_text(strip=True)
        except:
            pass
        return ''
    
    def _extrair_processos(self, soup):
        """Extrai os processos relacionados"""
        try:
            processos_elem = soup.find('p', class_='processos')
            if processos_elem:
                return processos_elem.get_text(strip=True)
        except:
            pass
        return ''
    
    def _extrair_assuntos(self, soup):
        """Extrai os assuntos relacionados"""
        try:
            assuntos = []
            assunto_links = soup.find_all('a', attrs={'data-codigo-assunto': True})
            for link in assunto_links:
                assunto = link.get_text(strip=True)
                if assunto:
                    assuntos.append(assunto)
            return '; '.join(assuntos)
        except:
            pass
        return ''
    
    def _extrair_texto_integral(self, soup):
        """Extrai o texto integral do documento"""
        try:
            # Procura pela div que contém o texto integral
            texto_container = soup.find('div', class_='texto-html-container')
            if texto_container:
                # Procura pela div com o texto completo
                texto_div = texto_container.find('div', class_='mainbox')
                if texto_div:
                    # Remove tags HTML e extrai apenas o texto
                    texto = texto_div.get_text(separator=' ', strip=True)
                    return texto
            
            # Fallback: procura por qualquer div com texto
            texto_divs = soup.find_all('div', class_='texto-html-container')
            for div in texto_divs:
                texto = div.get_text(separator=' ', strip=True)
                if len(texto) > 100:  # Texto significativo
                    return texto
        except:
            pass
        return ''
    
    def _extrair_link_pdf(self, soup):
        """Extrai o link do PDF"""
        try:
            # Procura por links de arquivo PDF
            pdf_links = soup.find_all('a', href=re.compile(r'Download.*codigoArquivo'))
            for link in pdf_links:
                href = link.get('href')
                if href and 'pdf' in href.lower():
                    return urljoin(self.base_url, href)
            
            # Fallback: procura por qualquer link de download
            download_links = soup.find_all('a', href=re.compile(r'Download'))
            for link in download_links:
                href = link.get('href')
                if href:
                    return urljoin(self.base_url, href)
        except:
            pass
        return ''
    
    def _extrair_conteudo_pdf(self, pdf_url):
        """
        Tenta extrair conteúdo do PDF se disponível
        """
        try:
            from Scrap import PDFExtractor
            pdf_extractor = PDFExtractor(self.session, timeout=30)
            resultado = pdf_extractor.extract_pdf_content(pdf_url)
            
            return {
                'conteudo_pdf': resultado.get('conteudo_pdf', ''),
                'metodo_extracao': resultado.get('metodo_extracao', ''),
                'tamanho_pdf': resultado.get('tamanho_pdf', 0),
                'paginas_extraidas': resultado.get('paginas_extraidas', 0),
                'erro_extracao': resultado.get('erro_extracao', '')
            }
        except Exception as e:
            logger.error(f"Erro ao extrair PDF {pdf_url}: {e}")
            return {
                'conteudo_pdf': '',
                'metodo_extracao': '',
                'tamanho_pdf': 0,
                'paginas_extraidas': 0,
                'erro_extracao': f'Erro na extração de PDF: {str(e)}'
            }

def identificar_registros_urls_vazias(arquivo):
    """
    Identifica registros com URLs vazias
    """
    print(f"🔍 IDENTIFICANDO REGISTROS COM URLs VAZIAS")
    print("=" * 50)
    
    df = pd.read_parquet(arquivo)
    
    # Identifica registros com URLs vazias
    urls_vazias = df[
        (df['link_pdf'].isna()) | 
        (df['link_pdf'] == '') |
        (df['link_pdf'].str.strip() == '')
    ]
    
    print(f"📊 ESTATÍSTICAS:")
    print(f"   📋 Total de registros: {len(df):,}")
    print(f"   ❌ URLs vazias encontradas: {len(urls_vazias):,}")
    
    return urls_vazias

def extrair_registros_urls_vazias(arquivo, max_registros=None):
    """
    Extrai dados dos registros com URLs vazias
    """
    print(f"\n🔄 EXTRAÇÃO DE REGISTROS COM URLs VAZIAS")
    print("=" * 50)
    
    df = pd.read_parquet(arquivo)
    
    # Identifica registros com URLs vazias
    urls_vazias = df[
        (df['link_pdf'].isna()) | 
        (df['link_pdf'] == '') |
        (df['link_pdf'].str.strip() == '')
    ]
    
    if len(urls_vazias) == 0:
        print("✅ Nenhum registro com URL vazia encontrado!")
        return df
    
    # Limita quantidade se especificado
    if max_registros and len(urls_vazias) > max_registros:
        urls_vazias = urls_vazias.head(max_registros)
        print(f"🎯 Processando apenas {max_registros} registros (de {len(df[df['link_pdf'].isna()])} URLs vazias)")
    else:
        print(f"🎯 Processando {len(urls_vazias)} registros com URLs vazias")
    
    # Cria extrator
    extrator = SophiaIndividualExtractor(delay=1.0)
    
    # Processa cada registro
    sucessos = 0
    erros = 0
    pdfs_encontrados = 0
    
    print(f"\n📥 Iniciando extração...")
    start_time = time.time()
    
    for idx, (index, row) in enumerate(urls_vazias.iterrows(), 1):
        codigo = row['codigo_registro']
        titulo_atual = row['titulo'][:40] + "..." if len(row['titulo']) > 40 else row['titulo']
        
        print(f"\n📄 [{idx}/{len(urls_vazias)}] ID {codigo}: {titulo_atual}")
        
        try:
            # Extrai dados da página
            dados = extrator.extrair_dados_pagina(codigo)
            
            # Atualiza o DataFrame
            for campo, valor in dados.items():
                if campo in df.columns:
                    df.loc[index, campo] = valor
            
            if dados['link_pdf']:
                print(f"   🔗 PDF encontrado: {dados['link_pdf']}")
                pdfs_encontrados += 1
                
                if dados['conteudo_pdf']:
                    chars = len(dados['conteudo_pdf'])
                    metodo = dados['metodo_extracao']
                    print(f"   ✅ PDF extraído: {chars} chars via {metodo}")
                else:
                    erro = dados['erro_extracao']
                    print(f"   ⚠️  PDF não extraído: {erro}")
            
            if dados['titulo']:
                print(f"   ✅ Dados extraídos: {dados['titulo']}")
                sucessos += 1
            else:
                print(f"   ❌ Falha na extração")
                erros += 1
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            df.loc[index, 'erro_extracao'] = f'Erro na extração: {str(e)}'
            erros += 1
        
        # Pausa entre requisições
        time.sleep(extrator.delay)
        
        # Salva progresso a cada 10 registros
        if idx % 10 == 0:
            backup_file = f"backup_urls_vazias_{int(time.time())}.parquet"
            df.to_parquet(backup_file, index=False)
            print(f"   💾 Progresso salvo em: {backup_file}")
    
    # Estatísticas finais
    elapsed_time = time.time() - start_time
    
    print(f"\n📊 EXTRAÇÃO CONCLUÍDA:")
    print(f"   ⏱️  Tempo total: {elapsed_time/60:.1f} minutos")
    print(f"   ✅ Sucessos: {sucessos}")
    print(f"   ❌ Erros: {erros}")
    print(f"   🔗 PDFs encontrados: {pdfs_encontrados}")
    print(f"   📈 Taxa de sucesso: {sucessos/(sucessos+erros)*100:.1f}%")
    
    return df

def main():
    """
    Função principal
    """
    print("🔄 EXTRAÇÃO DE REGISTROS COM URLs VAZIAS - SOPHIA ANTAQ")
    print("=" * 70)
    
    try:
        arquivo = "normas_antaq_completo.parquet"
        
        if not os.path.exists(arquivo):
            print("❌ Arquivo normas_antaq_completo.parquet não encontrado")
            return
        
        print(f"📂 Base de dados: {arquivo}")
        
        # Identifica registros com URLs vazias
        urls_vazias = identificar_registros_urls_vazias(arquivo)
        
        if len(urls_vazias) == 0:
            print(f"\n✅ Nenhum registro com URL vazia encontrado! Nada a fazer.")
            return
        
        # Pergunta se deve continuar
        print(f"\n❓ Deseja extrair dados dos {len(urls_vazias)} registros com URLs vazias?")
        print(f"⚠️  Isso pode demorar ~{len(urls_vazias)*2/60:.0f} minutos")
        
        resposta = input("Continuar? (s/N): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("❌ Extração cancelada pelo usuário")
            return
        
        # Pergunta sobre limite
        limite_str = input(f"Limite de registros (Enter para todos os {len(urls_vazias)}): ").strip()
        max_registros = None
        if limite_str:
            try:
                max_registros = int(limite_str)
                print(f"🎯 Limitando a {max_registros} registros")
            except ValueError:
                print("⚠️ Limite inválido, processando todos")
        
        # Extrai registros
        df_atualizado = extrair_registros_urls_vazias(arquivo, max_registros)
        
        # Salva dados atualizados
        timestamp = int(time.time())
        backup_original = f"backup_antes_urls_vazias_{timestamp}.parquet"
        
        if os.path.exists(arquivo):
            os.rename(arquivo, backup_original)
            print(f"📦 Backup do original: {backup_original}")
        
        df_atualizado.to_parquet(arquivo, index=False)
        print(f"💾 Dados atualizados salvos em: {arquivo}")
        
        # Estatísticas finais
        total = len(df_atualizado)
        com_conteudo = df_atualizado['conteudo_pdf'].str.len().gt(0).sum()
        com_link = df_atualizado['link_pdf'].str.len().gt(0).sum()
        
        print(f"\n📊 ESTATÍSTICAS FINAIS:")
        print(f"   📋 Total de normas: {total:,}")
        print(f"   📄 PDFs com conteúdo: {com_conteudo:,}")
        print(f"   🔗 PDFs com link: {com_link:,}")
        print(f"   📈 Cobertura: {com_conteudo/total*100:.1f}%")
        
        print(f"\n🎉 EXTRAÇÃO CONCLUÍDA!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Extração interrompida pelo usuário")
        print(f"💡 Progresso pode ter sido salvo automaticamente")
    except Exception as e:
        print(f"❌ Erro durante extração: {e}")

if __name__ == "__main__":
    main() 