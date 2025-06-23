"""Tool functions used by the character agent."""

"""Tool functions used by the character agent."""

from typing import Annotated, Optional, Literal, List
from core_game.character.constants import Gender, NarrativeImportance, NarrativeRole
from pydantic import BaseModel
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from pydantic import Field
from subsystems.agents.utils.schemas import InjectedToolContext
from .helpers import get_log_item, get_observation, _format_nested_dict
from simulated.game_state import SimulatedGameStateSingleton
from core_game.character.schemas import NarrativePurposeModel
import json

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
    scenario_id: str = Field(..., description="ID of the scenario where the player starts. The scenario must exist")

class ToolModifyIdentityArgs(InjectedToolContext):
    character_id: str = Field(...,description="ID of the character (NPC or player) to modify",)
    new_full_name: Optional[str] = Field(None, description="New full name")
    new_alias: Optional[str] = Field(None, description="New alias")
    new_age: Optional[int] = Field(None, description="New age")
    new_gender: Optional[Gender] = Field(None, description="New gender")
    new_profession: Optional[str] = Field(None, description="New profession")
    new_species: Optional[str] = Field(None, description="New species")
    new_alignment: Optional[str] = Field(None, description="New alignment")

class ToolModifyPhysicalArgs(InjectedToolContext):
    character_id: str = Field(..., description="ID of the character (NPC or player) to modify",)
    new_appearance: Optional[str] = Field(None, description="New appearance")
    new_distinctive_features: Optional[List[str]] = Field(None, description="New distinctive features list")
    append_distinctive_features: bool = Field(default=False,description="Append features instead of replacing the list",)
    new_clothing_style: Optional[str] = Field(None, description="New clothing style")
    new_characteristic_items: Optional[List[str]] = Field(None, description="New characteristic items list")
    append_characteristic_items: bool = Field(default=False,description="Append items instead of replacing the list",)

class ToolModifyPsychologicalArgs(InjectedToolContext):
    character_id: str = Field(..., description="ID of the character (NPC or player) to modify")
    new_personality_summary: Optional[str] = Field(None, description="New personality summary")
    new_personality_tags: Optional[List[str]] = Field(None, description="New personality tags")
    append_personality_tags: bool = Field(default=False, description="Append personality tags instead of replacing the list")
    new_motivations: Optional[List[str]] = Field(None, description="New motivations")
    append_motivations: bool = Field(default=False, description="Append motivations instead of replacing the list")
    new_values: Optional[List[str]] = Field(None, description="New values")
    append_values: bool = Field(default=False, description="Append values instead of replacing the list")
    new_fears_and_weaknesses: Optional[List[str]] = Field(None, description="New fears and weaknesses")
    append_fears_and_weaknesses: bool = Field(default=False, description="Append fears and weaknesses instead of replacing the list")
    new_communication_style: Optional[str] = Field(None, description="New communication style")
    new_backstory: Optional[str] = Field(None, description="New backstory")
    new_quirks: Optional[List[str]] = Field(None, description="New quirks list")
    append_quirks: bool = Field(default=False, description="Append quirks instead of replacing the list")

class ToolModifyKnowledgeArgs(InjectedToolContext):
    character_id: str = Field(..., description="ID of the character (NPC or player) to modify")
    new_background_knowledge: Optional[List[str]] = Field(None, description="New background knowledge")
    append_background_knowledge: bool = Field(default=False, description="Append background knowledge instead of replacing the list")
    new_acquired_knowledge: Optional[List[str]] = Field(None, description="New acquired knowledge")
    append_acquired_knowledge: bool = Field(default=False, description="Append acquired knowledge instead of replacing the list")

class ToolModifyDynamicStateArgs(InjectedToolContext):
    character_id: str = Field(..., description="ID of the NPC to modify; the player cannot be modified")
    new_current_emotion: Optional[str] = Field(None, description="New current emotion")
    new_immediate_goal: Optional[str] = Field(None, description="New immediate goal")

