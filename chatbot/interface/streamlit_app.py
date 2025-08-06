#!/usr/bin/env python3
"""
Interface Streamlit para o Chatbot ANTAQ
Interface amigável para consultas sobre normas da ANTAQ
"""

import streamlit as st
import streamlit.components.v1 as components
import os
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any
import time
import random

# Adicionar diretório do projeto ao path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.vector_store import VectorStoreANTAQ
from core.rag_system import RAGSystemANTAQ
from config.config import OPENAI_API_KEY, OPENAI_MODEL, CHROMA_PERSIST_DIRECTORY, DATA_PATH

# Configuração da página
st.set_page_config(
    page_title="Chatbot ANTAQ - Consultas sobre Normas",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.gov.br/antaq/pt-br',
        'Report a bug': 'mailto:gpf@antaq.gov.br',
        'About': """
        # Chatbot ANTAQ
        
        Sistema inteligente para consultas sobre normas da 
        Agência Nacional de Transportes Aquaviários.
        
        **Desenvolvido com:**
        - OpenAI GPT-4
        - ChromaDB (Banco Vetorial)
        - Streamlit
        - Técnicas RAG (Retrieval-Augmented Generation)
        """
    }
)

# Carregar CSS customizado
def load_css():
    css_file = Path(__file__).parent / "styles.css"
    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Carregar estilos CSS
load_css()

