"""Tool functions used by the character agent."""

"""Tool functions used by the character agent."""

from typing import Annotated, Optional, Literal
from core_game.character.constants import Gender, NarrativeImportance, NarrativeRole
from pydantic import BaseModel
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from pydantic import Field
from subsystems.agents.utils.schemas import InjectedToolContext
from .helpers import get_log_item, get_observation
from simulated.game_state import SimulatedGameStateSingleton


from core_game.character.schemas import (
    IdentityModel,
    PhysicalAttributesModel,
    PsychologicalAttributesModel,
    KnowledgeModel,
    DynamicStateModel,
    NarrativeWeightModel,
    NonPlayerCharacterModel,
    PlayerCharacterModel,
)

from ..schemas.simulated_characters import (
    SimulatedCharactersModel,
    CreateNPCArgs,
    ModifyIdentityArgs,
    ModifyPhysicalArgs,
    ModifyPsychologicalArgs,
    ModifyKnowledgeArgs,
    ModifyDynamicStateArgs,
    ModifyNarrativeArgs,
    DeleteCharacterArgs,
    PlaceCharacterArgs,
    RemoveCharacterFromScenarioArgs,
    ListCharactersArgs,
    GetCharacterDetailsArgs,
    CreatePlayerArgs,
    GetPlayerDetailsArgs,
    ListCharactersByScenarioArgs,
)


# --- Tools Schemas -- (adding the injected simulated map)
class ToolCreateNPCArgs(InjectedToolContext):
    identity: IdentityModel = Field(..., description="Full identity information")
    physical: PhysicalAttributesModel = Field(..., description="Full physical description")
    psychological: PsychologicalAttributesModel = Field(..., description="Detailed psychological profile")
    knowledge: KnowledgeModel = Field(..., description="Initial knowledge state, aquired knowledge should be empty")
    dynamic_state: DynamicStateModel = Field(default_factory=DynamicStateModel, description="Initial dynamic state")
    narrative: NarrativeWeightModel = Field(..., description="Narrative role and importance")

class ToolCreatePlayerArgs(InjectedToolContext):
    identity: IdentityModel = Field(..., description="Full identity information")
    physical: PhysicalAttributesModel = Field(..., description="Full physical description")
    psychological: PsychologicalAttributesModel = Field(..., description="Detailed psychological profile")
    knowledge: Optional[KnowledgeModel] = Field(default_factory=KnowledgeModel, description="Initial knowledge state")
    scenario_id: str = Field(..., description="ID of the scenario where the player starts")

class ToolModifyIdentityArgs(InjectedToolContext):

class ToolModifyPhysicalArgs(InjectedToolContext):


class ToolModifyPsychologicalArgs(InjectedToolContext):

class ToolModifyKnowledgeArgs(InjectedToolContext):


class ToolModifyDynamicStateArgs(InjectedToolContext):


class ToolModifyNarrativeArgs(InjectedToolContext):


class ToolDeleteCharacterArgs(InjectedToolContext):

class ToolPlaceCharacterArgs(InjectedToolContext):

class ToolRemoveCharacterFromScenarioArgs(InjectedToolContext):

class ToolListCharactersArgs(InjectedToolContext):

class ToolGetCharacterDetailsArgs(InjectedToolContext):



class ToolGetPlayerDetailsArgs(InjectedToolContext):

class ToolListCharactersByScenarioArgs(InjectedToolContext):

class ToolFinalizeSimulationArgs(InjectedToolContext):
    justification: str



@tool(args_schema=ToolCreateNPCArgs)
def create_npc(
    identity: IdentityModel,
    physical: PhysicalAttributesModel,
    psychological: PsychologicalAttributesModel,
    narrative: NarrativeWeightModel,
    knowledge: KnowledgeModel,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    dynamic_state: DynamicStateModel = DynamicStateModel()
) -> Command:
    """Create a new NPC providing its detailed information information."""

    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters

    effective_id = simulated_characters.create_npc(
        identity=identity,
        physical=physical,
        psychological=psychological,
        narrative=narrative,
        knowledge=knowledge,
        dynamic_state=dynamic_state
    )

    return Command(update={
        logs_field_to_update: [get_log_item("create_npc", True, f"NPC '{identity.full_name}' created with id {effective_id}.")],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_characters.characters_count(), "create_npc", True, f"NPC '{identity.full_name}' created with id {effective_id}."),
                tool_call_id=tool_call_id,
            )
        ]
    })

