from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Mapping, cast
from embeddings.interface import IEmbeddingModel
import chromadb
import warnings

# 1. Generic Interface for a Vector Repository
class IVectorRepository(ABC):
    """
    Abstract interface for a vector database.

    Allows interchangeable use of different vector DB backends (e.g., ChromaDB, FAISS),
    as long as they follow this contract and accept compatible input formats.
    """
    
    @abstractmethod
    def add(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Add documents with metadata. Each implementation must handle validation
        or sanitization of metadata to fit DB-specific requirements.
        """
        pass

    @abstractmethod
    def search(self, query: str, k: int, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Return the top-k most relevant results for a given query.
        Each result must be a metadata dictionary.
        """
        pass

# 2. ChromaDB Implementation
class ChromaVectorRepository(IVectorRepository):
    """
    ChromaDB-based implementation.

    - Only JSON-primitive metadata is supported (str, int, float, bool, None).
    - Metadata is automatically sanitized on insertion.
    """

    def __init__(self, db_path: str, collection_name: str, embedding_model: IEmbeddingModel):
        self.client = chromadb.PersistentClient(path=db_path)

        # Extract compatible LangChain embedding function
        langchain_embedding_function = getattr(embedding_model, '_model', None)
        if not langchain_embedding_function:
            raise TypeError("embedding_model must expose a valid LangChain-compatible '_model'.")

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=langchain_embedding_function
        )

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Union[str, int, float, bool, None]]:
        """
        Remove metadata keys with unsupported types. Chroma only accepts primitives.
        A warning is shown if any keys are dropped.
        """
        allowed_types = (str, int, float, bool, type(None))
        sanitized = {}
        removed_keys = []

        for k, v in metadata.items():
            if isinstance(v, allowed_types):
                sanitized[k] = v
            else:
                removed_keys.append(k)

        if removed_keys:
            warnings.warn(
                f"Removed metadata keys with unsupported types: {removed_keys}",
                UserWarning
            )

        return sanitized

    def add(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Sanitize and add data to ChromaDB.
        Casting ensures compatibility with Chroma's strict typing.
        """
        cleaned = [self._sanitize_metadata(md) for md in metadatas]
        typed_metadatas = cast(List[Mapping[str, Union[str, int, float, bool, None]]], cleaned)
        self.collection.add(documents=texts, metadatas=typed_metadatas, ids=ids)

    def search(self, query: str, k: int, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Run a similarity search and return metadata for top-k results.
        Converts ChromaDB mappings to plain dictionaries.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where=filter if filter else None
        )

        metadatas = results['metadatas'][0] if results and results['metadatas'] else []
        return [dict(md) for md in metadatas]
