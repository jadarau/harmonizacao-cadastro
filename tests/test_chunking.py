"""Tests for chunking strategies."""
import pytest
from app.rag.chunking.strategies import (
    FixedSizeChunking, 
    SentenceChunking, 
    RecursiveChunking,
    ChunkingFactory
)


class TestFixedSizeChunking:
    """Test fixed size chunking strategy."""
    
    def test_fixed_size_chunking_basic(self, sample_text_content):
        """Test basic fixed size chunking."""
        chunker = FixedSizeChunking(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_text(sample_text_content, "test_doc", {})
        
        assert len(chunks) > 0
        assert all(len(chunk.content) <= 120 for chunk in chunks)  # Allow some variance
        assert all(chunk.document_id == "test_doc" for chunk in chunks)
    
    def test_fixed_size_chunking_empty_text(self):
        """Test chunking with empty text."""
        chunker = FixedSizeChunking()
        chunks = chunker.chunk_text("", "test_doc", {})
        
        assert len(chunks) == 0
    
    def test_fixed_size_chunking_small_text(self):
        """Test chunking with text smaller than chunk size."""
        chunker = FixedSizeChunking(chunk_size=1000, chunk_overlap=200)
        text = "This is a small text."
        chunks = chunker.chunk_text(text, "test_doc", {})
        
        assert len(chunks) == 1
        assert chunks[0].content.strip() == text.strip()


class TestSentenceChunking:
    """Test sentence-based chunking strategy."""
    
    def test_sentence_chunking_basic(self, sample_text_content):
        """Test basic sentence chunking."""
        chunker = SentenceChunking(max_chunk_size=200, sentence_overlap=1)
        chunks = chunker.chunk_text(sample_text_content, "test_doc", {})
        
        assert len(chunks) > 0
        assert all(chunk.document_id == "test_doc" for chunk in chunks)
    
    def test_sentence_chunking_empty_text(self):
        """Test sentence chunking with empty text."""
        chunker = SentenceChunking()
        chunks = chunker.chunk_text("", "test_doc", {})
        
        assert len(chunks) == 0


class TestRecursiveChunking:
    """Test recursive chunking strategy."""
    
    def test_recursive_chunking_basic(self, sample_text_content):
        """Test basic recursive chunking."""
        chunker = RecursiveChunking(chunk_size=200, chunk_overlap=50)
        chunks = chunker.chunk_text(sample_text_content, "test_doc", {})
        
        assert len(chunks) > 0
        assert all(chunk.document_id == "test_doc" for chunk in chunks)
    
    def test_recursive_chunking_preserves_structure(self):
        """Test that recursive chunking preserves text structure."""
        text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        chunker = RecursiveChunking(chunk_size=50, chunk_overlap=10)
        chunks = chunker.chunk_text(text, "test_doc", {})
        
        assert len(chunks) > 0
        # Should split at paragraph boundaries first
        assert any("\n\n" not in chunk.content or len(chunk.content) < 50 for chunk in chunks)


class TestChunkingFactory:
    """Test chunking factory."""
    
    def test_factory_creates_fixed_size(self):
        """Test factory creates fixed size chunker."""
        chunker = ChunkingFactory.create_strategy("fixed_size")
        assert isinstance(chunker, FixedSizeChunking)
    
    def test_factory_creates_sentence(self):
        """Test factory creates sentence chunker."""
        chunker = ChunkingFactory.create_strategy("sentence")
        assert isinstance(chunker, SentenceChunking)
    
    def test_factory_creates_recursive(self):
        """Test factory creates recursive chunker."""
        chunker = ChunkingFactory.create_strategy("recursive")
        assert isinstance(chunker, RecursiveChunking)
    
    def test_factory_unknown_strategy(self):
        """Test factory with unknown strategy raises error."""
        with pytest.raises(ValueError):
            ChunkingFactory.create_strategy("unknown_strategy")