class ToolModifyNarrativeArgs(InjectedToolContext):
    character_id: str = Field(..., description="ID of the NPC to modify; the player cannot be modified")
    new_narrative_role: Optional[NarrativeRole] = Field(None, description="New narrative role")
    new_current_narrative_importance: Optional[NarrativeImportance] = Field(None, description="New narrative importance")
    new_narrative_purposes: Optional[List[NarrativePurposeModel]] = Field(None, description="New narrative purposes")
    append_narrative_purposes: bool = Field(default=False, description="Append narrative purposes instead of replacing the list")

class ToolDeleteCharacterArgs(InjectedToolContext):
    character_id: str = Field(..., description="ID of the NPC to delete. The player character cannot be deleted.")

class ToolPlaceCharacterArgs(InjectedToolContext):
    character_id: str = Field(..., description="ID of the character to place or move")
    new_scenario_id: str = Field(..., description="ID of the destination scenario. If the character was already in a scenario, it will be relocated here")

class ToolRemoveCharacterFromScenarioArgs(InjectedToolContext):
    character_id: str = Field(..., description="ID of the NPC to unplace; the player cannot be removed from its scenario.")

class ToolGetPlayerDetailsArgs(InjectedToolContext):
    pass

class ToolGetCharacterDetailsArgs(InjectedToolContext):
    character_id: str = Field(..., description="ID of the character")

class ToolListCharactersArgs(InjectedToolContext):
    attribute_to_filter: Optional[Literal[
        "narrative_role",
        "current_narrative_importance",
        "species",
        "profession",
        "gender",
        "alias",
        "name_contains",
    ]] = Field(
        default=None,
        description="Optional attribute to filter by",
    )
    value_to_match: Optional[str] = Field(default=None, description="Value that the attribute should match")
    max_results: Optional[int] = Field(default=10, le=25, description="Maximum number of characters to list when filtering")
    list_identity: bool = Field(default=False, description="Include full identity fields when listing")
    list_physical: bool = Field(default=False, description="Include physical attributes when listing")
    list_psychological: bool = Field(default=False, description="Include psychological traits when listing")
    list_knowledge: bool = Field(default=False, description="Include knowledge fields when listing")
    list_dynamic_state: bool = Field(default=False, description="Include dynamic state when listing")
    list_narrative: bool = Field(default=False, description="Include narrative attributes when listing")

class ToolListCharactersByScenarioArgs(InjectedToolContext):
    pass

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
    dynamic_state: DynamicStateModel
) -> Command:
    """Create a new NPC providing its detailed information information."""

    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters

    npc = simulated_characters.create_npc(
        identity=identity,
        physical=physical,
        psychological=psychological,
        narrative=narrative,
        knowledge=knowledge,
        dynamic_state=dynamic_state
    )

    return Command(update={
        logs_field_to_update: [get_log_item("create_npc", True, f"NPC '{identity.full_name}' created with id {npc.id}.")],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_characters.characters_count(), "create_npc", True, f"NPC '{identity.full_name}' created with id {npc.id}."),
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
            logs_field_to_update: [get_log_item("create_player", False, str(e))],
            messages_field_to_update: [ToolMessage(get_observation(simulated_characters.characters_count(), "create_player", False, str(e)), tool_call_id=tool_call_id)]
        })
    
    return Command(update={
        logs_field_to_update: [get_log_item("create_player", True, f"Player '{player.identity.full_name}' created with id {player.id} in scenario {scenario.name} with id {scenario.id}.")],
        messages_field_to_update: [ToolMessage(get_observation(simulated_characters.characters_count(), "create_player", True, f"Player '{player.identity.full_name}' created with id {player.id} in scenario {scenario.name} with id {scenario.id}."), tool_call_id=tool_call_id)]
    })

