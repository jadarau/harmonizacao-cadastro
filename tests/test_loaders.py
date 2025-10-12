"""Tests for document loaders."""
import io
import pytest
from app.rag.loaders.text_loader import TextLoader
from app.rag.loaders.factory import LoaderFactory


class TestTextLoader:
    """Test text document loader."""
    
    @pytest.mark.asyncio
    async def test_load_text_document(self, sample_text_content):
        """Test loading a text document."""
        loader = TextLoader()
        file_content = io.BytesIO(sample_text_content.encode('utf-8'))
        
        document = await loader.load_document(
            file_content=file_content,
            filename="test.txt",
            metadata={"test": "metadata"}
        )
        
        assert document.content.strip() == sample_text_content.strip()
        assert document.metadata.filename == "test.txt"
        assert document.metadata.content_type == "text/plain"
        assert document.metadata.custom_metadata["test"] == "metadata"
    
    def test_supports_file_type(self):
        """Test file type support detection."""
        loader = TextLoader()
        
        assert loader.supports_file_type("document.txt")
        assert loader.supports_file_type("README.md")
        assert loader.supports_file_type("notes.log")
        assert not loader.supports_file_type("document.pdf")
        assert not loader.supports_file_type("image.jpg")
    
    @pytest.mark.asyncio
    async def test_load_document_with_encoding_issues(self):
        """Test handling documents with encoding issues."""
        loader = TextLoader()
        # Create content with special characters
        content = "Teste com acentuação: ção, ã, é"
        file_content = io.BytesIO(content.encode('utf-8'))
        
        document = await loader.load_document(
            file_content=file_content,
            filename="test_encoding.txt"
        )
        
        assert "acentuação" in document.content
        assert "ção" in document.content


class TestLoaderFactory:
    """Test loader factory."""
    
    def test_factory_get_text_loader(self):
        """Test factory returns text loader for text files."""
        factory = LoaderFactory()
        loader = factory.get_loader("document.txt")
        assert isinstance(loader, TextLoader)
    
    def test_factory_get_supported_extensions(self):
        """Test factory returns supported extensions."""
        factory = LoaderFactory()
        extensions = factory.get_supported_extensions()
        
        assert ".txt" in extensions
        assert ".md" in extensions
        assert ".pdf" in extensions
    
    def test_factory_unknown_file_type(self):
        """Test factory with unknown file type raises error."""
        factory = LoaderFactory()
        
        with pytest.raises(ValueError):
            factory.get_loader("unknown.xyz")
    
    @pytest.mark.asyncio
    async def test_factory_load_document(self, sample_text_content):
        """Test factory document loading."""
        factory = LoaderFactory()
        file_content = io.BytesIO(sample_text_content.encode('utf-8'))
        
        document = await factory.load_document(
            file_content=file_content,
            filename="test.txt"
        )
        
        assert document.content.strip() == sample_text_content.strip()
        assert document.metadata.filename == "test.txt"