from typing import Optional
from pydantic import BaseModel, Field
from core_game.character.schemas import CharacterBaseModel

class CharacterProcessorState(BaseModel):
    """Represents the state while generating a single character image."""
    character: CharacterBaseModel = Field(..., description="Character to generate the image for.")
    graphic_style: str = Field(..., description="Desired graphic style for the image.")
    generated_image_prompt: Optional[str] = Field(default=None, description="Prompt to send to OpenAI image API.")
    image_base64: Optional[str] = Field(default=None, description="Base64 string of the generated image.")
    error: Optional[str] = Field(default=None, description="Error encountered during generation.")
    retry_count: int = Field(default=0, description="Number of payload generation retries.")
    general_game_context: str = Field(..., description="General context of the game for additional flavor.")
