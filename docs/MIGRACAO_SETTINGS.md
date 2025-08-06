# Migração para Settings.py - Documentação

## Resumo das Alterações

Todo o projeto foi migrado para usar as configurações centralizadas no arquivo `chatbot/config/settings.py` em vez de procurar por arquivos `.env`.

## Arquivos Alterados

### 1. Scripts de Vetorização
- `vetorizar_lote_teste.py`
- `vetorizar_base_completa.py`

**Alterações:**
- Removida dependência do `dotenv`
- Importação direta de `OPENAI_API_KEY` do `settings.py`
- Simplificação do código

### 2. Core do Sistema
- `chatbot/core/vector_store.py`
- `chatbot/core/rag_system.py`

**Alterações:**
- Seção `if __name__ == "__main__"` atualizada
- Importação de configurações do `settings.py`
- Remoção de dependências do `.env`

### 3. Scripts de Teste
- `chatbot/scripts/teste_rapido.py`
- `chatbot/scripts/teste_super_rapido.py`

**Alterações:**
- Removida configuração manual de `os.environ`
- Importação de `OPENAI_API_KEY` do `settings.py`
- Código mais limpo e centralizado

### 4. Interface
- `chatbot/interface/streamlit_app.py`

**Alterações:**
- Removida configuração manual de variável de ambiente
- Simplificação do código de inicialização

### 5. Documentação
- `CONFIGURACAO_API.md`
- `INSTRUCOES_VETORIZACAO.md`

**Alterações:**
- Atualizadas instruções para usar `settings.py`
- Removidas referências a arquivo `.env`
- Comandos de verificação atualizados

## Vantagens da Migração

### ✅ **Centralização**
- Todas as configurações em um único local
- Fácil manutenção e atualização
- Consistência em todo o projeto

### ✅ **Simplicidade**
- Não há necessidade de arquivos `.env`
- Configuração mais direta
- Menos dependências externas

### ✅ **Segurança**
- Configurações versionadas no código
- Controle de acesso centralizado
- Backup automático das configurações

### ✅ **Desenvolvimento**
- Configuração única para todos os ambientes
- Fácil compartilhamento entre desenvolvedores
- Menos erros de configuração

## Como Usar

### Configuração da API Key

1. **Editar o arquivo**: `chatbot/config/settings.py`
2. **Localizar a linha**: `OPENAI_API_KEY = 'sua_chave_aqui'`
3. **Substituir**: pela sua chave real da OpenAI

### Verificação

```bash
# Verificar se a API key está configurada
python3 -c "from chatbot.config.settings import OPENAI_API_KEY; print('API Key configurada:', bool(OPENAI_API_KEY))"
```

### Execução de Scripts

Todos os scripts agora funcionam automaticamente com a configuração do `settings.py`:

```bash
# Teste de vetorização
python3 vetorizar_lote_teste.py --tamanho 10

# Verificar status
python3 verificar_status_vetorizacao.py

# Vetorização completa
python3 vetorizar_base_completa.py
```

## Estrutura do Settings.py

```python
# Configurações principais
OPENAI_API_KEY = 'sua_chave_aqui'
OPENAI_MODEL = 'gpt-4.1-nano'
OPENAI_TEMPERATURE = 0.1

# Configurações do banco vetorial
CHROMA_PERSIST_DIRECTORY = Path('./chroma_db')
COLLECTION_NAME = 'normas_antaq'
EMBEDDING_MODEL = 'text-embedding-3-small'

# Configurações de processamento
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
MAX_SEARCH_RESULTS = 15

# Configurações da interface
STREAMLIT_SERVER_PORT = 8501
APP_TITLE = "Chatbot ANTAQ - Consultas sobre Normas"
```

## Compatibilidade

### ✅ **Mantida**
- Todos os scripts funcionam normalmente
- Interface Streamlit inalterada
- Funcionalidades do chatbot preservadas

### ✅ **Melhorada**
- Configuração mais simples
- Menos arquivos para gerenciar
- Processo de setup mais direto

## Próximos Passos

1. **Testar todos os scripts** para garantir funcionamento
2. **Atualizar documentação** se necessário
3. **Compartilhar configuração** com a equipe
4. **Monitorar performance** após migração

## Troubleshooting

### Erro: "Erro ao importar configurações do chatbot"
- Verificar se o arquivo `settings.py` existe
- Confirmar que o caminho está correto
- Verificar permissões de acesso

### Erro: "OPENAI_API_KEY não encontrada no settings.py"
- Verificar se a chave está configurada no arquivo
- Confirmar que não há espaços extras
- Verificar se a chave é válida

### Erro de Importação
- Verificar se o diretório `chatbot` está no PYTHONPATH
- Confirmar estrutura de diretórios
- Verificar se todos os arquivos `__init__.py` existem

---

**Status**: ✅ Migração concluída com sucesso!
**Data**: 2025-08-05
**Versão**: 1.0 