"""
Factory for creating embedding model instances.

This module decouples application logic from the concrete implementation
of embedding models. It uses a model ID to look up configuration
in a centralized catalog and returns the appropriate model instance.
"""

from typing import Optional
from pydantic import SecretStr

# Import interface and implementations
from .interface import IEmbeddingModel
from .models import LocalHuggingFaceEmbedder, OpenAIEmbedder

# Import the central catalog
from .catalog import EMBEDDING_MODEL_CATALOG


def create_embedding_model(model_id: str, api_key: Optional[SecretStr] = None) -> IEmbeddingModel:
    """
    Creates and returns an instance of an embedding model based on a catalog ID.

    Args:
        model_id: The unique identifier of the model as defined in EMBEDDING_MODEL_CATALOG.
        api_key: OpenAI API key, required only if using a model from that provider.

    Returns:
        An instance of an object that implements the IEmbeddingModel interface.

    Raises:
        ValueError: If the model_id is not found in the catalog.
        NotImplementedError: If the provider has no implementation in the factory.
    """
    # 1. Check if the requested model ID exists in the catalog.
    if model_id not in EMBEDDING_MODEL_CATALOG:
        available_ids = list(EMBEDDING_MODEL_CATALOG.keys())
        raise ValueError(
            f"Model ID '{model_id}' not found in the catalog. "
            f"Available models: {available_ids}"
        )

    # 2. Retrieve full model information from the catalog.
    model_info = EMBEDDING_MODEL_CATALOG[model_id]


    # 3. Instantiate the appropriate implementation based on the provider.
    if model_info.provider == "local":
        return LocalHuggingFaceEmbedder(model_name=model_info.technical_name)

    elif model_info.provider == "openai":
        assert api_key is not None, "OpenAI API key is required for OpenAI models."
        return OpenAIEmbedder(
            model_name=model_info.technical_name,
            api_key=api_key
        )

    else:
        raise NotImplementedError(
            f"Provider '{model_info.provider}' does not have a registered implementation."
        )
