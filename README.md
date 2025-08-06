# Chatbot de Normas - SophiaBot

Sistema completo para extração de dados e consultas inteligentes sobre normas da ANTAQ (Agência Nacional de Transportes Aquaviários).

## 📋 Visão Geral

O projeto Sophia é dividido em dois módulos principais:

- **🔄 Extração**: Sistema robusto para scraping e processamento de normas do site da ANTAQ
- **🤖 Chatbot**: Interface inteligente para consultas usando técnicas RAG (Retrieval-Augmented Generation)

## 📁 Estrutura do Projeto

```
SophiaBot/
├── extracao/                         # 📥 Módulo de extração de dados
│   ├── core/                         # Funcionalidades principais
│   │   ├── extrator.py              # Motor de extração principal
│   │   ├── controlador.py           # Controlador de processos
│   │   ├── monitorar_progresso.py   # Monitoramento de progresso
│   │   └── monitorar_extracao_historica.py # Monitoramento histórico
│   ├── scripts/                     # Scripts executáveis
│   │   ├── executar_completo.py     # Extração completa
│   │   ├── executar_completo_historico.py # Extração histórica
│   │   ├── continuar_extracao.py    # Continuação de processos
│   │   ├── retomar_extracao.py      # Retomar extração interrompida
│   │   ├── reprocessar_pdfs.py      # Reprocessar PDFs
│   │   ├── extrair_pdfs_incrementalmente.py # Extração incremental
│   │   ├── extrair_registros_urls_vazias.py # Extrair URLs vazias
│   │   ├── relatorio_pdfs_vazios.py # Relatório de PDFs vazios
│   │   └── run_extraction.py        # Script principal de execução
│   ├── config/                      # Configurações
│   ├── tests/                       # Testes do módulo
│   └── README.md                    # Documentação específica
├── chatbot/                         # 🤖 Módulo do chatbot
│   ├── core/                        # Sistema RAG
│   │   ├── vector_store.py          # Banco vetorial ChromaDB
│   │   └── rag_system.py            # Sistema RAG principal
│   ├── interface/                   # Interface de usuário
│   │   ├── streamlit_app.py         # App Streamlit principal
│   │   ├── exemplo.py               # Exemplo de uso
│   │   ├── styles.css               # Estilos CSS
│   │   └── README_CSS.md            # Documentação CSS
│   ├── config/                      # Configurações
│   │   ├── config.py                # Configuração principal
│   │   ├── settings.py              # Configurações do usuário
│   │   └── settings_example.py      # Exemplo de configuração
│   ├── scripts/                     # Scripts utilitários
│   │   ├── setup.py                 # Script de configuração
│   │   ├── run_chatbot.py           # Execução do chatbot
│   │   ├── vetorizar_base_completa.py # Vetorização de dados
│   │   ├── explorar_dados_chatbot.py # Exploração de dados
│   │   └── verificar_status_vetorizacao.py # Verificar status
│   ├── chroma_db/                   # Banco vetorial ChromaDB
│   ├── tests/                       # Testes do chatbot
│   ├── app.py                       # Aplicação principal
│   ├── run_chatbot.py               # Script de execução
│   └── README.md                    # Documentação específica
├── shared/                          # 📚 Recursos compartilhados
│   ├── data/                        # Dados processados
│   ├── logs/                        # Logs do sistema
│   ├── exports/                     # Arquivos exportados
│   ├── backups/                     # Backups automáticos
│   └── utils/                       # Utilitários compartilhados
├── requirements/                    # 📋 Dependências organizadas
│   ├── base.txt                     # Dependências comuns
│   ├── extracao.txt                 # Específicas da extração
│   └── chatbot.txt                  # Específicas do chatbot
├── docs/                            # 📖 Documentação
│   ├── EXTRACAO.md                  # Guia do módulo de extração
│   ├── CHATBOT.md                   # Guia do módulo chatbot
│   ├── COMO_USAR.md                 # Guia de uso
│   ├── CONFIGURACAO_API.md          # Configuração da API
│   ├── INSTRUCOES_VETORIZACAO.md    # Instruções de vetorização
│   ├── VETORIZACAO_INCREMENTAL.md   # Vetorização incremental
│   ├── MIGRACAO_ENV.md              # Migração de ambiente
│   ├── MIGRACAO_SETTINGS.md         # Migração de configurações
│   ├── RESUMO_IMPLEMENTACAO.md      # Resumo da implementação
│   ├── RESUMO_ORGANIZACAO.md        # Resumo da organização
│   └── RESUMO_REORGANIZACAO.md      # Resumo da reorganização
├── env_example                      # Exemplo de variáveis de ambiente
├── env_file                         # Arquivo de ambiente
└── README.md                        # Este arquivo
```

## 🚀 Início Rápido

### 1. Instalação Base

```bash
# Clonar repositório
git clone https://github.com/opedrosoares/SophiaBot.git
cd SophiaBot

# Instalar dependências base
pip install -r requirements/base.txt
```

### 2. Usar Módulo de Extração

