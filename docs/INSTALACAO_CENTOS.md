# 🚀 Instalação do SophiaBot em CentOS 8.5.2111

Guia completo para instalar e configurar o SophiaBot em servidores CentOS 8.5.2111 para produção.

## 🚀 Instalação Automatizada (Recomendado)

Para uma instalação rápida e automatizada, use o script oficial:

```bash
# Baixar e executar o script de instalação
curl -O https://raw.githubusercontent.com/opedrosoares/SophiaBot/main/scripts/install_centos.sh
chmod +x install_centos.sh
sudo ./install_centos.sh
```

**O script automatizado inclui:**
- ✅ Instalação automática do Python 3.9
- ✅ Configuração do ambiente virtual
- ✅ Instalação de dependências compatíveis
- ✅ Configuração do firewall
- ✅ Criação do serviço systemd
- ✅ Configuração opcional do Nginx
- ✅ Scripts de backup automático

## 📋 Instalação Manual (Passo a Passo)

## 📋 Pré-requisitos do Sistema

O CentOS 8.5.2111 tem algumas particularidades que precisamos considerar:

- **Python 3.8+** (CentOS 8 vem com Python 3.6 por padrão)
- **Git** para clonar o repositório
- **Dependências do sistema** para bibliotecas Python
- **Firewall** configurado para permitir acesso à porta 8501
- **Acesso root** ou sudo para configurações do sistema

## ⚠️ Problemas de Compatibilidade no CentOS

### Versões de Dependências
O CentOS 8.5.2111 pode ter problemas com versões muito recentes de algumas bibliotecas Python. Para resolver isso:

1. **Use os arquivos de requirements específicos** para CentOS
2. **Instale versões compatíveis** das dependências
3. **Atualize o pip** antes de instalar dependências
4. **Use ambiente virtual** para evitar conflitos

### Dependências Problemáticas
- **pandas**: Usar versão >=1.5.0,<2.1.0
- **numpy**: Usar versão >=1.24.0,<2.0.0
- **streamlit**: Usar versão >=1.31.0,<2.0.0

### 🚨 Erro Específico: pandas>=2.1.0

Se você encontrar o erro:
```
ERROR: Could not find a version that satisfies the requirement pandas>=2.1.0
```

**Solução imediata:**
```bash
# Usar versão compatível do pandas
pip install "pandas>=1.5.0,<2.1.0"

# Ou usar os arquivos de requirements específicos para CentOS
pip install -r requirements/centos_base.txt
pip install -r requirements/centos_chatbot.txt
```

## 🔧 Passo 1: Preparação do Sistema

```bash
# Atualizar o sistema
sudo dnf update -y

# Instalar ferramentas essenciais
sudo dnf install -y git wget curl unzip

# Instalar dependências do sistema para Python
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y python3-devel openssl-devel libffi-devel

# Instalar Python 3.9+ (CentOS 8 tem Python 3.6, precisamos de 3.8+)
sudo dnf install -y python39 python39-devel python39-pip

# Criar link simbólico para python3 apontar para python3.9
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
sudo alternatives --set python3 /usr/bin/python3.9

# Verificar versão
python3 --version
```

## 🐍 Passo 2: Configuração do Ambiente Python

```bash
# Criar usuário para o chatbot (recomendado)
sudo useradd -m -s /bin/bash sophiabot
sudo passwd sophiabot

# Mudar para o usuário
su - sophiabot

# Criar ambiente virtual
python3 -m venv sophiabot_env
source sophiabot_env/bin/activate

# Atualizar pip
pip install --upgrade pip setuptools wheel
```

## 📦 Passo 3: Instalação do SophiaBot

```bash
# Clonar o repositório
git clone https://github.com/opedrosoares/SophiaBot.git
cd SophiaBot

# ⚠️ IMPORTANTE: Para CentOS, usar requirements específicos
# Instalar dependências base (versões compatíveis)
pip install -r requirements/centos_base.txt

# Instalar dependências do chatbot (versões compatíveis)
pip install -r requirements/centos_chatbot.txt

# Alternativa: Se os arquivos específicos não existirem, usar versões compatíveis
# pip install "pandas>=1.5.0,<2.1.0"
# pip install "numpy>=1.24.0,<2.0.0"
# pip install -r requirements/base.txt --no-deps
# pip install -r requirements/chatbot.txt --no-deps
```

## ⚙️ Passo 4: Configuração do Ambiente

