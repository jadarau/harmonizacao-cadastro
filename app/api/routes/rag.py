"""RAG API routes for document management and enhanced chat."""
from __future__ import annotations
import json
from typing import AsyncGenerator
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import StreamingResponse
from app.services.rag_service import get_rag_service, RAGService
from app.llm.rag_deps import get_rag_llm_client
from app.llm.rag_client import RAGLlmClient
from app.schemas.rag import (
    DocumentIndexRequest,
    DocumentSearchRequest,
    RAGChatRequest,
    RAGChatResponse
)

router = APIRouter(prefix="/v1/rag", tags=["rag"])


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    tags: str = Form(default=""),
    custom_metadata: str = Form(default="{}"),
    rag_service: RAGService = Depends(get_rag_service)
):
    """Upload a document to the RAG system.
    
    Args:
        file: File to upload
        tags: Comma-separated tags
        custom_metadata: JSON string with custom metadata
    """
    try:
        # Parse tags and metadata
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        
        try:
            metadata_dict = json.loads(custom_metadata) if custom_metadata else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in custom_metadata")
        
        # Upload document
        response = await rag_service.upload_document(
            file_content=file.file,
            filename=file.filename,
            tags=tag_list,
            custom_metadata=metadata_dict
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/{document_id}/index")
async def index_document(
    document_id: str,
    request: DocumentIndexRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Index a document for search.
    
    Args:
        document_id: ID of document to index
        request: Indexing parameters
    """
    try:
        response = await rag_service.index_document(
            document_id=request.document_id or document_id,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            force_reindex=request.force_reindex
        )
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/search")
async def search_documents(
    request: DocumentSearchRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Search for relevant documents.
    
    Args:
        request: Search parameters
    """
    try:
        response = await rag_service.search_documents(
            query=request.query,
            max_results=request.max_results,
            min_score=request.min_score,
            filter_metadata=request.filter_metadata
        )
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    rag_service: RAGService = Depends(get_rag_service)
):
    """List all documents with pagination.
    
    Args:
        page: Page number (1-based)
        page_size: Number of documents per page
    """
    try:
        response = await rag_service.list_documents(page=page, page_size=page_size)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Delete a document and its chunks.
    
    Args:
        document_id: ID of document to delete
    """
    try:
        response = await rag_service.delete_document(document_id)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Get document details.
    
    Args:
        document_id: ID of document to retrieve
    """
    try:
        document = await rag_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
            
        return {
            "id": document.id,
            "filename": document.metadata.filename,
            "status": document.status,
            "uploaded_at": document.metadata.uploaded_at.isoformat(),
            "processed_at": document.metadata.processed_at.isoformat() if document.metadata.processed_at else None,
            "file_size": document.metadata.file_size,
            "content_type": document.metadata.content_type,
            "tags": document.metadata.tags,
            "chunk_count": len(document.chunks),
            "content_preview": document.content[:500] + "..." if len(document.content) > 500 else document.content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=RAGChatResponse)
async def rag_chat(
    request: RAGChatRequest,
    rag_client: RAGLlmClient = Depends(get_rag_llm_client)
):
    """RAG-enhanced chat endpoint.
    
    Args:
        request: RAG chat request
    """
    try:
        response = await rag_client.rag_chat(request)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def rag_chat_stream(
    request: RAGChatRequest,
    rag_client: RAGLlmClient = Depends(get_rag_llm_client)
):
    """RAG-enhanced streaming chat endpoint.
    
    Args:
        request: RAG chat request (stream will be set to True)
    """
    try:
        request.stream = True
        
        async def event_source() -> AsyncGenerator[bytes, None]:
            try:
                async for chunk in rag_client.rag_chat_stream(request):
                    # Format as Server-Sent Events
                    yield f"data: {json.dumps({'content': chunk})}\\n\\n".encode("utf-8")
                
                # Send done signal
                yield f"data: {json.dumps({'done': True})}\\n\\n".encode("utf-8")
                
            except Exception as e:
                error_msg = json.dumps({"error": str(e)})
                yield f"data: {error_msg}\\n\\n".encode("utf-8")
        
        return StreamingResponse(event_source(), media_type="text/event-stream")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_rag_stats(
    rag_service: RAGService = Depends(get_rag_service)
):
    """Get RAG system statistics.
    
    Returns:
        System statistics and health info
    """
    try:
        stats = await rag_service.get_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload-and-index")
async def upload_and_index_document(
    file: UploadFile = File(...),
    tags: str = Form(default=""),
    custom_metadata: str = Form(default="{}"),
    chunk_size: int = Form(default=1000),
    chunk_overlap: int = Form(default=200),
    chunking_strategy: str = Form(default="recursive"),
    rag_service: RAGService = Depends(get_rag_service)
):
    """Upload and immediately index a document.
    
    Args:
        file: File to upload
        tags: Comma-separated tags
        custom_metadata: JSON string with custom metadata
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        chunking_strategy: Strategy for chunking
    """
    try:
        # Parse tags and metadata
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        
        try:
            metadata_dict = json.loads(custom_metadata) if custom_metadata else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in custom_metadata")
        
        # Upload document
        upload_response = await rag_service.upload_document(
            file_content=file.file,
            filename=file.filename,
            tags=tag_list,
            custom_metadata=metadata_dict
        )
        
        if upload_response.status.value != "pending":
            return {"upload": upload_response, "index": None, "error": "Upload failed"}
        
        # Index document
        index_response = await rag_service.index_document(
            document_id=upload_response.document_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunking_strategy=chunking_strategy
        )
        
        return {
            "upload": upload_response,
            "index": index_response,
            "success": index_response.status.value == "indexed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))