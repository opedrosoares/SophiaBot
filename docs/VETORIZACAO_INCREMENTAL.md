# Vetorização Incremental - Sistema ANTAQ

## Visão Geral

O sistema de vetorização incremental permite processar apenas as normas que ainda não foram vetorizadas no banco ChromaDB, otimizando o tempo de processamento e evitando reprocessamento desnecessário.

## Funcionalidades Implementadas

### 1. Coluna de Controle de Vetorização

O arquivo `normas_antaq_completo.parquet` agora possui duas novas colunas:

- **`vetorizado`**: Boolean que indica se a norma foi vetorizada (True/False)
- **`ultima_verificacao_vetorizacao`**: Timestamp da última verificação de vetorização

### 2. Modo Incremental

O método `load_and_process_data()` agora suporta o parâmetro `incremental=True` (padrão), que:

- Filtra apenas normas não vetorizadas (`vetorizado=False`)
- Processa apenas essas normas
- Atualiza automaticamente o status para `vetorizado=True`
- Registra o timestamp da verificação

### 3. Estatísticas de Vetorização

Novo método `get_vetorizacao_stats()` que fornece:

- Total de normas
- Normas vetorizadas vs não vetorizadas
- Percentuais de vetorização
- Estatísticas específicas para normas em vigor com conteúdo
- Timestamp da última verificação

## Como Usar

### 1. Verificar Status Atual

```python
from chatbot.core.vector_store import VectorStoreANTAQ

# Inicializar vector store
vs = VectorStoreANTAQ(openai_api_key)

# Verificar estatísticas
stats = vs.get_vetorizacao_stats("normas_antaq_completo.parquet")
print(f"Normas vetorizadas: {stats['normas_vetorizadas']}/{stats['total_normas']}")
```

### 2. Vetorização Incremental

```python
# Processar apenas normas não vetorizadas
success = vs.load_and_process_data(
    "normas_antaq_completo.parquet",
    incremental=True,  # Padrão
    force_rebuild=False
)
```

### 3. Vetorização Completa (Forçar Rebuild)

```python
# Processar todas as normas (ignorar status)
success = vs.load_and_process_data(
    "normas_antaq_completo.parquet",
    incremental=False,
    force_rebuild=True
)
```

### 4. Teste com Amostra

```python
# Processar apenas 10 normas não vetorizadas para teste
success = vs.load_and_process_data(
    "normas_antaq_completo.parquet",
    incremental=True,
    sample_size=10
)
```

## Scripts de Teste

### 1. Verificar Estatísticas

```bash
python3 teste_estatisticas_sem_api.py
```

### 2. Simular Vetorização

```bash
python3 simular_vetorizacao.py
```

### 3. Teste Completo (requer API key)

```bash
python3 teste_vetorizacao_incremental.py
```

## Vantagens

1. **Eficiência**: Evita reprocessamento de normas já vetorizadas
2. **Controle**: Rastreamento preciso do status de cada norma
3. **Flexibilidade**: Suporte a processamento incremental e completo
4. **Monitoramento**: Estatísticas detalhadas do progresso
5. **Recuperação**: Pode retomar processamento interrompido

## Estrutura de Dados

### Colunas Adicionadas ao Parquet

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `vetorizado` | Boolean | True se a norma foi vetorizada |
| `ultima_verificacao_vetorizacao` | Timestamp | Data/hora da última verificação |

### Filtros Aplicados

O sistema filtra automaticamente:

- Normas com `situacao = 'Em vigor'`
- Normas com `conteudo_pdf` não nulo
- Normas com `conteudo_pdf` com mais de 100 caracteres
- Normas com `vetorizado = False` (modo incremental)

## Monitoramento

### Estatísticas Disponíveis

```python
stats = vs.get_vetorizacao_stats("normas_antaq_completo.parquet")

# Estatísticas gerais
total_normas = stats['total_normas']
normas_vetorizadas = stats['normas_vetorizadas']
percentual_vetorizado = stats['percentual_vetorizado']

# Estatísticas específicas
normas_em_vigor_com_conteudo = stats['normas_em_vigor_com_conteudo']
normas_em_vigor_vetorizadas = stats['normas_em_vigor_vetorizadas']
percentual_em_vigor_vetorizado = stats['percentual_em_vigor_vetorizado']

# Timestamp
ultima_verificacao = stats['ultima_verificacao']
```

## Tratamento de Erros

- Se a coluna `vetorizado` não existir, é criada automaticamente
- Backup automático antes de modificações
- Logs detalhados de todas as operações
- Tratamento de exceções com rollback

## Backup e Segurança

- Backup automático antes de adicionar colunas
- Verificação de integridade dos dados
- Logs de todas as operações
- Possibilidade de rollback em caso de erro

## Próximos Passos

1. Implementar interface web para monitoramento
2. Adicionar notificações de progresso
3. Implementar processamento em background
4. Adicionar métricas de performance
5. Criar dashboard de estatísticas 