from typing import List
from pydantic import BaseModel, Field
from core_game.character.schemas import CharacterBaseModel
from subsystems.image_generation.characters.create.character_processor.schemas import CharacterProcessorState

class GraphState(BaseModel):
    characters: List[CharacterBaseModel] = Field(description="Characters to generate images for.")
    graphic_style: str = Field(description="Global graphic style for all characters.")
    general_game_context: str = Field(..., description="General game context for prompts.")
    successful_characters: List[CharacterProcessorState] = Field(default_factory=list)
    failed_characters: List[CharacterProcessorState] = Field(default_factory=list)
    use_image_ref: bool = Field(
        default=True,
        description="Whether to use image reference for the image generation."
    )
