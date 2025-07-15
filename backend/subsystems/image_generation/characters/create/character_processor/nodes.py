from langchain_openai import ChatOpenAI
from subsystems.image_generation.characters.create.character_processor.schemas import CharacterProcessorState
from subsystems.image_generation.characters.create.character_processor.prompts import format_prompt
from subsystems.image_processing.character_facing_classifier.executor import FacingDirectionClassifier
from openai import AsyncOpenAI, OpenAIError, RateLimitError
from langchain_core.messages import HumanMessage, SystemMessage
import asyncio
import base64
from PIL import Image, ImageOps, ImageFilter
import io
from typing import cast
image_gen_client = AsyncOpenAI()

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)


direction_classifier = FacingDirectionClassifier(
    model_path="models/facing_direction_classifier_v1.keras"
)

async def generate_prompt_for_character(state: CharacterProcessorState) -> dict:
    """Generate the prompt using the LLM."""
    print(f"\n--- ⚙️ Trying to generate payload for ID: {state.character.id} (Attempt {state.retry_character_prompt_count + 1}) ---")
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
        
        if word_count > 130:
            error_msg = f"Validation failed: Prompt is too long ({word_count} words, maximum is 130)."
            print(f"  -  {error_msg}")
            return {"error": error_msg}

        print("  - ✅ Prompt generated and validated successfully.")
        return {"generated_image_prompt": generated_prompt, "error": None}
    
    except Exception as e:
        return {"error": str(e)}

def increment_retry_generate_character_prompt(state: CharacterProcessorState) -> dict:
    return {"retry_character_prompt_count": state.retry_character_prompt_count + 1}

async def _generate_image_call(state: CharacterProcessorState) -> dict:
    """
    Core image generation or editing call based on character state.
    """
    print(f"\n--- 🖼️ Starting image generation attempt for: {state.character.id} ---")

    if not state.generated_image_prompt:
        return {"error": "Cannot generate image without a base description."}

    prompt = _build_prompt(state)
    
    try:
        if state.use_image_ref:
            return await _generate_with_reference(prompt)
        else:
            return await _generate_without_reference(prompt)
    except FileNotFoundError as e:
        return {"error": f"Reference image not found: {str(e)}"}
    except OpenAIError as e:
        raise e
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}


def _build_prompt(state: CharacterProcessorState) -> str:
    """
    Create the final prompt text based on the generation mode.
    """
    base = (
        f"Full body image of a character, centered, with transparent background, no shadows casted. "
        f"In a {state.graphic_style} style. "
        f"The character is: {state.generated_image_prompt}. "
    )
    if state.use_image_ref:
        base += "Use the provided image as a reference only for the facing direction of the character."
    else:
        base += "The character is in a front-facing pose angled slightly to the right."
    return base


async def _generate_with_reference(prompt: str) -> dict:
    """
    Call the API using an image reference.
    """
    reference_image_path = "images/references/character_silhouette.png"
    with open(reference_image_path, "rb") as reference_image_file:
        response = await image_gen_client.images.edit(
            model="gpt-image-1",
            image=reference_image_file,
            prompt=prompt,
            size="1024x1536",
            quality="low",
            n=1,
            background="transparent"
        )
    return _extract_image_response(response)


async def _generate_without_reference(prompt: str) -> dict:
    """
    Call the API using only text (no image).
    """
    response = await image_gen_client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1536",
        quality="low",
        n=1,
        background="transparent"
    )
    return _extract_image_response(response)


def _extract_image_response(response) -> dict:
    """
    Validate and extract image data from API response.
    """
    if not response.data or not response.data[0].b64_json:
        raise ValueError("API response did not contain valid image data.")
    
    return {"image_base64": response.data[0].b64_json, "error": None}




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

    return {"error": "Exceeded maximum retry attempts."}
    
def _crop_to_alpha_bbox(base64_image_str:str, threshold: int = 10) -> str:
    """
    Crops an image based on its alpha channel using a threshold and
    morphological opening to remove noise and isolated pixels.

    Args:
        base64_image_str: The base64 encoded string of the PNG image.
        threshold: Alpha value (0-255) below which pixels are considered fully transparent.

    Returns:
        A base64 encoded string of the cropped PNG image.
    """
    image_data = base64.b64decode(base64_image_str)
    image = Image.open(io.BytesIO(image_data)).convert("RGBA")

    # 1. Get the alpha channel of the image.
    alpha = image.getchannel('A')

    # 2. Create a lookup table to apply the threshold.
    # All pixel values <= threshold become 0; all values > threshold become 255.
    lookup_table = [0] * (threshold + 1) + [255] * (255 - threshold)
    thresholded_mask = alpha.point(lookup_table)

    # 3. Perform a morphological opening to remove noise.
    #    - Erode: Shrinks bright regions, removing small noise pixels.
    #    - Dilate: Expands remaining regions back to their original size.
    eroded_mask = thresholded_mask.filter(ImageFilter.MinFilter(3))
    opened_mask = eroded_mask.filter(ImageFilter.MaxFilter(3))

    # 4. Get the bounding box from this clean, noise-free mask.
    bbox = opened_mask.getbbox()

    if bbox:
        # 5. Crop the *original* image using the calculated bounding box.
        cropped = image.crop(bbox)
    else:
        # If no content is found after cleaning, return the original image.
        cropped = image

    # 6. Save the cropped image to a buffer and encode it back to base64.
    buffered = io.BytesIO()
    cropped.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def _flip_image_horizontally(base64_image_str: str) -> str:
    """Decodes, flips, and re-encodes a base64 image."""
    print("  - Character is facing left. Flipping image horizontally...")
    # First, decode the base64 string into image data
    image_data = base64.b64decode(base64_image_str)
    # Second, open the image data with Pillow
    image = Image.open(io.BytesIO(image_data))
    # Third, perform the flip operation on the Image object
    flipped_image = ImageOps.mirror(image)
    
    # Finally, encode the flipped image back to a base64 string
    final_buffered = io.BytesIO()
    flipped_image.save(final_buffered, format="PNG")
    return base64.b64encode(final_buffered.getvalue()).decode("utf-8")

async def posprocess_generated_image(state: CharacterProcessorState) -> dict:
    """
    Post-processes the generated image: crops it and uses a multimodal LLM
    to determine the direction the character is facing, then makes it face to the right.
    """
    print(f"\n--- 🖼️ Post-processing image for: {state.character.id} (Attempt {state.retry_analize_facing_dir_count + 1}) ---")
    
    if not state.image_base64:
        return {"error": "Cannot post-process image: image_base64 is missing."}

    try:
        image_cropped_b64 = _crop_to_alpha_bbox(state.image_base64)

        # Decodifica imagen base64 a PIL.Image
        image_data = base64.b64decode(image_cropped_b64)
        pil_image = Image.open(io.BytesIO(image_data)).convert("RGBA")

        print("  - Analyzing image to determine facing direction using local CNN...")
        facing_direction = await direction_classifier.predict(pil_image)
        print(f"  - Character is facing: {facing_direction}")

        final_image_b64 = image_cropped_b64
        if facing_direction == "left":
            final_image_b64 = _flip_image_horizontally(image_cropped_b64)

        return {
            "image_base64": final_image_b64,
            "error": None
        }
    
    except Exception as e:
        error_msg = f"An unexpected error occurred during image post-processing: {e}"
        print(f"  - ❌ {error_msg}")
        return {"error": error_msg}

def increment_retry_analize_facing_dir(state: CharacterProcessorState) -> dict:
    return {"retry_analize_facing_dir_count": state.retry_analize_facing_dir_count + 1}