@tool(args_schema=ToolModifyIdentityArgs)
def modify_identity(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    character_id: str,
    new_full_name: Optional[str] = None,
    new_alias: Optional[str] = None,
    new_age: Optional[int] = None,
    new_gender: Optional[Gender] = None,
    new_profession: Optional[str] = None,
    new_species: Optional[str] = None,
    new_alignment: Optional[str] = None,
) -> Command:
    """Update identity attributes of a character."""

    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    try:
        simulated_characters.modify_character_identity(
            character_id=character_id,
            new_full_name=new_full_name,
            new_alias=new_alias,
            new_age=new_age,
            new_gender=new_gender,
            new_profession=new_profession,
            new_species=new_species,
            new_alignment=new_alignment
        )
    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("modify_identity", False, str(e))],
            messages_field_to_update: [ToolMessage(get_observation(simulated_characters.characters_count(), "modify_identity", False, str(e)), tool_call_id=tool_call_id)]
        })
    
    updated_fields = []
    if new_full_name is not None:
        updated_fields.append("full_name")
    if new_alias is not None:
        updated_fields.append("alias")
    if new_age is not None:
        updated_fields.append("age")
    if new_gender is not None:
        updated_fields.append("gender")
    if new_profession is not None:
        updated_fields.append("profession")
    if new_species is not None:
        updated_fields.append("species")
    if new_alignment is not None:
        updated_fields.append("alignment")

    message = "No changes applied." if not updated_fields else f"Updated fields: {', '.join(updated_fields)}."

    return Command(update={
        logs_field_to_update: [get_log_item("modify_identity", True, message)],
        messages_field_to_update: [ToolMessage(get_observation(simulated_characters.characters_count(), "modify_identity", True, message), tool_call_id=tool_call_id)]
    })


@tool(args_schema=ToolModifyPhysicalArgs)
def modify_physical(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    character_id: str,
    new_appearance: Optional[str] = None,
    new_distinctive_features: Optional[List[str]] = None,
    append_distinctive_features: bool = False,
    new_clothing_style: Optional[str] = None,
    new_characteristic_items: Optional[List[str]] = None,
    append_characteristic_items: bool = False,
) -> Command:
    """Update physical traits of a character."""

    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    try:
        simulated_characters.modify_character_physical(
            character_id=character_id,
            new_appearance=new_appearance,
            new_distinctive_features=new_distinctive_features,
            append_distinctive_features=append_distinctive_features,
            new_clothing_style=new_clothing_style,
            new_characteristic_items=new_characteristic_items,
            append_characteristic_items=append_characteristic_items,
        )
    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("modify_physical", False, str(e))],
            messages_field_to_update: [ToolMessage(get_observation(simulated_characters.characters_count(), "modify_physical", False, str(e)), tool_call_id=tool_call_id)]
        })

    updated_fields = []
    if new_appearance is not None:
        updated_fields.append("appearance")
    if new_distinctive_features is not None:
        updated_fields.append("distinctive_features")
    if new_clothing_style is not None:
        updated_fields.append("clothing_style")
    if new_characteristic_items is not None:
        updated_fields.append("characteristic_items")

    message = "No changes applied." if not updated_fields else f"Updated fields: {', '.join(updated_fields)}."

    return Command(update={
        logs_field_to_update: [get_log_item("modify_physical", True, message)],
        messages_field_to_update: [ToolMessage(get_observation(simulated_characters.characters_count(), "modify_physical", True, message), tool_call_id=tool_call_id)]
    })

