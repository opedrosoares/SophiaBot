# 📥 Módulo de Extração - Sophia

Sistema robusto para extração e processamento de normas da ANTAQ.

## 🎯 Objetivo

O módulo de extração é responsável por:
- Extrair normas do site oficial da ANTAQ
- Processar PDFs com múltiplas técnicas
- Manter base de dados atualizada
- Gerenciar backups e logs automáticos

## 📁 Estrutura do Módulo

```
extracao/
├── core/                            # 🏗️ Funcionalidades principais
│   ├── extrator.py                  # Motor principal de extração
│   ├── controlador.py               # controle de processos
│   ├── monitor.py                   # monitoramento de progresso
│   └── utils.py                     # utilitários auxiliares
├── scripts/                         # 🚀 Scripts executáveis
│   ├── executar_completo.py         # extração completa
│   ├── executar_historico.py        # extração histórica
│   ├── continuar_extracao.py        # continuação de processos
│   └── reprocessar_pdfs.py          # reprocessamento de PDFs
├── tests/                           # 🧪 Testes automatizados
│   ├── testar_extracao.py           # testes de extração
│   └── testar_pdf.py                # testes de PDF
├── config/                          # ⚙️ Configurações
│   └── settings.py                  # configurações do módulo
└── README.md                        # documentação específica
```

## 🚀 Como Usar

### Instalação

```bash
# Instalar dependências
pip install -r requirements/extracao.txt

# Ou instalar tudo
pip install -r requirements/base.txt -r requirements/extracao.txt
```

### Execução

#### 1. Extração Completa (Recomendado)
```bash
python extracao/scripts/executar_completo.py
```
- Extrai todas as normas disponíveis
- Processa PDFs automaticamente
- Cria backups automáticos
- Tempo estimado: 2-4 horas

#### 2. Extração Histórica
```bash
python extracao/scripts/executar_historico.py
```
- Foca em dados históricos específicos
- Processamento otimizado por períodos
- Ideal para análises temporais

#### 3. Continuação de Extração
```bash
python extracao/scripts/continuar_extracao.py
```
- Continua processo interrompido
- Usa estado salvo anteriormente
- Evita reprocessamento desnecessário

#### 4. Reprocessamento de PDFs
```bash
python extracao/scripts/reprocessar_pdfs.py
```
- Reprocessa PDFs com falhas
- Múltiplas técnicas de extração
- OCR para PDFs digitalizados

## ⚙️ Configurações

### Arquivo de Configuração
```python
# extracao/config/settings.py

# URLs e endpoints
BASE_URL = "https://sophia.antaq.gov.br"
SEARCH_ENDPOINT = "/Terminal/Busca"

# Configurações de scraping
DELAY_MIN = 1  # segundos
DELAY_MAX = 3  # segundos
TIMEOUT = 30   # segundos

# Processamento de PDFs
PDF_METHODS = ['pdfplumber', 'pypdf2', 'ocr']
OCR_ENABLED = True
OCR_LANG = 'por'  # português

# Backups
BACKUP_ENABLED = True
BACKUP_INTERVAL = 100  # a cada N registros
```

## 📊 Funcionalidades

### 1. Extração Web
- **Web Scraping Robusto**: BeautifulSoup4 + Selenium
- **Rate Limiting**: Delays configuráveis
- **Retry Logic**: Tentativas automáticas em falhas
- **User-Agent Rotation**: Evita bloqueios
- **Session Management**: Mantém estado de navegação

### 2. Processamento de PDFs
- **Múltiplas Técnicas**:
  - `pdfplumber`: Extração de texto nativo
  - `PyPDF2`: Processamento rápido
  - `OCR`: Para PDFs digitalizados
- **Detecção Automática**: Escolhe melhor método
- **Fallback**: Tenta métodos alternativos
- **Validação**: Verifica qualidade da extração

### 3. Monitoramento
- **Progress Bars**: Acompanhamento visual
- **Logs Detalhados**: Múltiplos níveis
- **Métricas**: Estatísticas de performance
- **Estado Persistente**: Continua de onde parou
- **Backups Automáticos**: Proteção de dados

### 4. Qualidade de Dados
- **Deduplicação**: Remove registros duplicados
- **Validação**: Verifica integridade dos dados
- **Limpeza**: Normaliza textos e metadados
- **Enriquecimento**: Adiciona informações derivadas

## 📈 Performance

### Estatísticas Típicas
- **Velocidade**: ~50-100 registros/minuto
- **Taxa de Sucesso**: 95%+ (extração)
- **Taxa OCR**: 85%+ (PDFs digitalizados)
- **Uso de Memória**: ~500MB-1GB
- **Uso de CPU**: 20-40% (single-core)

### Otimizações
- **Processamento em Lotes**: Reduz overhead
- **Cache de Sessões**: Reutiliza conexões
- **Processamento Assíncrono**: Para I/O bound
- **Compressão**: Dados salvos em Parquet
- **Indexação**: Busca rápida por metadados