```bash
# Copiar arquivo de exemplo de ambiente
cp env_example .env

# Editar o arquivo .env com suas configurações
nano .env
```

### Conteúdo recomendado para o arquivo `.env`:

```bash
# Configurações da API OpenAI (OBRIGATÓRIO)
OPENAI_API_KEY=sua-chave-openai-aqui

# Configurações do modelo OpenAI
OPENAI_MODEL=gpt-4.1-nano
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=1500

# Configurações de processamento
CHUNK_SIZE=800
CHUNK_OVERLAP=150
MAX_SEARCH_RESULTS=15
DEFAULT_SEARCH_RESULTS=8

# Configurações da interface (IMPORTANTE para servidor)
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Configurações de cache
ENABLE_CACHE=true
CACHE_TTL=3600

# Configurações de logging
LOG_LEVEL=INFO
```

## 🔥 Passo 5: Configuração do Firewall

```bash
# Como root ou com sudo
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload

# Verificar se a porta está aberta
sudo firewall-cmd --list-ports
```

## 🚀 Passo 6: Configuração do Sistema de Serviço

Criar um serviço systemd para executar o chatbot automaticamente:

```bash
# Como root
sudo nano /etc/systemd/system/sophiabot.service
```

### Conteúdo do arquivo de serviço:

```ini
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
```

## 🔧 Passo 7: Ativação e Teste

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar o serviço
sudo systemctl enable sophiabot

# Iniciar o serviço
sudo systemctl start sophiabot

# Verificar status
sudo systemctl status sophiabot

# Ver logs
sudo journalctl -u sophiabot -f
```

## 🌐 Passo 8: Configuração de Proxy Reverso (Opcional)

Para melhor segurança e performance, configure um proxy reverso com Nginx:

```bash
# Instalar Nginx
sudo dnf install -y nginx

# Configurar Nginx
sudo nano /etc/nginx/conf.d/sophiabot.conf
```

### Conteúdo da configuração Nginx:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

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
```

```bash
# Testar configuração
sudo nginx -t

# Iniciar Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Configurar firewall para porta 80
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

## 🔒 Passo 9: Configuração de SSL (Recomendado)

```bash
# Instalar Certbot
sudo dnf install -y certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com

# Configurar renovação automática
sudo crontab -e
# Adicionar linha: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Passo 10: Monitoramento e Manutenção

```bash
# Verificar logs do sistema
sudo journalctl -u sophiabot -f

# Verificar uso de recursos
htop

# Backup automático (criar script)
nano /home/sophiabot/backup_sophiabot.sh
```

### Script de backup:

```bash
#!/bin/bash
# Backup do SophiaBot
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/sophiabot/backups"
SOURCE_DIR="/home/sophiabot/SophiaBot"

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/sophiabot_backup_$DATE.tar.gz -C $SOURCE_DIR .

# Manter apenas os últimos 7 backups
find $BACKUP_DIR -name "sophiabot_backup_*.tar.gz" -mtime +7 -delete
```

```bash
# Tornar o script executável
chmod +x /home/sophiabot/backup_sophiabot.sh

# Configurar backup automático (diário às 2h da manhã)
sudo crontab -e
# Adicionar linha: 0 2 * * * /home/sophiabot/backup_sophiabot.sh
```

## 🚨 Solução de Problemas Comuns

### Problema 1: Python não encontrado
```bash
# Verificar versão do Python
python3 --version

# Se necessário, instalar Python 3.9
sudo dnf install -y python39 python39-devel
```

### Problema 2: Dependências não instalam

#### Erro com pandas>=2.1.0
Se você encontrar erro com versões específicas do pandas, tente estas soluções:

```bash
# Solução 1: Atualizar pip e setuptools primeiro
pip install --upgrade pip setuptools wheel

# Solução 2: Instalar pandas com versão compatível
pip install "pandas>=2.0.0,<2.1.0"

# Solução 3: Se ainda houver problemas, usar versão mais antiga
pip install "pandas>=1.5.0"

# Solução 4: Instalar dependências uma por vez com versões específicas
pip install "pandas>=1.5.0"
pip install "numpy>=1.24.0"
pip install "pyarrow>=14.0.0"
pip install "streamlit>=1.31.0"
pip install "openai>=1.12.0"
pip install "chromadb>=0.4.22"
```

