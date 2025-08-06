# Configuração da API OpenAI

## Passo 1: Obter API Key

1. Acesse [OpenAI Platform](https://platform.openai.com/)
2. Faça login ou crie uma conta
3. Vá para "API Keys" no menu lateral
4. Clique em "Create new secret key"
5. Copie a chave gerada

## Passo 2: Configurar API Key (Já Configurada)

A API key já está configurada no arquivo `chatbot/config/settings.py`:

```python
OPENAI_API_KEY = 'sua_chave_aqui'
```

## Passo 3: Verificar Configuração

Execute o comando para verificar se a configuração está correta:

```bash
python3 -c "from chatbot.config.settings import OPENAI_API_KEY; print('API Key configurada:', bool(OPENAI_API_KEY))"
```

## Passo 4: Executar Vetorização

Após configurar a API key, execute:

```bash
python3 vetorizar_base_completa.py
```

## ⚠️ Importante

- **Custo**: A vetorização de 15.695 normas pode gerar custos significativos
- **Tempo**: O processo pode levar várias horas
- **Conexão**: Certifique-se de ter conexão estável com a internet
- **Backup**: O sistema faz backup automático, mas é recomendável ter backup manual

## Estimativa de Custos

- **Embeddings**: ~$0.00002 por 1K tokens
- **15.695 normas**: Estimativa de $50-200 dependendo do tamanho dos documentos
- **Tempo estimado**: 4-8 horas

## Monitoramento

O script mostrará:
- Progresso em tempo real
- Estatísticas detalhadas
- Tempo de processamento
- Custos estimados 