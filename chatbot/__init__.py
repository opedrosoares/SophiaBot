#!/usr/bin/env python3
"""
Chatbot ANTAQ - Sistema Inteligente para Consultas sobre Normas

Este pacote contém um sistema completo de RAG (Retrieval-Augmented Generation)
para consultas sobre normas da Agência Nacional de Transportes Aquaviários.

Módulos principais:
- vector_store: Gerenciamento do banco vetorial ChromaDB
- rag_system: Sistema RAG principal
- app: Interface Streamlit
- config: Configurações do sistema

Exemplo de uso:
    from chatbot import VectorStoreANTAQ, RAGSystemANTAQ
    
    # Inicializar sistema
    vector_store = VectorStoreANTAQ(api_key)
    rag_system = RAGSystemANTAQ(api_key, vector_store)
    
    # Fazer consulta
    resposta = rag_system.query("Como funciona o licenciamento portuário?")
"""

__version__ = "1.0.0"
__author__ = "Equipe ANTAQ"
__email__ = "suporte@antaq.gov.br"

# Imports principais
try:
    from .core.vector_store import VectorStoreANTAQ
    from .core.rag_system import RAGSystemANTAQ, ChatMessage
    
    __all__ = [
        'VectorStoreANTAQ',
        'RAGSystemANTAQ', 
        'ChatMessage'
    ]
    
except ImportError as e:
    # Durante setup, algumas dependências podem não estar disponíveis
    __all__ = []