@tool(args_schema=ToolModifyPsychologicalArgs)
def modify_psychological(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    character_id: str,
    new_personality_summary: Optional[str] = None,
    new_personality_tags: Optional[List[str]] = None,
    append_personality_tags: bool = False,
    new_motivations: Optional[List[str]] = None,
    append_motivations: bool = False,
    new_values: Optional[List[str]] = None,
    append_values: bool = False,
    new_fears_and_weaknesses: Optional[List[str]] = None,
    append_fears_and_weaknesses: bool = False,
    new_communication_style: Optional[str] = None,
    new_backstory: Optional[str] = None,
    new_quirks: Optional[List[str]] = None,
    append_quirks: bool = False,
) -> Command:
    """Update psychological traits of a character."""

    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    try:
        simulated_characters.modify_character_psychological(
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
    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("modify_psychological", False, str(e))],
            messages_field_to_update: [ToolMessage(get_observation(simulated_characters.characters_count(), "modify_psychological", False, str(e)), tool_call_id=tool_call_id)]
        })

    updated_fields = []
    if new_personality_summary is not None: updated_fields.append("personality_summary")
    if new_personality_tags is not None: updated_fields.append("personality_tags")
    if new_motivations is not None: updated_fields.append("motivations")
    if new_values is not None: updated_fields.append("values")
    if new_fears_and_weaknesses is not None: updated_fields.append("fears_and_weaknesses")
    if new_communication_style is not None: updated_fields.append("communication_style")
    if new_backstory is not None: updated_fields.append("backstory")
    if new_quirks is not None: updated_fields.append("quirks")

    message = "No changes applied." if not updated_fields else f"Updated fields: {', '.join(updated_fields)}."

    return Command(update={
        logs_field_to_update: [get_log_item("modify_psychological", True, message)],
        messages_field_to_update: [ToolMessage(get_observation(simulated_characters.characters_count(), "modify_psychological", True, message), tool_call_id=tool_call_id)]
    })


@tool(args_schema=ToolModifyKnowledgeArgs)
def modify_knowledge(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    character_id: str,
    new_background_knowledge: Optional[list] = None,
    append_background_knowledge: bool = False,
    new_acquired_knowledge: Optional[list] = None,
    append_acquired_knowledge: bool = False,
) -> Command:
    """Update a character's knowledge."""

    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    try:
        simulated_characters.modify_character_knowledge(
            character_id=character_id,
            new_background_knowledge=new_background_knowledge,
            append_background_knowledge=append_background_knowledge,
            new_acquired_knowledge=new_acquired_knowledge,
            append_acquired_knowledge=append_acquired_knowledge,
        )
    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("modify_knowledge", False, str(e))],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_characters.characters_count(), "modify_knowledge", False, str(e)),
                    tool_call_id=tool_call_id
                )
            ]
        })

    updated_fields = []
    if new_background_knowledge is not None:
        updated_fields.append("background_knowledge")
    if new_acquired_knowledge is not None:
        updated_fields.append("acquired_knowledge")

    message = "No changes applied." if not updated_fields else f"Updated fields: {', '.join(updated_fields)}."

    return Command(update={
        logs_field_to_update: [get_log_item("modify_knowledge", True, message)],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_characters.characters_count(), "modify_knowledge", True, message),
                tool_call_id=tool_call_id
            )
        ]
    })

@tool(args_schema=ToolModifyDynamicStateArgs)
def modify_dynamic_state(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    character_id: str,
    new_current_emotion: Optional[str] = None,
    new_immediate_goal: Optional[str] = None,
) -> Command:
    """Update an NPC's dynamic state. This tool does NOT work on the player character."""
    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    try:
        simulated_characters.modify_character_dynamic_state(
            character_id=character_id,
            new_current_emotion=new_current_emotion,
            new_immediate_goal=new_immediate_goal
        )
    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("modify_dynamic_state", False, str(e))],
            messages_field_to_update: [
                ToolMessage(get_observation(simulated_characters.characters_count(), "modify_dynamic_state", False, str(e)), tool_call_id=tool_call_id)
            ]
        })

    updated_fields = []
    if new_current_emotion is not None:
        updated_fields.append("current_emotion")
    if new_immediate_goal is not None:
        updated_fields.append("immediate_goal")

    message = "No changes applied." if not updated_fields else f"Updated fields: {', '.join(updated_fields)}."

    return Command(update={
        logs_field_to_update: [get_log_item("modify_dynamic_state", True, message)],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_characters.characters_count(), "modify_dynamic_state", True, message), tool_call_id=tool_call_id)
        ]
    })


