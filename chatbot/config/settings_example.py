#!/usr/bin/env python3
"""
Configurações do Chatbot ANTAQ
Copie este arquivo para config.py e ajuste as configurações conforme necessário
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

# OpenAI API Key (obrigatória)
# Obtenha em: https://platform.openai.com/api-keys
# Configure no arquivo .env na raiz do projeto
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'sua-chave-openai-aqui')

# ===============================
# CONFIGURAÇÕES DO MODELO
# ===============================

# Modelo OpenAI a ser usado
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')

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

# ===============================
# CONFIGURAÇÕES DE PROCESSAMENTO
# ===============================

# Tamanho dos chunks de texto
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))

# Sobreposição entre chunks
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))

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

# Limite de contexto para o LLM
MAX_CONTEXT_LENGTH = int(os.getenv('MAX_CONTEXT_LENGTH', '8000'))

# Timeout para chamadas da API (segundos)
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '60'))

# ===============================
# CAMINHOS DE ARQUIVOS
# ===============================

# Caminho base do projeto
BASE_DIR = Path(__file__).parent.parent

# Caminho para o arquivo de dados
DATA_PATH = BASE_DIR.parent / 'shared' / 'data' / 'normas_antaq_completo.parquet'

# Diretório para exports
EXPORT_DIR = BASE_DIR / 'exports'

# Diretório para logs
LOG_DIR = BASE_DIR / 'logs'

# ===============================
# VALIDAÇÃO DE CONFIGURAÇÕES
# ===============================

def validate_config():
    """
    Valida as configurações obrigatórias
    
    Returns:
        tuple: (is_valid, error_messages)
    """
    
    errors = []
    
    # Verificar chave da API
    if not OPENAI_API_KEY or OPENAI_API_KEY == 'sua-chave-openai-aqui':
        errors.append("OPENAI_API_KEY não configurada")
    
    # Verificar arquivo de dados
    if not DATA_PATH.exists():
        errors.append(f"Arquivo de dados não encontrado: {DATA_PATH}")
    
    # Verificar modelo válido
    valid_models = ['gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o']
    if OPENAI_MODEL not in valid_models:
        errors.append(f"Modelo inválido: {OPENAI_MODEL}. Use um dos: {valid_models}")
    
    # Verificar valores numéricos
    if CHUNK_SIZE <= 0:
        errors.append("CHUNK_SIZE deve ser maior que 0")
    
    if CHUNK_OVERLAP < 0:
        errors.append("CHUNK_OVERLAP deve ser >= 0")
    
    if CHUNK_OVERLAP >= CHUNK_SIZE:
        errors.append("CHUNK_OVERLAP deve ser menor que CHUNK_SIZE")
    
    return len(errors) == 0, errors

# ===============================
# CONFIGURAÇÕES DE DESENVOLVIMENTO
# ===============================

# Modo debug
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Recarregar dados sempre (desenvolvimento)
FORCE_RELOAD_DATA = os.getenv('FORCE_RELOAD_DATA', 'false').lower() == 'true'

# Mostrar informações detalhadas
VERBOSE = os.getenv('VERBOSE', 'false').lower() == 'true'

if __name__ == "__main__":
    # Teste de configuração
    print("🔧 Validando configurações...")
    
    is_valid, errors = validate_config()
    
    if is_valid:
        print("✅ Todas as configurações são válidas!")
        print(f"   • Modelo: {OPENAI_MODEL}")
        print(f"   • Chunk size: {CHUNK_SIZE}")
        print(f"   • Resultados padrão: {DEFAULT_SEARCH_RESULTS}")
        print(f"   • Dados: {DATA_PATH}")
    else:
        print("❌ Erros de configuração encontrados:")
        for error in errors:
            print(f"   • {error}")
        exit(1)