"""PDF document loader."""
from __future__ import annotations
import hashlib
from datetime import datetime
from typing import BinaryIO, Dict, Any
from app.rag.loaders.base import DocumentLoader
from app.models.document import Document, DocumentMetadata, DocumentStatus


class PDFLoader(DocumentLoader):
    """Loader for PDF files."""
    
    def __init__(self):
        """Initialize PDF loader."""
        self.supported_extensions = {".pdf"}
    
    async def load_document(
        self, 
        file_content: BinaryIO, 
        filename: str, 
        metadata: Dict[str, Any] = None
    ) -> Document:
        """Load document from PDF file."""
        content_bytes = file_content.read()
        
        try:
            # Try PyPDF2 first
            content = await self._extract_with_pypdf2(content_bytes)
        except Exception:
            try:
                # Fallback to pdfplumber
                content = await self._extract_with_pdfplumber(content_bytes)
            except Exception as e:
                raise ValueError(f"Unable to extract text from PDF {filename}: {str(e)}")
        
        # Generate document ID
        content_hash = hashlib.md5(content_bytes).hexdigest()
        doc_id = f"doc_{content_hash}"
        
        # Create metadata
        doc_metadata = DocumentMetadata(
            filename=filename,
            file_size=len(content_bytes),
            content_type="application/pdf",
            uploaded_at=datetime.utcnow(),
            custom_metadata=metadata or {}
        )
        
        return Document(
            id=doc_id,
            content=content,
            metadata=doc_metadata,
            status=DocumentStatus.PENDING
        )
    
    async def _extract_with_pypdf2(self, content_bytes: bytes) -> str:
        """Extract text using PyPDF2."""
        import io
        from PyPDF2 import PdfReader
        
        pdf_file = io.BytesIO(content_bytes)
        reader = PdfReader(pdf_file)
        
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text.strip():
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    async def _extract_with_pdfplumber(self, content_bytes: bytes) -> str:
        """Extract text using pdfplumber."""
        import io
        import pdfplumber
        
        pdf_file = io.BytesIO(content_bytes)
        text_parts = []
        
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and text.strip():
                    text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    def supports_file_type(self, filename: str) -> bool:
        """Check if this loader supports the given file type."""
        return filename.lower().endswith(".pdf")