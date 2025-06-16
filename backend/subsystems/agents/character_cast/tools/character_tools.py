"""Tool functions used by the character agent."""

from typing import Annotated, Optional
from pydantic import BaseModel
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from core_game.character.schemas import (
    IdentityModel,
    PhysicalAttributesModel,
    PsychologicalAttributesModel,
    KnowledgeModel,
    DynamicStateModel,
    NarrativeWeightModel,
    NonPlayerCharacterModel,
)

from ..schemas.simulated_characters import (
    SimulatedCharactersModel,
    CreateNPCArgs,
    ModifyCharacterArgs,
    DeleteCharacterArgs,
)


# --- Tools Schemas -- (adding the injected simulated map)
class ToolCreateScenarioArgs(CreateNPCArgs):
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")]



@tool(args_schema=ToolCreateScenarioArgs)
def create_full_npc(
    identity: IdentityModel,
    physical: PhysicalAttributesModel,
    psychological: PsychologicalAttributesModel,
    narrative: NarrativeWeightModel,
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    knowledge: KnowledgeModel = KnowledgeModel(),
    dynamic_state: DynamicStateModel = DynamicStateModel(),
) -> str:
    """Create a new NPC providing complete attribute information."""

    new_id = SimulatedCharactersModel.generate_sequential_character_id(list(simulated_characters_state.simulated_characters.keys()))
    npc = NonPlayerCharacterModel(
        id=new_id,
        identity=identity,
        physical=physical,
        psychological=psychological,
        knowledge=knowledge,
        present_in_scenario=None,
        dynamic_state=dynamic_state,
        narrative=narrative,
    )

    simulated_characters_state.simulated_characters[new_id] = npc
    return simulated_characters_state._log_and_summarize(
        "create_full_npc",
        CreateNPCArgs(
            identity=identity,
            physical=physical,
            psychological=psychological,
            knowledge=knowledge,
            dynamic_state=dynamic_state,
            narrative=narrative,
        ),
        True,
        f"Full NPC '{identity.full_name}' created with id {new_id}.",
    )


@tool(args_schema=ModifyCharacterArgs)
def modify_character(
    character_id: str,
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    new_full_name: Optional[str] = None,
    new_personality_summary: Optional[str] = None,
) -> str:
    """Modify basic character information."""
    if character_id not in simulated_characters_state.simulated_characters:
        return simulated_characters_state._log_and_summarize(
            "modify_character",
            ModifyCharacterArgs(character_id=character_id, new_full_name=new_full_name, new_personality_summary=new_personality_summary),
            False,
            f"Character id '{character_id}' not found.",
        )

    char = simulated_characters_state.simulated_characters[character_id]
    if new_full_name is not None:
        char.identity.full_name = new_full_name
    if new_personality_summary is not None:
        char.psychological.personality_summary = new_personality_summary

    return simulated_characters_state._log_and_summarize(
        "modify_character",
        ModifyCharacterArgs(character_id=character_id, new_full_name=new_full_name, new_personality_summary=new_personality_summary),
        True,
        f"Character '{character_id}' modified.",
    )


@tool(args_schema=DeleteCharacterArgs)
def delete_character(
    character_id: str,
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
) -> str:
    """Delete a character from the simulation."""
    if character_id not in simulated_characters_state.simulated_characters:
        return simulated_characters_state._log_and_summarize(
            "delete_character",
            DeleteCharacterArgs(character_id=character_id),
            False,
            f"Character id '{character_id}' not found.",
        )

    char = simulated_characters_state.simulated_characters.pop(character_id)
    simulated_characters_state.deleted_characters[character_id] = char
    return simulated_characters_state._log_and_summarize(
        "delete_character",
        DeleteCharacterArgs(character_id=character_id),
        True,
        f"Character '{character_id}' deleted.",
    )


@tool
def list_characters(simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")]) -> str:
    """Return a short summary of current characters."""
    return simulated_characters_state.get_summary()


@tool
def finalize_simulation(
    justification: str,
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
) -> str:
    """Mark the simulation as completed with a justification."""
    simulated_characters_state.task_finalized_by_agent = True
    simulated_characters_state.task_finalized_justification = justification
    return simulated_characters_state._log_and_summarize(
        "finalize_simulation",
        BaseModel(),
        True,
        justification,
    )


EXECUTORTOOLS = [
    create_full_npc,
    modify_character,
    delete_character,
    list_characters,
    finalize_simulation,
]