class ChatbotANTAQApp:
    """Classe principal da aplicação Streamlit"""
    
    def __init__(self):
        """Inicializa a aplicação"""
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Inicializa estados da sessão"""
        
        # Estados principais
        if 'rag_system' not in st.session_state:
            st.session_state.rag_system = None
            
        if 'vector_store' not in st.session_state:
            st.session_state.vector_store = None
            
        if 'messages' not in st.session_state:
            st.session_state.messages = []
            
        if 'system_initialized' not in st.session_state:
            st.session_state.system_initialized = False
            
        # Configurações
        if 'show_sources' not in st.session_state:
            st.session_state.show_sources = True
            
        if 'max_results' not in st.session_state:
            st.session_state.max_results = 8
            
        if 'model_choice' not in st.session_state:
            st.session_state.model_choice = OPENAI_MODEL
            
        # Estatísticas
        if 'total_queries' not in st.session_state:
            st.session_state.total_queries = 0
            
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
            
        # Estados para perguntas de exemplo
        if 'shuffled_questions' not in st.session_state:
            st.session_state.shuffled_questions = []
            
        if 'preset_prompt' not in st.session_state:
            st.session_state.preset_prompt = ""
            
        if 'process_preset_prompt' not in st.session_state:
            st.session_state.process_preset_prompt = False
            
        if 'show_all_questions' not in st.session_state:
            st.session_state.show_all_questions = False
    
    def render_header(self):
        """Renderiza o cabeçalho da aplicação"""
        
        st.markdown("""
        <div class="main-header">
            <h1>Chatbot Sophia - ANTAQ</h1>
            <p>Sistema Inteligente para Consultas sobre Normas de Transporte Aquaviário</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Renderiza a barra lateral com configurações"""
        
        with st.sidebar:
            
            # Inicializar sistema automaticamente se não estiver inicializado
            # if not st.session_state.system_initialized:
                # if st.button("🚀 Inicializar Sistema", type="primary"):
                    # self.initialize_system()
            
            # Configurações avançadas
            if st.session_state.system_initialized:
                st.subheader("🎛️ Configurações Avançadas")
                
                # Modelo GPT
                model_options = ["gpt-4.1-nano", "gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
                current_model = st.session_state.model_choice
                
                # Se o modelo atual não estiver na lista, usar o primeiro
                if current_model not in model_options:
                    current_model = model_options[0]
                    st.session_state.model_choice = current_model
                
                st.session_state.model_choice = st.selectbox(
                    "Modelo GPT",
                    options=model_options,
                    index=model_options.index(current_model),
                    help="Escolha o modelo GPT para gerar respostas"
                )
                
                # Número de resultados
                st.session_state.max_results = st.slider(
                    "Documentos para Contexto",
                    min_value=3,
                    max_value=15,
                    value=st.session_state.max_results,
                    help="Número de documentos relevantes para incluir no contexto"
                )
                
                # Mostrar fontes
                st.session_state.show_sources = st.checkbox(
                    "Mostrar Fontes",
                    value=st.session_state.show_sources,
                    help="Exibir documentos fonte das respostas"
                )
                
                st.divider()
                
                # Estatísticas da sessão
                st.subheader("📊 Estatísticas da Sessão")
                
                duration = datetime.now() - st.session_state.session_start
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Consultas", st.session_state.total_queries)
                with col2:
                    st.metric("Duração", f"{duration.seconds//60}min")
                
                # Ações
                st.subheader("🔧 Ações")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🗑️ Limpar Chat"):
                        self.clear_chat()
                        st.rerun()
                
                with col2:
                    if st.button("📥 Exportar Chat"):
                        self.export_chat()
                
                # Informações do sistema
                if st.expander("ℹ️ Informações do Sistema"):
                    if st.session_state.vector_store:
                        try:
                            stats = st.session_state.vector_store.get_collection_stats()
                            
                            if 'error' in stats:
                                st.error(f"Erro ao carregar estatísticas: {stats['error']}")
                                return
                            
                            st.write("**📊 Banco de Dados:**")
                            st.write(f"• Total de registros: {stats.get('total_chunks', 'N/A'):,}")
                            st.write(f"• Normas únicas: {stats.get('total_normas_unicas', 'N/A'):,}")
                            
                            # Tipos de normas
                            if 'tipos_normas' in stats and stats['tipos_normas']:
                                st.write("**📋 Tipos de Normas:**")
                                for tipo, count in list(stats['tipos_normas'].items())[:6]:
                                    st.write(f"• {tipo}: {count:,}")
                            
                            # Situações das normas
                            if 'situacoes' in stats and stats['situacoes']:
                                st.write("**⚖️ Situação das Normas:**")
                                for situacao, count in list(stats['situacoes'].items())[:3]:
                                    st.write(f"• {situacao}: {count:,}")
                            
                            # Top assuntos
                            if 'top_assuntos' in stats and stats['top_assuntos']:
                                st.write("**🏷️ Top Assuntos:**")
                                for assunto, count in list(stats['top_assuntos'].items())[:5]:
                                    if assunto and assunto.strip():
                                        st.write(f"• {assunto}: {count}")
                                    else:
                                        st.write(f"• Sem assunto: {count}")
                            
                            # Distribuição por ano
                            if 'distribuicao_anos' in stats and stats['distribuicao_anos']:
                                anos_ordenados = sorted(stats['distribuicao_anos'].items(), reverse=True)
                                if anos_ordenados:
                                    st.write("**📅 Período:**")
                                    ano_mais_recente = anos_ordenados[0][0]
                                    ano_mais_antigo = anos_ordenados[-1][0]
                                    st.write(f"• {ano_mais_antigo} - {ano_mais_recente}")
                                    st.write(f"• Ano mais recente: {ano_mais_recente} ({anos_ordenados[0][1]} registros)")
                        
                        except Exception as e:
                            st.error(f"Erro ao carregar estatísticas: {str(e)}")
    
    def initialize_system(self):
        """Inicializa o sistema RAG"""
        
        try:
            with st.spinner("🔄 Inicializando sistema..."):
                
                # Inicializar vector store
                st.session_state.vector_store = VectorStoreANTAQ(
                    openai_api_key=OPENAI_API_KEY,
                    persist_directory=str(CHROMA_PERSIST_DIRECTORY)
                )
                
                # Verificar se precisa carregar dados
                if not DATA_PATH.exists():
                    st.error(f"❌ Arquivo de dados não encontrado: {DATA_PATH}")
                    return
                
                # Carregar dados se necessário
                success = st.session_state.vector_store.load_and_process_data(
                    str(DATA_PATH),
                    force_rebuild=False
                )
                
                if not success:
                    st.error("❌ Erro ao carregar dados no banco vetorial")
                    return
                
                # Inicializar RAG system
                st.session_state.rag_system = RAGSystemANTAQ(
                    openai_api_key=OPENAI_API_KEY,
                    vector_store=st.session_state.vector_store,
                    model=OPENAI_MODEL
                )
                
                st.session_state.system_initialized = True
                st.success("✅ Sistema inicializado com sucesso!")
                
        except Exception as e:
            st.error(f"❌ Erro ao inicializar sistema: {str(e)}")
            st.session_state.system_initialized = False
    
    def generate_example_questions(self):
        """Gera perguntas de exemplo dinâmicas"""
        
        if not st.session_state.shuffled_questions:
            preset_questions = [
                "Como funciona o licenciamento de terminais portuários?",
                "Quais são as tarifas para navegação interior?",
                "O que é necessário para autorização de operação portuária?",
                "Quais normas regulam o transporte de cargas perigosas?",
                "Como é feita a fiscalização de embarcações?",
                "Quais são os requisitos para concessão de terminais?",
                "Como funciona o sistema de tarifas portuárias?",
                "Quais são as normas para transporte de passageiros?",
                "Como é regulamentado o transporte de contêineres?",
                "Quais são as obrigações dos operadores portuários?",
                "Como funciona o sistema de monitoramento de embarcações?"
            ]
            random.shuffle(preset_questions)
            st.session_state.shuffled_questions = preset_questions
    
    def render_example_questions(self):
        """Renderiza as perguntas de exemplo"""
        
        self.generate_example_questions()
        
        questions_to_show = st.session_state.shuffled_questions
        questions_limit = len(questions_to_show) if st.session_state.show_all_questions else 3

        for i, q in enumerate(questions_to_show[:questions_limit]):
            if st.button(q, key=f"q_button_{i}", use_container_width=True):
                st.session_state.preset_prompt = q
                st.session_state.process_preset_prompt = True
                st.rerun()

        if not st.session_state.show_all_questions and len(questions_to_show) > 3:
            if st.button("➕ Ver mais exemplos", key="show_more", use_container_width=True):
                st.session_state.show_all_questions = True
                st.rerun()
    
    def render_chat_interface(self):
        """Renderiza a interface de chat"""
        
        if not st.session_state.system_initialized:
            st.error("❌ Erro ao inicializar o sistema. Verifique as configurações.")
            return
        
        # Exibir histórico do chat usando st.chat_message
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if isinstance(message["content"], tuple):
                    text_content, image_content = message["content"]
                    st.markdown(text_content)
                    if image_content:
                        st.image(image_content, use_container_width=True)
                else:
                    st.markdown(message["content"])
                
                # Mostrar fontes se habilitado
                if (message["role"] == "assistant" and 
                    st.session_state.show_sources and 
                    message.get('sources')):
                    with st.expander(f"📚 Fontes consultadas ({len(message['sources'])} documentos)"):
                        self.render_sources(message['sources'])
        
        # Perguntas de exemplo (apenas se não há mensagens)
        if not st.session_state.messages:
            st.markdown("### Bem-vindo ao Chatbo Sophia - ANTAQ!")
            st.markdown("**Exemplos de perguntas que você pode fazer:**")
            self.render_example_questions()
        
        # Área de entrada usando st.chat_input
        prompt = st.chat_input("Pergunte-me sobre normas da ANTAQ...", key="chat_input")
        
        # Processar entrada
        if prompt:
            self.process_user_query(prompt)
            st.rerun()
        
        # Processar perguntas de exemplo
        if st.session_state.get('process_preset_prompt'):
            preset_prompt = st.session_state.get('preset_prompt')
            st.session_state.process_preset_prompt = False
            if preset_prompt:
                self.process_user_query(preset_prompt)
                st.rerun()
    
    def process_user_query(self, query: str):
        """Processa uma consulta do usuário"""
        
        try:
            # Adicionar mensagem do usuário
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Atualizar estatísticas
            st.session_state.total_queries += 1
            
            # Processar consulta
            with st.chat_message("assistant"):
                with st.spinner("🤔 Analisando sua pergunta..."):
                    result = st.session_state.rag_system.query(
                        user_query=query,
                        n_results=st.session_state.max_results
                    )
                
                # Exibir resposta
                st.markdown(result['response'])
                
                # Mostrar fontes se habilitado
                if st.session_state.show_sources and result.get('sources'):
                    with st.expander(f"📚 Fontes consultadas ({len(result['sources'])} documentos)"):
                        self.render_sources(result['sources'])
            
            # Adicionar resposta ao histórico
            assistant_message = {
                'role': 'assistant',
                'content': result['response'],
                'sources': result.get('sources', []),
                'metadata': result.get('metadata', {}),
                'timestamp': datetime.now()
            }
            st.session_state.messages.append(assistant_message)
            
            # Scroll automático para a última mensagem
            components.html(
                """
                <script>
                    setTimeout(function() {
                        var stMain = window.parent.document.getElementsByClassName("stMain")[0];
                        if (stMain) { stMain.scrollTo({ top: stMain.scrollHeight, behavior: 'smooth' }); }
                    }, 200);
                </script>
                """
            )
            
        except Exception as e:
            st.error(f"❌ Erro ao processar consulta: {str(e)}")
    
    def render_sources(self, sources: List[Dict[str, Any]]):
        """Renderiza as fontes consultadas"""
        
        for i, source in enumerate(sources, 1):
            relevance = source.get('relevance_score', 0)
            relevance_color = "🟢" if relevance > 0.8 else "🟡" if relevance > 0.6 else "🔴"
            
            st.markdown(f"""
            <div class="source-card">
                <h4>{i}. {f'<a href="{source.get("link_pdf")}" target="_blank">{source.get("titulo", "N/A")} ↗️</a>' if source.get("link_pdf") and source.get("link_pdf") != "N/A" else source.get("titulo", "N/A")}</h4>
                <p><strong>Código:</strong> {source.get('codigo_registro', 'N/A')}</p>
                <p><strong>Assunto:</strong> {source.get('assunto', 'N/A')}</p>
                <p><strong>Situação:</strong> {source.get('situacao', 'N/A')}</p>
                <p><strong>Data:</strong> {datetime.strptime(source.get('assinatura', ''), '%Y-%m-%d').strftime('%d/%m/%Y') if source.get('assinatura', '') not in ['', 'N/A', None] else 'N/A'}</p>
                <p><strong>Relevância:</strong>{relevance_color} {relevance:.1%}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def clear_chat(self):
        """Limpa o histórico do chat"""
        st.session_state.messages = []
        if st.session_state.rag_system:
            st.session_state.rag_system.clear_history()
        st.success("🗑️ Chat limpo com sucesso!")
    
    def export_chat(self):
        """Exporta o histórico do chat"""
        try:
            if not st.session_state.messages:
                st.warning("⚠️ Não há conversa para exportar")
                return
            
            # Preparar dados para exportação
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'total_messages': len(st.session_state.messages),
                'session_duration': str(datetime.now() - st.session_state.session_start),
                'conversation': []
            }
            
            for msg in st.session_state.messages:
                export_msg = {
                    'role': msg['role'],
                    'content': msg['content'],
                    'timestamp': msg.get('timestamp', datetime.now()).isoformat() if isinstance(msg.get('timestamp'), datetime) else str(msg.get('timestamp', ''))
                }
                
                if msg['role'] == 'assistant' and 'sources' in msg:
                    export_msg['sources_count'] = len(msg['sources'])
                    export_msg['metadata'] = msg.get('metadata', {})
                
                export_data['conversation'].append(export_msg)
            
            # Criar arquivo JSON
            export_json = json.dumps(export_data, ensure_ascii=False, indent=2)
            
            # Oferecer download
            st.download_button(
                label="📥 Baixar conversa",
                data=export_json,
                file_name=f"conversa_antaq_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"❌ Erro ao exportar conversa: {str(e)}")
    
    def render_dashboard(self):
        """Renderiza dashboard com estatísticas"""
        
        if not st.session_state.system_initialized:
            return
        
        with st.expander("📊 Dashboard"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Consultas na Sessão",
                    st.session_state.total_queries,
                    delta=None
                )
            
            with col2:
                messages_count = len([m for m in st.session_state.messages if m['role'] == 'user'])
                st.metric(
                    "Mensagens",
                    messages_count,
                    delta=None
                )
            
            with col3:
                duration = datetime.now() - st.session_state.session_start
                st.metric(
                    "Tempo de Sessão",
                    f"{duration.seconds//60}min",
                    delta=None
                )
            
            with col4:
                avg_response_time = "< 10s"  # Estimativa
                st.metric(
                    "Tempo Médio",
                    avg_response_time,
                    delta=None
                )
    
    def run(self):
        """Executa a aplicação"""
        
        # Renderizar componentes
        self.render_header()
        self.render_sidebar()
        
        # Inicializar sistema automaticamente na primeira execução
        if not st.session_state.system_initialized:
            with st.spinner("🔄 Inicializando sistema automaticamente..."):
                self.initialize_system()
        
        self.render_dashboard()
        self.render_chat_interface()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666;">
            <p>Chatbot Sophia - ANTAQ - Sistema inteligente para consultas sobre normas de transporte aquaviário</p>
            <p>Desenvolvido com OpenAI GPT-4 • ChromaDB • Streamlit</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Função principal"""
    app = ChatbotANTAQApp()
    app.run()

if __name__ == "__main__":
    main()