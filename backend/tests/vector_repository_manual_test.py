import os
import sys

# Ensure project root is on the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from persistence.vector_repository import ChromaVectorRepository
from embeddings.factory import create_embedding_model
from pydantic import SecretStr


DOCS = [
    "A small red apple with a shiny skin.",
    "A ripe yellow banana ready to eat.",
    "An orange cat sleeping peacefully on the sofa.",
]
METAS = [{"desc": d} for d in DOCS]
IDS = [f"id_{i}" for i in range(len(DOCS))]


def run_test(model_id: str, api_key: SecretStr | None = None) -> None:
    """Index and search documents using the given embedding model."""
    print(f"\n=== Testing model: {model_id} ===")
    try:
        embedding_model = create_embedding_model(model_id, api_key=api_key)
    except Exception as e:  # model might not be available
        print(f"Could not load model {model_id}: {e}")
        return

    repo = ChromaVectorRepository(
        db_path=f"./tmp_{model_id}",
        collection_name=f"collection_{model_id}",
        embedding_model=embedding_model,
    )

    repo.add(DOCS, METAS, IDS)
    results = repo.search("banana", k=1)
    print("Top result:", results[0] if results else "None")


if __name__ == "__main__":
    models = ["local_en_fast", "local_multi_balanced"]
    for mid in models:
        run_test(mid)

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        run_test("openai_sota_small", api_key=SecretStr(openai_key))
    else:
        print("OPENAI_API_KEY not configured; skipping OpenAI model")