@tool(args_schema=ToolModifyNarrativeArgs)
def modify_narrative(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    character_id: str,
    new_narrative_role: Optional[NarrativeRole] = None,
    new_current_narrative_importance: Optional[NarrativeImportance] = None,
    new_narrative_purposes: Optional[list] = None,
    append_narrative_purposes: bool = False,
) -> Command:
    """Update an NPC's narrative attributes. This tool does NOT work on the player character."""
    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    try:
        simulated_characters.modify_character_narrative(
            character_id=character_id,
            new_narrative_role=new_narrative_role,
            new_current_narrative_importance=new_current_narrative_importance,
            new_narrative_purposes=new_narrative_purposes,
            append_narrative_purposes=append_narrative_purposes,
        )

    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("modify_narrative", False, str(e))],
            messages_field_to_update: [
                ToolMessage(get_observation(simulated_characters.characters_count(), "modify_narrative", False, str(e)), tool_call_id=tool_call_id)
            ]
        })

    updated_fields = []
    if new_narrative_role is not None:
        updated_fields.append("narrative_role")
    if new_current_narrative_importance is not None:
        updated_fields.append("current_narrative_importance")
    if new_narrative_purposes is not None:
        updated_fields.append("narrative_purposes")

    message = "No changes applied." if not updated_fields else f"Updated fields: {', '.join(updated_fields)}."

    return Command(update={
        logs_field_to_update: [get_log_item("modify_narrative", True, message)],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_characters.characters_count(), "modify_narrative", True, message), tool_call_id=tool_call_id)
        ]
    })


@tool(args_schema=ToolDeleteCharacterArgs)
def delete_character(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    character_id: str,
) -> Command:
    """Delete an NPC from the cast. The player cannot be deleted. This tool should only be must to remove characters created by error or in exceptional ocasions. If you want to disable a character temporarly o permanetly remove_character_from_scenario tool instead"""
    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters

    try:
        character=simulated_characters.delete_character(character_id)

    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("delete_character", False, str(e))],
            messages_field_to_update: [
                ToolMessage(get_observation(simulated_characters.characters_count(), "delete_character", False, str(e)), tool_call_id=tool_call_id)
            ]
        })
    
    return Command(update={
        logs_field_to_update: [get_log_item("delete_character", True, f"Character {character.id} '{character.identity.full_name}' deleted.")],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_characters.characters_count(), "delete_character", True, f"Character {character.id} '{character.identity.full_name}' deleted."), tool_call_id=tool_call_id)
        ]
    })

@tool(args_schema=ToolPlaceCharacterArgs)
def place_character(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    character_id: str,
    new_scenario_id: str,
) -> Command:
    """Place a character into a scenario.
    If the character is already in another scenario, it will be moved to the provided one. Works on both NPCs and the player.
    """

    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    try:
        character, scenario = simulated_characters.place_character(character_id, new_scenario_id)
    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("place_character", False, str(e))],
            messages_field_to_update: [
                ToolMessage(get_observation(simulated_characters.characters_count(), "place_character", False, str(e)), tool_call_id=tool_call_id)
            ]
        })

    message = f"Character {character.id}, {character.identity.full_name} placed into scenario {scenario.id}, {scenario.name}."

    return Command(update={
        logs_field_to_update: [get_log_item("place_character", True, message)],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_characters.characters_count(), "place_character", True, message), tool_call_id=tool_call_id)
        ]
    })


