from typing import List
from pydantic import BaseModel, Field
from subsystems.generation.refinement_loop.constants import AgentName
class PipelineStep(BaseModel):
    """Represents a single step in the generation pipeline."""

    step_name: str = Field(..., description="A descriptive name for the step, e.g., 'Initial Character Creation'.")
    agent_name: AgentName = Field(..., description="The name of the agent to be executed for this step.")
    objective_prompt: str = Field(..., description="A prompt template for the agent's objective.")
    rules_and_constraints: List[str] = Field(default_factory=list, description="Any rules or constraints to apply to the agent for current step")
    other_guidelines: str = Field(default="", description="Any other guidelines for the agent to follow")
    max_executor_iterations: int = Field(..., description="Max executor iterations to achieve the objective")
    max_validation_iterations: int = Field(..., description="Max iterations to validate the result")
    max_retries: int = Field(..., description="Max retries for the agent to achieve its task")
    weight: float = Field(..., description="Weight of the step in the overall pipeline, used for progress compute.")

class PipelineConfig(BaseModel):
    """Defines a complete configuration for a generation pipeline."""

    name: str = Field(..., description="The unique name of the pipeline, e.g., 'FastPrototype_v1'.")
    description: str = Field(..., description="A brief explanation of what this pipeline does and its intended use.")
    steps: List[PipelineStep] = Field(..., description="The ordered list of PipelineStep objects that define the sequence of operations for this pipeline.")