#### Erro geral com dependências
```bash
# Atualizar pip e setuptools
pip install --upgrade pip setuptools wheel

# Limpar cache do pip
pip cache purge

# Instalar com --no-cache-dir
pip install -r requirements/base.txt --no-cache-dir
pip install -r requirements/chatbot.txt --no-cache-dir
```

### Problema 3: Porta 8501 não acessível
```bash
# Verificar se o serviço está rodando
sudo systemctl status sophiabot

# Verificar firewall
sudo firewall-cmd --list-ports

# Testar localmente
curl http://localhost:8501
```

### Problema 4: Erro de permissões
```bash
# Corrigir permissões
sudo chown -R sophiabot:sophiabot /home/sophiabot/SophiaBot
sudo chmod -R 755 /home/sophiabot/SophiaBot
```

### Problema 5: Erro de memória insuficiente
```bash
# Verificar uso de memória
free -h

# Aumentar swap se necessário
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📊 Verificação da Instalação

Após a instalação, verifique se tudo está funcionando:

```bash
# Verificar se o serviço está ativo
sudo systemctl is-active sophiabot

# Verificar se a porta está aberta
netstat -tlnp | grep 8501

# Testar acesso web
curl -I http://localhost:8501

# Verificar logs
sudo journalctl -u sophiabot --no-pager -n 50
```

## 🔄 Comandos Úteis para Manutenção

```bash
# Reiniciar o chatbot
sudo systemctl restart sophiabot

# Parar o chatbot
sudo systemctl stop sophiabot

# Ver logs em tempo real
sudo journalctl -u sophiabot -f

# Verificar uso de recursos
ps aux | grep streamlit

# Verificar espaço em disco
df -h

# Verificar uso de memória
free -h
```

## 📈 Monitoramento de Performance

### Script de monitoramento básico:

```bash
#!/bin/bash
# Monitoramento do SophiaBot
echo "=== Status do SophiaBot ==="
echo "Data/Hora: $(date)"
echo "Serviço: $(systemctl is-active sophiabot)"
echo "Porta 8501: $(netstat -tlnp | grep 8501 | wc -l) processos"
echo "Uso de CPU: $(ps aux | grep streamlit | awk '{print $3}' | head -1)%"
echo "Uso de Memória: $(ps aux | grep streamlit | awk '{print $4}' | head -1)%"
echo "========================"
```

## 🔧 Configurações Avançadas

### Otimização de Performance

```bash
# Ajustar limites do sistema
sudo nano /etc/security/limits.conf

# Adicionar linhas:
sophiabot soft nofile 65536
sophiabot hard nofile 65536
```

### Configuração de Logs

```bash
# Configurar rotação de logs
sudo nano /etc/logrotate.d/sophiabot

# Conteúdo:
/home/sophiabot/SophiaBot/shared/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 sophiabot sophiabot
}
```

## 📞 Suporte

Se encontrar problemas durante a instalação:

1. **Verifique os logs**: `sudo journalctl -u sophiabot -f`
2. **Teste manualmente**: Execute o chatbot diretamente para ver erros
3. **Verifique dependências**: Confirme se todas as bibliotecas foram instaladas
4. **Consulte a documentação**: Veja os arquivos em `docs/` do projeto
5. **Contato**: pedro.soares@antaq.gov.br

## 🎯 Checklist de Instalação

- [ ] Sistema atualizado
- [ ] Python 3.9+ instalado
- [ ] Usuário sophiabot criado
- [ ] Ambiente virtual configurado
- [ ] SophiaBot clonado e dependências instaladas
- [ ] Arquivo .env configurado
- [ ] Firewall configurado
- [ ] Serviço systemd criado e ativo
- [ ] Nginx configurado (opcional)
- [ ] SSL configurado (opcional)
- [ ] Backup automático configurado
- [ ] Monitoramento configurado
- [ ] Teste de acesso realizado

## 🚀 Próximos Passos

Após a instalação bem-sucedida:

1. **Configure a API OpenAI** no arquivo `.env`
2. **Execute a vetorização inicial** dos dados
3. **Teste as funcionalidades** do chatbot
4. **Configure monitoramento** e alertas
5. **Documente a instalação** para sua equipe

---

**O SophiaBot agora deve estar funcionando em seu servidor CentOS 8.5.2111 e acessível via navegador web!**

Para acessar: `http://seu-servidor:8501` ou `http://seu-dominio.com` (se configurou Nginx) 