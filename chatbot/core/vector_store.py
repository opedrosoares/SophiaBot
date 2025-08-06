#!/usr/bin/env python3
"""
Sistema de Banco Vetorial para o Chatbot ANTAQ
Gerencia embeddings e busca semântica das normas
"""

import pandas as pd
import numpy as np
import chromadb
from chromadb.config import Settings
import openai
from typing import List, Dict, Any, Optional, Tuple
import json
import hashlib
import os
from pathlib import Path
import logging
from tqdm import tqdm
import tiktoken
import re
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStoreANTAQ:
    """
    Classe para gerenciar o banco vetorial das normas ANTAQ
    """
    
    def __init__(
        self, 
        openai_api_key: str,
        persist_directory: str = "./chroma_db",
        collection_name: str = "normas_antaq",
        chunk_size: int = 600,  # Reduzido para evitar erro de contexto
        chunk_overlap: int = 100  # Reduzido proporcionalmente
    ):
        """
        Inicializa o sistema de banco vetorial
        
        Args:
            openai_api_key: Chave da API OpenAI
            persist_directory: Diretório para persistir o banco
            collection_name: Nome da coleção no ChromaDB
            chunk_size: Tamanho dos chunks de texto
            chunk_overlap: Sobreposição entre chunks
        """
        
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Tokenizer para contagem de tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        logger.info(f"VectorStore inicializado em: {self.persist_directory}")
    
    def _count_tokens(self, text: str) -> int:
        """Conta tokens no texto"""
        return len(self.tokenizer.encode(text))
    
    def _chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Divide texto em chunks inteligentes
        
        Args:
            text: Texto para dividir
            metadata: Metadados do documento
            
        Returns:
            Lista de chunks com metadados
        """
        
        if not text or len(text.strip()) < 50:
            return []
        
        chunks = []
        
        # Limpar e normalizar texto
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Dividir por parágrafos primeiro
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_chunk = ""
        current_tokens = 0
        
        for paragraph in paragraphs:
            paragraph_tokens = self._count_tokens(paragraph)
            
            # Se parágrafo é muito grande, dividir por sentenças
            if paragraph_tokens > self.chunk_size:
                sentences = re.split(r'[.!?]+', paragraph)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                        
                    sentence_tokens = self._count_tokens(sentence)
                    
                    if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                        # Salvar chunk atual
                        chunks.append({
                            'text': current_chunk.strip(),
                            'metadata': {
                                **metadata,
                                'chunk_index': len(chunks),
                                'tokens': current_tokens
                            }
                        })
                        
                        # Iniciar novo chunk com overlap
                        overlap_text = self._get_overlap(current_chunk)
                        current_chunk = overlap_text + " " + sentence
                        current_tokens = self._count_tokens(current_chunk)
                    else:
                        current_chunk += " " + sentence
                        current_tokens += sentence_tokens
            else:
                # Parágrafo normal
                if current_tokens + paragraph_tokens > self.chunk_size and current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'metadata': {
                            **metadata,
                            'chunk_index': len(chunks),
                            'tokens': current_tokens
                        }
                    })
                    
                    overlap_text = self._get_overlap(current_chunk)
                    current_chunk = overlap_text + " " + paragraph
                    current_tokens = self._count_tokens(current_chunk)
                else:
                    current_chunk += " " + paragraph
                    current_tokens += paragraph_tokens
        
        # Adicionar último chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': {
                    **metadata,
                    'chunk_index': len(chunks),
                    'tokens': current_tokens
                }
            })
        
        return chunks
    
    def _get_overlap(self, text: str) -> str:
        """Obter texto de overlap do final do chunk"""
        words = text.split()
        overlap_words = min(self.chunk_overlap // 4, len(words))  # Aproximação
        return " ".join(words[-overlap_words:]) if overlap_words > 0 else ""
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding usando OpenAI
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Lista de floats representando o embedding
        """
        
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=text.replace("\n", " ")
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            raise
    
    def _generate_document_id(self, codigo_registro: str, chunk_index: int) -> str:
        """Gera ID único para documento"""
        return f"{codigo_registro}_chunk_{chunk_index}"
    
    def _atualizar_status_vetorizacao(self, parquet_path: str, codigos_registro: List[str]) -> None:
        """
        Atualiza o status de vetorização das normas no arquivo parquet
        
        Args:
            parquet_path: Caminho para o arquivo parquet
            codigos_registro: Lista de códigos de registro das normas processadas
        """
        try:
            logger.info(f"Atualizando status de vetorização para {len(codigos_registro)} normas...")
            
            # Carregar dados
            df = pd.read_parquet(parquet_path)
            
            # Marcar normas como vetorizadas
            mask = df['codigo_registro'].isin(codigos_registro)
            df.loc[mask, 'vetorizado'] = True
            df.loc[mask, 'ultima_verificacao_vetorizacao'] = datetime.now()
            
            # Salvar arquivo atualizado
            df.to_parquet(parquet_path, index=False)
            
            logger.info(f"✅ Status de vetorização atualizado com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar status de vetorização: {e}")
            import traceback
            traceback.print_exc()
    
    def load_and_process_data(self, parquet_path: str, force_rebuild: bool = False, sample_size: Optional[int] = None, incremental: bool = True) -> bool:
        """
        Carrega e processa dados do parquet para o banco vetorial
        
        Args:
            parquet_path: Caminho para o arquivo parquet
            force_rebuild: Se deve reconstruir o banco mesmo se existir
            sample_size: Tamanho da amostra para teste
            incremental: Se deve processar apenas normas não vetorizadas
            
        Returns:
            True se processado com sucesso
        """
        
        try:
            # Verificar se coleção já existe
            collection_exists = False
            try:
                collection = self.client.get_collection(self.collection_name)
                collection_exists = True
                if not force_rebuild:
                    count = collection.count()
                    logger.info(f"Coleção já existe com {count} documentos")
            except:
                pass
            
            if force_rebuild and collection_exists:
                logger.info("Reconstruindo banco vetorial...")
                self.client.delete_collection(self.collection_name)
                collection_exists = False
            
            # Criar nova coleção se não existir
            if not collection_exists:
                collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            else:
                collection = self.client.get_collection(self.collection_name)
            
            # Carregar dados
            logger.info(f"Carregando dados de: {parquet_path}")
            df = pd.read_parquet(parquet_path)
            
            # Verificar se coluna vetorizado existe
            if 'vetorizado' not in df.columns:
                logger.warning("Coluna 'vetorizado' não encontrada. Adicionando coluna...")
                df['vetorizado'] = False
                df['ultima_verificacao_vetorizacao'] = None
                # Salvar arquivo atualizado
                df.to_parquet(parquet_path, index=False)
                logger.info("Arquivo atualizado com coluna 'vetorizado'")
            
            # Filtrar apenas normas em vigor com conteúdo
            df_filtered = df[
                (df['situacao'] == 'Em vigor') & 
                (df['conteudo_pdf'].notna()) & 
                (df['conteudo_pdf'].str.len() > 100)
            ].copy()
            
            # Se modo incremental, filtrar apenas não vetorizadas
            if incremental and not force_rebuild:
                df_filtered = df_filtered[~df_filtered['vetorizado']].copy()
                logger.info(f"Modo incremental: {len(df_filtered)} normas não vetorizadas encontradas")
            else:
                logger.info(f"Processando todas as {len(df_filtered)} normas em vigor com conteúdo...")
            
            # Aplicar amostra se especificado
            if sample_size and sample_size < len(df_filtered):
                df_filtered = df_filtered.sample(n=sample_size, random_state=42).copy()
                logger.info(f"Usando amostra de {sample_size} normas para teste rápido...")
            
            if len(df_filtered) == 0:
                logger.info("Nenhuma norma para processar!")
                return True
            
            logger.info(f"Processando {len(df_filtered)} normas...")
            
            # Processar cada norma individualmente
            total_chunks = 0
            normas_processadas = []
            
            # Processar cada norma individualmente para garantir persistência
            for _, row in tqdm(df_filtered.iterrows(), total=len(df_filtered), desc="Processando normas"):
                try:
                    # Preparar metadados
                    metadata = {
                        'codigo_registro': str(row['codigo_registro']),
                        'titulo': str(row['titulo']),
                        'autor': str(row['autor']),
                        'assunto': str(row['assunto']),
                        'situacao': str(row['situacao']),
                        'link_pdf': str(row['link_pdf']),
                        'tipo_material': str(row['tipo_material']),
                        'assinatura': row['assinatura'].strftime('%Y-%m-%d') if pd.notna(row['assinatura']) else 'N/A',
                        'publicacao': row['publicacao'].strftime('%Y-%m-%d') if pd.notna(row['publicacao']) else 'N/A',
                        'tamanho_pdf': int(row['tamanho_pdf']) if pd.notna(row['tamanho_pdf']) else 0,
                        'paginas_extraidas': int(row['paginas_extraidas']) if pd.notna(row['paginas_extraidas']) else 0
                    }
                    
                    # Criar texto combinado para busca
                    texto_completo = f"""
                    TÍTULO: {row['titulo']}
                    ASSUNTO: {row['assunto']}
                    CONTEÚDO: {row['conteudo_pdf']}
                    """.strip()
                    
                    # Dividir em chunks
                    chunks = self._chunk_text(texto_completo, metadata)
                    
                    # Preparar dados para inserção
                    documents = []
                    embeddings = []
                    ids = []
                    metadatas = []
                    
                    for chunk in chunks:
                        # Gerar embedding
                        embedding = self._generate_embedding(chunk['text'])
                        
                        # Preparar dados para inserção
                        doc_id = self._generate_document_id(
                            metadata['codigo_registro'], 
                            chunk['metadata']['chunk_index']
                        )
                        
                        documents.append(chunk['text'])
                        embeddings.append(embedding)
                        ids.append(doc_id)
                        metadatas.append(chunk['metadata'])
                        total_chunks += 1
                    
                    # Inserir norma individual no banco vetorial
                    if documents:
                        collection.add(
                            documents=documents,
                            embeddings=embeddings,
                            ids=ids,
                            metadatas=metadatas
                        )
                    
                    # Adicionar à lista de normas processadas
                    normas_processadas.append(row['codigo_registro'])
                    
                    # Atualizar status de vetorização individualmente
                    if incremental:
                        self._atualizar_status_vetorizacao(parquet_path, [row['codigo_registro']])
                    
                    # Log da norma sendo processada
                    logger.info(f"📄 Processado e salvo: {row['titulo']} (Código: {row['codigo_registro']}) - {len(documents)} chunks")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar norma {row['codigo_registro']}: {e}")
                    continue
            
            # Remover a atualização em lote no final, pois já foi feita individualmente
            
            logger.info(f"✅ Processamento concluído! {total_chunks} chunks inseridos no banco vetorial")
            logger.info(f"✅ {len(normas_processadas)} normas marcadas como vetorizadas")
            
            # Listar nomes das normas vetorizadas
            if normas_processadas:
                logger.info("📋 NORMAS VETORIZADAS NESTE LOTE:")
                for codigo in normas_processadas:
                    # Buscar o título da norma no DataFrame
                    norma_info = df_filtered[df_filtered['codigo_registro'] == codigo]
                    if not norma_info.empty:
                        titulo = norma_info.iloc[0]['titulo']
                        logger.info(f"   • {titulo} (Código: {codigo})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar dados: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def search(
        self, 
        query: str, 
        n_results: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca semântica no banco vetorial
        
        Args:
            query: Consulta do usuário
            n_results: Número de resultados
            filters: Filtros de metadados
            
        Returns:
            Lista de resultados ranqueados
        """
        
        try:
            collection = self.client.get_collection(self.collection_name)
            
            # Gerar embedding da consulta
            query_embedding = self._generate_embedding(query)
            
            # Preparar filtros
            where = {}
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        where[key] = value
            
            # Realizar busca
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where if where else None,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Formatar resultados
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity': 1 - results['distances'][0][i],  # Converter distância para similaridade
                    'distance': results['distances'][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas da coleção"""
        try:
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()
            
            # Obter todos os metadados para análise completa
            all_data = collection.get(limit=count, include=['metadatas'])
            
            # Análise dos metadados
            autores = {}
            assuntos = {}
            anos = {}
            tipos_normas = {}
            situacoes = {}
            normas_unicas = set()
            
            for meta in all_data['metadatas']:
                # Contagem de normas únicas
                codigo_registro = meta.get('codigo_registro', '')
                if codigo_registro:
                    normas_unicas.add(codigo_registro)
                
                # Análise de autores
                autor = meta.get('autor', 'Desconhecido')
                autores[autor] = autores.get(autor, 0) + 1
                
                # Análise de assuntos
                assunto = meta.get('assunto', 'Desconhecido')
                assuntos[assunto] = assuntos.get(assunto, 0) + 1
                
                # Análise de anos
                if meta.get('assinatura'):
                    ano = meta['assinatura'][:4]
                    anos[ano] = anos.get(ano, 0) + 1
                
                # Análise de tipos de normas
                titulo = meta.get('titulo', '')
                if titulo:
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
                    
                    tipos_normas[tipo] = tipos_normas.get(tipo, 0) + 1
                
                # Análise de situações
                situacao = meta.get('situacao', 'Desconhecida')
                situacoes[situacao] = situacoes.get(situacao, 0) + 1
            
            return {
                'total_chunks': count,
                'total_normas_unicas': len(normas_unicas),
                'top_autores': dict(list(sorted(autores.items(), key=lambda x: x[1], reverse=True))[:10]),
                'top_assuntos': dict(list(sorted(assuntos.items(), key=lambda x: x[1], reverse=True))[:10]),
                'distribuicao_anos': dict(sorted(anos.items())),
                'tipos_normas': dict(sorted(tipos_normas.items(), key=lambda x: x[1], reverse=True)),
                'situacoes': dict(sorted(situacoes.items(), key=lambda x: x[1], reverse=True))
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {'error': str(e)}
    
    def get_vetorizacao_stats(self, parquet_path: str) -> Dict[str, Any]:
        """
        Obtém estatísticas de vetorização do arquivo parquet
        
        Args:
            parquet_path: Caminho para o arquivo parquet
            
        Returns:
            Dicionário com estatísticas de vetorização
        """
        try:
            df = pd.read_parquet(parquet_path)
            
            # Verificar se coluna vetorizado existe
            if 'vetorizado' not in df.columns:
                return {
                    'error': 'Coluna vetorizado não encontrada',
                    'total_normas': len(df)
                }
            
            # Estatísticas básicas
            total_normas = len(df)
            normas_vetorizadas = df['vetorizado'].sum()
            normas_nao_vetorizadas = total_normas - normas_vetorizadas
            
            # Normas em vigor com conteúdo
            normas_em_vigor = df[
                (df['situacao'] == 'Em vigor') & 
                (df['conteudo_pdf'].notna()) & 
                (df['conteudo_pdf'].str.len() > 100)
            ]
            
            normas_em_vigor_vetorizadas = normas_em_vigor['vetorizado'].sum()
            normas_em_vigor_nao_vetorizadas = len(normas_em_vigor) - normas_em_vigor_vetorizadas
            
            # Última verificação
            ultima_verificacao = df['ultima_verificacao_vetorizacao'].max() if 'ultima_verificacao_vetorizacao' in df.columns else None
            
            return {
                'total_normas': total_normas,
                'normas_vetorizadas': int(normas_vetorizadas),
                'normas_nao_vetorizadas': int(normas_nao_vetorizadas),
                'percentual_vetorizado': float(normas_vetorizadas / total_normas * 100) if total_normas > 0 else 0,
                'normas_em_vigor_com_conteudo': len(normas_em_vigor),
                'normas_em_vigor_vetorizadas': int(normas_em_vigor_vetorizadas),
                'normas_em_vigor_nao_vetorizadas': int(normas_em_vigor_nao_vetorizadas),
                'percentual_em_vigor_vetorizado': float(normas_em_vigor_vetorizadas / len(normas_em_vigor) * 100) if len(normas_em_vigor) > 0 else 0,
                'ultima_verificacao': ultima_verificacao.isoformat() if ultima_verificacao else None
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de vetorização: {e}")
            return {'error': str(e)}

if __name__ == "__main__":
    # Teste básico
    try:
        from chatbot.config.config import OPENAI_API_KEY
    except ImportError:
        print("❌ Erro ao importar configurações do chatbot")
        exit(1)
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY não encontrada no arquivo .env")
        exit(1)
    
    # Inicializar vector store
    vs = VectorStoreANTAQ(OPENAI_API_KEY)
    
    # Verificar estatísticas de vetorização
    parquet_path = "../normas_antaq_completo.parquet"
    vetorizacao_stats = vs.get_vetorizacao_stats(parquet_path)
    
    print("\n📊 ESTATÍSTICAS DE VETORIZAÇÃO:")
    if 'error' not in vetorizacao_stats:
        print(f"   Total de normas: {vetorizacao_stats['total_normas']}")
        print(f"   Normas vetorizadas: {vetorizacao_stats['normas_vetorizadas']}")
        print(f"   Normas não vetorizadas: {vetorizacao_stats['normas_nao_vetorizadas']}")
        print(f"   Percentual vetorizado: {vetorizacao_stats['percentual_vetorizado']:.1f}%")
        print(f"   Normas em vigor com conteúdo: {vetorizacao_stats['normas_em_vigor_com_conteudo']}")
        print(f"   Normas em vigor vetorizadas: {vetorizacao_stats['normas_em_vigor_vetorizadas']}")
        print(f"   Percentual em vigor vetorizado: {vetorizacao_stats['percentual_em_vigor_vetorizado']:.1f}%")
        if vetorizacao_stats['ultima_verificacao']:
            print(f"   Última verificação: {vetorizacao_stats['ultima_verificacao']}")
    else:
        print(f"   Erro: {vetorizacao_stats['error']}")
    
    # Carregar dados (modo incremental)
    print(f"\n🚀 Iniciando vetorização incremental...")
    success = vs.load_and_process_data(parquet_path, incremental=True, sample_size=5)
    
    if success:
        # Teste de busca
        results = vs.search("licenciamento portuário", n_results=5)
        
        print("\n🔍 TESTE DE BUSCA:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Similaridade: {result['similarity']:.3f}")
            print(f"   Título: {result['metadata'].get('titulo', 'N/A')}")
            print(f"   Texto: {result['document'][:200]}...")
        
        # Estatísticas da coleção
        stats = vs.get_collection_stats()
        print(f"\n📊 ESTATÍSTICAS DA COLEÇÃO:")
        print(f"   Total chunks: {stats.get('total_chunks', 0)}")
        
        # Verificar estatísticas atualizadas
        vetorizacao_stats_atualizada = vs.get_vetorizacao_stats(parquet_path)
        print(f"\n📊 ESTATÍSTICAS ATUALIZADAS:")
        print(f"   Normas vetorizadas: {vetorizacao_stats_atualizada['normas_vetorizadas']}")
        print(f"   Percentual vetorizado: {vetorizacao_stats_atualizada['percentual_vetorizado']:.1f}%")