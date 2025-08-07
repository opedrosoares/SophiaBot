# Chatbot ANTAQ - Deploy Streamlit Cloud

Este projeto foi configurado para deploy no Streamlit Cloud com múltiplas coleções ChromaDB.

## 🚀 Deploy no Streamlit Cloud

### 1. Preparação
- ✅ Múltiplas coleções ChromaDB criadas (cada uma < 100MB)
- ✅ Configurações otimizadas para Streamlit Cloud
- ✅ Requirements.txt configurado

### 2. Configuração no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Conecte seu repositório GitHub
3. Configure as seguintes variáveis de ambiente:
   - `OPENAI_API_KEY`: Sua chave da API OpenAI

### 3. Estrutura do Projeto
```
SophiaBot/
├── chatbot/           # Código principal
│   ├── core/         # Sistema RAG e Vector Store
│   ├── config/       # Configurações
│   └── scripts/      # Scripts utilitários
├── chroma_db/        # Base de dados vetorial (múltiplas coleções)
├── streamlit_app.py  # App principal do Streamlit
├── requirements.txt  # Dependências
└── .streamlit/       # Configurações do Streamlit
```

### 4. Coleções ChromaDB
O sistema utiliza múltiplas coleções para manter cada arquivo abaixo de 100MB:
- `normas_antaq_part_000`: Primeira parte
- `normas_antaq_part_001`: Segunda parte
- `normas_antaq_part_002`: Terceira parte
- etc.

### 5. Funcionalidades
- 🔍 Busca semântica em todas as coleções
- 💬 Chat interativo com histórico
- 📊 Estatísticas das coleções
- 🎯 Respostas baseadas em normas da ANTAQ

### 6. Troubleshooting

#### Erro de memória
- Verifique se todas as coleções estão abaixo de 100MB
- Execute o script de verificação: `python chatbot/scripts/verificar_tamanho_colecoes.py`

#### Erro de inicialização
- Verifique se a `OPENAI_API_KEY` está configurada
- Confirme se o arquivo `requirements.txt` está atualizado

#### Performance lenta
- Reduza o número de documentos para contexto
- Ajuste a temperatura para valores mais baixos

### 7. Manutenção

Para atualizar a base de dados:
1. Execute o script de migração: `python chatbot/scripts/migrar_para_multiplas_colecoes.py`
2. Verifique os tamanhos: `python chatbot/scripts/verificar_tamanho_colecoes.py`
3. Faça commit das novas coleções
4. Redeploy no Streamlit Cloud

## 📞 Suporte

Para problemas ou dúvidas, consulte a documentação ou abra uma issue no repositório.
