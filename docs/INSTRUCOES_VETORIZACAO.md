# Instruções para Vetorização da Base ANTAQ

## Status Atual

✅ **Base preparada**: 18.381 normas no total
✅ **Sistema incremental**: Implementado e funcionando
✅ **Colunas de controle**: Adicionadas (`vetorizado`, `ultima_verificacao_vetorizacao`)
✅ **Teste inicial**: 10 normas vetorizadas com sucesso

📊 **Estatísticas atuais**:
- Total de normas: 18.381
- Normas em vigor com conteúdo: 15.705
- Normas vetorizadas: 10 (0.1%)
- Normas pendentes: 15.695

## Passos para Vetorizar Toda a Base

### 1. API Key OpenAI (Já Configurada)

A API key já está configurada no arquivo `chatbot/config/settings.py`:

```python
OPENAI_API_KEY = 'sua_chave_aqui'
```

**Para alterar a API Key**:
1. Acesse [OpenAI Platform](https://platform.openai.com/)
2. Vá em "API Keys" → "Create new secret key"
3. Copie a chave e atualize no arquivo `chatbot/config/settings.py`

### 2. Verificar Status Atual

```bash
python3 verificar_status_vetorizacao.py
```

### 3. Teste com Lote Pequeno (Recomendado)

```bash
# Testar com 50 normas primeiro
python3 vetorizar_lote_teste.py --tamanho 50
```

### 4. Vetorizar Base Completa

```bash
python3 vetorizar_base_completa.py
```

## Estimativas

### Tempo
- **Lote de 50 normas**: ~10-15 minutos
- **Base completa (15.695 normas)**: 4-8 horas

### Custo
- **Embeddings**: ~$0.00002 por 1K tokens
- **Base completa**: Estimativa $50-200

## Scripts Disponíveis

| Script | Descrição | Uso |
|--------|-----------|-----|
| `verificar_status_vetorizacao.py` | Verifica status atual | `python3 verificar_status_vetorizacao.py` |
| `vetorizar_lote_teste.py` | Vetoriza lote pequeno | `python3 vetorizar_lote_teste.py --tamanho 50` |
| `vetorizar_base_completa.py` | Vetoriza toda a base | `python3 vetorizar_base_completa.py` |

## Monitoramento

### Durante a Execução
- Progresso em tempo real
- Estatísticas detalhadas
- Logs de operações
- Estimativas de tempo restante

### Após a Execução
- Relatório completo de estatísticas
- Informações de tempo e performance
- Status de cada norma

## Recursos de Segurança

✅ **Backup automático**: Antes de modificações
✅ **Processamento incremental**: Evita reprocessamento
✅ **Tratamento de erros**: Rollback em caso de falha
✅ **Logs detalhados**: Rastreamento completo
✅ **Verificação de integridade**: Validação dos dados

## Estrutura de Dados

### Arquivo Parquet Atualizado
- **Colunas originais**: 15
- **Novas colunas**: 2
- **Total**: 17 colunas

### Novas Colunas
- `vetorizado`: Boolean (True/False)
- `ultima_verificacao_vetorizacao`: Timestamp

## Banco Vetorial (ChromaDB)

### Localização
- **Diretório**: `./chatbot/chroma_db/`
- **Coleção**: `normas_antaq`
- **Espaço**: Cosine similarity

### Estrutura
- **Chunks**: Texto dividido em pedaços
- **Embeddings**: Vetores OpenAI text-embedding-3-small
- **Metadados**: Informações completas de cada norma

## Próximos Passos

1. **Configurar API Key** (obrigatório)
2. **Executar teste pequeno** (recomendado)
3. **Vetorizar base completa** (quando estiver pronto)
4. **Verificar resultados** com script de status
5. **Usar no chatbot** para busca semântica

## Suporte

- **Documentação**: `docs/VETORIZACAO_INCREMENTAL.md`
- **Configuração**: `CONFIGURACAO_API.md`
- **Logs**: Verificar saída dos scripts
- **Backup**: `backup_antes_vetorizado_*.parquet`

---

**⚠️ Importante**: Certifique-se de ter tempo suficiente e conexão estável antes de iniciar a vetorização completa! 