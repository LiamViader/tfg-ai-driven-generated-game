from pydantic import BaseModel, Field
from typing import Dict, Literal

class EmbeddingModelInfo(BaseModel):
    """Structure to store metadata of local and OpenAI embedding models usable commercially."""
    id: str = Field(..., description="Unique catalog identifier.")
    provider: Literal["local", "openai"]
    technical_name: str
    description: str
    language: str
    strengths: str
    weaknesses: str
    speed: str
    requirements: str
    max_tokens: int

# Commercial-use embedding model catalog
EMBEDDING_MODEL_CATALOG: Dict[str, EmbeddingModelInfo] = {
    "local_en_fast": EmbeddingModelInfo(
        id="local_en_fast",
        provider="local",
        technical_name="all-MiniLM-L6-v2",
        description="Fast and light English-only model (MIT license).",
        language="English only",
        strengths="Very fast, low memory usage.",
        weaknesses="Only English.",
        speed="~1000 tokens/sec (GPU)",
        requirements="2 GB VRAM or 4 GB RAM",
        max_tokens=512
    ),
    "local_multi_balanced": EmbeddingModelInfo(
        id="local_multi_balanced",
        provider="local",
        technical_name="paraphrase-multilingual-MiniLM-L12-v2",
        description="Balanced multilingual model (MIT license).",
        language="Multilingual",
        strengths="Offline use, good quality.",
        weaknesses="Slightly below SOTA.",
        speed="~700 tokens/sec (GPU)",
        requirements="4 GB VRAM or 6 GB RAM",
        max_tokens=512
    ),
    "openai_sota_small": EmbeddingModelInfo(
        id="openai_sota_small",
        provider="openai",
        technical_name="text-embedding-3-small",
        description="OpenAI’s small SOTA multilingual model.",
        language="Multilingual",
        strengths="Great semantic accuracy, low cost.",
        weaknesses="Internet required, paid.",
        speed="~1000+ tokens/sec (API)",
        requirements="None (API)",
        max_tokens=8192
    ),
    "openai_sota_large": EmbeddingModelInfo(
        id="openai_sota_large",
        provider="openai",
        technical_name="text-embedding-3-large",
        description="Best OpenAI embedding model.",
        language="Multilingual",
        strengths="Top-tier quality.",
        weaknesses="Higher cost, Internet needed.",
        speed="~700 tokens/sec (API)",
        requirements="None (API)",
        max_tokens=8192
    ),
    "stella_v5": EmbeddingModelInfo(
        id="stella_v5",
        provider="local",
        technical_name="WhereIsAI/UAE-Large-V1",
        description="Fast, multilingual, MIT-licensed open model.",
        language="Multilingual",
        strengths="Strong retrieval quality, MIT license.",
        weaknesses="Not top in semantic nuance.",
        speed="~600 tokens/sec (RTX 3060)",
        requirements="6 GB VRAM or 8 GB RAM",
        max_tokens=512
    ),
    "bge_base_en": EmbeddingModelInfo(
        id="bge_base_en",
        provider="local",
        technical_name="BAAI/bge-base-en-v1.5",
        description="High-performing English-only model (Apache 2.0).",
        language="English",
        strengths="Excellent for retrieval tasks.",
        weaknesses="No multilingual support.",
        speed="~800 tokens/sec (GPU)",
        requirements="4 GB VRAM or 4 GB RAM",
        max_tokens=512
    ),
    "nomic_embed_text_v2": EmbeddingModelInfo(
        id="nomic_embed_text_v2",
        provider="local",
        technical_name="nomic-ai/nomic-embed-text-v2-moe",
        description="Mixture-of-experts model supporting long context (MIT).",
        language="Multilingual",
        strengths="Supports long context, high quality.",
        weaknesses="Slower, requires more memory.",
        speed="~300 tokens/sec (GPU)",
        requirements="8 GB VRAM minimum",
        max_tokens=8192
    )
}
