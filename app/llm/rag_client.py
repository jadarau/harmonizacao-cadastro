"""RAG-enhanced LLM client."""
from __future__ import annotations
import time
from typing import AsyncGenerator
from app.llm.client import LlmClient
from app.llm.groq import GroqLlmClient
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.rag import RAGChatRequest, RAGChatResponse


class RAGLlmClient:
    """LLM client enhanced with RAG capabilities."""
    
    def __init__(self, base_client: LlmClient):
        """Initialize with base LLM client.
        
        Args:
            base_client: Base LLM client (e.g., GroqLlmClient)
        """
        self.base_client = base_client
        self._rag_service = None
    
    @property
    def rag_service(self):
        """Get RAG service instance (lazy loading)."""
        if self._rag_service is None:
            from app.services.rag_service import get_rag_service
            self._rag_service = get_rag_service()
        return self._rag_service
    
    async def chat(self, req: ChatRequest) -> ChatResponse:
        """Standard chat without RAG."""
        return await self.base_client.chat(req)
    
    async def chat_stream(self, req: ChatRequest) -> AsyncGenerator[str, None]:
        """Standard streaming chat without RAG."""
        async for chunk in self.base_client.chat_stream(req):
            yield chunk
    
    async def rag_chat(self, req: RAGChatRequest) -> RAGChatResponse:
        """RAG-enhanced chat.
        
        Args:
            req: RAG chat request
            
        Returns:
            RAG chat response with sources
        """
        start_time = time.time()
        
        # If RAG is disabled, use normal chat
        if not req.use_rag:
            chat_req = ChatRequest(
                messages=[{"role": "user", "content": req.query}],
                model=req.model,
                temperature=req.temperature,
                max_tokens=req.max_tokens,
                stream=False
            )
            chat_response = await self.base_client.chat(chat_req)
            
            return RAGChatResponse(
                response=chat_response.choices[0].message.content,
                sources=[],
                context_used=False,
                model_used=chat_response.model,
                processing_time_seconds=time.time() - start_time
            )
        
        # Retrieve relevant context
        search_response = await self.rag_service.search_documents(
            query=req.query,
            max_results=req.max_context_chunks,
            min_score=req.min_relevance_score
        )
        
        sources = search_response.results
        context_used = len(sources) > 0
        
        # Build enhanced prompt with context
        if context_used:
            context_text = "\\n\\n".join([
                f"[Fonte {i+1}] {result.content}" 
                for i, result in enumerate(sources)
            ])
            
            enhanced_prompt = f"""Você é um assistente especializado que responde perguntas baseado em documentos fornecidos.

CONTEXTO DOS DOCUMENTOS:
{context_text}

PERGUNTA DO USUÁRIO: {req.query}

INSTRUÇÕES:
1. Responda à pergunta usando APENAS as informações dos documentos fornecidos
2. Se a resposta não estiver nos documentos, diga que não tem informação suficiente
3. Cite as fontes quando apropriado (ex: "Segundo a Fonte 1...")
4. Seja preciso e objetivo

RESPOSTA:"""
        else:
            enhanced_prompt = f"""Não foi possível encontrar informações relevantes nos documentos para responder à pergunta: {req.query}

Por favor, reformule sua pergunta ou faça upload de documentos relacionados ao tópico desejado."""
        
        # Make LLM request
        chat_req = ChatRequest(
            messages=[{"role": "user", "content": enhanced_prompt}],
            model=req.model,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            stream=False
        )
        
        chat_response = await self.base_client.chat(chat_req)
        
        return RAGChatResponse(
            response=chat_response.choices[0].message.content,
            sources=sources,
            context_used=context_used,
            model_used=chat_response.model,
            processing_time_seconds=time.time() - start_time
        )
    
    async def rag_chat_stream(self, req: RAGChatRequest) -> AsyncGenerator[str, None]:
        """RAG-enhanced streaming chat.
        
        Args:
            req: RAG chat request
            
        Yields:
            Streaming response chunks
        """
        # For streaming, we need to handle context retrieval first
        # This is a simplified implementation
        
        if not req.use_rag:
            chat_req = ChatRequest(
                messages=[{"role": "user", "content": req.query}],
                model=req.model,
                temperature=req.temperature,
                max_tokens=req.max_tokens,
                stream=True
            )
            async for chunk in self.base_client.chat_stream(chat_req):
                yield chunk
            return
        
        # Retrieve context (same as in rag_chat)
        search_response = await self.rag_service.search_documents(
            query=req.query,
            max_results=req.max_context_chunks,
            min_score=req.min_relevance_score
        )
        
        sources = search_response.results
        context_used = len(sources) > 0
        
        # Build enhanced prompt
        if context_used:
            context_text = "\\n\\n".join([
                f"[Fonte {i+1}] {result.content}" 
                for i, result in enumerate(sources)
            ])
            
            enhanced_prompt = f"""Você é um assistente especializado que responde perguntas baseado em documentos fornecidos.

CONTEXTO DOS DOCUMENTOS:
{context_text}

PERGUNTA DO USUÁRIO: {req.query}

INSTRUÇÕES:
1. Responda à pergunta usando APENAS as informações dos documentos fornecidos
2. Se a resposta não estiver nos documentos, diga que não tem informação suficiente
3. Cite as fontes quando apropriado (ex: "Segundo a Fonte 1...")
4. Seja preciso e objetivo

RESPOSTA:"""
        else:
            enhanced_prompt = f"""Não foi possível encontrar informações relevantes nos documentos para responder à pergunta: {req.query}

Por favor, reformule sua pergunta ou faça upload de documentos relacionados ao tópico desejado."""
        
        # Stream LLM response
        chat_req = ChatRequest(
            messages=[{"role": "user", "content": enhanced_prompt}],
            model=req.model,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            stream=True
        )
        
        async for chunk in self.base_client.chat_stream(chat_req):
            yield chunk