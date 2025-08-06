#!/usr/bin/env python3
"""
Configurações do Chatbot ANTAQ
Configuração com chave da OpenAI fornecida pelo usuário
"""

import os
from pathlib import Path
from dotenv import dotenv_values

# Carregar variáveis de ambiente do arquivo .env na raiz do projeto
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    env_vars = dotenv_values(env_path)
    for key, value in env_vars.items():
        os.environ[key] = value

# ===============================
# CONFIGURAÇÕES OBRIGATÓRIAS
# ===============================

# OpenAI API Key (carregada do arquivo .env)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# ===============================
# CONFIGURAÇÕES DO MODELO
# ===============================

# Modelo OpenAI a ser usado (GPT-4.1-nano é mais rápido e econômico)
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1-nano')

# Temperatura para geração (0.0 = determinístico, 1.0 = criativo)
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.1'))

# Máximo de tokens na resposta
OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '1500'))

# ===============================
# CONFIGURAÇÕES DO BANCO VETORIAL
# ===============================

# Diretório para persistir o banco ChromaDB
CHROMA_PERSIST_DIRECTORY = Path('./chroma_db')

# Nome da coleção no ChromaDB
COLLECTION_NAME = 'normas_antaq'

# Configurações de embedding
EMBEDDING_MODEL = 'text-embedding-3-small'

# Caminho para o arquivo de dados
DATA_PATH = Path(__file__).parent.parent.parent / 'shared' / 'data' / 'normas_antaq_completo.parquet'

# ===============================
# CONFIGURAÇÕES DE PROCESSAMENTO
# ===============================

# Tamanho dos chunks de texto (reduzido para evitar erro de contexto)
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '800'))

# Sobreposição entre chunks
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '150'))

# Número máximo de resultados na busca
MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', '15'))

# Número padrão de resultados
DEFAULT_SEARCH_RESULTS = int(os.getenv('DEFAULT_SEARCH_RESULTS', '8'))

# ===============================
# CONFIGURAÇÕES DA INTERFACE
# ===============================

# Porta do servidor Streamlit
STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', '8501'))

# Endereço do servidor
STREAMLIT_SERVER_ADDRESS = os.getenv('STREAMLIT_SERVER_ADDRESS', 'localhost')

# Título da aplicação
APP_TITLE = "Chatbot ANTAQ - Consultas sobre Normas"

# Ícone da aplicação
APP_ICON = "⚓"

# ===============================
# CONFIGURAÇÕES DE CACHE
# ===============================

# Habilitar cache
ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'

# Tempo de vida do cache (segundos)
CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))

# ===============================
# CONFIGURAÇÕES DE LOGGING
# ===============================

# Nível de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Arquivo de log
LOG_FILE = os.getenv('LOG_FILE', 'chatbot_logs.log')

# ===============================
# CONFIGURAÇÕES AVANÇADAS
# ===============================

# Habilitar re-ranking de resultados
ENABLE_RERANKING = os.getenv('ENABLE_RERANKING', 'true').lower() == 'true'

# ===============================
# FUNÇÃO DE VALIDAÇÃO
# ===============================

def validate_config():
    """
    Valida as configurações obrigatórias
    Retorna: (is_valid, list_of_errors)
    """
    errors = []
    
    # Validar API Key
    if not OPENAI_API_KEY or OPENAI_API_KEY == 'sua-chave-openai-aqui':
        errors.append("OPENAI_API_KEY não configurada")
    
    # Validar modelo
    if not OPENAI_MODEL:
        errors.append("OPENAI_MODEL não configurado")
    
    # Validar diretório do ChromaDB
    if not CHROMA_PERSIST_DIRECTORY:
        errors.append("CHROMA_PERSIST_DIRECTORY não configurado")
    
    # Validar porta do Streamlit
    if not isinstance(STREAMLIT_SERVER_PORT, int) or STREAMLIT_SERVER_PORT <= 0:
        errors.append("STREAMLIT_SERVER_PORT deve ser um número positivo")
    
    return len(errors) == 0, errors

# ===============================
# CONFIGURAÇÕES DE DESENVOLVIMENTO
# ===============================

# Habilitar modo debug
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Habilitar logs detalhados
VERBOSE_LOGGING = os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true'

# ===============================
# CONFIGURAÇÕES DE SEGURANÇA
# ===============================

# Habilitar validação de entrada
ENABLE_INPUT_VALIDATION = os.getenv('ENABLE_INPUT_VALIDATION', 'true').lower() == 'true'

# Máximo de caracteres por consulta
MAX_QUERY_LENGTH = int(os.getenv('MAX_QUERY_LENGTH', '1000'))

# ===============================
# CONFIGURAÇÕES DE PERFORMANCE
# ===============================

# Número máximo de threads para processamento
MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))

# Timeout para requisições (segundos)
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))

# ===============================
# CONFIGURAÇÕES DE MONITORAMENTO
# ===============================

# Habilitar métricas
ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'false').lower() == 'true'

# Intervalo de salvamento de métricas (segundos)
METRICS_SAVE_INTERVAL = int(os.getenv('METRICS_SAVE_INTERVAL', '300')) 