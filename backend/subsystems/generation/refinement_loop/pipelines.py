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
                max_executor_iterations=7,
                max_validation_iterations=1,
                max_retries=2,
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
                objective_prompt="Create 4 unique NPCs.",
                rules_and_constraints=[],
                other_guidelines="Keep them distinct and interesting.",
                max_executor_iterations=3,
                max_validation_iterations=0,
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
                objective_prompt="Create a concise map with 3 scenarios all connected.",
                rules_and_constraints=[],
                other_guidelines="",
                max_executor_iterations=4,
                max_validation_iterations=1,
                max_retries=1,
            ),
            PipelineStep(
                step_name="Add Characters",
                agent_name=AgentName.CHARACTERS,
                objective_prompt="Add 1 NPC and the player to the previously generated map.",
                rules_and_constraints=[],
                other_guidelines="Ensure the characters fit within the scenarios created. Made the characters have so little short data",
                max_executor_iterations=5,
                max_validation_iterations=1,
                max_retries=1,
            ),
        ],
    )


def map_characters_relationships_pipeline() -> PipelineConfig:
    """Pipeline that generates a map, then characters and finally relationships."""
    return PipelineConfig(
        name="map_characters_relationships",
        description="Generates a map and characters first and then establishes relationships between them.",
        steps=[
            PipelineStep(
                step_name="Initial Map",
                agent_name=AgentName.MAP,
                objective_prompt="Create a concise map with three connected scenarios.",
                rules_and_constraints=[],
                other_guidelines="",
                max_executor_iterations=4,
                max_validation_iterations=1,
                max_retries=1,
            ),
            PipelineStep(
                step_name="Add Characters",
                agent_name=AgentName.CHARACTERS,
                objective_prompt="Introduce two characters placed in the generated scenarios.",
                rules_and_constraints=[],
                other_guidelines="",
                max_executor_iterations=3,
                max_validation_iterations=1,
                max_retries=1,
            ),
            PipelineStep(
                step_name="Create Relationships",
                agent_name=AgentName.RELATIONSHIP,
                objective_prompt="Create relationships between the characters.",
                rules_and_constraints=[],
                other_guidelines="Ensure the relationships make sense with the character backgrounds and map.",
                max_executor_iterations=3,
                max_validation_iterations=1,
                max_retries=1,
            ),
        ],
    )


def map_characters_relationships_narrative_pipeline() -> PipelineConfig:
    """Pipeline that generates a map, characters, relationships and a basic narrative."""
    return PipelineConfig(
        name="map_characters_relationships_narrative",
        description="Generates map, characters, relationships and then crafts an initial narrative structure.",
        steps=[
            PipelineStep(
                step_name="Initial Map",
                agent_name=AgentName.MAP,
                objective_prompt="Create a concise map with three connected scenarios.",
                rules_and_constraints=[],
                other_guidelines="",
                max_executor_iterations=4,
                max_validation_iterations=1,
                max_retries=1,
            ),
            PipelineStep(
                step_name="Add Characters",
                agent_name=AgentName.CHARACTERS,
                objective_prompt="Introduce two characters placed in the generated scenarios.",
                rules_and_constraints=[],
                other_guidelines="",
                max_executor_iterations=3,
                max_validation_iterations=1,
                max_retries=1,
            ),
            PipelineStep(
                step_name="Create Relationships",
                agent_name=AgentName.RELATIONSHIP,
                objective_prompt="Create 2-4 relationships between characters.",
                rules_and_constraints=[],
                other_guidelines="Ensure the relationships make sense with the character backgrounds and map.",
                max_executor_iterations=3,
                max_validation_iterations=1,
                max_retries=1,
            ),
            PipelineStep(
                step_name="Create Narrative",
                agent_name=AgentName.NARRATIVE,
                objective_prompt="Create 2-3 narrative beats for the current stage and 1 failure condition.",
                rules_and_constraints=[],
                other_guidelines="",
                max_executor_iterations=5,
                max_validation_iterations=1,
                max_retries=1,
            ),
        ],
    )


