from typing import List, TypedDict, Dict, Any, Optional
from pydantic import BaseModel, Field
from core_game.map.schemas import ScenarioModel
from subsystems.image_generation.scenarios.create.scenario_processor.schemas import ScenarioProcessorState
class GraphState(BaseModel):
    scenarios: List[ScenarioModel] = Field(description="A list of scenario to generate the images.")
    graphic_style: str = Field(description="The global graphic style to be applied to all generated images.")
    general_game_context: str = Field(
        ...,
        description="A string containing a description of the general game context"
    )
    successful_scenarios: List[ScenarioProcessorState] = Field(
        default_factory=list,
        description="A list of scenarios that were processed successfully, including the generated image."
    )
    failed_scenarios: List[ScenarioProcessorState] = Field(
        default_factory=list,
        description="A list of scenarios that failed during processing."
    )
    image_api_url: str = Field(description="The URL for the image generation API.")


