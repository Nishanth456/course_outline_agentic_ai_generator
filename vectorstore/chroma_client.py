"""ChromaDB vector store connector (PHASE 3+)."""

from typing import List, Dict, Any, Optional


class ChromaDBClient:
    """
    Interface to ChromaDB vector database.
    
    Responsibilities:
    - Connect to ChromaDB instance
    - Manage collections (curricula)
    - Insert/delete documents with embeddings
    - Search with similarity scoring
    - Support metadata filtering
    """
    
    def __init__(self, path: str = "./chroma_data"):
        """Initialize ChromaDB client."""
        raise NotImplementedError("PHASE 3")
    
    def get_or_create_collection(self, collection_name: str) -> Any:
        """Get or create a collection."""
        raise NotImplementedError("PHASE 3")
    
    def add_documents(
        self, 
        collection_name: str, 
        documents: List[str], 
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to collection (with embeddings auto-generated)."""
        raise NotImplementedError("PHASE 3")
    
    def search(
        self, 
        collection_name: str, 
        query: str, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search collection with optional metadata filters."""
        raise NotImplementedError("PHASE 3")
    
    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection."""
        raise NotImplementedError("PHASE 3")


class EmbeddingProvider:
    """Wrapper for embedding models (PHASE 3)."""
    
    @staticmethod
    def embed_text(text: str) -> List[float]:
        """Generate embedding for text."""
        raise NotImplementedError("PHASE 3")
    
    @staticmethod
    def embed_batch(texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts."""
        raise NotImplementedError("PHASE 3")
