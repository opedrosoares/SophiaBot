# Migração para Arquivo .env

## Resumo das Mudanças

A chave da API OpenAI foi movida de arquivos de configuração Python para um arquivo `.env` isolado na raiz do projeto, seguindo as melhores práticas de segurança.

## Arquivos Modificados

### 1. Arquivo `.env` (Novo)
- **Localização**: Raiz do projeto (`/Sophia/.env`)
- **Conteúdo**: Todas as variáveis de ambiente do projeto
- **Segurança**: Adicionado ao `.gitignore` para não ser commitado

### 2. Arquivo `.env.example` (Novo)
- **Localização**: Raiz do projeto (`/Sophia/.env.example`)
- **Propósito**: Modelo para configuração das variáveis de ambiente
- **Segurança**: Pode ser commitado no repositório

### 3. Arquivo `.gitignore` (Atualizado)
- **Adicionado**: Proteção para arquivos `.env`
- **Inclui**: `.env`, `.env.local`, `.env.*.local`

### 4. Arquivos de Configuração Python

#### `chatbot/config/config.py`
- **Mudança**: Carregamento de variáveis do arquivo `.env`
- **Método**: Uso de `dotenv_values()` para carregamento robusto
- **Adicionado**: Definição de `DATA_PATH`

#### `chatbot/config/settings.py`
- **Mudança**: Carregamento de variáveis do arquivo `.env`
- **Método**: Uso de `dotenv_values()` para carregamento robusto

#### `chatbot/config/settings_example.py`
- **Mudança**: Carregamento de variáveis do arquivo `.env`
- **Método**: Uso de `dotenv_values()` para carregamento robusto

### 5. Scripts Atualizados

#### `chatbot/scripts/vetorizar_base_completa.py`
- **Mudança**: Importação de `config` em vez de `settings`
- **Mensagem**: Atualizada para referenciar arquivo `.env`

#### `chatbot/core/rag_system.py`
- **Mudança**: Importação de `config` em vez de `settings`
- **Mensagem**: Atualizada para referenciar arquivo `.env`

#### `chatbot/core/vector_store.py`
- **Mudança**: Importação de `config` em vez de `settings`
- **Mensagem**: Atualizada para referenciar arquivo `.env`

#### `chatbot/interface/streamlit_app.py`
- **Mudança**: Importação de `config` em vez de `settings`

#### `chatbot/scripts/run_chatbot.py`
- **Mudança**: Verificação de `config.py` em vez de `settings.py`
- **Mensagem**: Atualizada para referenciar arquivo `.env`

## Como Configurar

### 1. Para Desenvolvedores Existentes

1. **Copiar o arquivo de exemplo**:
   ```bash
   cp .env.example .env
   ```

2. **Editar o arquivo `.env`**:
   ```bash
   nano .env
   # ou
   vim .env
   ```

3. **Configurar sua chave da API**:
   ```
   OPENAI_API_KEY=sua-chave-openai-aqui
   ```

### 2. Para Novos Desenvolvedores

1. **Clonar o repositório**
2. **Copiar o arquivo de exemplo**:
   ```bash
   cp .env.example .env
   ```
3. **Configurar as variáveis no arquivo `.env`**

## Vantagens da Mudança

### 1. Segurança
- Chaves sensíveis não são mais commitadas no repositório
- Cada desenvolvedor pode ter suas próprias configurações
- Redução do risco de exposição de credenciais

### 2. Flexibilidade
- Configurações diferentes para diferentes ambientes
- Fácil mudança de configurações sem alterar código
- Padrão da indústria para configurações

### 3. Manutenibilidade
- Centralização das configurações em um local
- Fácil backup e restauração de configurações
- Documentação clara com arquivo de exemplo

## Verificação da Configuração

Para verificar se a configuração está funcionando:

```bash
python3 -c "from chatbot.config.config import OPENAI_API_KEY; print('API Key carregada:', bool(OPENAI_API_KEY))"
```

**Saída esperada**: `API Key carregada: True`

## Troubleshooting

### Problema: "API Key carregada: False"

**Solução**:
1. Verificar se o arquivo `.env` existe na raiz do projeto
2. Verificar se a variável `OPENAI_API_KEY` está definida no arquivo
3. Verificar se não há espaços extras ou caracteres especiais

### Problema: "ModuleNotFoundError: No module named 'dotenv'"

**Solução**:
```bash
pip install python-dotenv
```

### Problema: Arquivo `.env` não encontrado

**Solução**:
1. Verificar se está executando o comando na raiz do projeto
2. Verificar se o arquivo `.env` existe
3. Copiar o arquivo de exemplo se necessário: `cp .env.example .env`

## Estrutura do Arquivo .env

```env
# Configurações da API OpenAI
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

# Configurações da interface
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost

# Configurações de cache
ENABLE_CACHE=true
CACHE_TTL=3600

# Configurações de logging
LOG_LEVEL=INFO
LOG_FILE=chatbot_logs.log

# Configurações avançadas
ENABLE_RERANKING=true

# Configurações de desenvolvimento
DEBUG=false
VERBOSE_LOGGING=false

# Configurações de segurança
ENABLE_INPUT_VALIDATION=true
MAX_QUERY_LENGTH=1000

# Configurações de performance
MAX_WORKERS=4
REQUEST_TIMEOUT=30

# Configurações de monitoramento
ENABLE_METRICS=false
METRICS_SAVE_INTERVAL=300
```

## Notas Importantes

1. **Nunca commite o arquivo `.env`** - ele contém informações sensíveis
2. **Sempre mantenha o `.env.example` atualizado** - para novos desenvolvedores
3. **Use valores padrão seguros** no arquivo de exemplo
4. **Documente mudanças** nas variáveis de ambiente 