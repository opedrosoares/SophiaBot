#!/usr/bin/env python3
"""
Sistema RAG (Retrieval-Augmented Generation) para o Chatbot ANTAQ
Integra busca semântica com geração de respostas via OpenAI
"""

import openai
from typing import List, Dict, Any, Optional, Tuple
import json
import logging
from datetime import datetime
import re
from dataclasses import dataclass
from .vector_store import VectorStoreANTAQ

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Representa uma mensagem no chat"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

class RAGSystemANTAQ:
    """
    Sistema RAG principal para consultas sobre normas ANTAQ
    """
    
    def __init__(
        self,
        openai_api_key: str,
        vector_store: VectorStoreANTAQ,
        model: str = "gpt-4",
        max_context_length: int = 8000,
        temperature: float = 0.1
    ):
        """
        Inicializa o sistema RAG
        
        Args:
            openai_api_key: Chave da API OpenAI
            vector_store: Instância do banco vetorial
            model: Modelo GPT a usar
            max_context_length: Comprimento máximo do contexto
            temperature: Temperatura para geração
        """
        
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        self.vector_store = vector_store
        self.model = model
        self.max_context_length = max_context_length
        self.temperature = temperature
        
        # Histórico da conversa
        self.conversation_history: List[ChatMessage] = []
        
        logger.info(f"Sistema RAG inicializado com modelo: {model}")
    
    def _create_system_prompt(self) -> str:
        """Cria o prompt do sistema"""
        return """Você é um assistente especializado em normas da ANTAQ (Agência Nacional de Transportes Aquaviários). 

SUAS RESPONSABILIDADES:
• Responder perguntas sobre normas, regulamentações e legislação portuária e aquaviária
• Fornecer informações precisas baseadas apenas no conteúdo das normas fornecidas
• Citar sempre as normas específicas ao responder
• Explicar conceitos técnicos de forma clara
• Alertar quando não há informação suficiente nos documentos

DIRETRIZES DE RESPOSTA:
• Use apenas informações do contexto fornecido
• Cite o título e código das normas relevantes
• Se não souber algo, seja honesto sobre a limitação
• Forneça respostas estruturadas e organizadas
• Use linguagem técnica quando apropriado, mas sempre explicativa

FORMATO DE RESPOSTA:
• Resposta direta à pergunta
• Fundamentação legal (citando normas específicas)
• Informações complementares quando relevante
• Links para documentos quando disponíveis

Responda sempre em português brasileiro e seja preciso nas citações."""

    def _extract_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analisa a intenção da consulta para otimizar a busca
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Dicionário com análise da intenção
        """
        
        # Palavras-chave para diferentes tipos de consulta
        keywords_mapping = {
            'licenciamento': ['licença', 'licenciamento', 'autorização', 'permissão'],
            'tarifas': ['tarifa', 'preço', 'cobrança', 'taxa', 'valor'],
            'operacional': ['operação', 'funcionamento', 'procedimento', 'processo'],
            'fiscalizacao': ['fiscalização', 'multa', 'infração', 'penalidade', 'autuação'],
            'ambiental': ['ambiental', 'meio ambiente', 'sustentabilidade', 'poluição'],
            'seguranca': ['segurança', 'acidente', 'emergência', 'risco'],
            'portuario': ['porto', 'terminal', 'cais', 'berço', 'atracação'],
            'aquaviario': ['aquaviário', 'navegação', 'embarcação', 'navio', 'transporte']
        }
        
        # Detectar categoria principal
        query_lower = query.lower()
        categories = []
        
        for category, keywords in keywords_mapping.items():
            if any(keyword in query_lower for keyword in keywords):
                categories.append(category)
        
        # Detectar filtros temporais
        temporal_patterns = [
            r'\b20\d{2}\b',  # Anos
            r'\b(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\b',
            r'\b(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)\b'
        ]
        
        temporal_info = []
        for pattern in temporal_patterns:
            matches = re.findall(pattern, query_lower)
            temporal_info.extend(matches)
        
        return {
            'categories': categories,
            'temporal_info': temporal_info,
            'query_type': self._classify_query_type(query_lower),
            'entities': self._extract_entities(query)
        }
    
    def _classify_query_type(self, query: str) -> str:
        """Classifica o tipo de consulta"""
        
        if any(word in query for word in ['o que é', 'definição', 'conceito', 'significa']):
            return 'definition'
        elif any(word in query for word in ['como', 'procedimento', 'processo', 'etapas']):
            return 'procedure'
        elif any(word in query for word in ['quando', 'prazo', 'data', 'período']):
            return 'temporal'
        elif any(word in query for word in ['onde', 'local', 'endereço', 'localização']):
            return 'location'
        elif any(word in query for word in ['quem', 'responsável', 'competência']):
            return 'responsibility'
        elif any(word in query for word in ['quanto', 'valor', 'custo', 'preço']):
            return 'value'
        else:
            return 'general'
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extrai entidades nomeadas da consulta"""
        
        # Padrões para entidades comuns
        patterns = [
            r'\b[A-Z]{2,}\b',  # Siglas
            r'\b\d{1,4}/\d{2,4}\b',  # Números de normas
            r'\bResolução\s+\d+\b',  # Resoluções
            r'\bPortaria\s+\d+\b',  # Portarias
            r'\bDecreto\s+\d+\b'  # Decretos
        ]
        
        entities = []
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _rerank_results(
        self, 
        query: str, 
        results: List[Dict[str, Any]], 
        intent: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Re-ranqueia resultados baseado na intenção da consulta
        
        Args:
            query: Consulta original
            results: Resultados da busca vetorial
            intent: Análise da intenção
            
        Returns:
            Resultados re-ranqueados
        """
        
        def calculate_relevance_score(result: Dict[str, Any]) -> float:
            """Calcula score de relevância"""
            
            base_score = result['similarity']
            
            # Bonus por categoria
            document = result['document'].lower()
            title = result['metadata'].get('titulo', '').lower()
            
            category_bonus = 0
            for category in intent['categories']:
                if category in document or category in title:
                    category_bonus += 0.1
            
            # Bonus por entidades encontradas
            entity_bonus = 0
            for entity in intent['entities']:
                if entity.lower() in document or entity.lower() in title:
                    entity_bonus += 0.15
            
            # Penalty por documentos muito antigos se consulta for recente
            date_penalty = 0
            if result['metadata'].get('assinatura'):
                try:
                    year = int(result['metadata']['assinatura'][:4])
                    current_year = datetime.now().year
                    if current_year - year > 10:
                        date_penalty = -0.05
                except:
                    pass
            
            # Bonus por documentos em vigor
            status_bonus = 0.1 if result['metadata'].get('situacao') == 'Em vigor' else 0
            
            final_score = base_score + category_bonus + entity_bonus + date_penalty + status_bonus
            
            return max(0, min(1, final_score))  # Manter entre 0 e 1
        
        # Aplicar novo score
        for result in results:
            result['relevance_score'] = calculate_relevance_score(result)
        
        # Re-ordenar por relevância
        return sorted(results, key=lambda x: x['relevance_score'], reverse=True)
    
    def _format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Formata o contexto para o prompt do LLM
        
        Args:
            results: Resultados da busca
            
        Returns:
            Contexto formatado
        """
        
        if not results:
            return "Nenhum documento relevante encontrado."
        
        context_parts = []
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            
            context_part = f"""
DOCUMENTO {i}:
Título: {metadata.get('titulo', 'N/A')}
Código: {metadata.get('codigo_registro', 'N/A')}
Assunto: {metadata.get('assunto', 'N/A')}
Data de Assinatura: {metadata.get('assinatura', 'N/A')}
Situação: {metadata.get('situacao', 'N/A')}
Link: {metadata.get('link_pdf', 'N/A')}
Relevância: {result.get('relevance_score', result['similarity']):.3f}

CONTEÚDO:
{result['document']}
            """.strip()
            
            context_parts.append(context_part)
        
        return "\n\n" + "="*80 + "\n\n".join(context_parts)
    
    def _create_prompt(
        self, 
        query: str, 
        context: str, 
        conversation_history: List[ChatMessage]
    ) -> List[Dict[str, str]]:
        """
        Cria o prompt completo para o LLM
        
        Args:
            query: Consulta do usuário
            context: Contexto dos documentos relevantes
            conversation_history: Histórico da conversa
            
        Returns:
            Lista de mensagens formatadas para a API
        """
        
        messages = [
            {"role": "system", "content": self._create_system_prompt()}
        ]
        
        # Adicionar histórico recente (últimas 3 interações)
        recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        
        for msg in recent_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Adicionar contexto e consulta atual
        user_message = f"""
CONTEXTO DOS DOCUMENTOS RELEVANTES:
{context}

PERGUNTA DO USUÁRIO:
{query}

Por favor, responda à pergunta baseando-se exclusivamente nos documentos fornecidos no contexto. 
Cite sempre as fontes específicas (título e código do documento) ao elaborar sua resposta.
        """.strip()
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def query(
        self, 
        user_query: str, 
        n_results: int = 8,
        filters: Optional[Dict[str, Any]] = None,
        include_history: bool = True
    ) -> Dict[str, Any]:
        """
        Processa uma consulta do usuário
        
        Args:
            user_query: Pergunta do usuário
            n_results: Número de documentos para contexto
            filters: Filtros para a busca
            include_history: Se deve incluir histórico da conversa
            
        Returns:
            Resposta estruturada com metadados
        """
        
        try:
            # Adicionar mensagem do usuário ao histórico
            user_message = ChatMessage(role="user", content=user_query)
            if include_history:
                self.conversation_history.append(user_message)
            
            # Analisar intenção da consulta
            intent = self._extract_query_intent(user_query)
            logger.info(f"Intenção detectada: {intent}")
            
            # Busca semântica
            search_results = self.vector_store.search(
                query=user_query,
                n_results=n_results,
                filters=filters
            )
            
            if not search_results:
                response_content = """
Desculpe, não encontrei documentos relevantes para sua consulta na base de normas da ANTAQ. 

Algumas sugestões:
• Tente reformular sua pergunta com termos mais específicos
• Verifique se está perguntando sobre temas relacionados a transporte aquaviário
• Use palavras-chave como: licenciamento, tarifas, portos, navegação, etc.
                """.strip()
                
                assistant_message = ChatMessage(role="assistant", content=response_content)
                if include_history:
                    self.conversation_history.append(assistant_message)
                
                return {
                    'response': response_content,
                    'sources': [],
                    'metadata': {
                        'intent': intent,
                        'search_results_count': 0,
                        'model_used': self.model
                    }
                }
            
            # Re-ranquear resultados
            reranked_results = self._rerank_results(user_query, search_results, intent)
            
            # Preparar contexto
            context = self._format_context(reranked_results)
            
            # Criar prompt
            messages = self._create_prompt(
                user_query, 
                context, 
                self.conversation_history if include_history else []
            )
            
            # Gerar resposta
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=1500
            )
            
            response_content = response.choices[0].message.content
            
            # Adicionar resposta ao histórico
            assistant_message = ChatMessage(
                role="assistant", 
                content=response_content,
                metadata={
                    'sources_used': len(reranked_results),
                    'intent': intent
                }
            )
            
            if include_history:
                self.conversation_history.append(assistant_message)
            
            # Preparar fontes
            sources = []
            for result in reranked_results[:5]:  # Top 5 fontes
                metadata = result['metadata']
                sources.append({
                    'titulo': metadata.get('titulo', 'N/A'),
                    'codigo_registro': metadata.get('codigo_registro', 'N/A'),
                    'assunto': metadata.get('assunto', 'N/A'),
                    'situacao': metadata.get('situacao', 'N/A'),
                    'assinatura': metadata.get('assinatura', 'N/A'),
                    'link_pdf': metadata.get('link_pdf', 'N/A'),
                    'relevance_score': result.get('relevance_score', result['similarity'])
                })
            
            return {
                'response': response_content,
                'sources': sources,
                'metadata': {
                    'intent': intent,
                    'search_results_count': len(search_results),
                    'reranked_results_count': len(reranked_results),
                    'model_used': self.model,
                    'temperature': self.temperature,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar consulta: {e}")
            import traceback
            traceback.print_exc()
            
            error_response = f"Desculpe, ocorreu um erro ao processar sua consulta: {str(e)}"
            
            return {
                'response': error_response,
                'sources': [],
                'metadata': {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            }
    
    def clear_history(self):
        """Limpa o histórico da conversa"""
        self.conversation_history = []
        logger.info("Histórico da conversa limpo")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Retorna o histórico da conversa"""
        return [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'metadata': msg.metadata
            }
            for msg in self.conversation_history
        ]
    
    def export_conversation(self, filepath: str):
        """Exporta conversa para arquivo JSON"""
        try:
            history = self.get_conversation_history()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'conversation': history,
                    'export_timestamp': datetime.now().isoformat(),
                    'total_messages': len(history)
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Conversa exportada para: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao exportar conversa: {e}")

if __name__ == "__main__":
    # Teste básico
    try:
        from chatbot.config.config import OPENAI_API_KEY
    except ImportError:
        print("❌ Erro ao importar configurações do chatbot")
        exit(1)
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY não encontrada no arquivo .env")
        exit(1)
    
    # Inicializar sistema
    vector_store = VectorStoreANTAQ(OPENAI_API_KEY)
    rag_system = RAGSystemANTAQ(OPENAI_API_KEY, vector_store)
    
    # Teste de consulta
    test_query = "Como funciona o licenciamento de terminais portuários?"
    
    print(f"🔍 Testando consulta: {test_query}")
    result = rag_system.query(test_query)
    
    print(f"\n📝 RESPOSTA:")
    print(result['response'])
    
    print(f"\n📚 FONTES ({len(result['sources'])}):")
    for i, source in enumerate(result['sources'], 1):
        print(f"{i}. {source['titulo']} (Relevância: {source['relevance_score']:.3f})")