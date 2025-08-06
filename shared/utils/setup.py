#!/usr/bin/env python3
"""
Setup unificado do Projeto Sophia - ANTAQ

Instala e configura tanto o módulo de extração quanto o chatbot.
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

class SophiaSetup:
    """Classe para configurar o projeto Sophia completo"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.requirements_dir = self.project_root / 'requirements'
        
    def print_banner(self):
        """Exibe banner do setup"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    🚢 SOPHIA ANTAQ SETUP                    ║
║                                                              ║
║       Sistema Integrado para Extração e Consulta de         ║
║            Normas de Transporte Aquaviário                  ║
║                                                              ║
║  📥 Módulo de Extração  +  🤖 Módulo Chatbot                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
    
    def check_python_version(self):
        """Verifica versão do Python"""
        print("🐍 Verificando versão do Python...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8+ é necessário!")
            print(f"   Versão atual: {version.major}.{version.minor}.{version.micro}")
            return False
        
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    
    def check_project_structure(self):
        """Verifica estrutura do projeto"""
        print("📁 Verificando estrutura do projeto...")
        
        required_dirs = [
            'extracao/core',
            'extracao/scripts', 
            'chatbot/core',
            'chatbot/interface',
            'shared/data',
            'requirements'
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            print(f"❌ Diretórios ausentes: {missing_dirs}")
            return False
        
        print("✅ Estrutura do projeto - OK")
        return True
    
    def install_dependencies(self, module=None):
        """Instala dependências"""
        print(f"📦 Instalando dependências{f' do módulo {module}' if module else ''}...")
        
        try:
            # Upgrade pip
            print("   🔄 Atualizando pip...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
            ], check=True, capture_output=True)
            
            # Determinar quais requirements instalar
            if module == 'extracao':
                req_files = ['base.txt', 'extracao.txt']
            elif module == 'chatbot':
                req_files = ['base.txt', 'chatbot.txt']
            else:
                req_files = ['base.txt', 'extracao.txt', 'chatbot.txt']
            
            # Instalar requirements
            for req_file in req_files:
                req_path = self.requirements_dir / req_file
                if req_path.exists():
                    print(f"   📚 Instalando {req_file}...")
                    subprocess.run([
                        sys.executable, '-m', 'pip', 'install', 
                        '-r', str(req_path), '--quiet'
                    ], check=True)
            
            print("✅ Dependências instaladas com sucesso!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências:")
            print(f"   {e}")
            return False
    
    def setup_extraction_module(self):
        """Configura módulo de extração"""
        print("📥 Configurando módulo de extração...")
        
        # Verificar se arquivo principal existe
        extractor_file = self.project_root / 'extracao' / 'core' / 'extrator.py'
        if not extractor_file.exists():
            print(f"⚠️ Arquivo principal de extração não encontrado: {extractor_file}")
            return False
        
        # Criar configuração de exemplo se não existir
        config_dir = self.project_root / 'extracao' / 'config'
        config_file = config_dir / 'settings.py'
        
        if not config_file.exists():
            print("   📝 Criando configuração de exemplo...")
            config_content = '''# Configurações do módulo de extração
BASE_URL = "https://sophia.antaq.gov.br"
SEARCH_ENDPOINT = "/Terminal/Busca"

# Delays para evitar sobrecarga
DELAY_MIN = 1
DELAY_MAX = 3
TIMEOUT = 30

# Processamento de PDFs
PDF_METHODS = ['pdfplumber', 'pypdf2', 'ocr']
OCR_ENABLED = True

# Backups
BACKUP_ENABLED = True
BACKUP_INTERVAL = 100
'''
            config_file.write_text(config_content)
        
        print("✅ Módulo de extração configurado!")
        return True
    
    def setup_chatbot_module(self):
        """Configura módulo do chatbot"""
        print("🤖 Configurando módulo do chatbot...")
        
        # Verificar arquivos principais
        core_files = [
            'chatbot/core/vector_store.py',
            'chatbot/core/rag_system.py',
            'chatbot/interface/streamlit_app.py'
        ]
        
        for file_path in core_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                print(f"⚠️ Arquivo principal não encontrado: {file_path}")
                return False
        
        # Verificar configuração
        config_dir = self.project_root / 'chatbot' / 'config'
        settings_file = config_dir / 'settings.py'
        example_file = config_dir / 'settings_example.py'
        
        if not settings_file.exists() and example_file.exists():
            print("   📝 Criando configuração inicial...")
            shutil.copy(example_file, settings_file)
            print("   ⚠️ IMPORTANTE: Configure sua OPENAI_API_KEY em chatbot/config/settings.py")
        
        print("✅ Módulo do chatbot configurado!")
        return True
    
    def create_convenience_scripts(self):
        """Cria scripts de conveniência"""
        print("🚀 Criando scripts de conveniência...")
        
        # Script para executar extração
        extract_script = self.project_root / 'run_extraction.py'
        extract_content = '''#!/usr/bin/env python3
"""Script de conveniência para executar extração"""
import sys
from pathlib import Path

# Adicionar projeto ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    from extracao.scripts.executar_completo import main
    main()
except ImportError as e:
    print(f"Erro: {e}")
    print("Execute: pip install -r requirements/extracao.txt")
    sys.exit(1)
'''
        extract_script.write_text(extract_content)
        extract_script.chmod(0o755)
        
        # Script para executar chatbot
        chatbot_script = self.project_root / 'run_chatbot.py'
        chatbot_content = '''#!/usr/bin/env python3
"""Script de conveniência para executar chatbot"""
import sys
import os
from pathlib import Path

# Adicionar projeto ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    import streamlit.web.cli as stcli
    
    # Configurar argumentos
    app_path = project_root / "chatbot" / "interface" / "streamlit_app.py"
    
    sys.argv = [
        "streamlit", 
        "run", 
        str(app_path),
        "--server.port", "8501",
        "--server.address", "localhost"
    ]
    
    stcli.main()
    
except ImportError as e:
    print(f"Erro: {e}")
    print("Execute: pip install -r requirements/chatbot.txt")
    sys.exit(1)
'''
        chatbot_script.write_text(chatbot_content)
        chatbot_script.chmod(0o755)
        
        print("✅ Scripts de conveniência criados!")
        return True
    
    def test_installation(self, module=None):
        """Testa a instalação"""
        print(f"🧪 Testando instalação{f' do módulo {module}' if module else ''}...")
        
        try:
            # Testar imports básicos
            import pandas
            import numpy
            print("✅ Bibliotecas base importadas com sucesso!")
            
            # Testar módulo específico
            if module == 'extracao' or module is None:
                try:
                    import requests
                    import beautifulsoup4
                    print("✅ Bibliotecas de extração importadas com sucesso!")
                except ImportError as e:
                    print(f"⚠️ Aviso: Algumas bibliotecas de extração ausentes: {e}")
            
            if module == 'chatbot' or module is None:
                try:
                    import openai
                    import streamlit
                    import chromadb
                    print("✅ Bibliotecas do chatbot importadas com sucesso!")
                except ImportError as e:
                    print(f"⚠️ Aviso: Algumas bibliotecas do chatbot ausentes: {e}")
            
            return True
            
        except ImportError as e:
            print(f"❌ Erro na importação: {e}")
            return False
    
    def print_final_instructions(self, module=None):
        """Exibe instruções finais"""
        
        if module == 'extracao':
            print("""
