from langchain_openai import ChatOpenAI
from .schemas import CharacterProcessorState
from .prompts import format_prompt
from openai import AsyncOpenAI, OpenAIError, RateLimitError
import asyncio
image_gen_client = AsyncOpenAI()

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)

async def generate_prompt_for_character(state: CharacterProcessorState) -> dict:
    """Generate the prompt using the LLM."""
    try:
        result = await llm.ainvoke(
            format_prompt(state.general_game_context, state.character)
        )
        
        generated_prompt = result.content
        if not isinstance(generated_prompt, str):
            error_msg = f"LLM returned an unexpected type: {type(generated_prompt)}. Expected a string."
            print(f"  - ❌ {error_msg}")
            return {"error": error_msg}
        
        word_count = len(generated_prompt.split())
        if word_count < 30:
            error_msg = f"Validation failed: Prompt is too short ({word_count} words, minimum is 30)."
            print(f"  -  {error_msg}")
            return {"error": error_msg}
        
        if word_count > 120:
            error_msg = f"Validation failed: Prompt is too long ({word_count} words, maximum is 120)."
            print(f"  -  {error_msg}")
            return {"error": error_msg}

        print("  - ✅ Prompt generated and validated successfully.")
        return {"generated_image_prompt": generated_prompt, "error": None}
    
    except Exception as e:
        return {"error": str(e)}



async def _generate_image_call(state: CharacterProcessorState) -> dict:
    """
    The core API call to generate an image. This is the part that might fail.
    """
    print(f"\n--- 🖼️ Starting image generation attempt for: {state.character.id} ---")
    
    base_description = state.generated_image_prompt
    if not base_description:
        return {"error": "Cannot generate image without a base description."}

    final_prompt = (
        f"Full body image of a character, centered, with transparent background, no shadows casted."
        f"In a {state.graphic_style} style, "
        f"The character is: {base_description}. "
        f"Use the provided image as a reference only for the facing direction of the character"
    )
    
    reference_image_path = "images/references/character_silhouette.png"

    try:
        with open(reference_image_path, "rb") as reference_image_file:
            response = await image_gen_client.images.edit(
                model="gpt-image-1",
                image=reference_image_file,
                prompt=final_prompt,
                size="1024x1536",
                quality="low",
                n=1,
                background="transparent"
            )
            
        if not response.data or not response.data[0].b64_json:
            raise ValueError("API response did not contain valid image data.")
        
        image_b64 = response.data[0].b64_json
        if not image_b64:
            raise ValueError("API response did not contain image data.")

        print("  - ✅ Image generated successfully on this attempt.")
        return {"image_base64": image_b64, "error": None}

    except FileNotFoundError:
        return {"error": f"Reference image not found at path: {reference_image_path}"}
    except OpenAIError as e:
        raise e
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

async def generate_image_from_prompt(state: CharacterProcessorState) -> dict:
    """
    A robust wrapper node that calls the image generation function
    and implements a manual retry logic based on the API's feedback.
    """
    max_retries = 7
    # Default wait time if the API doesn't specify one.
    DEFAULT_RETRY_AFTER = 30  # seconds

    for attempt in range(max_retries):
        try:
            # Call the internal function that makes the actual API request
            result = await _generate_image_call(state)
            
            # If there was a non-API error (e.g., file not found), return it
            if result.get("error"):
                return result
            
            # If successful, return the result immediately
            return result

        except RateLimitError as e:
            if attempt < max_retries - 1:
                # Use the 'retry_after' value from the API if available, otherwise use our default.
                # The 'body' attribute in the modern library holds details like this.
                retry_time = e.body.get('retry_after', DEFAULT_RETRY_AFTER) if isinstance(e.body, dict) else DEFAULT_RETRY_AFTER
                
                print(f"  - ⚠️ Rate limit hit on attempt {attempt + 1}/{max_retries}. API suggests waiting {retry_time} seconds. Retrying...")
                await asyncio.sleep(retry_time)
            else:
                # If all retries fail, return a final error
                error_msg = f"Failed after {max_retries} attempts due to rate limiting."
                print(f"  - ❌ {error_msg}")
                return {"error": error_msg}
        except OpenAIError as e:
            # Handle other potential OpenAI API errors
            error_msg = f"An OpenAI API error occurred: {e}"
            print(f"  - ❌ {error_msg}")
            return {"error": error_msg}

    # This part should ideally not be reached, but as a fallback
    return {"error": "Exceeded maximum retry attempts."}
    



def increment_retry_counter(state: CharacterProcessorState) -> dict:
    return {"retry_count": state.retry_count + 1}