## 🔍 Monitoramento e Logs

### Estrutura de Logs
```
shared/logs/
├── extracao_main.log              # log principal
├── extracao_errors.log            # apenas erros
├── pdf_processing.log             # processamento PDFs
└── performance.log                # métricas de performance
```

### Níveis de Log
- **DEBUG**: Informações detalhadas de debugging
- **INFO**: Progresso normal e marcos importantes
- **WARNING**: Situações que requerem atenção
- **ERROR**: Erros que impedem processamento
- **CRITICAL**: Falhas críticas do sistema

### Métricas Monitoradas
- Páginas processadas por minuto
- Taxa de sucesso de extração
- Tamanho médio dos PDFs
- Tempo médio de processamento
- Uso de recursos (CPU, memória)

## 🛠️ Troubleshooting

### Problemas Comuns

#### ❌ "ConnectionError: Max retries exceeded"
**Causa**: Site indisponível ou bloqueio
**Solução**: 
```bash
# Aguardar e tentar novamente
# Verificar conectividade
ping sophia.antaq.gov.br

# Ajustar delays no config
DELAY_MIN = 2
DELAY_MAX = 5
```

#### ❌ "PDF extraction failed"
**Causa**: PDF corrompido ou protegido
**Solução**:
```bash
# Habilitar OCR
OCR_ENABLED = True

# Reprocessar PDFs específicos
python extracao/scripts/reprocessar_pdfs.py --codigo 12345
```

#### ❌ "Memory error during processing"
**Causa**: Processamento de PDFs muito grandes
**Solução**:
```bash
# Processar em lotes menores
BATCH_SIZE = 50  # reduzir de 100

# Aumentar limite de memória virtual
ulimit -v 4000000  # 4GB
```

### Debug Mode

```bash
# Executar com debug habilitado
DEBUG=true python extracao/scripts/executar_completo.py

# Logs mais verbosos
LOG_LEVEL=DEBUG python extracao/scripts/executar_completo.py

# Processar apenas alguns registros
LIMIT=10 python extracao/scripts/executar_completo.py
```

## 🧪 Testes

### Executar Testes
```bash
# Todos os testes
python -m pytest extracao/tests/

# Testes específicos
python -m pytest extracao/tests/testar_extracao.py

# Com coverage
python -m pytest extracao/tests/ --cov=extracao
```

### Tipos de Teste
- **Unit Tests**: Funções individuais
- **Integration Tests**: Fluxo completo
- **PDF Tests**: Diferentes tipos de PDF
- **Performance Tests**: Benchmarks

## 📋 Checklist de Extração

### Antes de Executar
- [ ] Verificar conectividade com ANTAQ
- [ ] Configurar delays adequados
- [ ] Verificar espaço em disco (>5GB)
- [ ] Configurar backups automáticos

### Durante Execução
- [ ] Monitorar logs de erro
- [ ] Verificar uso de recursos
- [ ] Acompanhar progress bars
- [ ] Verificar qualidade dos dados

### Após Execução
- [ ] Validar dados extraídos
- [ ] Verificar backups gerados
- [ ] Analisar métricas de performance
- [ ] Documentar problemas encontrados

## 📊 Análise de Dados

### Exploração Básica
```python
import pandas as pd

# Carregar dados
df = pd.read_parquet('shared/data/normas_antaq_completo.parquet')

# Estatísticas básicas
print(f"Total de normas: {len(df):,}")
print(f"Período: {df['assinatura'].min()} a {df['assinatura'].max()}")
print(f"Taxa de extração: {(df['conteudo_pdf'].notna().sum() / len(df) * 100):.1f}%")

# Por ano
df['ano'] = pd.to_datetime(df['assinatura']).dt.year
distribuicao = df['ano'].value_counts().sort_index()
print(distribuicao.tail(10))
```

### Qualidade dos Dados
```python
# Verificar completude
completude = df.isnull().sum() / len(df) * 100
print("Completude dos campos:")
print(completude.sort_values())

# Tamanho médio dos PDFs
df_com_pdf = df[df['conteudo_pdf'].notna()]
tamanho_medio = df_com_pdf['conteudo_pdf'].str.len().mean()
print(f"Tamanho médio do texto: {tamanho_medio:.0f} caracteres")
```

## 🔄 Manutenção

### Atualizações Regulares
- **Diárias**: Verificar novas normas
- **Semanais**: Reprocessar PDFs falhados
- **Mensais**: Backup completo e validação
- **Trimestrais**: Otimização e limpeza

### Backup Strategy
- **Incremental**: A cada execução
- **Completo**: Semanal
- **Histórico**: Manter últimos 30 dias
- **Offsite**: Backup em nuvem (opcional)

---

**Para dúvidas específicas sobre extração, consulte os logs em `shared/logs/` ou abra uma issue no repositório.**