@tool(args_schema=ToolRemoveCharacterFromScenarioArgs)
def remove_character_from_scenario(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    character_id: str,
) -> Command:
    """
    Removes an NPC from their current scenario. This means they are no longer present in any location and are considered temporarly inactive or absent from the game world. Player cannot be removed from a scenario, if you want to move it use the place_character.
    """
    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    try:
        character, scenario = simulated_characters.remove_character_from_scenario(character_id)
    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("remove_character_from_scenario", False, str(e))],
            messages_field_to_update: [
                ToolMessage(get_observation(simulated_characters.characters_count(), "remove_character_from_scenario", False, str(e)), tool_call_id=tool_call_id)
            ]
        })
    message = f"Character {character.id}, {character.identity.full_name} removed from scenario {scenario.id}, {scenario.name}."
    return Command(update={
        logs_field_to_update: [get_log_item("remove_character_from_scenario", True, message)],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_characters.characters_count(), "remove_character_from_scenario", True, message), tool_call_id=tool_call_id)
        ]
    })

@tool(args_schema=ToolGetPlayerDetailsArgs)
def get_player_details(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """(QUERY tool) Get details of the player character."""
    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    player = simulated_characters.get_player()
    if player is None:
        return Command(update={
            logs_field_to_update: [get_log_item("get_player_details", False, "Player character does not exist.")],
            messages_field_to_update: [
                ToolMessage(get_observation(simulated_characters.characters_count(), "get_player_details", False, "Player character does not exist."), tool_call_id=tool_call_id)
            ]
        })

    details = player.get_model().model_dump()
    details["present_in_scenario"] = player.present_in_scenario or "None"
    pretty_details = "\n"+"\n".join(_format_nested_dict(details))
    return Command(update={
        logs_field_to_update: [get_log_item("get_player_details", True, pretty_details)],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_characters.characters_count(), "get_player_details", True, pretty_details), tool_call_id=tool_call_id)
        ]
    })

@tool(args_schema=ToolGetCharacterDetailsArgs)
def get_character_details(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    character_id: str,
) -> Command:
    """(QUERY tool) Get full details of a character."""
    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    character = simulated_characters.get_character(character_id)
    if not character:
        return Command(update={
            logs_field_to_update: [get_log_item("get_character_details", False, f"Character with ID '{character_id}' not found.")],
            messages_field_to_update: [
                ToolMessage(get_observation(simulated_characters.characters_count(), "get_character_details", False, f"Character with ID '{character_id}' not found."), tool_call_id=tool_call_id)
            ]
        })
    
    details = character.get_model().model_dump()
    details["present_in_scenario"] = character.present_in_scenario or "None"
    pretty_details = "\n"+"\n".join(_format_nested_dict(details))
    return Command(update={
        logs_field_to_update: [get_log_item("get_character_details", True, pretty_details)],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_characters.characters_count(), "get_character_details", True, pretty_details), tool_call_id=tool_call_id)
        ]
    })


