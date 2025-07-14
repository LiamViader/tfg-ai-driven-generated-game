from typing import Optional, Literal
from pydantic import BaseModel, Field
from core_game.character.schemas import CharacterBaseModel

class CharacterProcessorState(BaseModel):
    """Represents the state while generating a single character image."""
    character: CharacterBaseModel = Field(..., description="Character to generate the image for.")
    graphic_style: str = Field(..., description="Desired graphic style for the image.")
    generated_image_prompt: Optional[str] = Field(default=None, description="Prompt to send to OpenAI image API.")
    image_base64: Optional[str] = Field(default=None, description="Base64 string of the generated image.")
    error: Optional[str] = Field(default=None, description="Error encountered during generation.")
    retry_character_prompt_count: int = Field(default=0, description="Number of character prompt generation retries.")
    retry_analize_facing_dir_count: int = Field(default=0, description="Number of character prompt generation retries.")
    general_game_context: str = Field(..., description="General context of the game for additional flavor.")

class FacingDirectionStructure(BaseModel):
    """Structure to hold the facing direction of the character."""
    facing_direction: Literal["left", "right"] = Field(
        ...,
        description="Facing direction 'left' or 'right' ."
    )
