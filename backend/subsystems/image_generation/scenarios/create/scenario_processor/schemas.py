from typing import List, TypedDict, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from core_game.map.schemas import ScenarioModel

class ImageGenerationPayload(BaseModel):
    """Payload específico para la API de generación de imágenes."""
    scene_summary: str = Field(description="A very brief summary of the main scene (1-3 words). Example: 'A floating castle'.")
    scene_detail: str = Field(description="A detailed visual description of the main scene. Example: 'A majestic castle with glowing towers drifts silently among a sea of clouds.'")
    ground_detail: str = Field(description="A detailed description of the ground or base of the scene. Example: 'cracked, ancient stone with glowing blue lava flowing through the fissures.'")
    ground_summary: str = Field(description="A very brief summary of the ground or base (1-3 words). Example: 'Cracked lava stone'.")
    graphic_style: str = Field(description="Defines the artistic look and feel. Examples: 'Oil painting', 'Pixel art', 'Photorealistic 3D render', 'in the style of Studio Ghibli'.")

class LlmGeneratedPayload(BaseModel):
    """Specific payload for llm."""
    scene_summary: str = Field(description="A very brief summary of the main scene (1-3 words). Example: 'A floating castle'.")
    scene_detail: str = Field(description="A detailed visual description of the main scene (5-12 words). Example: 'A majestic castle with glowing towers drifts silently among a sea of clouds.'")
    ground_detail: str = Field(description="A detailed description of the ground or base of the scene (3-6 words). Example: 'cracked, ancient stone with glowing blue lava flowing through the fissures.'")
    ground_summary: str = Field(description="A very brief summary of the ground or base (1-3 words). Example: 'Cracked lava stone'.")
    
    @field_validator('scene_summary')
    @classmethod
    def validate_scene_summary_word_count(cls, v: str) -> str:
        """Validates that the scene_summary field has between 1 and 5 words."""
        word_count = len(v.split())
        if not 1 <= word_count <= 5:
            raise ValueError(f"must contain between 1 and 5 words, but has {word_count}")
        return v

    @field_validator('scene_detail')
    @classmethod
    def validate_scene_detail_word_count(cls, v: str) -> str:
        """Validates that the scene_detail field has between 2 and 15 words."""
        word_count = len(v.split())
        if not 2 <= word_count <= 15:
            raise ValueError(f"must contain between 2 and 15 words, but has {word_count}")
        return v
    
    @field_validator('ground_detail')
    @classmethod
    def validate_ground_detail_word_count(cls, v: str) -> str:
        """Validates that the ground_detail field has between 2 and 8 words."""
        word_count = len(v.split())
        if not 2 <= word_count <= 8:
            raise ValueError(f"must contain between 2 and 8 words, but has {word_count}")
        return v
        
    @field_validator('ground_summary')
    @classmethod
    def validate_ground_summary_word_count(cls, v: str) -> str:
        """Validates that the ground_summary field has between 1 and 5 words."""
        word_count = len(v.split())
        if not 1 <= word_count <= 5:
            raise ValueError(f"must contain between 1 and 5 words, but has {word_count}")
        return v

class ScenarioProcessorState(BaseModel):
    """
    Represents the state for a single processed scenario.
    This is the object that flows through the 'scenario_processor' subgraph.
    """
    scenario: ScenarioModel = Field(
        ...,
        description="The scenario to generate the image from."
    )
    graphic_style: str = Field(
        ...,
        description="The global graphic style passed down from the main graph."
    )
    generation_payload: Optional[ImageGenerationPayload] = Field(
        default=None, 
        description="The detailed payload generated by the LLM for the image API."
    )
    image_base64: Optional[str] = Field(
        default=None, 
        description="The base64 encoded string of the generated image."
    )
    error: Optional[str] = Field(
        default=None, 
        description="An error message if anything fails during the processing of this scenario."
    )
    retry_count: int = Field(
        default=0, 
        description="A counter to track the number of retries for the payload generation."
    )
    general_game_context: str = Field(
        ...,
        description="A string containing a description of the general game context"
    )
    image_api_url: str = Field(description="The URL for the image generation API.")