@tool(args_schema=ToolListCharactersArgs)
def list_characters(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    attribute_to_filter: Optional[Literal[ "narrative_role","current_narrative_importance", "species","profession","gender","alias","name_contains"]] = None,
    value_to_match: Optional[str] = None,
    max_results: Optional[int] = 10,
    list_identity: bool = False,
    list_physical: bool = False,
    list_psychological: bool = False,
    list_knowledge: bool = False,
    list_dynamic_state: bool = False,
    list_narrative: bool = False,
) -> Command:
    """(QUERY tool) List characters optionally filtered by an attribute."""
    
    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    
    if simulated_characters.characters_count()<=0:
        return Command(update={
            logs_field_to_update: [get_log_item("list_characters", True, "The cast is currently empty.")],
            messages_field_to_update: [
                ToolMessage(get_observation(simulated_characters.characters_count(), "list_characters", True, "The cast is currently empty."), tool_call_id=tool_call_id)
            ]
        })

    filtered_characters = simulated_characters.filter_characters(attribute_to_filter,value_to_match)

    if len(filtered_characters)<=0:
        return Command(update={
            logs_field_to_update: [get_log_item("list_characters", True, "No characters found matching the criteria.")],
            messages_field_to_update: [
                ToolMessage(get_observation(simulated_characters.characters_count(), "list_characters", True, "No characters found matching the criteria."), tool_call_id=tool_call_id)
            ]
        })

    matches: List[str] = []

    for char in filtered_characters.values():
        lines: List[str] = []
        lines.append(f"\n=== Character ID: {char.id} ===")
        lines.append(f"Name: {char.identity.full_name}")
        lines.append(f"Type: {char.type}")
        role = char.narrative.narrative_role if isinstance(char, NonPlayerCharacterModel) else "N/A"
        lines.append(f"Narrative Role: {role}")

        # Optional sections
        if list_identity:
            lines.append("--- Identity ---")
            lines.extend(_format_nested_dict(char.identity.model_dump(), indent=1))

        if list_physical:
            lines.append("--- Physical ---")
            lines.extend(_format_nested_dict(char.physical.model_dump(), indent=1))

        if list_psychological:
            lines.append("--- Psychological ---")
            lines.extend(_format_nested_dict(char.psychological.model_dump(), indent=1))

        if list_knowledge:
            lines.append("--- Knowledge ---")
            lines.extend(_format_nested_dict(char.knowledge.model_dump(), indent=1))

        if isinstance(char, NonPlayerCharacterModel) and list_dynamic_state:
            lines.append("--- Dynamic State ---")
            lines.extend(_format_nested_dict(char.dynamic_state.model_dump(), indent=1))

        if isinstance(char, NonPlayerCharacterModel) and list_narrative:
            lines.append("--- Narrative ---")
            lines.extend(_format_nested_dict(char.narrative.model_dump(), indent=1))

        matches.append("\n".join(lines))
        if max_results and len(matches) >= max_results:
            break

    return Command(update={
        logs_field_to_update: [get_log_item("list_characters", True, "\n".join(matches))],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_characters.characters_count(), "list_characters", True, "\n".join(matches)), tool_call_id=tool_call_id)
        ]
    })

@tool(args_schema=ToolListCharactersByScenarioArgs)
def list_characters_by_scenario(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """(QUERY tool) List characters grouped by scenario."""

    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    if simulated_characters.characters_count()<=0:
        return Command(update={
            logs_field_to_update: [get_log_item("list_characters_by_scenario", True, "The cast is currently empty.")],
            messages_field_to_update: [
                ToolMessage(get_observation(simulated_characters.characters_count(), "list_characters_by_scenario", True, "The cast is currently empty."), tool_call_id=tool_call_id)
            ]
        })

    groups = simulated_characters.group_by_scenario()

    lines: List[str] = []
    for scenario in sorted(groups.keys()):
        lines.append(f"Scenario '{scenario}':")
        lines.extend(f"  - {character.identity.full_name} ({character.id})" for character in groups[scenario])
        lines.append("")

    return Command(update={
        logs_field_to_update: [get_log_item("list_characters_by_scenario", True, "\n"+"\n".join(lines).strip())],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_characters.characters_count(), "list_characters_by_scenario", True, "\n"+"\n".join(lines).strip()), tool_call_id=tool_call_id)
        ]
    })




@tool(args_schema=ToolFinalizeSimulationArgs)
def finalize_simulation(
    justification: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Mark the simulation as completed with a justification."""
    simulated_characters = SimulatedGameStateSingleton.get_instance().simulated_characters
    return Command(update={
        logs_field_to_update: [get_log_item("finalize_simulation", True, justification)],
        messages_field_to_update: [ToolMessage(get_observation(simulated_characters.characters_count(), "finalize_simulation", True, justification), tool_call_id=tool_call_id)],
        "characters_task_finalized_by_agent": True,
        "characters_task_finalized_justification": justification,
    })


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

