from __future__ import annotations

"""Predefined test pipelines for the refinement loop."""

from .schemas.pipeline_config import PipelineConfig, PipelineStep
from .constants import AgentName


def map_only_pipeline() -> PipelineConfig:
    """Single step pipeline that only runs the map agent."""
    return PipelineConfig(
        name="map_only",
        description="Pipeline that runs only the map agent to generate a simple map.",
        steps=[
            PipelineStep(
                step_name="Map Generation",
                agent_name=AgentName.MAP,
                objective_prompt="Create a small map with three connected scenarios.",
                rules_and_constraints=[],
                other_guidelines="Keep it brief.",
                max_executor_iterations=3,
                max_validation_iterations=1,
                max_retries=0,
            )
        ],
    )


def characters_only_pipeline() -> PipelineConfig:
    """Pipeline that runs only the character agent."""
    return PipelineConfig(
        name="characters_only",
        description="Pipeline that creates a couple of characters in a single step.",
        steps=[
            PipelineStep(
                step_name="Characters Generation",
                agent_name=AgentName.CHARACTERS,
                objective_prompt="Create two unique NPCs and the player character in the current map.",
                rules_and_constraints=[],
                other_guidelines="Keep them distinct and interesting.",
                max_executor_iterations=3,
                max_validation_iterations=1,
                max_retries=0,
            )
        ],
    )


def map_then_characters_pipeline() -> PipelineConfig:
    """Pipeline that first generates a map and then creates characters."""
    return PipelineConfig(
        name="map_then_characters",
        description="Generates a map and then populates it with characters.",
        steps=[
            PipelineStep(
                step_name="Initial Map",
                agent_name=AgentName.MAP,
                objective_prompt="Create a concise map with five scenarios all connected.",
                rules_and_constraints=[],
                other_guidelines="",
                max_executor_iterations=4,
                max_validation_iterations=1,
                max_retries=1,
            ),
            PipelineStep(
                step_name="Add Characters",
                agent_name=AgentName.CHARACTERS,
                objective_prompt="Add interesting NPCs to the previously generated map.",
                rules_and_constraints=[],
                other_guidelines="Ensure the characters fit within the scenarios created.",
                max_executor_iterations=3,
                max_validation_iterations=1,
                max_retries=1,
            ),
        ],
    )

__all__ = [
    "map_only_pipeline",
    "characters_only_pipeline",
    "map_then_characters_pipeline",
]
