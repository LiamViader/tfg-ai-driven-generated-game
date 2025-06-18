"""
Implementation of the persistence layer for vector databases.

This module defines a generic interface (IVectorRepository) and provides
a concrete implementation for ChromaDB (ChromaVectorRepository).

The implementation uses the high-level `langchain_chroma.Chroma` wrapper class
to align with the LangChain ecosystem and simplify interactions,
while remaining behind our own interface to ensure system
scalability and interchangeability.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import warnings

# Import the high-level LangChain classes we will use
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Import our custom embedding interface
from embeddings.interface import IEmbeddingModel


# 1. Our generic interface remains unchanged. This contract is solid.
class IVectorRepository(ABC):
    """
    Abstract interface for a vector data repository.
    Ensures that any vector DB backend can be swapped in.
    """

    @abstractmethod
    def add(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Adds documents with their metadata to the vector DB."""
        pass

    @abstractmethod
    def search(self, query: str, k: int, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Searches for the k most relevant documents and returns their metadata."""
        pass


# 2. The Chroma implementation, now using LangChain's tools.
class ChromaVectorRepository(IVectorRepository):
    """
    Implementation of IVectorRepository that uses LangChain's 'Chroma' class as its backend.
    """
    
    # The initializer now creates an instance of 'langchain_chroma.Chroma'.
    def __init__(self, db_path: str, collection_name: str, embedding_model: IEmbeddingModel):
        # Get the LangChain-compatible model via the explicit interface method.
        langchain_embedding_function = embedding_model.get_langchain_compatible_model()

        # Create the instance of the LangChain vector store. This will be our internal tool.
        self._vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=langchain_embedding_function,
            persist_directory=db_path
        )
        print(f"INFO: ChromaVectorRepository initialized and connected to collection '{collection_name}'.")

    # The sanitization function remains as good data hygiene.
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for k, v in metadata.items():
            if isinstance(v, (str, int, float, bool, type(None))):
                sanitized[k] = v
            else:
                # For other types, convert to string to prevent errors.
                sanitized[k] = str(v)
                warnings.warn(
                    f"Metadata key '{k}' with non-primitive value converted to string.", UserWarning
                )
        return sanitized

    # The 'add' method is now simpler and more idiomatic within the LangChain ecosystem.
    def add(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Adds documents to the Chroma vector store.
        Converts the input data into LangChain 'Document' objects.
        """
        # LangChain works with its own 'Document' object.
        # We create it from the data we receive.
        docs = [
            Document(page_content=text, metadata=self._sanitize_metadata(metadata))
            for text, metadata in zip(texts, metadatas)
        ]

        # We use the '.add_documents()' method from LangChain's Chroma class.
        self._vector_store.add_documents(documents=docs, ids=ids)

    # The 'search' method is also simplified.
    def search(self, query: str, k: int, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Performs a similarity search using LangChain's method.
        Returns a list of metadata from the found documents.
        """
        # We use the '.similarity_search()' method from LangChain's Chroma class.
        # This method returns a list of 'Document' objects.
        result_docs = self._vector_store.similarity_search(
            query=query, k=k, filter=filter
        )

        # Our interface dictates that we must return a list of dictionaries (the metadata),
        # so we extract the 'metadata' property from each 'Document' object.
        return [doc.metadata for doc in result_docs]
