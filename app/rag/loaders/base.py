"""Document loader base classes and interfaces."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, Any
from app.models.document import Document, DocumentMetadata


class DocumentLoader(ABC):
    """Abstract base class for document loaders."""
    
    @abstractmethod
    async def load_document(
        self, 
        file_content: BinaryIO, 
        filename: str, 
        metadata: Dict[str, Any] = None
    ) -> Document:
        """Load document from file content."""
        pass
    
    @abstractmethod
    def supports_file_type(self, filename: str) -> bool:
        """Check if this loader supports the given file type."""
        pass