```bash
# Instalar dependências específicas
pip install -r requirements/extracao.txt

# Executar extração completa
python extracao/scripts/executar_completo.py

# Executar extração histórica
python extracao/scripts/executar_completo_historico.py

# Continuar extração interrompida
python extracao/scripts/continuar_extracao.py

# Ver documentação específica
cat docs/EXTRACAO.md
```

### 3. Usar Chatbot

```bash
# Instalar dependências específicas
pip install -r requirements/chatbot.txt

# Configurar ambiente
cp env_example .env
# Editar .env com sua OPENAI_API_KEY

# Configurar chatbot
python chatbot/scripts/setup.py

# Executar chatbot (método 1)
streamlit run chatbot/interface/streamlit_app.py

# Executar chatbot (método 2)
python chatbot/run_chatbot.py

# Ver documentação específica
cat docs/CHATBOT.md
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto baseado no `env_example`:

```bash
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
```

### Configuração do Chatbot

O chatbot pode ser configurado através de:

1. **Arquivo `.env`** - Variáveis de ambiente
2. **`chatbot/config/settings.py`** - Configurações específicas
3. **Interface web** - Configurações em tempo real

## 📊 Status do Projeto

### Módulo de Extração
- ✅ **18.381+ normas** extraídas e processadas
- ✅ **Extração de PDFs** com múltiplas técnicas (pdfplumber, OCR)
- ✅ **Monitoramento robusto** com backups automáticos
- ✅ **Processamento incremental** para atualizações
- ✅ **Scripts especializados** para diferentes cenários

### Módulo Chatbot
- ✅ **Sistema RAG completo** com ChromaDB
- ✅ **Interface Streamlit** intuitiva e responsiva
- ✅ **Busca semântica avançada** com re-ranking
- ✅ **Suporte a GPT-4.1-nano** para respostas otimizadas
- ✅ **Sistema de cache** para melhor performance
- ✅ **Configuração flexível** via arquivos e interface

## 🛠️ Tecnologias Utilizadas

### Extração
- **Python 3.8+** - Linguagem principal
- **BeautifulSoup4** - Web scraping
- **Selenium** - Automação web
- **pdfplumber** - Extração de PDFs
- **Pandas** - Processamento de dados
- **PyPDF2** - Manipulação de PDFs
- **pytesseract** - OCR para PDFs

### Chatbot
- **OpenAI GPT-4.1-nano** - Modelo de linguagem
- **ChromaDB** - Banco vetorial
- **Streamlit** - Interface web
- **LangChain** - Framework RAG
- **text-embedding-3-small** - Embeddings
- **Plotly** - Visualizações interativas
- **diskcache** - Sistema de cache

## 📈 Estatísticas

- **📄 Normas Processadas**: 18.381+
- **💾 Tamanho da Base**: ~32MB (parquet comprimido)
- **🔍 Chunks Vetoriais**: 50.000+ (estimado)
- **⚡ Tempo de Resposta**: < 5 segundos
- **🎯 Precisão**: 95%+ (baseado em testes)

## 🤝 Como Contribuir

1. **Fork** do repositório
2. **Crie** uma branch para sua feature: `git checkout -b feature/nova-feature`
3. **Faça** commit das mudanças: `git commit -am 'Adiciona nova feature'`
4. **Push** para a branch: `git push origin feature/nova-feature`
5. **Abra** um Pull Request

### Áreas de Contribuição

- 🐛 Correção de bugs
- ✨ Novas funcionalidades
- 📚 Melhoria da documentação
- 🧪 Testes automatizados
- ⚡ Otimizações de performance

## 📋 Roadmap

### Próximas Versões

#### v1.1.0
- [ ] API REST para o chatbot
- [ ] Integração com WhatsApp/Telegram
- [ ] Sistema de analytics avançado
- [ ] Cache inteligente de consultas

#### v1.2.0
- [ ] Interface web personalizada (além do Streamlit)
- [ ] Suporte a múltiplos idiomas
- [ ] Sistema de feedback de usuários
- [ ] Integração com bancos de dados externos

## 📞 Suporte

- **📧 Email**: pedro.soares@antaq.gov.br
- **📖 Documentação**: Veja a pasta `docs/`
- **🐛 Issues**: Use o sistema de issues do GitHub

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **ANTAQ** - Pelos dados públicos disponibilizados
- **OpenAI** - Pela tecnologia GPT e embeddings
- **Comunidade Python** - Pelas bibliotecas open source
- **Contribuidores** - Por melhorias e feedback

---

**Desenvolvido com ❤️ para modernizar o acesso às normas de transporte aquaviário brasileiro**

## 📱 Links Rápidos

- [📖 Documentação da Extração](docs/EXTRACAO.md)
- [🤖 Documentação do Chatbot](docs/CHATBOT.md)
- [📋 Como Usar](docs/COMO_USAR.md)
- [⚙️ Configuração da API](docs/CONFIGURACAO_API.md)
- [🔧 Instruções de Vetorização](docs/INSTRUCOES_VETORIZACAO.md)