def map_characters_relationships_narrative_events_pipeline() -> PipelineConfig:
    """Pipeline that generates a map, characters, relationships, narrative and game events."""
    return PipelineConfig(
        name="map_characters_relationships_narrative_events",
        description="Generates map, characters, relationships, a basic narrative and then game events.",
        steps=[
            PipelineStep(
                step_name="Initial Map",
                agent_name=AgentName.MAP,
                objective_prompt="Create a concise map with three connected scenarios.",
                rules_and_constraints=[],
                other_guidelines="",
                max_executor_iterations=4,
                max_validation_iterations=1,
                max_retries=1,
            ),
            PipelineStep(
                step_name="Add Characters",
                agent_name=AgentName.CHARACTERS,
                objective_prompt="Introduce two characters placed in the generated scenarios.",
                rules_and_constraints=[],
                other_guidelines="",
                max_executor_iterations=3,
                max_validation_iterations=1,
                max_retries=1,
            ),
            PipelineStep(
                step_name="Create Relationships",
                agent_name=AgentName.RELATIONSHIP,
                objective_prompt="Create 2-4 relationships between characters.",
                rules_and_constraints=[],
                other_guidelines="Ensure the relationships make sense with the character backgrounds and map.",
                max_executor_iterations=3,
                max_validation_iterations=1,
                max_retries=1,
            ),
            PipelineStep(
                step_name="Create Narrative",
                agent_name=AgentName.NARRATIVE,
                objective_prompt="Create 2-3 narrative beats for the current stage and 1 failure condition.",
                rules_and_constraints=[],
                other_guidelines="",
                max_executor_iterations=5,
                max_validation_iterations=1,
                max_retries=1,
            ),
            PipelineStep(
                step_name="Create Game Events",
                agent_name=AgentName.EVENTS,
                objective_prompt="Generate 2-3 key game events based on the narrative and world so far.",
                rules_and_constraints=[],
                other_guidelines="",
                max_executor_iterations=4,
                max_validation_iterations=1,
                max_retries=1,
            ),
        ],
    )

def alternating_expansion_pipeline() -> PipelineConfig:
    """Pipeline with six steps alternating between map and characters."""

    steps = []
    for i in range(1, 4):
        steps.append(
            PipelineStep(
                step_name=f"Map Expansion {i}",
                agent_name=AgentName.MAP,
                objective_prompt=(
                    "Expand the world map with 2-5 new scenarios based on the current context. Use the context of characters to maybe create some scenarios coherent with them."
                ),
                rules_and_constraints=["Be as creative as you can while creating the map. You can create interiors made of more than one scenario, cities, villages, forages, forests anything you can think of. Always think the design is to surprise the player in quality, coherence and narrative"],
                other_guidelines="Ensure new scenarios are interconected with eachother. The map should be interesting for the player to explore, you can keep expanding zones or adding new ones. Use the provided context to make interesting decisions",
                max_executor_iterations=9,
                max_validation_iterations=1,
                max_retries=1,
            )
        )
        steps.append(
            PipelineStep(
                step_name=f"Character Expansion {i}",
                agent_name=AgentName.CHARACTERS,
                objective_prompt=(
                    "Introduce 1-2 new characters that enrich the expanded world. Give characters diferent narrative roles. When you feel like so, you can create the player."
                ),
                rules_and_constraints=["Characters should have unique personalities and physical atributes that make them outstand."],
                other_guidelines="Place characters in appropriate scenarios and expand the given context lore by adding background knowledge to existing characters, or updating other atributes",
                max_executor_iterations=7,
                max_validation_iterations=1,
                max_retries=1,
        )
    )

    return PipelineConfig(
        name="alternating_expansion",
        description=(
            "Six-step pipeline alternating between map and character generation to gradually expand the world."
        ),
        steps=steps,
    )

__all__ = [
    "map_only_pipeline",
    "characters_only_pipeline",
    "map_then_characters_pipeline",
    "alternating_expansion_pipeline",
    "map_characters_relationships_pipeline",
    "map_characters_relationships_narrative_pipeline",
    "map_characters_relationships_narrative_events_pipeline",
]
