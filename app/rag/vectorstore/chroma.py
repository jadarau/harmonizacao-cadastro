"""Chroma vector store implementation."""
from __future__ import annotations
import asyncio
from typing import List, Dict, Any, Optional
from app.rag.vectorstore.base import VectorStore
from app.models.document import DocumentChunk, SearchResult


class ChromaVectorStore(VectorStore):
    """Chroma vector store implementation."""
    
    def __init__(
        self, 
        collection_name: str = "harmonizacao_docs",
        persist_directory: str = "./data/vectorstore/chroma"
    ):
        """Initialize Chroma vector store.
        
        Args:
            collection_name: Name of the Chroma collection
            persist_directory: Directory to persist the vector store
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._client = None
        self._collection = None
    
    async def _get_client(self):
        """Get or create Chroma client."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings
            
            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        return self._client
    
    async def _get_collection(self):
        """Get or create Chroma collection."""
        if self._collection is None:
            client = await self._get_client()
            
            # Get or create collection
            try:
                self._collection = client.get_collection(self.collection_name)
            except Exception:
                self._collection = client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
        return self._collection
    
    async def add_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to the vector store."""
        if not chunks:
            return True
            
        collection = await self._get_collection()
        
        # Prepare data for Chroma
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for chunk in chunks:
            if chunk.embedding is None:
                raise ValueError(f"Chunk {chunk.id} has no embedding")
                
            ids.append(chunk.id)
            embeddings.append(chunk.embedding)
            documents.append(chunk.content)
            
            # Prepare metadata
            metadata = {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
                **chunk.metadata
            }
            # Ensure all metadata values are JSON serializable
            metadata = {k: str(v) if not isinstance(v, (str, int, float, bool)) else v 
                       for k, v in metadata.items()}
            metadatas.append(metadata)
        
        # Add to collection (run in thread pool)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
        )
        
        return True
    
    async def search(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        filter_metadata: Dict[str, Any] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """Search for similar chunks."""
        collection = await self._get_collection()
        
        # Prepare where clause for filtering
        where_clause = None
        if filter_metadata:
            where_clause = {k: {"$eq": v} for k, v in filter_metadata.items()}
        
        # Perform search (run in thread pool)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause,
                include=["metadatas", "documents", "distances"]
            )
        )
        
        # Convert results to SearchResult objects
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                # Convert distance to similarity score (assuming cosine distance)
                score = 1.0 - distance
                
                if score >= min_score:
                    metadata = results["metadatas"][0][i]
                    content = results["documents"][0][i]
                    
                    search_result = SearchResult(
                        chunk_id=chunk_id,
                        document_id=metadata.get("document_id", ""),
                        content=content,
                        score=score,
                        metadata=metadata
                    )
                    search_results.append(search_result)
        
        return search_results
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a document."""
        collection = await self._get_collection()
        
        # Delete chunks with matching document_id
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: collection.delete(
                where={"document_id": {"$eq": document_id}}
            )
        )
        
        return True
    
    async def get_chunk(self, chunk_id: str) -> Optional[DocumentChunk]:
        """Get a specific chunk by ID."""
        collection = await self._get_collection()
        
        # Get chunk by ID
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: collection.get(
                ids=[chunk_id],
                include=["metadatas", "documents", "embeddings"]
            )
        )
        
        if result["ids"] and result["ids"][0]:
            metadata = result["metadatas"][0]
            content = result["documents"][0]
            embedding = result["embeddings"][0] if result["embeddings"] else None
            
            return DocumentChunk(
                id=chunk_id,
                document_id=metadata.get("document_id", ""),
                content=content,
                chunk_index=int(metadata.get("chunk_index", 0)),
                start_char=int(metadata.get("start_char", 0)),
                end_char=int(metadata.get("end_char", 0)),
                embedding=embedding,
                metadata=metadata
            )
        
        return None
    
    async def list_documents(self) -> List[str]:
        """List all document IDs in the store."""
        collection = await self._get_collection()
        
        # Get all unique document IDs
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: collection.get(include=["metadatas"])
        )
        
        document_ids = set()
        if result["metadatas"]:
            for metadata in result["metadatas"]:
                doc_id = metadata.get("document_id")
                if doc_id:
                    document_ids.add(doc_id)
        
        return list(document_ids)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        collection = await self._get_collection()
        
        # Get collection info
        loop = asyncio.get_event_loop()
        count = await loop.run_in_executor(None, lambda: collection.count())
        
        documents = await self.list_documents()
        
        return {
            "total_chunks": count,
            "total_documents": len(documents),
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory
        }