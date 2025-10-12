"""Text chunking strategies for document processing."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.models.document import DocumentChunk


class ChunkingStrategy(ABC):
    """Abstract base class for text chunking strategies."""
    
    @abstractmethod
    def chunk_text(
        self, 
        text: str, 
        document_id: str, 
        metadata: Dict[str, Any] = None
    ) -> List[DocumentChunk]:
        """Split text into chunks."""
        pass


class FixedSizeChunking(ChunkingStrategy):
    """Fixed size chunking with overlap."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize with chunk parameters.
        
        Args:
            chunk_size: Maximum number of characters per chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def chunk_text(
        self, 
        text: str, 
        document_id: str, 
        metadata: Dict[str, Any] = None
    ) -> List[DocumentChunk]:
        """Split text into fixed-size chunks with overlap."""
        if not text.strip():
            return []
            
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at word boundary if possible
            if end < len(text):
                # Look back for a space or punctuation
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in ' \n\t.!?;':
                        end = i + 1
                        break
            
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunk = DocumentChunk(
                    id=f"{document_id}_chunk_{chunk_index}",
                    document_id=document_id,
                    content=chunk_content,
                    chunk_index=chunk_index,
                    start_char=start,
                    end_char=end,
                    metadata=metadata or {}
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # Move start position with overlap
            start = max(start + 1, end - self.chunk_overlap)
            
        return chunks


class SentenceChunking(ChunkingStrategy):
    """Sentence-based chunking strategy."""
    
    def __init__(self, max_chunk_size: int = 1000, sentence_overlap: int = 1):
        """Initialize with chunk parameters.
        
        Args:
            max_chunk_size: Maximum number of characters per chunk
            sentence_overlap: Number of sentences to overlap between chunks
        """
        self.max_chunk_size = max_chunk_size
        self.sentence_overlap = sentence_overlap
        
    def _split_into_sentences(self, text: str) -> List[str]:
        """Simple sentence splitting."""
        import re
        # Split on sentence-ending punctuation followed by whitespace
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def chunk_text(
        self, 
        text: str, 
        document_id: str, 
        metadata: Dict[str, Any] = None
    ) -> List[DocumentChunk]:
        """Split text into sentence-based chunks."""
        if not text.strip():
            return []
            
        sentences = self._split_into_sentences(text)
        if not sentences:
            return []
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for i, sentence in enumerate(sentences):
            sentence_size = len(sentence)
            
            # If adding this sentence would exceed max size and we have content
            if current_size + sentence_size > self.max_chunk_size and current_chunk:
                # Create chunk from current sentences
                chunk_content = ' '.join(current_chunk)
                start_char = text.find(current_chunk[0])
                end_char = start_char + len(chunk_content)
                
                chunk = DocumentChunk(
                    id=f"{document_id}_chunk_{chunk_index}",
                    document_id=document_id,
                    content=chunk_content,
                    chunk_index=chunk_index,
                    start_char=start_char,
                    end_char=end_char,
                    metadata=metadata or {}
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk) - self.sentence_overlap)
                current_chunk = current_chunk[overlap_start:] + [sentence]
                current_size = sum(len(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        # Handle remaining sentences
        if current_chunk:
            chunk_content = ' '.join(current_chunk)
            start_char = text.find(current_chunk[0])
            end_char = start_char + len(chunk_content)
            
            chunk = DocumentChunk(
                id=f"{document_id}_chunk_{chunk_index}",
                document_id=document_id,
                content=chunk_content,
                chunk_index=chunk_index,
                start_char=start_char,
                end_char=end_char,
                metadata=metadata or {}
            )
            chunks.append(chunk)
        
        return chunks


class RecursiveChunking(ChunkingStrategy):
    """Recursive text chunking that tries to maintain semantic coherence."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize with chunk parameters."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]
        
    def chunk_text(
        self, 
        text: str, 
        document_id: str, 
        metadata: Dict[str, Any] = None
    ) -> List[DocumentChunk]:
        """Split text recursively maintaining semantic boundaries."""
        if not text.strip():
            return []
            
        chunks = self._recursive_split(text, self.separators)
        
        # Convert to DocumentChunk objects
        document_chunks = []
        start_pos = 0
        
        for i, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                id=f"{document_id}_chunk_{i}",
                document_id=document_id,
                content=chunk_text,
                chunk_index=i,
                start_char=start_pos,
                end_char=start_pos + len(chunk_text),
                metadata=metadata or {}
            )
            document_chunks.append(chunk)
            start_pos += len(chunk_text)
            
        return document_chunks
    
    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using separators."""
        if not separators:
            return [text] if text else []
            
        separator = separators[0]
        remaining_separators = separators[1:]
        
        if separator == "":
            # Last resort: split by character
            return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]
        
        splits = text.split(separator)
        chunks = []
        current_chunk = ""
        
        for split in splits:
            if len(current_chunk) + len(split) + len(separator) <= self.chunk_size:
                current_chunk += split + separator if current_chunk else split
            else:
                if current_chunk:
                    chunks.append(current_chunk.rstrip(separator))
                
                if len(split) > self.chunk_size:
                    # Recursively split large pieces
                    sub_chunks = self._recursive_split(split, remaining_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = split
        
        if current_chunk:
            chunks.append(current_chunk.rstrip(separator))
            
        return chunks


class ChunkingFactory:
    """Factory for creating chunking strategies."""
    
    @staticmethod
    def create_strategy(
        strategy_type: str = "fixed_size",
        **kwargs
    ) -> ChunkingStrategy:
        """Create a chunking strategy.
        
        Args:
            strategy_type: Type of strategy ("fixed_size", "sentence", "recursive")
            **kwargs: Additional arguments for the strategy
        """
        if strategy_type == "fixed_size":
            return FixedSizeChunking(
                chunk_size=kwargs.get("chunk_size", 1000),
                chunk_overlap=kwargs.get("chunk_overlap", 200)
            )
        elif strategy_type == "sentence":
            return SentenceChunking(
                max_chunk_size=kwargs.get("max_chunk_size", 1000),
                sentence_overlap=kwargs.get("sentence_overlap", 1)
            )
        elif strategy_type == "recursive":
            return RecursiveChunking(
                chunk_size=kwargs.get("chunk_size", 1000),
                chunk_overlap=kwargs.get("chunk_overlap", 200)
            )
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy_type}")