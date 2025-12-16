"""RAG schemas for API requests and responses."""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from app.models.document import DocumentStatus, SearchResult


class DocumentUploadRequest(BaseModel):
    """Request schema for document upload."""
    filename: str
    content_type: str
    tags: List[str] = Field(default_factory=list)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentUploadResponse(BaseModel):
    """Response schema for document upload."""
    document_id: str
    filename: str
    status: DocumentStatus
    message: str


class DocumentIndexRequest(BaseModel):
    """Request schema for document indexing."""
    document_id: str
    chunk_size: int = Field(default=1000, ge=100, le=4000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    force_reindex: bool = False


class DocumentIndexResponse(BaseModel):
    """Response schema for document indexing."""
    document_id: str
    chunks_created: int
    status: DocumentStatus
    processing_time_seconds: float


class DocumentSearchRequest(BaseModel):
    """Request schema for document search."""
    query: str
    max_results: int = Field(default=5, ge=1, le=20)
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)
    filter_metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentSearchResponse(BaseModel):
    """Response schema for document search."""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_seconds: float




class DocumentListResponse(BaseModel):
    """Response schema for document listing."""
    documents: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int


class DocumentDeleteResponse(BaseModel):
    """Response schema for document deletion."""
    document_id: str
    deleted: bool
    message: str


# ----------------------------
# RAG Chat Schemas
# ----------------------------

class RAGChatRequest(BaseModel):
    """Request schema for RAG-enhanced chat."""
    query: str
    # LLM params (fallback to service defaults if None)
    model: Optional[str] = None
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1)
    # RAG controls
    use_rag: bool = True
    max_context_chunks: int = Field(5, ge=1, le=50)
    min_relevance_score: float = Field(0.0, ge=0.0, le=1.0)
    # Streaming toggle (endpoint pode sobrescrever)
    stream: Optional[bool] = False

    @validator("query")
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("query must not be empty")
        return v.strip()


class RAGChatResponse(BaseModel):
    """Response schema for RAG-enhanced chat with sources."""
    response: str
    sources: List[SearchResult] = Field(default_factory=list)
    context_used: bool = False
    model_used: Optional[str] = None
    processing_time_seconds: float = 0.0