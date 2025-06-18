from abc import ABC, abstractmethod
from typing import List, Any

# This is our abstract interface
class IEmbeddingModel(ABC):
    """
    Abstract interface defining the contract for any embedding model
    within our system.
    """

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Converts a list of documents into a list of vectors."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Converts a single query text into a vector."""
        pass

    @abstractmethod
    def get_langchain_compatible_model(self) -> Any:
        """
        Returns the underlying embedding object that LangChain libraries
        (like langchain-chroma) expect to receive.
        This acts as an "adapter" to connect our internal system
        with external libraries.
        """
        pass