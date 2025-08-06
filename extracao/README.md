# 📥 Extração ANTAQ

Módulo robusto para extração e processamento de normas da ANTAQ.

## 🚀 Início Rápido

```bash
# 1. Instalar dependências
pip install -r ../requirements/extracao.txt

# 2. Executar extração completa
python ../run_extraction.py
# ou
python scripts/executar_completo.py
```

## 📁 Estrutura

```
extracao/
├── core/                    # 🏗️ Funcionalidades principais
│   ├── extrator.py          # motor principal de extração
│   ├── controlador.py       # controle de processos
│   └── monitor.py           # monitoramento
├── scripts/                 # 🚀 Scripts executáveis
│   ├── executar_completo.py # extração completa
│   ├── executar_historico.py# extração histórica
│   └── continuar_extracao.py# continuação
├── config/                  # ⚙️ Configurações
│   └── settings.py          # configurações principais
└── tests/                   # 🧪 Testes
```

## 💡 Scripts Disponíveis

### Extração Completa
```bash
python scripts/executar_completo.py
```
- Extrai todas as normas disponíveis
- Tempo estimado: 2-4 horas
- Cria backups automáticos

### Extração Histórica
```bash
python scripts/executar_historico.py
```
- Foca em dados históricos específicos
- Processamento otimizado por períodos

### Continuação
```bash
python scripts/continuar_extracao.py
```
- Continua processo interrompido
- Usa estado salvo anteriormente

### Reprocessamento
```bash
python scripts/reprocessar_pdfs.py
```
- Reprocessa PDFs com falhas
- Múltiplas técnicas (OCR incluído)

## ⚙️ Configurações

```python
# config/settings.py

BASE_URL = "https://sophia.antaq.gov.br"
DELAY_MIN = 1  # segundos entre requests
DELAY_MAX = 3
PDF_METHODS = ['pdfplumber', 'pypdf2', 'ocr']
BACKUP_ENABLED = True
```

## 📊 Funcionalidades

- **Web Scraping Robusto**: BeautifulSoup4 + Selenium
- **Processamento de PDFs**: 3 técnicas diferentes
- **OCR**: Para PDFs digitalizados
- **Monitoramento**: Progress bars e logs detalhados
- **Backups Automáticos**: Proteção de dados
- **Rate Limiting**: Evita sobrecarga do servidor

## 📈 Performance

- **Velocidade**: ~50-100 registros/minuto
- **Taxa de Sucesso**: 95%+ (extração)
- **Taxa OCR**: 85%+ (PDFs digitalizados)
- **Dados Processados**: 18.381+ normas

## 🔍 Monitoramento

### Logs
```bash
# Log principal
tail -f ../shared/logs/extracao_main.log

# Apenas erros
tail -f ../shared/logs/extracao_errors.log

# Performance
tail -f ../shared/logs/performance.log
```

### Dados
```bash
# Verificar dados extraídos
ls -la ../shared/data/

# Estatísticas básicas
python -c "import pandas as pd; df=pd.read_parquet('../shared/data/normas_antaq_completo.parquet'); print(f'Total: {len(df):,} normas')"
```

## 🧪 Testes

```bash
# Todos os testes
python -m pytest tests/

# Teste específico
python -m pytest tests/testar_extracao.py
```

## 🛠️ Troubleshooting

### Problemas Comuns

#### ConnectionError
```bash
# Aguardar e ajustar delays
# config/settings.py
DELAY_MIN = 2
DELAY_MAX = 5
```

#### PDF extraction failed
```bash
# Habilitar OCR
OCR_ENABLED = True
```

#### Memory error
```bash
# Reduzir batch size
BATCH_SIZE = 50
```

## 📚 Documentação Completa

Veja [../docs/EXTRACAO.md](../docs/EXTRACAO.md) para documentação detalhada.

## 🔗 Links Úteis

- [Documentação Principal](../README.md)
- [Guia do Chatbot](../docs/CHATBOT.md)
- [Setup Unificado](../setup.py)