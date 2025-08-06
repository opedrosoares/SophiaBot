#!/usr/bin/env python3
"""
Script para executar o Chatbot ANTAQ
"""

import sys
import os
from pathlib import Path

# Adicionar diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

try:
    # Importar configurações
    from config import config
    
    # Validar configurações
    is_valid, errors = config.validate_config()
    
    if not is_valid:
        print("❌ Erros de configuração:")
        for error in errors:
            print(f"   • {error}")
        print("\n📝 Edite o arquivo config.py para corrigir os erros")
        sys.exit(1)
    
    print("✅ Configurações válidas!")
    print("🚀 Iniciando Chatbot ANTAQ...")
    
    # Executar Streamlit
    import streamlit.web.cli as stcli
    
    # Configurar argumentos
    sys.argv = [
        "streamlit", 
        "run", 
        str(project_dir / "app.py"),
        "--server.port", str(config.STREAMLIT_SERVER_PORT),
        "--server.address", config.STREAMLIT_SERVER_ADDRESS,
        "--theme.base", "light",
        "--theme.primaryColor", "#1f4e79",
        "--theme.backgroundColor", "#ffffff",
        "--theme.secondaryBackgroundColor", "#f0f8ff"
    ]
    
    stcli.main()
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("   Execute python setup.py para instalar dependências")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
