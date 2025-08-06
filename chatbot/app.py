#!/usr/bin/env python3
"""
Aplicação principal do Chatbot ANTAQ
Interface Streamlit para consultas sobre normas
"""

import sys
from pathlib import Path

# Adicionar diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

# Importar e executar a aplicação Streamlit
from interface.streamlit_app import main

if __name__ == "__main__":
    main() 