╔══════════════════════════════════════════════════════╗
║              ✅ MÓDULO DE EXTRAÇÃO PRONTO             ║
╚══════════════════════════════════════════════════════╝

📋 COMO USAR:

1. 🚀 Executar extração completa:
   python run_extraction.py

2. 📊 Monitorar progresso:
   tail -f shared/logs/extracao_main.log

3. 📁 Verificar dados extraídos:
   ls -la shared/data/

📚 DOCUMENTAÇÃO: docs/EXTRACAO.md
            """)
        
        elif module == 'chatbot':
            print("""
╔══════════════════════════════════════════════════════╗
║               ✅ MÓDULO CHATBOT PRONTO               ║
╚══════════════════════════════════════════════════════╝

📋 PRÓXIMOS PASSOS:

1. 🔑 Configure sua chave OpenAI:
   nano chatbot/config/settings.py
   # Adicione: OPENAI_API_KEY = 'sk-...'

2. 🚀 Execute o chatbot:
   python run_chatbot.py

3. 🌐 Acesse no navegador:
   http://localhost:8501

📚 DOCUMENTAÇÃO: docs/CHATBOT.md
            """)
        
        else:
            print("""
╔══════════════════════════════════════════════════════╗
║                ✅ SOPHIA SETUP COMPLETO             ║
╚══════════════════════════════════════════════════════╝

📋 PRÓXIMOS PASSOS:

🔧 CONFIGURAÇÃO:
1. Configure OpenAI API Key:
   nano chatbot/config/settings.py

🚀 EXECUÇÃO:
2. Para extrair dados:
   python run_extraction.py

3. Para usar chatbot:
   python run_chatbot.py

🌐 ACESSO:
4. Interface web: http://localhost:8501

📚 DOCUMENTAÇÃO:
   • docs/README.md - Visão geral
   • docs/EXTRACAO.md - Módulo de extração  
   • docs/CHATBOT.md - Módulo chatbot

🆘 SUPORTE:
   • Logs: shared/logs/
   • Issues: GitHub repository

════════════════════════════════════════════════════════
            """)
    
    def run_setup(self, module=None):
        """Executa setup completo ou de módulo específico"""
        self.print_banner()
        
        steps = [
            ("Verificação do Python", self.check_python_version),
            ("Verificação da estrutura", self.check_project_structure),
            ("Instalação de dependências", lambda: self.install_dependencies(module)),
        ]
        
        if module == 'extracao' or module is None:
            steps.append(("Configuração do módulo de extração", self.setup_extraction_module))
        
        if module == 'chatbot' or module is None:
            steps.append(("Configuração do módulo chatbot", self.setup_chatbot_module))
        
        if module is None:
            steps.append(("Criação de scripts de conveniência", self.create_convenience_scripts))
        
        steps.append(("Teste da instalação", lambda: self.test_installation(module)))
        
        print(f"🔧 Iniciando setup{f' do módulo {module}' if module else ' completo'}...\n")
        
        for step_name, step_func in steps:
            print(f"➡️  {step_name}")
            
            if not step_func():
                print(f"\n❌ Falha na etapa: {step_name}")
                print("   Corrija os erros e execute novamente")
                return False
            
            print()
        
        self.print_final_instructions(module)
        return True

def main():
    """Função principal"""
    setup = SophiaSetup()
    
    # Verificar argumentos
    module = None
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['extracao', 'extraction']:
            module = 'extracao'
        elif arg in ['chatbot', 'chat']:
            module = 'chatbot'
        elif arg in ['help', '-h', '--help']:
            print("Uso: python setup.py [extracao|chatbot]")
            print("  extracao - Instala apenas módulo de extração")
            print("  chatbot  - Instala apenas módulo do chatbot")
            print("  (sem arg) - Instala sistema completo")
            return 0
    
    try:
        success = setup.run_setup(module)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrompido pelo usuário")
        return 1
        
    except Exception as e:
        print(f"\n❌ Erro inesperado durante o setup: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())