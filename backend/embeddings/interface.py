from abc import ABC, abstractmethod
from typing import List

# This is our abstract interface
class IEmbeddingModel(ABC):
    """Defines the contract for any embedding model."""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Converts a list of documents into a list of vectors."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Converts a single query text into a vector."""
        pass