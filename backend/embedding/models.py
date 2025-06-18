from typing import List, Any
from pydantic import SecretStr
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from .interface import IEmbeddingModel

# Implementació per a models locals de Hugging Face
class LocalHuggingFaceEmbedder(IEmbeddingModel):
    def __init__(self, model_name: str):
        self._model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'}
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._model.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._model.embed_query(text)
    
    def get_langchain_compatible_model(self) -> Any:
        return self._model

# Implementació per a l'API d'OpenAI
class OpenAIEmbedder(IEmbeddingModel):
    def __init__(self, model_name: str, api_key: SecretStr):
        if not api_key:
            raise ValueError("OpenAi Api key not configured.")
        self._model = OpenAIEmbeddings(model=model_name, api_key=api_key)
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._model.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._model.embed_query(text)
    
    def get_langchain_compatible_model(self) -> Any:
        return self._model