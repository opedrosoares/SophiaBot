#!/usr/bin/env python3
"""
Módulo de Extração - Sophia ANTAQ

Sistema robusto para extração e processamento de normas da ANTAQ.

Módulos principais:
- core.extrator: Motor principal de extração
- core.controlador: Controle de processos
- core.monitor: Monitoramento de progresso
- scripts: Scripts executáveis para diferentes tipos de extração

Exemplo de uso:
    from extracao.core.extrator import ExtratorANTAQ
    
    extrator = ExtratorANTAQ()
    normas = extrator.extrair_normas()
"""

__version__ = "1.0.0"
__author__ = "Equipe ANTAQ"
__email__ = "suporte@antaq.gov.br"

# Imports principais
try:
    from .core.extrator import ExtratorANTAQ
    from .core.controlador import ControladorExtracao
    
    __all__ = [
        'ExtratorANTAQ',
        'ControladorExtracao'
    ]
    
except ImportError as e:
    # Durante setup, algumas dependências podem não estar disponíveis
    __all__ = []
