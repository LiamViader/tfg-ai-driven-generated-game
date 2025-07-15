import os
import sys
from dotenv import load_dotenv
from pydantic import SecretStr

# Importem la classe 'Document' de LangChain, ja que ara és el nostre objecte de dades
from langchain_core.documents import Document

# Ens assegurem que l'arrel del projecte estigui al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importem les nostres peces d'arquitectura
from persistence.vector_repository import ChromaVectorRepository
from embedding.factory import create_embedding_model


# Les dades de prova es mantenen igual
DOCS = [
    "A small red apple with a shiny skin.",
    "A ripe yellow long shaped banana ready to eat.", # He canviat 'ready to eat' a 'banana' per a una millor prova
    "An orange cat sleeping peacefully on the sofa.",
]
METAS = [{"source": "fruit_description"} for _ in DOCS]
IDS = [f"id_{i}" for i in range(len(DOCS))]


def run_test(model_id: str, api_key: SecretStr | None = None) -> None:
    """Indexa i busca documents utilitzant el model d'embedding donat."""
    print(f"\n=== Testing model: {model_id} ===")
    try:
        embedding_model = create_embedding_model(model_id, api_key=api_key)
    except Exception as e: 
        print(f"No s'ha pogut carregar el model {model_id}: {e}")
        return

    repo = ChromaVectorRepository(
        db_path=f"./data/tmp_{model_id}",
        collection_name=f"collection_{model_id}",
        embedding_model=embedding_model,
    )

    documents_to_add = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(DOCS, METAS)
    ]


    repo.add(documents=documents_to_add, ids=IDS)
    print(f"Successfully added {len(documents_to_add)} documents.")


    results = repo.search("a yellow banana", k=1) # He canviat la query per a una millor prova


    print("--- Search Results for 'a yellow banana' ---")
    if results:
        top_result = results[0]
        print(f"Top result: page_content='{top_result.page_content}', metadata={top_result.metadata}")
    else:
        print("Top result: None")


if __name__ == "__main__":
    # Carreguem les variables d'entorn (per a l'API Key)
    load_dotenv()
    
    # Provem els models locals
    models = ["local_en_fast", "local_multi_balanced", "stella_v5"]
    for mid in models:
        run_test(mid)

    # Provem el model d'OpenAI només si la clau està configurada
    api_key_str = os.getenv("OPENAI_API_KEY")
    if api_key_str:
        print("\nOpenAI API key found, running OpenAI model test...")
        run_test("openai_small", api_key=SecretStr(api_key_str))
    else:
        print("\nWARNING: OPENAI_API_KEY not configured; skipping OpenAI model test.")