"""
Implementation of the persistence layer for vector databases.
This module is aligned with LangChain's core concepts, using the 'Document'
object as the primary data transfer object to ensure maximum compatibility
and interchangeability between different vector store backends.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

# LangChain's high-level classes that we will now use in our interface
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Our custom embedding model interface
from embedding.interface import IEmbeddingModel


# 1. The generic interface, now updated to be LangChain-native.
class IVectorRepository(ABC):
    """
    Abstract interface for a vector database, designed to be LangChain-native.
    It operates on LangChain's 'Document' objects.
    """

    @abstractmethod
    def add(self, documents: List[Document], ids: List[str]):
        """
        Adds a list of LangChain Document objects to the vector store.
        """
        pass

    @abstractmethod
    def search(self, query: str, k: int, filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Returns the top-k most relevant LangChain Document objects for a given query.
        """
        pass


# 2. The ChromaDB implementation becomes even simpler.
class ChromaVectorRepository(IVectorRepository):
    """
    ChromaDB-based implementation that uses LangChain's high-level 'Chroma' class.
    It acts as a thin, compliant wrapper around the LangChain vector store.
    """

    def __init__(self, db_path: str, collection_name: str, embedding_model: IEmbeddingModel):
        langchain_embedding_function = embedding_model.get_langchain_compatible_model()

        self._vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=langchain_embedding_function,
            persist_directory=db_path
        )
        print(f"INFO: ChromaVectorRepository initialized for collection '{collection_name}'.")


    def add(self, documents: List[Document], ids: List[str]):
        """
        Adds documents directly using LangChain's vector store method.
        The data transformation logic is no longer needed here, it's done before.
        """
        self._vector_store.add_documents(documents=documents, ids=ids)

    def search(self, query: str, k: int, filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Performs a similarity search and returns the resulting Document objects directly.
        """
        return self._vector_store.similarity_search(
            query=query, k=k, filter=filter
        )