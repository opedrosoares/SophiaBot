#!/bin/bash
# Script de instalação do SophiaBot para CentOS 8.5.2111
# Execute como root ou com sudo

set -e  # Parar em caso de erro

echo "🚀 Instalando SophiaBot no CentOS 8.5.2111..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está rodando como root
if [[ $EUID -ne 0 ]]; then
   print_error "Este script deve ser executado como root ou com sudo"
   exit 1
fi

# Passo 1: Atualizar sistema
print_status "Atualizando sistema..."
dnf update -y

# Passo 2: Instalar ferramentas essenciais
print_status "Instalando ferramentas essenciais..."
dnf install -y git wget curl unzip

# Passo 3: Instalar dependências do sistema
print_status "Instalando dependências do sistema..."
dnf groupinstall -y "Development Tools"
dnf install -y python3-devel openssl-devel libffi-devel

# Passo 4: Instalar Python 3.9
print_status "Instalando Python 3.9..."
dnf install -y python39 python39-devel python39-pip

# Passo 5: Configurar Python 3.9 como padrão
print_status "Configurando Python 3.9 como padrão..."
alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
alternatives --set python3 /usr/bin/python3.9

# Verificar versão do Python
PYTHON_VERSION=$(python3 --version 2>&1)
print_status "Python instalado: $PYTHON_VERSION"

# Passo 6: Criar usuário sophiabot
print_status "Criando usuário sophiabot..."
if ! id "sophiabot" &>/dev/null; then
    useradd -m -s /bin/bash sophiabot
    echo "sophiabot:sophiabot123" | chpasswd
    print_warning "Usuário sophiabot criado com senha: sophiabot123"
    print_warning "IMPORTANTE: Altere a senha após a instalação!"
else
    print_status "Usuário sophiabot já existe"
fi

# Passo 7: Configurar ambiente Python
print_status "Configurando ambiente Python..."
su - sophiabot << 'EOF'
# Criar ambiente virtual
python3 -m venv ~/sophiabot_env
source ~/sophiabot_env/bin/activate

# Atualizar pip
pip install --upgrade pip setuptools wheel

# Clonar repositório
cd ~
if [ ! -d "SophiaBot" ]; then
    git clone https://github.com/opedrosoares/SophiaBot.git
fi

cd SophiaBot

# Instalar dependências com versões compatíveis
print_status "Instalando dependências..."

# Tentar usar requirements específicos para CentOS
if [ -f "requirements/centos_base.txt" ]; then
    pip install -r requirements/centos_base.txt
else
    # Fallback para versões compatíveis
    pip install "pandas>=1.5.0,<2.1.0"
    pip install "numpy>=1.24.0,<2.0.0"
    pip install "pyarrow>=14.0.0,<15.0.0"
    pip install "python-dotenv>=1.0.0"
    pip install "tqdm>=4.66.0"
    pip install "dateparser>=1.2.0"
    pip install "loguru>=0.7.2"
fi

if [ -f "requirements/centos_chatbot.txt" ]; then
    pip install -r requirements/centos_chatbot.txt
else
    # Fallback para versões compatíveis do chatbot
    pip install "openai>=1.12.0,<2.0.0"
    pip install "tiktoken>=0.5.0,<1.0.0"
    pip install "streamlit>=1.31.0,<2.0.0"
    pip install "streamlit-chat>=0.1.1,<1.0.0"
    pip install "chromadb>=0.4.22,<1.0.0"
    pip install "sentence-transformers>=2.2.2,<3.0.0"
    pip install "langchain>=0.1.0,<1.0.0"
    pip install "langchain-openai>=0.0.8,<1.0.0"
    pip install "langchain-community>=0.0.19,<1.0.0"
    pip install "plotly>=5.17.0,<6.0.0"
    pip install "altair>=5.2.0,<6.0.0"
    pip install "diskcache>=5.6.3,<6.0.0"
fi

# Configurar arquivo .env
if [ ! -f ".env" ]; then
    cp env_example .env
    print_status "Arquivo .env criado. Configure sua OPENAI_API_KEY!"
fi

EOF

# Passo 8: Configurar firewall
print_status "Configurando firewall..."
firewall-cmd --permanent --add-port=8501/tcp
firewall-cmd --reload

# Passo 9: Criar serviço systemd
print_status "Criando serviço systemd..."
cat > /etc/systemd/system/sophiabot.service << 'EOF'
[Unit]
Description=SophiaBot ANTAQ Chatbot
After=network.target

[Service]
Type=simple
User=sophiabot
Group=sophiabot
WorkingDirectory=/home/sophiabot/SophiaBot
Environment=PATH=/home/sophiabot/sophiabot_env/bin
ExecStart=/home/sophiabot/sophiabot_env/bin/streamlit run chatbot/interface/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Passo 10: Ativar serviço
print_status "Ativando serviço..."
systemctl daemon-reload
systemctl enable sophiabot

# Passo 11: Criar script de backup
print_status "Criando script de backup..."
cat > /home/sophiabot/backup_sophiabot.sh << 'EOF'
#!/bin/bash
# Backup do SophiaBot
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/sophiabot/backups"
SOURCE_DIR="/home/sophiabot/SophiaBot"

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/sophiabot_backup_$DATE.tar.gz -C $SOURCE_DIR .

# Manter apenas os últimos 7 backups
find $BACKUP_DIR -name "sophiabot_backup_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/sophiabot/backup_sophiabot.sh
chown sophiabot:sophiabot /home/sophiabot/backup_sophiabot.sh

# Passo 12: Configurar permissões
print_status "Configurando permissões..."
chown -R sophiabot:sophiabot /home/sophiabot/SophiaBot
chmod -R 755 /home/sophiabot/SophiaBot

# Passo 13: Instalar Nginx (opcional)
read -p "Deseja instalar Nginx como proxy reverso? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Instalando Nginx..."
    dnf install -y nginx
    
    cat > /etc/nginx/conf.d/sophiabot.conf << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
EOF

    systemctl enable nginx
    systemctl start nginx
    firewall-cmd --permanent --add-service=http
    firewall-cmd --reload
fi

# Passo 14: Iniciar serviço
print_status "Iniciando serviço SophiaBot..."
systemctl start sophiabot

# Verificar status
if systemctl is-active --quiet sophiabot; then
    print_status "✅ SophiaBot iniciado com sucesso!"
else
    print_error "❌ Erro ao iniciar SophiaBot"
    systemctl status sophiabot
fi

# Informações finais
echo
echo "🎉 Instalação concluída!"
echo
echo "📋 Próximos passos:"
echo "1. Configure sua OPENAI_API_KEY no arquivo /home/sophiabot/SophiaBot/.env"
echo "2. Acesse o chatbot em: http://$(hostname -I | awk '{print $1}'):8501"
echo "3. Altere a senha do usuário sophiabot: passwd sophiabot"
echo "4. Configure backup automático: crontab -e (adicione: 0 2 * * * /home/sophiabot/backup_sophiabot.sh)"
echo
echo "🔧 Comandos úteis:"
echo "- Verificar status: systemctl status sophiabot"
echo "- Ver logs: journalctl -u sophiabot -f"
echo "- Reiniciar: systemctl restart sophiabot"
echo "- Parar: systemctl stop sophiabot"
echo
echo "📞 Para suporte, consulte: docs/INSTALACAO_CENTOS.md" 