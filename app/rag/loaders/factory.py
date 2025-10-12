"""Document loader factory and management."""
from __future__ import annotations
from typing import List, BinaryIO, Dict, Any
from app.rag.loaders.base import DocumentLoader
from app.rag.loaders.text_loader import TextLoader
from app.rag.loaders.pdf_loader import PDFLoader
from app.models.document import Document


class LoaderFactory:
    """Factory for creating document loaders."""
    
    def __init__(self):
        """Initialize with default loaders."""
        self.loaders: List[DocumentLoader] = [
            TextLoader(),
            PDFLoader(),
        ]
    
    def add_loader(self, loader: DocumentLoader):
        """Add a custom loader."""
        self.loaders.append(loader)
    
    def get_loader(self, filename: str) -> DocumentLoader:
        """Get the appropriate loader for a file."""
        for loader in self.loaders:
            if loader.supports_file_type(filename):
                return loader
        raise ValueError(f"No loader found for file type: {filename}")
    
    async def load_document(
        self, 
        file_content: BinaryIO, 
        filename: str, 
        metadata: Dict[str, Any] = None
    ) -> Document:
        """Load document using the appropriate loader."""
        loader = self.get_loader(filename)
        return await loader.load_document(file_content, filename, metadata)
    
    def get_supported_extensions(self) -> List[str]:
        """Get all supported file extensions."""
        extensions = set()
        for loader in self.loaders:
            if hasattr(loader, "supported_extensions"):
                extensions.update(loader.supported_extensions)
        return sorted(list(extensions))


# Global loader factory instance
_loader_factory = LoaderFactory()


def get_loader_factory() -> LoaderFactory:
    """Get the global loader factory."""
    return _loader_factory