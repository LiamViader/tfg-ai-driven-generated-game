from langchain_openai import ChatOpenAI
from subsystems.image_generation.scenarios.create.scenario_processor.schemas import ImageGenerationPayload, LlmGeneratedPayload, ScenarioProcessorState
from subsystems.image_generation.scenarios.create.scenario_processor.prompts import format_prompt
from typing import cast
import httpx

# --- LLM Setup ---
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)
structured_llm = llm.with_structured_output(LlmGeneratedPayload)

# --- Graph Nodes ---

async def generate_payload_for_scenario(state: ScenarioProcessorState) -> dict:
    """
    This node tries to generate the payload for a single scenario.
    """
    print(f"\n--- ⚙️ Trying to generate payload for ID: {state.scenario.id} (Attempt {state.retry_count + 1}) ---")
    
    try:
        llm_payload = cast(LlmGeneratedPayload, await structured_llm.ainvoke(
            format_prompt(state.general_game_context, state.scenario)
        ))
        final_payload = ImageGenerationPayload(
            **llm_payload.model_dump(),
            graphic_style=state.graphic_style
        )
        print(f"  - ✅ Payload generated for {state.scenario.id}")
        return {
            "generation_payload": final_payload, 
            "error": None
        }

    except Exception as e:
        print(f"  - ⚠️ Error for {state.scenario.id}: {e}")
        return {"error": str(e)}

async def generate_image_from_payload(state: ScenarioProcessorState) -> dict:
    """
    This node takes the generated payload and calls the image generation API.
    """
    print(f"\n--- 🖼️ Starting image generation for: {state.scenario.id} ---")
    payload = state.generation_payload
    if not payload:
        error_msg = "Cannot generate image without a payload."
        return {"error": error_msg}

    try:
        async with httpx.AsyncClient(timeout=500.0) as client:
            print(f"  - 📤 Sending request to the image API...")
            full_url_endpoint = f"{state.image_api_url}/create-scenario-image"
            response = await client.post(full_url_endpoint, json=payload.model_dump())
            
            response.raise_for_status()
            
            data = response.json()
            image_b64 = data.get("image_base64")

            if not image_b64:
                raise ValueError("API response did not contain 'image_base64'.")

            print(f"  - ✅ Image generated and received in base64.")
            return {"image_base64": image_b64, "error": None}

    except httpx.HTTPStatusError as e:
        error_msg = f"Image API HTTP Error: {e.response.status_code} - {e.response.text}"
        print(f"  - ❌ Error: {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred during image generation: {e}"
        print(f"  - ❌ Error: {error_msg}")
        return {"error": error_msg}

def increment_retry_counter(state: ScenarioProcessorState) -> dict:
    """
    A simple node to update the retry counter.
    """
    return {"retry_count": state.retry_count + 1}
