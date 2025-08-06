#!/usr/bin/env python3
"""
Webscraper para extrair normas do Sistema Sophia da ANTAQ
Extrai títulos, autores, datas e links de PDFs das normas da ANTAQ
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin, parse_qs, urlparse
import logging
from typing import List, Dict, Optional
import uuid
import os
import warnings
from urllib3.exceptions import InsecureRequestWarning
import tempfile
import io

# Bibliotecas para extração de PDF e OCR
try:
    import PyPDF2
    import pdfplumber
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_bytes
    PDF_EXTRACTION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Bibliotecas de PDF/OCR não disponíveis: {e}")
    PDF_EXTRACTION_AVAILABLE = False

# Suprime warnings de SSL quando verificação é desabilitada
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Classe para extração de conteúdo de PDFs com fallback para OCR
    """
    
    def __init__(self, session: requests.Session, timeout: int = 30):
        """
        Inicializa o extrator de PDF
        
        Args:
            session: Sessão requests para downloads
            timeout: Timeout para downloads em segundos
        """
        self.session = session
        self.timeout = timeout
        self.pdf_cache = {}  # Cache para evitar redownload
    
    def download_pdf(self, pdf_url: str) -> Optional[bytes]:
        """
        Faz download do PDF
        
        Args:
            pdf_url: URL do PDF
            
        Returns:
            Bytes do PDF ou None se erro
        """
        try:
            if not pdf_url:
                return None
            
            # Verifica cache
            if pdf_url in self.pdf_cache:
                logger.debug(f"PDF encontrado no cache: {pdf_url}")
                return self.pdf_cache[pdf_url]
            
            logger.debug(f"Fazendo download do PDF: {pdf_url}")
            response = self.session.get(pdf_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Verifica se é realmente um PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not pdf_url.lower().endswith('.pdf'):
                logger.warning(f"Arquivo pode não ser PDF: {content_type}")
            
            pdf_bytes = response.content
            
            # Cache do resultado
            self.pdf_cache[pdf_url] = pdf_bytes
            
            logger.debug(f"PDF baixado com sucesso: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout no download do PDF: {pdf_url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro no download do PDF {pdf_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado no download do PDF {pdf_url}: {e}")
            return None
    
    def extract_text_pypdf2(self, pdf_bytes: bytes) -> str:
        """
        Extrai texto usando PyPDF2
        
        Args:
            pdf_bytes: Bytes do PDF
            
        Returns:
            Texto extraído
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    logger.debug(f"Erro ao extrair página com PyPDF2: {e}")
                    continue
            
            return text.strip()
            
        except Exception as e:
            logger.debug(f"Erro com PyPDF2: {e}")
            return ""
    
    def extract_text_pdfplumber(self, pdf_bytes: bytes) -> str:
        """
        Extrai texto usando pdfplumber (mais robusto)
        
        Args:
            pdf_bytes: Bytes do PDF
            
        Returns:
            Texto extraído
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            text = ""
            
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        logger.debug(f"Erro ao extrair página com pdfplumber: {e}")
                        continue
            
            return text.strip()
            
        except Exception as e:
            logger.debug(f"Erro com pdfplumber: {e}")
            return ""
    
    def extract_text_ocr(self, pdf_bytes: bytes) -> str:
        """
        Extrai texto usando OCR (fallback para PDFs digitalizados)
        
        Args:
            pdf_bytes: Bytes do PDF
            
        Returns:
            Texto extraído via OCR
        """
        try:
            logger.debug("Tentando extração via OCR...")
            
            # Converte PDF para imagens
            images = convert_from_bytes(pdf_bytes, dpi=300)
            
            text = ""
            for i, image in enumerate(images):
                try:
                    # Extrai texto da imagem usando Tesseract
                    page_text = pytesseract.image_to_string(image, lang='por')
                    if page_text.strip():
                        text += f"--- Página {i+1} ---\n{page_text}\n\n"
                except Exception as e:
                    logger.debug(f"Erro OCR na página {i+1}: {e}")
                    continue
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Erro no OCR: {e}")
            return ""
    
    def extract_pdf_content(self, pdf_url: str) -> Dict[str, str]:
        """
        Extrai conteúdo do PDF usando múltiplas estratégias
        
        Args:
            pdf_url: URL do PDF
            
        Returns:
            Dicionário com informações da extração
        """
        result = {
            'conteudo_pdf': '',
            'metodo_extracao': '',
            'tamanho_pdf': 0,
            'paginas_extraidas': 0,
            'erro_extracao': ''
        }
        
        if not PDF_EXTRACTION_AVAILABLE:
            result['erro_extracao'] = 'Bibliotecas de PDF/OCR não disponíveis'
            return result
        
        # Download do PDF
        pdf_bytes = self.download_pdf(pdf_url)
        if not pdf_bytes:
            result['erro_extracao'] = 'Erro no download do PDF'
            return result
        
        result['tamanho_pdf'] = len(pdf_bytes)
        
        # Estratégia 1: pdfplumber (mais robusto)
        text = self.extract_text_pdfplumber(pdf_bytes)
        if text and len(text.strip()) > 50:  # Mínimo de 50 caracteres
            result['conteudo_pdf'] = text
            result['metodo_extracao'] = 'pdfplumber'
            result['paginas_extraidas'] = text.count('\n') // 20  # Estimativa
            return result
        
        # Estratégia 2: PyPDF2 (fallback)
        text = self.extract_text_pypdf2(pdf_bytes)
        if text and len(text.strip()) > 50:
            result['conteudo_pdf'] = text
            result['metodo_extracao'] = 'PyPDF2'
            result['paginas_extraidas'] = text.count('\n') // 20
            return result
        
        # Estratégia 3: OCR (para PDFs digitalizados)
        logger.info(f"PDF parece ser digitalizado, tentando OCR...")
        text = self.extract_text_ocr(pdf_bytes)
        if text and len(text.strip()) > 50:
            result['conteudo_pdf'] = text
            result['metodo_extracao'] = 'OCR'
            result['paginas_extraidas'] = text.count('--- Página')
            return result
        
        # Nenhuma estratégia funcionou
        result['erro_extracao'] = 'Não foi possível extrair texto do PDF'
        return result

class SophiaANTAQScraper:
    def __init__(self, delay: float = 1.0, verify_ssl: bool = False, extract_pdf_content: bool = True):
        """
        Inicializa o scraper para o Sistema Sophia da ANTAQ
        
        Args:
            delay: Tempo de espera entre requisições em segundos
            verify_ssl: Se deve verificar certificados SSL (False por padrão para evitar erros)
            extract_pdf_content: Se deve extrair conteúdo dos PDFs (padrão True)
        """
        self.base_url = "https://sophia.antaq.gov.br"
        self.session = requests.Session()
        self.session.verify = verify_ssl  # Desabilita verificação SSL por padrão
        self.delay = delay
        self.guid = None
        self.extract_pdf_content = extract_pdf_content
        
        # Inicializa extrator de PDF se habilitado
        if self.extract_pdf_content:
            self.pdf_extractor = PDFExtractor(self.session, timeout=30)
        else:
            self.pdf_extractor = None
        
        # Headers padrão baseados na requisição fornecida
        self.session.headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        })
    
    def get_initial_guid(self) -> str:
        """
        Acessa a página inicial para obter o GUID de sessão
        
        Returns:
            GUID de sessão extraído da página
        """
        try:
            logger.info("Acessando página inicial para obter GUID...")
            url = f"{self.base_url}/Terminal/"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Procura por campo GUID no formulário ou JavaScript
            guid_patterns = [
                r'Guid["\']?\s*[:=]\s*["\']?([a-f0-9-]+)',
                r'guid["\']?\s*[:=]\s*["\']?([a-f0-9-]+)',
                r'value\s*=\s*["\']([0-9]+)["\'].*?name\s*=\s*["\']Guid["\']',
                r'name\s*=\s*["\']Guid["\'].*?value\s*=\s*["\']([0-9]+)["\']'
            ]
            
            for pattern in guid_patterns:
                match = re.search(pattern, response.text, re.IGNORECASE)
                if match:
                    self.guid = match.group(1)
                    logger.info(f"GUID encontrado: {self.guid}")
                    return self.guid
            
            # Se não encontrou, gera um timestamp como fallback
            self.guid = str(int(time.time() * 1000))
            logger.warning(f"GUID não encontrado, usando timestamp: {self.guid}")
            return self.guid
            
        except Exception as e:
            logger.error(f"Erro ao obter GUID: {e}")
            # Fallback para timestamp atual
            self.guid = str(int(time.time() * 1000))
            return self.guid
    
    def submit_search_form(self, ano: int = 2025) -> str:
        """
        Submete o formulário de busca com CodigosOrgao = 6
        
        Args:
            ano: Ano para filtrar a busca (padrão: 2025)
        
        Returns:
            URL de redirecionamento com o novo GUID
        """
        try:
            logger.info(f"Submetendo formulário de busca para o ano {ano}...")
            
            # Gera novo GUID para esta busca
            search_guid = str(int(time.time() * 1000))
            
            url = f"{self.base_url}/Terminal/Busca/RapidaLegislacao?bibliotecas="
            
            data = {
                'Guid': search_guid,
                'TipoBuscaRapida': '0',
                'IniciadoCom': 'false',
                'PalavraChave': '',
                'ValidacaoLegislacao': '',
                'CodigosNorma': '',
                'Numero': '',
                'Ano': str(ano),
                'CodigosOrgao': ''
            }
            
            headers = {
                'content-type': 'application/x-www-form-urlencoded',
                'cache-control': 'max-age=0'
            }
            
            response = self.session.post(url, data=data, headers=headers, allow_redirects=False)
            
            if response.status_code in [302, 303]:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    full_redirect_url = urljoin(self.base_url, redirect_url)
                    self.guid = search_guid
                    logger.info(f"Redirecionamento para: {full_redirect_url}")
                    return full_redirect_url
            
            # Se não houve redirecionamento, constrói a URL esperada
            results_url = f"{self.base_url}/Terminal/Resultado/ListarLegislacao?guid={search_guid}"
            self.guid = search_guid
            return results_url
            
        except Exception as e:
            logger.error(f"Erro ao submeter formulário: {e}")
            raise
    
    def extract_card_data(self, card_element) -> Dict:
        """
        Extrai dados de um card de norma
        
        Args:
            card_element: Elemento BeautifulSoup do card
            
        Returns:
            Dicionário com os dados extraídos
        """
        data = {
            'titulo': '',
            'autor': '',
            'esfera': '',
            'situacao': '',
            'assinatura': '',
            'publicacao': '',
            'assunto': '',
            'link_pdf': '',
            'codigo_registro': '',
            'tipo_material': '',
            'conteudo_pdf': '',
            'metodo_extracao': '',
            'tamanho_pdf': 0,
            'paginas_extraidas': 0,
            'erro_extracao': ''
        }
        
        try:
            # Título
            titulo_elem = card_element.find('p', class_='titulo')
            if titulo_elem:
                titulo_link = titulo_elem.find('a')
                if titulo_link:
                    data['titulo'] = titulo_link.get_text(strip=True)
                    # Extrai código do registro da URL
                    href = titulo_link.get('href', '')
                    match = re.search(r'detalhe/(\d+)', href)
                    if match:
                        data['codigo_registro'] = match.group(1)
            
            # Autor
            autor_elem = card_element.find('p', class_='autor')
            if autor_elem:
                autor_link = autor_elem.find('a', class_='link-autor')
                if autor_link:
                    data['autor'] = autor_link.get_text(strip=True)
            
            # Tipo de material
            material_elem = card_element.find('p', class_='material')
            if material_elem:
                data['tipo_material'] = material_elem.get_text(strip=True)
            
            # Esfera
            esfera_elem = card_element.find('p', class_='esfera')
            if esfera_elem:
                esfera_text = esfera_elem.get_text(strip=True)
                data['esfera'] = esfera_text.replace('Esfera:', '').strip()
            
            # Situação
            situacao_elem = card_element.find('p', class_='situacao')
            if situacao_elem:
                situacao_span = situacao_elem.find('span', class_='destaque-situacao')
                if situacao_span:
                    data['situacao'] = situacao_span.get_text(strip=True)
            
            # Data de assinatura
            assinatura_elem = card_element.find('p', class_='assinatura')
            if assinatura_elem:
                assinatura_text = assinatura_elem.get_text(strip=True)
                data['assinatura'] = assinatura_text.replace('Assinatura:', '').strip()
            
            # Data de publicação
            publicacao_elem = card_element.find('p', class_='publicacao')
            if publicacao_elem:
                publicacao_text = publicacao_elem.get_text(strip=True)
                data['publicacao'] = publicacao_text.replace('Publicação:', '').strip()
            
            # Assunto
            assunto_elem = card_element.find('p', class_='assunto')
            if assunto_elem:
                assunto_link = assunto_elem.find('a')
                if assunto_link:
                    data['assunto'] = assunto_link.get_text(strip=True)
            
            # Link do PDF
            pdf_elem = card_element.find('div', class_='arquivos')
            if pdf_elem:
                pdf_link = pdf_elem.find('a')
                if pdf_link:
                    href = pdf_link.get('href', '')
                    if href:
                        data['link_pdf'] = urljoin(self.base_url, href)
            
            # Extração do conteúdo do PDF (se habilitado)
            if self.extract_pdf_content and self.pdf_extractor and data['link_pdf']:
                try:
                    logger.info(f"Extraindo conteúdo do PDF: {data['codigo_registro']} - {data['titulo'][:50]}...")
                    pdf_result = self.pdf_extractor.extract_pdf_content(data['link_pdf'])
                    
                    data['conteudo_pdf'] = pdf_result.get('conteudo_pdf', '')
                    data['metodo_extracao'] = pdf_result.get('metodo_extracao', '')
                    data['tamanho_pdf'] = pdf_result.get('tamanho_pdf', 0)
                    data['paginas_extraidas'] = pdf_result.get('paginas_extraidas', 0)
                    data['erro_extracao'] = pdf_result.get('erro_extracao', '')
                    
                    if data['conteudo_pdf']:
                        logger.info(f"✅ PDF extraído: {len(data['conteudo_pdf'])} chars via {data['metodo_extracao']}")
                    else:
                        logger.warning(f"⚠️ PDF vazio ou erro: {data['erro_extracao']}")
                    
                    # Pequena pausa após extração de PDF para não sobrecarregar
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Erro na extração de PDF: {e}")
                    data['erro_extracao'] = f"Erro inesperado: {str(e)}"
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do card: {e}")
        
        return data
    
    def scrape_page(self, url: str) -> List[Dict]:
        """
        Extrai dados de uma página de resultados
        
        Args:
            url: URL da página de resultados
            
        Returns:
            Lista de dicionários com dados das normas
        """
        try:
            logger.info(f"Extraindo dados da página: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Encontra todos os cards de normas
            cards = soup.find_all('div', class_='ficha-acervo-detalhe')
            
            logger.info(f"Encontrados {len(cards)} cards na página")
            
            results = []
            for card in cards:
                card_data = self.extract_card_data(card)
                if card_data['titulo']:  # Só adiciona se tiver título
                    results.append(card_data)
            
            time.sleep(self.delay)  # Aguarda entre requisições
            return results
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados da página: {e}")
            return []
    
    def get_next_page(self, page_number: int) -> Optional[str]:
        """
        Obtém a URL da próxima página
        
        Args:
            page_number: Número da página desejada
            
        Returns:
            URL da próxima página ou None if não houver
        """
        try:
            url = f"{self.base_url}/Terminal/Resultado/CarregarPaginaLayoutDetalhe"
            
            headers = {
                'accept': '*/*',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'x-requested-with': 'XMLHttpRequest'
            }
            
            params = {
                'paginaInicial': str(page_number),
                'guid': self.guid
            }
            
            response = self.session.post(url, params=params, headers=headers)
            response.raise_for_status()
            
            # Se a resposta está vazia ou tem erro, não há mais páginas
            if not response.text.strip() or 'erro' in response.text.lower():
                return None
                
            return response.text
            
        except Exception as e:
            logger.error(f"Erro ao obter página {page_number}: {e}")
            return None
    
    def scrape_all_pages(self, max_pages: int = None, ano: int = 2025) -> List[Dict]:
        """
        Extrai dados de todas as páginas disponíveis
        
        Args:
            max_pages: Número máximo de páginas (None para todas)
            ano: Ano para filtrar a busca (padrão: 2025)
            
        Returns:
            Lista com todos os dados extraídos
        """
        all_data = []
        
        try:
            # Primeira busca
            initial_url = self.submit_search_form(ano)
            
            # Extrai dados da primeira página
            page_data = self.scrape_page(initial_url)
            all_data.extend(page_data)
            
            logger.info(f"Primeira página: {len(page_data)} itens extraídos")
            
            # Processa páginas subsequentes
            page_number = 2
            while True:
                if max_pages and page_number > max_pages:
                    break
                
                logger.info(f"Processando página {page_number}...")
                
                page_html = self.get_next_page(page_number)
                if not page_html:
                    logger.info("Não há mais páginas disponíveis")
                    break
                
                # Parse do HTML da página
                soup = BeautifulSoup(page_html, 'html.parser')
                cards = soup.find_all('div', class_='ficha-acervo-detalhe')
                
                if not cards:
                    logger.info("Nenhum card encontrado na página, finalizando")
                    break
                
                page_results = []
                for card in cards:
                    card_data = self.extract_card_data(card)
                    if card_data['titulo']:
                        page_results.append(card_data)
                
                all_data.extend(page_results)
                logger.info(f"Página {page_number}: {len(page_results)} itens extraídos")
                
                page_number += 1
                time.sleep(self.delay)
            
            logger.info(f"Extração completa: {len(all_data)} itens totais")
            return all_data
            
        except Exception as e:
            logger.error(f"Erro durante extração completa: {e}")
            return all_data
    
    def load_existing_ids(self, filename: str) -> set:
        """
        Carrega IDs já existentes no arquivo para evitar duplicatas
        
        Args:
            filename: Nome do arquivo Parquet
            
        Returns:
            Set com IDs já existentes
        """
        try:
            full_path = os.path.join(os.getcwd(), filename)
            if os.path.exists(full_path):
                df_existing = pd.read_parquet(full_path)
                existing_ids = set(df_existing['codigo_registro'].astype(str))
                logger.info(f"Carregados {len(existing_ids)} IDs existentes do arquivo")
                return existing_ids
            else:
                logger.info("Arquivo não existe, iniciando nova extração")
                return set()
        except Exception as e:
            logger.error(f"Erro ao carregar IDs existentes: {e}")
            return set()
    
    def filter_duplicates(self, data: List[Dict], existing_ids: set) -> List[Dict]:
        """
        Remove duplicatas baseado no codigo_registro (ID)
        
        Args:
            data: Lista de dados extraídos
            existing_ids: Set de IDs já existentes
            
        Returns:
            Lista filtrada sem duplicatas
        """
        filtered_data = []
        new_ids = set()
        
        for item in data:
            item_id = str(item.get('codigo_registro', ''))
            
            # Pula se ID está vazio
            if not item_id:
                logger.warning(f"Item sem ID encontrado: {item.get('titulo', 'Sem título')}")
                continue
            
            # Pula se ID já existe no arquivo ou já foi processado nesta execução
            if item_id in existing_ids or item_id in new_ids:
                logger.debug(f"ID {item_id} já existe, ignorando duplicata")
                continue
            
            filtered_data.append(item)
            new_ids.add(item_id)
        
        logger.info(f"Filtrados {len(filtered_data)} novos registros de {len(data)} extraídos")
        return filtered_data
    
    def save_to_parquet(self, data: List[Dict], filename: str = "data/normas_antaq.parquet", 
                       merge_with_existing: bool = True):
        """
        Salva os dados extraídos em formato Parquet com controle de duplicatas
        
        Args:
            data: Lista de dicionários com os dados
            filename: Nome do arquivo de saída
            merge_with_existing: Se deve mesclar com dados existentes
        """
        try:
            if not data:
                logger.warning("Nenhum dado para salvar")
                return
            
            full_path = os.path.join(os.getcwd(), filename)
            
            # Se deve mesclar com dados existentes
            if merge_with_existing and os.path.exists(full_path):
                logger.info("Mesclando com dados existentes...")
                
                # Carrega dados existentes
                df_existing = pd.read_parquet(full_path)
                logger.info(f"Dados existentes: {len(df_existing)} registros")
                
                # Converte novos dados para DataFrame
                df_new = pd.DataFrame(data)
                
                # Garante que codigo_registro está como string em ambos
                df_existing['codigo_registro'] = df_existing['codigo_registro'].astype(str)
                df_new['codigo_registro'] = df_new['codigo_registro'].astype(str)
                
                # Remove duplicatas baseado no codigo_registro
                existing_ids = set(df_existing['codigo_registro'])
                df_new_filtered = df_new[~df_new['codigo_registro'].isin(existing_ids)]
                
                logger.info(f"Novos registros únicos: {len(df_new_filtered)}")
                
                if len(df_new_filtered) > 0:
                    # Combina dados
                    df_combined = pd.concat([df_existing, df_new_filtered], ignore_index=True)
                else:
                    df_combined = df_existing
                    logger.info("Nenhum registro novo para adicionar")
            else:
                # Não mescla, apenas salva novos dados
                df_combined = pd.DataFrame(data)
                
                # Remove duplicatas internas
                df_combined['codigo_registro'] = df_combined['codigo_registro'].astype(str)
                df_combined = df_combined.drop_duplicates(subset=['codigo_registro'], keep='first')
                logger.info(f"Removidas duplicatas internas, restando {len(df_combined)} registros únicos")
            
            # Converte datas para datetime quando possível
            for date_col in ['assinatura', 'publicacao']:
                if date_col in df_combined.columns:
                    df_combined[date_col] = pd.to_datetime(df_combined[date_col], format='%d/%m/%Y', errors='coerce')
            
            # Define codigo_registro como índice (chave primária)
            df_combined = df_combined.set_index('codigo_registro', drop=False)
            
            # Salva em formato Parquet
            df_combined.to_parquet(full_path, engine='pyarrow', index=True)
            
            logger.info(f"Dados salvos em: {full_path}")
            logger.info(f"Total de registros: {len(df_combined)}")
            logger.info(f"Colunas: {list(df_combined.columns)}")
            
            # Mostra estatísticas básicas
            print(f"\n=== ESTATÍSTICAS ===")
            print(f"Total de normas no arquivo: {len(df_combined)}")
            if len(df_combined) > 0:
                print(f"IDs: {df_combined['codigo_registro'].min()} - {df_combined['codigo_registro'].max()}")
                print(f"Tipos de normas:")
                print(df_combined['tipo_material'].value_counts())
                print(f"\nSituações:")
                print(df_combined['situacao'].value_counts())
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")
            raise

def main():
    """
    Função principal para executar o scraper com controle de duplicatas
    """
    print("=== WEBSCRAPER NORMAS ANTAQ (COM CONTROLE DE DUPLICATAS) ===\n")
    
    # Configurações
    scraper = SophiaANTAQScraper(delay=1.5)  # 1.5 segundos entre requisições
    arquivo_principal = "data/normas_antaq.parquet"
    
    try:
        # Verifica se já existe arquivo com dados
        if os.path.exists(arquivo_principal):
            print(f"📂 Arquivo existente encontrado: {arquivo_principal}")
            existing_ids = scraper.load_existing_ids(arquivo_principal)
            print(f"🔑 {len(existing_ids)} IDs já existentes no banco")
        else:
            print("📂 Iniciando nova base de dados")
            existing_ids = set()
        
        # Inicia o processo
        scraper.get_initial_guid()
        
        # Extrai todas as páginas
        print("🔄 Iniciando extração de dados...")
        all_data = scraper.scrape_all_pages(max_pages=None)
        
        if all_data:
            # Filtra duplicatas antes de salvar
            print(f"🔍 Filtrando duplicatas de {len(all_data)} registros extraídos...")
            new_data = scraper.filter_duplicates(all_data, existing_ids)
            
            if new_data:
                # Salva apenas dados novos, mesclando com existentes
                scraper.save_to_parquet(new_data, arquivo_principal, merge_with_existing=True)
                print(f"\n✅ Extração concluída com sucesso!")
                print(f"📊 {len(new_data)} normas NOVAS adicionadas ao banco")
                print(f"🗃️  Total no arquivo: {len(existing_ids) + len(new_data)} normas")
            else:
                print(f"\n📋 Nenhuma norma nova encontrada")
                print(f"🗃️  Base de dados já está atualizada com {len(existing_ids)} normas")
        else:
            print("❌ Nenhum dado foi extraído")
            
    except KeyboardInterrupt:
        print("\n⚠️ Extração interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        logger.error(f"Erro fatal: {e}")

if __name__ == "__main__":
    main()
