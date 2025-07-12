from langchain_openai import ChatOpenAI
from .schemas import CharacterProcessorState, CharacterPromptPayload
from .prompts import format_prompt
import openai

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)
structured_llm = llm.with_structured_output(CharacterPromptPayload)

async def generate_prompt_for_character(state: CharacterProcessorState) -> dict:
    """Generate the prompt using the LLM."""
    try:
        payload = await structured_llm.ainvoke(
            format_prompt(state.general_game_context, state.character, state.graphic_style)
        )
        return {"prompt": payload.prompt, "error": None}
    except Exception as e:
        return {"error": str(e)}

async def generate_image_from_prompt(state: CharacterProcessorState) -> dict:
    """Use OpenAI's image API to create the character image."""
    if not state.prompt:
        return {"error": "Cannot generate image without a prompt."}

    try:
        response = await openai.images.async_create(
            prompt=state.prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json",
        )
        image_b64 = response.data[0].b64_json
        return {"image_base64": image_b64, "error": None}
    except Exception as e:
        return {"error": str(e)}


def increment_retry_counter(state: CharacterProcessorState) -> dict:
    return {"retry_count": state.retry_count + 1}
