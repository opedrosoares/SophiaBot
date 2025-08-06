#!/usr/bin/env python3
"""
Script de configuração e instalação do Chatbot ANTAQ
Instala dependências e configura o ambiente
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

class ChatbotSetup:
    """Classe para configurar o chatbot"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.chatbot_dir = Path(__file__).parent
        self.requirements_file = self.project_root / 'requirements_chatbot.txt'
        
    def print_banner(self):
        """Exibe banner do setup"""
        print("""
╔══════════════════════════════════════════════════════╗
║                                                      ║
║               🚢 CHATBOT ANTAQ SETUP                ║
║                                                      ║
║     Sistema Inteligente para Consultas sobre        ║
║           Normas de Transporte Aquaviário           ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
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
    
    def check_data_file(self):
        """Verifica se o arquivo de dados existe"""
        print("📁 Verificando arquivo de dados...")
        
        data_file = self.project_root / 'data' / 'normas_antaq_completo.parquet'
        
        if not data_file.exists():
            print(f"❌ Arquivo de dados não encontrado: {data_file}")
            print("   Execute primeiro o script de extração de dados")
            return False
        
        # Verificar tamanho do arquivo
        size_mb = data_file.stat().st_size / (1024 * 1024)
        print(f"✅ Arquivo de dados encontrado ({size_mb:.1f} MB)")
        return True
    
    def install_dependencies(self):
        """Instala dependências"""
        print("📦 Instalando dependências...")
        
        if not self.requirements_file.exists():
            print(f"❌ Arquivo requirements não encontrado: {self.requirements_file}")
            return False
        
        try:
            # Upgrade pip
            print("   🔄 Atualizando pip...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
            ], check=True, capture_output=True)
            
            # Instalar dependências
            print("   📚 Instalando bibliotecas...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(self.requirements_file)
            ], check=True, capture_output=True, text=True)
            
            print("✅ Dependências instaladas com sucesso!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências:")
            print(f"   {e.stdout}")
            print(f"   {e.stderr}")
            return False
    
    def create_directories(self):
        """Cria diretórios necessários"""
        print("📂 Criando diretórios...")
        
        directories = [
            self.chatbot_dir / 'chroma_db',
            self.project_root / 'logs',
            self.project_root / 'exports'
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"   ✅ {directory}")
        
        return True
    
    def setup_config(self):
        """Configura arquivo de configuração"""
        print("⚙️ Configurando arquivo de configuração...")
        
        config_example = self.chatbot_dir / 'config_example.py'
        config_file = self.chatbot_dir / 'config.py'
        
        if not config_file.exists():
            shutil.copy(config_example, config_file)
            print(f"✅ Arquivo de configuração criado: {config_file}")
            print("   📝 Edite config.py para adicionar sua chave da OpenAI")
        else:
            print("   ⚠️ Arquivo config.py já existe")
        
        return True
    
    def create_run_script(self):
        """Cria script para executar o chatbot"""
        print("🚀 Criando script de execução...")
        
        run_script = self.chatbot_dir / 'run_chatbot.py'
        
        script_content = '''#!/usr/bin/env python3
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
    import config
    
    # Validar configurações
    is_valid, errors = config.validate_config()
    
    if not is_valid:
        print("❌ Erros de configuração:")
        for error in errors:
            print(f"   • {error}")
        print("\\n📝 Edite o arquivo config.py para corrigir os erros")
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
'''
        
        with open(run_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Tornar executável
        run_script.chmod(0o755)
        
        print(f"✅ Script criado: {run_script}")
        return True
    
    def test_installation(self):
        """Testa a instalação"""
        print("🧪 Testando instalação...")
        
        try:
            # Testar imports principais
            import openai
            import streamlit
            import chromadb
            import pandas
            
            print("✅ Todas as bibliotecas foram importadas com sucesso!")
            
            # Testar módulos do chatbot (opcional)
            try:
                sys.path.append(str(self.chatbot_dir))
                import vector_store
                import rag_system
                print("✅ Módulos do chatbot importados com sucesso!")
            except ImportError as e:
                print(f"⚠️ Aviso: Alguns módulos não puderam ser importados: {e}")
                print("   Isso é normal durante o setup inicial")
            return True
            
        except ImportError as e:
            print(f"❌ Erro na importação: {e}")
            return False
    
    def print_instructions(self):
        """Exibe instruções finais"""
        print("""
╔══════════════════════════════════════════════════════╗
║                   ✅ SETUP CONCLUÍDO                ║
╚══════════════════════════════════════════════════════╝

📋 PRÓXIMOS PASSOS:

1. 🔑 Configure sua chave da OpenAI:
   • Edite o arquivo: chatbot/config.py
   • Adicione sua OPENAI_API_KEY

2. 🚀 Execute o chatbot:
   • Via script: python chatbot/run_chatbot.py
   • Ou diretamente: streamlit run chatbot/app.py

3. 🌐 Acesse no navegador:
   • http://localhost:8501

📚 DOCUMENTAÇÃO:
   • README.md - Instruções detalhadas
   • config_example.py - Todas as configurações
   • chatbot/app.py - Interface principal

🆘 SUPORTE:
   • Verifique os logs em: logs/
   • Issues: https://antaq.gov.br

════════════════════════════════════════════════════════
""")
    
    def run_setup(self):
        """Executa setup completo"""
        self.print_banner()
        
        steps = [
            ("Verificação do Python", self.check_python_version),
            ("Verificação dos dados", self.check_data_file),
            ("Instalação de dependências", self.install_dependencies),
            ("Criação de diretórios", self.create_directories),
            ("Configuração inicial", self.setup_config),
            ("Script de execução", self.create_run_script),
            ("Teste da instalação", self.test_installation)
        ]
        
        print("🔧 Iniciando configuração...\n")
        
        for step_name, step_func in steps:
            print(f"➡️  {step_name}")
            
            if not step_func():
                print(f"\n❌ Falha na etapa: {step_name}")
                print("   Corrija os erros e execute novamente")
                return False
            
            print()
        
        self.print_instructions()
        return True

def main():
    """Função principal"""
    setup = ChatbotSetup()
    
    try:
        success = setup.run_setup()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrompido pelo usuário")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Erro inesperado durante o setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()