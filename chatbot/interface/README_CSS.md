# Estilos CSS Customizados - Chatbot ANTAQ

## Visão Geral

Este diretório contém os arquivos de interface do Streamlit para o Chatbot ANTAQ, incluindo estilos CSS customizados para melhorar a aparência da aplicação.

## Arquivos

### `streamlit_app.py`
- Aplicação principal do Streamlit
- Carrega automaticamente o arquivo CSS externo
- Implementa a interface do chat com estilos customizados

### `styles.css`
- Arquivo CSS com estilos customizados
- Contém definições para classes como `.source-card`, `.main-header`, etc.
- Estilos específicos para melhorar a aparência dos cards de fontes

## Estilos Implementados

### `.source-card`
```css
.source-card {
    border: none;
    box-shadow: none;
    border-bottom: 1px solid #ccc;
    border-radius: 0;
    background-color: #ffffff;
    padding: 1rem;
    margin: 0.5rem 0;
}
```

**Características:**
- Remove bordas e sombras padrão
- Adiciona apenas uma borda inferior sutil
- Mantém padding e margem para espaçamento adequado
- Fundo branco para contraste

### Outros Estilos
- `.main-header`: Cabeçalho com gradiente azul
- `.metric-card`: Cards para métricas do dashboard
- `.example-question`: Estilo para perguntas de exemplo

## Como Funciona

1. A função `load_css()` é chamada no início da aplicação
2. O arquivo `styles.css` é lido e injetado no HTML do Streamlit
3. Os estilos são aplicados automaticamente aos elementos com as classes correspondentes

## Modificações Recentes

- **Antes**: Estilos CSS inline no código Python
- **Depois**: Arquivo CSS separado para melhor organização
- **Benefício**: Facilita manutenção e customização dos estilos

## Como Modificar Estilos

Para alterar os estilos:

1. Edite o arquivo `styles.css`
2. As mudanças serão aplicadas automaticamente na próxima execução
3. Não é necessário modificar o código Python

## Exemplo de Uso

```python
# No HTML do Streamlit
st.markdown("""
<div class="source-card">
    <h4>Título do Documento</h4>
    <p>Conteúdo do documento...</p>
</div>
""", unsafe_allow_html=True)
``` 