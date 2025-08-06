# Chatbot de Normas - SophiaBot

Sistema completo para extração de dados e consultas inteligentes sobre normas da ANTAQ (Agência Nacional de Transportes Aquaviários).

## 📋 Visão Geral

O projeto Sophia é dividido em dois módulos principais:

- **🔄 Extração**: Sistema robusto para scraping e processamento de normas do site da ANTAQ
- **🤖 Chatbot**: Interface inteligente para consultas usando técnicas RAG (Retrieval-Augmented Generation)

## 📁 Estrutura do Projeto

```
Sophia/
├── extracao/                         # 📥 Módulo de extração de dados
│   ├── core/                         # Funcionalidades principais
│   │   ├── extrator.py              # Motor de extração principal
│   │   ├── controlador.py           # Controlador de processos
│   │   └── monitor.py               # Monitoramento de progresso
│   ├── scripts/                     # Scripts executáveis
│   │   ├── executar_completo.py     # Extração completa
│   │   ├── executar_historico.py    # Extração histórica
│   │   └── continuar_extracao.py    # Continuação de processos
│   ├── tests/                       # Testes do módulo
│   └── config/                      # Configurações
├── chatbot/                         # 🤖 Módulo do chatbot
│   ├── core/                        # Sistema RAG
│   │   ├── vector_store.py          # Banco vetorial ChromaDB
│   │   └── rag_system.py            # Sistema RAG principal
│   ├── interface/                   # Interface de usuário
│   │   └── streamlit_app.py         # App Streamlit
│   ├── config/                      # Configurações
│   ├── scripts/                     # Scripts utilitários
│   └── tests/                       # Testes do chatbot
├── shared/                          # 📚 Recursos compartilhados
│   ├── data/                        # Dados processados
│   ├── logs/                        # Logs do sistema
│   ├── exports/                     # Arquivos exportados
│   └── backups/                     # Backups automáticos
├── requirements/                    # 📋 Dependências organizadas
│   ├── base.txt                     # Dependências comuns
│   ├── extracao.txt                 # Específicas da extração
│   └── chatbot.txt                  # Específicas do chatbot
└── docs/                            # 📖 Documentação
    ├── EXTRACAO.md                  # Guia do módulo de extração
    └── CHATBOT.md                   # Guia do módulo chatbot
```

## 🚀 Início Rápido

### 1. Instalação Base

```bash
# Clonar repositório
git clone <repo-url>
cd Sophia

# Instalar dependências base
pip install -r requirements/base.txt
```

### 2. Usar Módulo de Extração

```bash
# Instalar dependências específicas
pip install -r requirements/extracao.txt

# Executar extração completa
python extracao/scripts/executar_completo.py

# Ver documentação específica
cat docs/EXTRACAO.md
```

### 3. Usar Chatbot

```bash
# Instalar dependências específicas
pip install -r requirements/chatbot.txt

# Configurar chave OpenAI
cp chatbot/config/settings_example.py chatbot/config/settings.py
# Editar settings.py com sua OPENAI_API_KEY

# Executar chatbot
streamlit run chatbot/interface/streamlit_app.py

# Ver documentação específica
cat docs/CHATBOT.md
```

## 📊 Status do Projeto

### Módulo de Extração
- ✅ **18.381+ normas** extraídas e processadas
- ✅ **Extração de PDFs** com múltiplas técnicas (pdfplumber, OCR)
- ✅ **Monitoramento robusto** com backups automáticos
- ✅ **Processamento incremental** para atualizações

### Módulo Chatbot
- ✅ **Sistema RAG completo** com ChromaDB
- ✅ **Interface Streamlit** intuitiva
- ✅ **Busca semântica avançada** com re-ranking
- ✅ **Suporte a GPT-4.1-nano** para respostas otimizadas

## 🛠️ Tecnologias Utilizadas

### Extração
- **Python 3.8+** - Linguagem principal
- **BeautifulSoup4** - Web scraping
- **Selenium** - Automação web
- **pdfplumber** - Extração de PDFs
- **Pandas** - Processamento de dados

### Chatbot
- **OpenAI GPT-4.1-nano** - Modelo de linguagem
- **ChromaDB** - Banco vetorial
- **Streamlit** - Interface web
- **LangChain** - Framework RAG
- **text-embedding-3-small** - Embeddings

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
- [🏗️ Guia de Arquitetura](docs/ARQUITETURA.md)
- [🧪 Como Testar](docs/TESTES.md)