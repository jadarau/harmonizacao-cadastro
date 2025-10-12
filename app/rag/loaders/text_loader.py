"""Text file document loader."""
from __future__ import annotations
import hashlib
from datetime import datetime
from typing import BinaryIO, Dict, Any
from app.rag.loaders.base import DocumentLoader
from app.models.document import Document, DocumentMetadata, DocumentStatus


class TextLoader(DocumentLoader):
    """Loader for plain text files."""
    
    def __init__(self, encoding: str = "utf-8"):
        """Initialize with text encoding."""
        self.encoding = encoding
        self.supported_extensions = {".txt", ".md", ".rst", ".log"}
    
    async def load_document(
        self, 
        file_content: BinaryIO, 
        filename: str, 
        metadata: Dict[str, Any] = None
    ) -> Document:
        """Load document from text file."""
        # Read content
        content_bytes = file_content.read()
        
        try:
            content = content_bytes.decode(self.encoding)
        except UnicodeDecodeError:
            # Try common encodings
            for encoding in ["utf-8", "latin-1", "cp1252"]:
                try:
                    content = content_bytes.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"Unable to decode text file {filename}")
        
        # Generate document ID
        content_hash = hashlib.md5(content_bytes).hexdigest()
        doc_id = f"doc_{content_hash}"
        
        # Create metadata
        doc_metadata = DocumentMetadata(
            filename=filename,
            file_size=len(content_bytes),
            content_type="text/plain",
            uploaded_at=datetime.utcnow(),
            custom_metadata=metadata or {}
        )
        
        return Document(
            id=doc_id,
            content=content,
            metadata=doc_metadata,
            status=DocumentStatus.PENDING
        )
    
    def supports_file_type(self, filename: str) -> bool:
        """Check if this loader supports the given file type."""
        return any(filename.lower().endswith(ext) for ext in self.supported_extensions)