@tool(args_schema=ToolCreatePlayerArgs)
def create_player(
    identity: IdentityModel,
    physical: PhysicalAttributesModel,
    psychological: PsychologicalAttributesModel,
    scenario_id: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    knowledge: Optional[KnowledgeModel] = KnowledgeModel()
) -> Command:
    "Creates the player character in the specified scenario. The scenario ID must refer to an existing scenario. Operation fails if a player character already exists."
    
    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    
    try:
        player, scenario = simulated_characters.create_player(
            identity=identity,
            physical=physical,
            psychological=psychological,
            knowledge=knowledge,
            scenario_id=scenario_id,
        )
    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("create_player", True, str(e))],
            messages_field_to_update: [ToolMessage(get_observation(simulated_characters.characters_count(), "create_player", True, str(e)), tool_call_id=tool_call_id)]
        })
    
    return Command(update={
        logs_field_to_update: [get_log_item("create_player", True, f"Player '{player.identity.full_name}' created with id {player.id} in scenario {scenario.name} with id {scenario.id}.")],
        messages_field_to_update: [ToolMessage(get_observation(simulated_characters.characters_count(), "create_player", True, f"Player '{player.identity.full_name}' created with id {player.id} in scenario {scenario.name} with id {scenario.id}."), tool_call_id=tool_call_id)]
    })


