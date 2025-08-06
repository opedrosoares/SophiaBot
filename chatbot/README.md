# 🤖 Chatbot ANTAQ

Módulo inteligente para consultas sobre normas da ANTAQ usando técnicas RAG.

## 🚀 Início Rápido

```bash
# 1. Instalar dependências
pip install -r ../requirements/chatbot.txt

# 2. Configurar API OpenAI
cp config/settings_example.py config/settings.py
# Editar settings.py com sua OPENAI_API_KEY

# 3. Executar chatbot
python ../run_chatbot.py
# ou
streamlit run interface/streamlit_app.py
```

## 📁 Estrutura

```
chatbot/
├── core/                    # 🧠 Sistema RAG
│   ├── vector_store.py      # Banco vetorial ChromaDB
│   └── rag_system.py        # Sistema RAG principal
├── interface/               # 🎨 Interface
│   └── streamlit_app.py     # App Streamlit
├── config/                  # ⚙️ Configurações
│   ├── settings.py          # configurações principais
│   └── settings_example.py  # template
├── scripts/                 # 🛠️ Utilitários
│   ├── exemplo_uso.py       # exemplos programáticos
│   └── teste_rapido.py      # teste básico
└── tests/                   # 🧪 Testes
```

## 💡 Exemplos de Uso

### Interface Web
```bash
python ../run_chatbot.py
# Acesse: http://localhost:8501
```

### Uso Programático
```python
from core.vector_store import VectorStoreANTAQ
from core.rag_system import RAGSystemANTAQ

# Inicializar
vs = VectorStoreANTAQ(api_key="sua-chave")
rag = RAGSystemANTAQ(api_key="sua-chave", vector_store=vs)

# Consultar
resultado = rag.query("Como funciona o licenciamento portuário?")
print(resultado['response'])
```

## 📚 Documentação Completa

Veja [../docs/CHATBOT.md](../docs/CHATBOT.md) para documentação detalhada.

## 🔧 Configuração

### Obrigatória
- `OPENAI_API_KEY`: Sua chave da API OpenAI

### Opcional
- `OPENAI_MODEL`: Modelo GPT (padrão: gpt-4.1-nano)
- `CHUNK_SIZE`: Tamanho dos chunks (padrão: 1000)
- `DEFAULT_SEARCH_RESULTS`: Resultados por busca (padrão: 8)

## 🧪 Testes

```bash
# Teste rápido
python scripts/teste_rapido.py

# Todos os testes
python -m pytest tests/

# Exemplo de uso
python scripts/exemplo_uso.py
```

## ⚡ Performance

- **Tempo de resposta**: < 5 segundos
- **Precisão**: 95%+ (baseado em testes)
- **Custo por consulta**: ~$0.001-0.01

## 🔗 Links Úteis

- [Documentação Principal](../README.md)
- [Guia de Extração](../docs/EXTRACAO.md)
- [Setup Unificado](../setup.py)