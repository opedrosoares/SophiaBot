# 🚀 COMO USAR - WEBSCRAPER ANTAQ (GUIA RÁPIDO)

## ⚡ INÍCIO RÁPIDO

### 1. **Extração básica SEM PDFs (mais rápida)**
```bash
python3 Scrap.py
```
> ⏱️ ~3-5 horas para todas as normas
> 💾 ~100MB de dados

### 2. **Extração completa COM PDFs (mais completa)**
```bash
python3 executar_completo.py
```
> ⏱️ ~8-12 horas para todas as normas
> 💾 ~500MB-2GB de dados

### 3. **Extração incremental de PDFs**
```bash
python3 extrair_pdfs_incrementalmente.py
```
> 🔄 Extrai apenas PDFs não processados
> ⚡ Ideal para atualizações graduais

---

## 🔍 BUSCA E ANÁLISE

### Buscar por conteúdo dos PDFs:
```python
import pandas as pd

# Carrega dados
df = pd.read_parquet("normas_antaq_completo.parquet")

# Busca por termo
termo = "navegação interior"
matches = df[df['conteudo_pdf'].str.contains(termo, case=False, na=False)]
print(f"Encontradas {len(matches)} normas sobre '{termo}'")

# Lista resultados
for _, norma in matches.iterrows():
    print(f"- {norma['titulo']} (ID: {norma['codigo_registro']})")
```

### Estatísticas rápidas:
```python
# Resumo geral
print(f"Total de normas: {len(df)}")
print(f"Com PDFs extraídos: {df['conteudo_pdf'].str.len().gt(0).sum()}")
print(f"Normas em vigor: {(df['situacao'] == 'Em vigor').sum()}")

# Métodos de extração
print(df['metodo_extracao'].value_counts())
```

---

## 🧪 TESTES

### Testar extração de PDFs:
```bash
python3 testar_pdf_extracao.py
```

### Testar sistema de chave primária:
```bash
python3 testar_duplicatas.py
```

### Ver exemplos práticos:
```bash
python3 exemplo_pdf_extracao.py
python3 exemplo_chave_primaria.py
```

---

## 📊 CENÁRIOS COMUNS

### 🏛️ **Para Compliance/Jurídico:**
1. Execute extração completa: `python3 executar_completo.py`
2. Configure execução semanal para atualizações
3. Use busca por conteúdo para monitorar termos específicos

### 📚 **Para Pesquisa Acadêmica:**
1. Execute com PDFs: `python3 Scrap.py` (com `extract_pdf_content=True`)
2. Analise evolução temporal das regulamentações
3. Use análise textual para identificar padrões

### 🔍 **Para Monitoramento:**
1. Execute extração básica regularmente
2. Compare com dados anteriores para detectar mudanças
3. Configure alertas para novas normas

### 📈 **Para Análise de Dados:**
1. Extraia todos os dados com PDFs
2. Use pandas para análises estatísticas
3. Crie visualizações e relatórios

---

## ⚙️ CONFIGURAÇÕES RECOMENDADAS

### Para uso em produção:
```python
scraper = SophiaANTAQScraper(
    delay=2.0,              # Mais respeitoso com servidor
    extract_pdf_content=True # Conteúdo completo
)
```

### Para testes/desenvolvimento:
```python
scraper = SophiaANTAQScraper(
    delay=1.0,               # Mais rápido
    extract_pdf_content=False # Só metadados
)
```

### Para extração histórica:
```python
# Extrair tudo de uma vez
dados = scraper.scrape_all_pages()  # Sem limite de páginas
```

### Para atualizações regulares:
```python
# Usar sistema incremental automático
python3 executar_completo.py  # Detecta automaticamente novos dados
```

---

## 🚨 DICAS IMPORTANTES

### ✅ **Faça sempre:**
- Execute em horários de menor tráfego
- Monitore logs para identificar problemas
- Faça backup dos dados antes de grandes extrações
- Use `delay >= 1.5` para ser respeitoso com o servidor

### ❌ **Evite:**
- Executar múltiplas instâncias simultaneamente
- Usar delays muito baixos (`< 1.0`)
- Processar todos os PDFs de uma vez (use incrementalmente)
- Ignorar mensagens de erro nos logs

### 🛠️ **Em caso de problemas:**
1. Verifique conexão com internet
2. Confirme que Tesseract está instalado (`brew install tesseract`)
3. Reinstale dependências (`pip install -r requirements.txt`)
4. Execute testes (`python3 testar_pdf_extracao.py`)

---

## 📞 AJUDA RÁPIDA

### Comandos essenciais:
```bash
# Ver dados extraídos
python3 visualizar_dados.py

# Análise detalhada
python3 analise_detalhada.py

# Todos os exemplos
python3 exemplo_uso.py
```

### Arquivos importantes:
- `normas_antaq_completo.parquet` - Base principal
- `backup_*.parquet` - Backups automáticos
- `teste_*.parquet` - Dados de teste

### Logs e debug:
- Logs são mostrados no terminal
- Erros são salvos na coluna `erro_extracao`
- Use `logging.DEBUG` para mais detalhes

---

**🎯 Este é um sistema completo e robusto. Com essas instruções você pode extrair e analisar todas as normas da ANTAQ de forma eficiente e confiável!**