@tool(args_schema=ToolFinalizeSimulationArgs)
def finalize_simulation(
    justification: str,
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Mark the simulation as completed with a justification."""
    simulated_characters_state.task_finalized_by_agent = True
    simulated_characters_state.task_finalized_justification = justification
    observation = simulated_characters_state._log_and_summarize(
        "finalize_simulation",
        BaseModel(),
        True,
        justification,
    )
    return Command(update={
        logs_field_to_update: [get_log_item("finalize_simulation", True, justification)],
        messages_field_to_update: [ToolMessage(get_observation(len(simulated_characters_state.simulated_characters), "finalize_simulation", True, justification), tool_call_id=tool_call_id)],
        "task_finalized_by_agent": True,
        "task_finalized_justification": justification,
    })





@tool(args_schema=ToolGetPlayerDetailsArgs)
def get_player_details(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """(QUERY tool) Get details of the player character."""
    observation = simulated_characters_state.get_player_details(args_model=GetPlayerDetailsArgs())
    return Command(update={
        logs_field_to_update: [get_log_item("get_player_details", True, "Player details retrieved")],
        messages_field_to_update: [ToolMessage(observation, tool_call_id=tool_call_id)]
    })


@tool(args_schema=ToolListCharactersArgs)
def list_characters(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    attribute_to_filter: Optional[Literal[ "narrative_role","current_narrative_importance", "species","profession","gender","alias","name_contains"]] = None,
    value_to_match: Optional[str] = None,
    max_results: Optional[int] = 10,
    list_identity: bool = False,
    list_physical: bool = False,
    list_psychological: bool = False,
    list_knowledge: bool = False,
    list_dynamic_state: bool = False,
    list_narrative: bool = False,
) -> str:
    """(QUERY tool) List characters optionally filtered by an attribute."""
    args_model = ListCharactersArgs(
        attribute_to_filter=attribute_to_filter,
        value_to_match=value_to_match,
        max_results=max_results,
        list_identity=list_identity,
        list_physical=list_physical,
        list_psychological=list_psychological,
        list_knowledge=list_knowledge,
        list_dynamic_state=list_dynamic_state,
        list_narrative=list_narrative,
    )
    return simulated_characters_state.list_characters(args_model=args_model)


@tool(args_schema=ToolListCharactersByScenarioArgs)
def list_characters_by_scenario(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")]
) -> str:
    """(QUERY tool) List characters grouped by scenario."""
    args_model = ListCharactersByScenarioArgs()
    return simulated_characters_state.list_characters_by_scenario(args_model=args_model)


@tool(args_schema=ToolGetCharacterDetailsArgs)
def get_character_details(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    character_id: str,
) -> str:
    """(QUERY tool) Get full details of a character."""
    args_model = GetCharacterDetailsArgs(character_id=character_id)
    return simulated_characters_state.get_character_details(args_model=args_model)



@tool(args_schema=ToolModifyIdentityArgs)
def modify_identity(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    character_id: str,
    new_full_name: Optional[str] = None,
    new_alias: Optional[str] = None,
    new_age: Optional[int] = None,
    new_gender: Optional[Gender] = None,
    new_profession: Optional[str] = None,
    new_species: Optional[str] = None,
    new_alignment: Optional[str] = None,
) -> str:
    """(MODIFICATION tool) Update identity attributes of a character."""

    # Works for both NPCs and the player.
    args_model = ModifyIdentityArgs(
        character_id=character_id,
        new_full_name=new_full_name,
        new_alias=new_alias,
        new_age=new_age,
        new_gender=new_gender,
        new_profession=new_profession,
        new_species=new_species,
        new_alignment=new_alignment,
    )
    char = simulated_characters_state.simulated_characters.get(character_id)
    if not char:
        return simulated_characters_state._log_and_summarize(
            "modify_identity",
            args_model,
            False,
            f"Error: Character ID '{character_id}' not found.",
        )

    updated_fields = []
    if new_full_name is not None:
        char.identity.full_name = new_full_name
        updated_fields.append("full_name")
    if new_alias is not None:
        char.identity.alias = new_alias
        updated_fields.append("alias")
    if new_age is not None:
        char.identity.age = new_age
        updated_fields.append("age")
    if new_gender is not None:
        char.identity.gender = new_gender
        updated_fields.append("gender")
    if new_profession is not None:
        char.identity.profession = new_profession
        updated_fields.append("profession")
    if new_species is not None:
        char.identity.species = new_species
        updated_fields.append("species")
    if new_alignment is not None:
        char.identity.alignment = new_alignment
        updated_fields.append("alignment")

    message = "No changes applied." if not updated_fields else f"Updated fields: {', '.join(updated_fields)}."
    return simulated_characters_state._log_and_summarize(
        "modify_identity",
        args_model,
        True,
        message,
    )


@tool(args_schema=ToolModifyPhysicalArgs)
def modify_physical(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    character_id: str,
    new_appearance: Optional[str] = None,
    new_distinctive_features: Optional[list] = None,
    append_distinctive_features: bool = False,
    new_clothing_style: Optional[str] = None,
    new_characteristic_items: Optional[list] = None,
    append_characteristic_items: bool = False,
) -> str:
    """(MODIFICATION tool) Update physical traits of a character."""

    # Works for both NPCs and the player.
    args_model = ModifyPhysicalArgs(
        character_id=character_id,
        new_appearance=new_appearance,
        new_distinctive_features=new_distinctive_features,
        append_distinctive_features=append_distinctive_features,
        new_clothing_style=new_clothing_style,
        new_characteristic_items=new_characteristic_items,
        append_characteristic_items=append_characteristic_items,
    )
    char = simulated_characters_state.simulated_characters.get(character_id)
    if not char:
        return simulated_characters_state._log_and_summarize(
            "modify_physical",
            args_model,
            False,
            f"Error: Character ID '{character_id}' not found.",
        )

    updated_fields = []
    if new_appearance is not None:
        char.physical.appearance = new_appearance
        updated_fields.append("appearance")
    if new_distinctive_features is not None:
        if args_model.append_distinctive_features:
            char.physical.distinctive_features.extend(new_distinctive_features)
        else:
            char.physical.distinctive_features = new_distinctive_features
        updated_fields.append("distinctive_features")
    if new_clothing_style is not None:
        char.physical.clothing_style = new_clothing_style
        updated_fields.append("clothing_style")
    if new_characteristic_items is not None:
        if args_model.append_characteristic_items:
            char.physical.characteristic_items.extend(new_characteristic_items)
        else:
            char.physical.characteristic_items = new_characteristic_items
        updated_fields.append("characteristic_items")

    message = "No changes applied." if not updated_fields else f"Updated fields: {', '.join(updated_fields)}."
    return simulated_characters_state._log_and_summarize(
        "modify_physical",
        args_model,
        True,
        message,
    )


@tool(args_schema=ToolModifyPsychologicalArgs)
def modify_psychological(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    character_id: str,
    new_personality_summary: Optional[str] = None,
    new_personality_tags: Optional[list] = None,
    append_personality_tags: bool = False,
    new_motivations: Optional[list] = None,
    append_motivations: bool = False,
    new_values: Optional[list] = None,
    append_values: bool = False,
    new_fears_and_weaknesses: Optional[list] = None,
    append_fears_and_weaknesses: bool = False,
    new_communication_style: Optional[str] = None,
    new_backstory: Optional[str] = None,
    new_quirks: Optional[list] = None,
    append_quirks: bool = False,
) -> str:
    """(MODIFICATION tool) Update psychological traits of a character."""

    # Works for both NPCs and the player.
    args_model = ModifyPsychologicalArgs(
        character_id=character_id,
        new_personality_summary=new_personality_summary,
        new_personality_tags=new_personality_tags,
        append_personality_tags=append_personality_tags,
        new_motivations=new_motivations,
        append_motivations=append_motivations,
        new_values=new_values,
        append_values=append_values,
        new_fears_and_weaknesses=new_fears_and_weaknesses,
        append_fears_and_weaknesses=append_fears_and_weaknesses,
        new_communication_style=new_communication_style,
        new_backstory=new_backstory,
        new_quirks=new_quirks,
        append_quirks=append_quirks,
    )
    char = simulated_characters_state.simulated_characters.get(character_id)
    if not char:
        return simulated_characters_state._log_and_summarize(
            "modify_psychological",
            args_model,
            False,
            f"Error: Character ID '{character_id}' not found.",
        )

    updated_fields = []
    if new_personality_summary is not None:
        char.psychological.personality_summary = new_personality_summary
        updated_fields.append("personality_summary")
    if new_personality_tags is not None:
        if args_model.append_personality_tags:
            char.psychological.personality_tags.extend(new_personality_tags)
        else:
            char.psychological.personality_tags = new_personality_tags
        updated_fields.append("personality_tags")
    if new_motivations is not None:
        if args_model.append_motivations:
            char.psychological.motivations.extend(new_motivations)
        else:
            char.psychological.motivations = new_motivations
        updated_fields.append("motivations")
    if new_values is not None:
        if args_model.append_values:
            char.psychological.values.extend(new_values)
        else:
            char.psychological.values = new_values
        updated_fields.append("values")
    if new_fears_and_weaknesses is not None:
        if args_model.append_fears_and_weaknesses:
            char.psychological.fears_and_weaknesses.extend(new_fears_and_weaknesses)
        else:
            char.psychological.fears_and_weaknesses = new_fears_and_weaknesses
        updated_fields.append("fears_and_weaknesses")
    if new_communication_style is not None:
        char.psychological.communication_style = new_communication_style
        updated_fields.append("communication_style")
    if new_backstory is not None:
        char.psychological.backstory = new_backstory
        updated_fields.append("backstory")
    if new_quirks is not None:
        if args_model.append_quirks:
            char.psychological.quirks.extend(new_quirks)
        else:
            char.psychological.quirks = new_quirks
        updated_fields.append("quirks")

    message = "No changes applied." if not updated_fields else f"Updated fields: {', '.join(updated_fields)}."
    return simulated_characters_state._log_and_summarize(
        "modify_psychological",
        args_model,
        True,
        message,
    )


@tool(args_schema=ToolModifyKnowledgeArgs)
def modify_knowledge(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    character_id: str,
    new_background_knowledge: Optional[list] = None,
    append_background_knowledge: bool = False,
    new_acquired_knowledge: Optional[list] = None,
    append_acquired_knowledge: bool = False,
) -> str:
    """(MODIFICATION tool) Update a character's knowledge."""

    # Works for both NPCs and the player.
    args_model = ModifyKnowledgeArgs(
        character_id=character_id,
        new_background_knowledge=new_background_knowledge,
        append_background_knowledge=append_background_knowledge,
        new_acquired_knowledge=new_acquired_knowledge,
        append_acquired_knowledge=append_acquired_knowledge,
    )
    char = simulated_characters_state.simulated_characters.get(character_id)
    if not char:
        return simulated_characters_state._log_and_summarize(
            "modify_knowledge",
            args_model,
            False,
            f"Error: Character ID '{character_id}' not found.",
        )

    updated_fields = []
    if new_background_knowledge is not None:
        if args_model.append_background_knowledge:
            char.knowledge.background_knowledge.extend(new_background_knowledge)
        else:
            char.knowledge.background_knowledge = new_background_knowledge
        updated_fields.append("background_knowledge")
    if new_acquired_knowledge is not None:
        if args_model.append_acquired_knowledge:
            char.knowledge.acquired_knowledge.extend(new_acquired_knowledge)
        else:
            char.knowledge.acquired_knowledge = new_acquired_knowledge
        updated_fields.append("acquired_knowledge")

    message = "No changes applied." if not updated_fields else f"Updated fields: {', '.join(updated_fields)}."
    return simulated_characters_state._log_and_summarize(
        "modify_knowledge",
        args_model,
        True,
        message,
    )


@tool(args_schema=ToolModifyDynamicStateArgs)
def modify_dynamic_state(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    character_id: str,
    new_current_emotion: Optional[str] = None,
    new_immediate_goal: Optional[str] = None,
) -> str:
    """(MODIFICATION tool) Update an NPC's dynamic state.

    This tool does not work on the player character.
    """
    args_model = ModifyDynamicStateArgs(
        character_id=character_id,
        new_current_emotion=new_current_emotion,
        new_immediate_goal=new_immediate_goal,
    )
    char = simulated_characters_state.simulated_characters.get(character_id)
    if not char:
        return simulated_characters_state._log_and_summarize(
            "modify_dynamic_state",
            args_model,
            False,
            f"Error: Character ID '{character_id}' not found.",
        )

    if isinstance(char, PlayerCharacterModel):
        return simulated_characters_state._log_and_summarize(
            "modify_dynamic_state",
            args_model,
            False,
            "Error: Cannot modify the player's dynamic state.",
        )

    assert isinstance(char, NonPlayerCharacterModel), "Character must be an NPC."

    updated_fields = []
    if new_current_emotion is not None:
        char.dynamic_state.current_emotion = new_current_emotion
        updated_fields.append("current_emotion")
    if new_immediate_goal is not None:
        char.dynamic_state.immediate_goal = new_immediate_goal
        updated_fields.append("immediate_goal")

    message = "No changes applied." if not updated_fields else f"Updated fields: {', '.join(updated_fields)}."
    return simulated_characters_state._log_and_summarize(
        "modify_dynamic_state",
        args_model,
        True,
        message,
    )


@tool(args_schema=ToolModifyNarrativeArgs)
def modify_narrative(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    character_id: str,
    new_narrative_role: Optional[NarrativeRole] = None,
    new_current_narrative_importance: Optional[NarrativeImportance] = None,
    new_narrative_purposes: Optional[list] = None,
    append_narrative_purposes: bool = False,
) -> str:
    """(MODIFICATION tool) Update an NPC's narrative attributes.

    """
    args_model = ModifyNarrativeArgs(
        character_id=character_id,
        new_narrative_role=new_narrative_role,
        new_current_narrative_importance=new_current_narrative_importance,
        new_narrative_purposes=new_narrative_purposes,
        append_narrative_purposes=append_narrative_purposes,
    )
    char = simulated_characters_state.simulated_characters.get(character_id)
    if not char:
        return simulated_characters_state._log_and_summarize(
            "modify_narrative",
            args_model,
            False,
            f"Error: Character ID '{character_id}' not found.",
        )

    if isinstance(char, PlayerCharacterModel):
        return simulated_characters_state._log_and_summarize(
            "modify_narrative",
            args_model,
            False,
            "Error: Cannot modify the player's narrative attributes.",
        )
    assert isinstance(char, NonPlayerCharacterModel), "Character must be an NPC."
    updated_fields = []
    if new_narrative_role is not None:
        char.narrative.narrative_role = new_narrative_role
        updated_fields.append("narrative_role")
    if new_current_narrative_importance is not None:
        char.narrative.current_narrative_importance = new_current_narrative_importance
        updated_fields.append("current_narrative_importance")
    if new_narrative_purposes is not None:
        if args_model.append_narrative_purposes:
            char.narrative.narrative_purposes.extend(new_narrative_purposes)
        else:
            char.narrative.narrative_purposes = new_narrative_purposes
        updated_fields.append("narrative_purposes")

    message = "No changes applied." if not updated_fields else f"Updated fields: {', '.join(updated_fields)}."
    return simulated_characters_state._log_and_summarize(
        "modify_narrative",
        args_model,
        True,
        message,
    )


@tool(args_schema=ToolPlaceCharacterArgs)
def place_character(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    character_id: str,
    new_scenario_id: str,
) -> str:
    """(MODIFICATION tool) Place a character into a scenario.

    If the character is already in another scenario, it will be moved to the
    provided one. Works on both NPCs and the player.
    """

    args_model = PlaceCharacterArgs(character_id=character_id, new_scenario_id=new_scenario_id)

    char = simulated_characters_state.simulated_characters.get(character_id)
    if not char:
        return simulated_characters_state._log_and_summarize(
            "place_character",
            args_model,
            False,
            f"Error: Character ID '{character_id}' not found.",
        )

    previous_scenario = char.present_in_scenario
    char.present_in_scenario = new_scenario_id
    action = "moved" if previous_scenario and previous_scenario != new_scenario_id else "placed"
    return simulated_characters_state._log_and_summarize(
        "place_character",
        args_model,
        True,
        f"Character '{char.identity.full_name}' {action} to scenario {new_scenario_id}.",
    )


@tool(args_schema=ToolRemoveCharacterFromScenarioArgs)
def remove_character_from_scenario(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    character_id: str,
) -> str:
    """(MODIFICATION tool) Remove an NPC from its current scenario.
    """

    args_model = RemoveCharacterFromScenarioArgs(character_id=character_id)

    char = simulated_characters_state.simulated_characters.get(character_id)
    if not char:
        return simulated_characters_state._log_and_summarize(
            "remove_character_from_scenario",
            args_model,
            False,
            f"Error: Character ID '{character_id}' not found.",
        )

    if isinstance(char, PlayerCharacterModel):
        return simulated_characters_state._log_and_summarize(
            "remove_character_from_scenario",
            args_model,
            False,
            "Error: Cannot remove the player from a scenario.",
        )

    char.present_in_scenario = None
    return simulated_characters_state._log_and_summarize(
        "remove_character_from_scenario",
        args_model,
        True,
        f"Character '{char.identity.full_name}' removed from its scenario.",
    )


@tool(args_schema=ToolDeleteCharacterArgs)
def delete_character(
    simulated_characters_state: Annotated[SimulatedCharactersModel, InjectedState("working_simulated_characters")],
    character_id: str,
) -> str:
    """(MODIFICATION tool) Delete an NPC from the cast. The player cannot be deleted."""
    args_model = DeleteCharacterArgs(character_id=character_id)

    char = simulated_characters_state.simulated_characters.get(character_id)
    if not char:
        return simulated_characters_state._log_and_summarize(
            "delete_character",
            args_model,
            False,
            f"Error: Character ID '{character_id}' not found.",
        )

    if isinstance(char, PlayerCharacterModel):
        return simulated_characters_state._log_and_summarize(
            "delete_character",
            args_model,
            False,
            "Error: Cannot delete the player character.",
        )

    simulated_characters_state.simulated_characters.pop(character_id)
    simulated_characters_state.deleted_characters[character_id] = char
    return simulated_characters_state._log_and_summarize(
        "delete_character",
        args_model,
        True,
        f"Character '{char.identity.full_name}' deleted.",
    )


EXECUTORTOOLS = [
    create_npc,
    create_player,
    list_characters,
    list_characters_by_scenario,
    get_player_details,
    get_character_details,
    modify_identity,
    modify_physical,
    modify_psychological,
    modify_knowledge,
    modify_dynamic_state,
    modify_narrative,
    place_character,
    remove_character_from_scenario,
    delete_character,
    finalize_simulation,
]

