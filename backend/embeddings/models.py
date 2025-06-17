from typing import List
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
        print(f"Model d'embedding local '{model_name}' carregat.")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._model.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._model.embed_query(text)

# Implementació per a l'API d'OpenAI
class OpenAIEmbedder(IEmbeddingModel):
    def __init__(self, model_name: str, api_key: SecretStr):
        if not api_key:
            raise ValueError("La clau API d'OpenAI no està configurada.")
        self._model = OpenAIEmbeddings(model=model_name, api_key=api_key)
        print(f"Model d'embedding d'OpenAI '{model_name}' configurat.")
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._model.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._model.embed_query(text)