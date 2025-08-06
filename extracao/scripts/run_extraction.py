#!/usr/bin/env python3
"""
Script de conveniência para executar extração de dados ANTAQ
"""

import sys
import os
from pathlib import Path

# Adicionar projeto ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    """Executa a extração de dados"""
    
    print("📥 Iniciando Extração de Dados ANTAQ...")
    
    # Verificar se arquivos principais existem
    extractor_file = project_root / "extracao" / "core" / "extrator.py"
    if not extractor_file.exists():
        print("❌ Módulo de extração não encontrado!")
        print("Execute: python setup.py extracao")
        return 1
    
    try:
        # Verificar dependências
        import requests
        import pandas as pd
        from bs4 import BeautifulSoup
        print("✅ Dependências verificadas!")
        
        # Executar extração
        print("🔄 Iniciando processo de extração...")
        
        # Importar e executar script de extração completa
        sys.path.append(str(project_root / "extracao" / "scripts"))
        
        # Verificar se existe executar_completo.py
        script_completo = project_root / "extracao" / "scripts" / "executar_completo.py"
        if script_completo.exists():
            print("📋 Executando extração completa...")
            exec(script_completo.read_text())
        else:
            print("⚠️ Script de extração completa não encontrado")
            print("Executando extração básica...")
            
            # Fallback: executar extração básica
            from extracao.core.extrator import ExtratorANTAQ
            extrator = ExtratorANTAQ()
            extrator.executar_extracao_completa()
        
        print("✅ Extração concluída!")
        print("📁 Dados salvos em: shared/data/")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("Execute: pip install -r requirements/extracao.txt")
        return 1
    
    except Exception as e:
        print(f"❌ Erro durante extração: {e}")
        print("📋 Verifique os logs em: shared/logs/")
        return 1

if __name__ == "__main__":
    sys.exit(main())