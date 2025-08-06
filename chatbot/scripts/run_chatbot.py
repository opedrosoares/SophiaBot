#!/usr/bin/env python3
"""
Script de conveniência para executar o Chatbot ANTAQ
"""

import sys
import os
from pathlib import Path

# Adicionar projeto ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    """Executa o chatbot Streamlit"""
    
    print("🚢 Iniciando Chatbot ANTAQ...")
    
    # Verificar se a configuração existe
    config_file = project_root / "chatbot" / "config" / "config.py"
    if not config_file.exists():
        print("❌ Arquivo de configuração não encontrado!")
        print("Execute: python setup.py chatbot")
        return 1
    
    try:
        # Importar e validar configuração
        sys.path.append(str(project_root / "chatbot" / "config"))
        import config
        
        if not hasattr(config, 'OPENAI_API_KEY') or not config.OPENAI_API_KEY or config.OPENAI_API_KEY == 'sua-chave-aqui':
            print("❌ OPENAI_API_KEY não configurada!")
            print("Configure a chave no arquivo .env na raiz do projeto")
            return 1
        
        print("✅ Configuração válida!")
        
        # Executar Streamlit
        import streamlit.web.cli as stcli
        
        app_path = project_root / "chatbot" / "interface" / "streamlit_app.py"
        
        sys.argv = [
            "streamlit", 
            "run", 
            str(app_path),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--theme.base", "light",
            "--theme.primaryColor", "#1f4e79"
        ]
        
        stcli.main()
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("Execute: pip install -r requirements/chatbot.txt")
        return 1
    
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())