"""Document models for RAG system."""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    """Document metadata."""
    filename: str
    file_size: int
    content_type: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    source_path: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class Document(BaseModel):
    """Document model."""
    id: str
    content: str
    metadata: DocumentMetadata
    status: DocumentStatus = DocumentStatus.PENDING
    chunks: List["DocumentChunk"] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": {
                "filename": self.metadata.filename,
                "file_size": self.metadata.file_size,
                "content_type": self.metadata.content_type,
                "uploaded_at": self.metadata.uploaded_at.isoformat(),
                "processed_at": self.metadata.processed_at.isoformat() if self.metadata.processed_at else None,
                "source_path": self.metadata.source_path,
                "tags": self.metadata.tags,
                "custom_metadata": self.metadata.custom_metadata
            },
            "status": self.status.value,
            "chunks": [
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "chunk_index": chunk.chunk_index,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "token_count": chunk.token_count,
                    "metadata": chunk.metadata
                }
                for chunk in self.chunks
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create document from dictionary."""
        metadata_data = data["metadata"]
        
        # Parse dates
        uploaded_at = datetime.fromisoformat(metadata_data["uploaded_at"].replace('Z', '+00:00'))
        processed_at = None
        if metadata_data.get("processed_at"):
            processed_at = datetime.fromisoformat(metadata_data["processed_at"].replace('Z', '+00:00'))
        
        # Create metadata
        metadata = DocumentMetadata(
            filename=metadata_data["filename"],
            file_size=metadata_data["file_size"],
            content_type=metadata_data["content_type"],
            uploaded_at=uploaded_at,
            processed_at=processed_at,
            source_path=metadata_data.get("source_path"),
            tags=metadata_data.get("tags", []),
            custom_metadata=metadata_data.get("custom_metadata", {})
        )
        
        # Create chunks
        chunks = []
        for chunk_data in data.get("chunks", []):
            chunk = DocumentChunk(
                id=chunk_data["id"],
                document_id=chunk_data["document_id"],
                content=chunk_data["content"],
                chunk_index=chunk_data["chunk_index"],
                start_char=chunk_data["start_char"],
                end_char=chunk_data["end_char"],
                token_count=chunk_data.get("token_count"),
                metadata=chunk_data.get("metadata", {})
            )
            chunks.append(chunk)
        
        return cls(
            id=data["id"],
            content=data.get("content", ""),
            metadata=metadata,
            status=DocumentStatus(data["status"]),
            chunks=chunks
        )


class DocumentChunk(BaseModel):
    """Document chunk model for text splitting."""
    id: str
    document_id: str
    content: str
    chunk_index: int
    start_char: int
    end_char: int
    token_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
    class Config:
        from_attributes = True


class QueryEmbedding(BaseModel):
    """Query embedding model."""
    query: str
    embedding: List[float]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SearchResult(BaseModel):
    """Search result from vector store."""
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Forward reference resolution
Document.model_rebuild()