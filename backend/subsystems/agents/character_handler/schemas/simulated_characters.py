"""Pydantic models used by the character creation agent."""

from typing import Dict, List, Any, Optional, Annotated, Literal
import json
from pydantic import BaseModel, Field 
from core_game.character.constants import Gender, NarrativeRole, NarrativeImportance


from core_game.character.schemas import (
    IdentityModel,
    PhysicalAttributesModel,
    PsychologicalAttributesModel,
    KnowledgeModel,
    DynamicStateModel,
    NarrativeWeightModel,
    NarrativePurposeModel,
    NonPlayerCharacterModel,
    PlayerCharacterModel,
    CharacterBaseModel,
)


def _format_nested_dict(data: Dict[str, Any], indent: int = 0) -> List[str]:
    """Pretty-print a nested dictionary with clean indentation and clear structure."""
    lines: List[str] = []
    indent_str = "    " * indent

    for key, value in data.items():
        display_key = str(key).replace("_", " ").capitalize()

        if isinstance(value, dict):
            lines.append(f"{indent_str}{display_key}:")
            lines.extend(_format_nested_dict(value, indent + 1))

        elif isinstance(value, list):
            lines.append(f"{indent_str}{display_key}:")
            if not value:
                lines.append(f"{indent_str}    (None)")
            else:
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{indent_str}    -")
                        lines.extend(_format_nested_dict(item, indent + 2))
                    else:
                        lines.append(f"{indent_str}    - {item}")

        elif value is None or value == "":
            lines.append(f"{indent_str}{display_key}: (None)")

        else:
            lines.append(f"{indent_str}{display_key}: {value}")

    return lines

class CreateNPCArgs(BaseModel):
    """Arguments required to create a NPC."""
    identity: IdentityModel = Field(..., description="Full identity information")
    physical: PhysicalAttributesModel = Field(..., description="Full physical description")
    psychological: PsychologicalAttributesModel = Field(..., description="Detailed psychological profile")
    knowledge: KnowledgeModel = Field(default_factory=KnowledgeModel, description="Initial knowledge state, aquired knowledge should be empty")
    dynamic_state: DynamicStateModel = Field(default_factory=DynamicStateModel, description="Initial dynamic state")
    narrative: NarrativeWeightModel = Field(..., description="Narrative role and importance")


class CreatePlayerArgs(BaseModel):
    """Arguments required to create the player character."""
    identity: IdentityModel = Field(..., description="Full identity information")
    physical: PhysicalAttributesModel = Field(..., description="Full physical description")
    psychological: PsychologicalAttributesModel = Field(..., description="Detailed psychological profile")
    knowledge: Optional[KnowledgeModel] = Field(default_factory=KnowledgeModel, description="Initial knowledge state")
    present_in_scenario: str = Field(..., description="ID of the scenario where the player starts")




class ModifyIdentityArgs(BaseModel):
    """Arguments for updating identity attributes on NPCs or the player."""

    character_id: str = Field(
        ...,
        description="ID of the character (NPC or player) to modify",
    )
    new_full_name: Optional[str] = Field(None, description="New full name")
    new_alias: Optional[str] = Field(None, description="New alias")
    new_age: Optional[int] = Field(None, description="New age")
    new_gender: Optional[Gender] = Field(
        None, description="New gender"
    )
    new_profession: Optional[str] = Field(None, description="New profession")
    new_species: Optional[str] = Field(None, description="New species")
    new_alignment: Optional[str] = Field(None, description="New alignment")


class ModifyPhysicalArgs(BaseModel):
    """Arguments for updating physical attributes on NPCs or the player."""

    character_id: str = Field(
        ...,
        description="ID of the character (NPC or player) to modify",
    )
    new_appearance: Optional[str] = Field(None, description="New appearance")
    new_distinctive_features: Optional[List[str]] = Field(
        None, description="New distinctive features list"
    )
    append_distinctive_features: bool = Field(
        default=False,
        description="Append features instead of replacing the list",
    )
    new_clothing_style: Optional[str] = Field(None, description="New clothing style")
    new_characteristic_items: Optional[List[str]] = Field(
        None, description="New characteristic items list"
    )
    append_characteristic_items: bool = Field(
        default=False,
        description="Append items instead of replacing the list",
    )


class ModifyPsychologicalArgs(BaseModel):
    """Arguments for updating psychological traits on NPCs or the player."""

    character_id: str = Field(
        ...,
        description="ID of the character (NPC or player) to modify",
    )
    new_personality_summary: Optional[str] = Field(None, description="New personality summary")
    new_personality_tags: Optional[List[str]] = Field(None, description="New personality tags")
    append_personality_tags: bool = Field(
        default=False,
        description="Append personality tags instead of replacing the list",
    )
    new_motivations: Optional[List[str]] = Field(None, description="New motivations")
    append_motivations: bool = Field(
        default=False,
        description="Append motivations instead of replacing the list",
    )
    new_values: Optional[List[str]] = Field(None, description="New values")
    append_values: bool = Field(
        default=False,
        description="Append values instead of replacing the list",
    )
    new_fears_and_weaknesses: Optional[List[str]] = Field(
        None, description="New fears and weaknesses"
    )
    append_fears_and_weaknesses: bool = Field(
        default=False,
        description="Append fears and weaknesses instead of replacing the list",
    )
    new_communication_style: Optional[str] = Field(None, description="New communication style")
    new_backstory: Optional[str] = Field(None, description="New backstory")
    new_quirks: Optional[List[str]] = Field(None, description="New quirks list")
    append_quirks: bool = Field(
        default=False,
        description="Append quirks instead of replacing the list",
    )


class ModifyKnowledgeArgs(BaseModel):
    """Arguments for updating knowledge on NPCs or the player."""

    character_id: str = Field(
        ...,
        description="ID of the character (NPC or player) to modify",
    )
    new_background_knowledge: Optional[List[str]] = Field(None, description="New background knowledge")
    append_background_knowledge: bool = Field(
        default=False,
        description="Append background knowledge instead of replacing the list",
    )
    new_acquired_knowledge: Optional[List[str]] = Field(None, description="New acquired knowledge")
    append_acquired_knowledge: bool = Field(
        default=False,
        description="Append acquired knowledge instead of replacing the list",
    )


class ModifyDynamicStateArgs(BaseModel):
    """Arguments for updating an NPC's dynamic state. Does not work on the player."""

    character_id: str = Field(
        ...,
        description="ID of the NPC to modify; the player cannot be modified",
    )
    new_current_emotion: Optional[str] = Field(None, description="New current emotion")
    new_immediate_goal: Optional[str] = Field(None, description="New immediate goal")


class ModifyNarrativeArgs(BaseModel):
    """Arguments for updating an NPC's narrative role. Does not work on the player."""

    character_id: str = Field(
        ...,
        description="ID of the NPC to modify; the player cannot be modified",
    )
    new_narrative_role: Optional[NarrativeRole] = Field(
        None, description="New narrative role"
    )
    new_current_narrative_importance: Optional[NarrativeImportance] = Field(
        None, description="New narrative importance"
    )
    new_narrative_purposes: Optional[List[NarrativePurposeModel]] = Field(
        None, description="New narrative purposes"
    )
    append_narrative_purposes: bool = Field(
        default=False,
        description="Append narrative purposes instead of replacing the list",
    )


class DeleteCharacterArgs(BaseModel):
    """Arguments for deleting an NPC. The player cannot be deleted."""

    character_id: str = Field(
        ...,
        description="ID of the NPC to delete. The player character cannot be deleted.",
    )


class PlaceCharacterArgs(BaseModel):
    """Arguments for placing a character in a scenario.

    If the character is already in another scenario, it will be moved to the
    specified one. This works for both NPCs and the player.
    """

    character_id: str = Field(
        ..., description="ID of the character to place or move"
    )
    new_scenario_id: str = Field(
        ...,
        description=(
            "ID of the destination scenario. If the character was already in a scenario, it will be relocated here"
        ),
    )


class RemoveCharacterFromScenarioArgs(BaseModel):
    """Arguments for removing a character from its current scenario.

    Only NPCs can be unplaced; the player must always belong to a scenario.
    """

    character_id: str = Field(
        ...,
        description="ID of the NPC to unplace; the player cannot be removed from its scenario.",
    )


class ListCharactersArgs(BaseModel):
    """Arguments for listing or filtering characters."""
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
    value_to_match: Optional[str] = Field(
        default=None,
        description="Value that the attribute should match",
    )
    max_results: Optional[int] = Field(
        default=10,
        le=25,
        description="Maximum number of characters to list when filtering",
    )
    list_identity: bool = Field(
        default=False,
        description="Include full identity fields when listing",
    )
    list_physical: bool = Field(
        default=False,
        description="Include physical attributes when listing",
    )
    list_psychological: bool = Field(
        default=False,
        description="Include psychological traits when listing",
    )
    list_knowledge: bool = Field(
        default=False,
        description="Include knowledge fields when listing",
    )
    list_dynamic_state: bool = Field(
        default=False,
        description="Include dynamic state when listing",
    )
    list_narrative: bool = Field(
        default=False,
        description="Include narrative attributes when listing",
    )


class GetCharacterDetailsArgs(BaseModel):
    """Arguments for retrieving a character's full details."""
    character_id: str = Field(..., description="ID of the character")


class GetPlayerDetailsArgs(BaseModel):
    """Arguments for retrieving details of the player character."""
    pass


class ListCharactersByScenarioArgs(BaseModel):
    """Arguments for listing characters grouped by scenario."""
    pass


class SimulatedCharactersModel(BaseModel):
    """In-memory representation of characters cast manipulated by the agent."""

    simulated_characters: Dict[str, CharacterBaseModel] = Field(default_factory=dict)
    deleted_characters: Dict[str, CharacterBaseModel] = Field(default_factory=dict)
    player_character: Optional[PlayerCharacterModel] = Field(default=None)
    executor_applied_operations_log: List[Dict[str, Any]] = Field(default_factory=list)

    validator_applied_operations_log: List[Dict[str, Any]] = Field(default_factory=list)

    task_finalized_by_agent: bool = Field(default=False)
    task_finalized_justification: Optional[str] = Field(default=None)
    executor_or_validator: Literal["executor", "validator"] = Field(default="executor", description="Whether the cast is currently being used by the executor agent or the validator agent.")

    @staticmethod
    def generate_sequential_character_id(existing_ids: List[str]) -> str:
        """Generate a unique sequential character id."""
        new_id = _generate_character_id()
        while new_id in existing_ids:
            new_id = _generate_character_id()
        return new_id

    def _log_and_summarize(self, tool_name: str, args: BaseModel, success: bool, message: str) -> str:
        """Helper to log the operation and create consistent observation messages."""
        if self.executor_or_validator == "executor":
            self.executor_applied_operations_log.append({
                "tool_called": tool_name,
                "args": args.model_dump(),
                "success": success,
                "message": message
            })
        else:
            self.validator_applied_operations_log.append({
                "tool_called": tool_name,
                "args": args.model_dump(),
                "success": success,
                "message": message
            })
        
        observation = f"Result of '{tool_name}': {message} \nCast has {len(self.simulated_characters)} characters."
        print(observation)
        return observation

    def get_summary(self) -> str:
        if not self.simulated_characters:
            return "No characters created yet."
        return "Characters: " + ", ".join(f"{c.identity.full_name}({cid})" for cid, c in self.simulated_characters.items())

    def list_characters(self, args_model: ListCharactersArgs) -> str:
        """(QUERY tool) Lists characters optionally filtered by an attribute."""
        if not self.simulated_characters:
            return self._log_and_summarize(
                "list_characters",
                args_model,
                True,
                "The cast is currently empty.",
            )

        matches: List[str] = []
        for char in self.simulated_characters.values():
            if args_model.attribute_to_filter and args_model.value_to_match:
                value = ""
                match_val = args_model.value_to_match.lower()
                if args_model.attribute_to_filter == "narrative_role":
                    if isinstance(char, NonPlayerCharacterModel):
                        value = char.narrative.narrative_role
                elif args_model.attribute_to_filter == "current_narrative_importance":
                    if isinstance(char, NonPlayerCharacterModel):
                        value = char.narrative.current_narrative_importance
                elif args_model.attribute_to_filter == "species":
                    value = char.identity.species
                elif args_model.attribute_to_filter == "profession":
                    value = char.identity.profession
                elif args_model.attribute_to_filter == "gender":
                    value = char.identity.gender
                elif args_model.attribute_to_filter == "alias":
                    value = char.identity.alias or ""
                elif args_model.attribute_to_filter == "name_contains":
                    value = char.identity.full_name
                if match_val not in str(value).lower():
                    continue

            lines: List[str] = []
            lines.append(f"\n=== Character ID: {char.id} ===")
            lines.append(f"Name: {char.identity.full_name}")
            lines.append(f"Type: {char.type}")
            role = char.narrative.narrative_role if isinstance(char, NonPlayerCharacterModel) else "N/A"
            lines.append(f"Narrative Role: {role}")

            # Optional sections
            if args_model.list_identity:
                lines.append("--- Identity ---")
                lines.extend(_format_nested_dict(char.identity.model_dump(), indent=1))

            if args_model.list_physical:
                lines.append("--- Physical ---")
                lines.extend(_format_nested_dict(char.physical.model_dump(), indent=1))

            if args_model.list_psychological:
                lines.append("--- Psychological ---")
                lines.extend(_format_nested_dict(char.psychological.model_dump(), indent=1))

            if args_model.list_knowledge:
                lines.append("--- Knowledge ---")
                lines.extend(_format_nested_dict(char.knowledge.model_dump(), indent=1))

            if isinstance(char, NonPlayerCharacterModel) and args_model.list_dynamic_state:
                lines.append("--- Dynamic State ---")
                lines.extend(_format_nested_dict(char.dynamic_state.model_dump(), indent=1))

            if isinstance(char, NonPlayerCharacterModel) and args_model.list_narrative:
                lines.append("--- Narrative ---")
                lines.extend(_format_nested_dict(char.narrative.model_dump(), indent=1))

            matches.append("\n".join(lines))
            if args_model.max_results and len(matches) >= args_model.max_results:
                break

        if not matches:
            return self._log_and_summarize(
                "list_characters",
                args_model,
                True,
                "No characters found matching the criteria.",
            )

        return self._log_and_summarize(
            "list_characters",
            args_model,
            True,
            "\n".join(matches),
        )

    def list_characters_by_scenario(
        self, args_model: ListCharactersByScenarioArgs
    ) -> str:
        """(QUERY tool) Lists characters grouped by their current scenario."""
        if not self.simulated_characters:
            return self._log_and_summarize(
                "list_characters_by_scenario",
                args_model,
                True,
                "The cast is currently empty.",
            )

        groups: Dict[str, List[str]] = {}
        for char in self.simulated_characters.values():
            scenario = char.present_in_scenario or "OUT_OF_ANY_SCENARIO"
            groups.setdefault(scenario, []).append(
                f"{char.identity.full_name} ({char.id})"
            )

        lines: List[str] = []
        for scenario in sorted(groups.keys()):
            lines.append(f"Scenario '{scenario}':")
            lines.extend(f"  - {name}" for name in sorted(groups[scenario]))
            lines.append("")
        return self._log_and_summarize(
            "list_characters_by_scenario",
            args_model,
            True,
            "\n"+"\n".join(lines).strip(),
        )


    def get_player_details(self, args_model: GetPlayerDetailsArgs) -> str:
        """(QUERY tool) Get details about the player character."""
        if self.player_character is None:
            return self._log_and_summarize(
                "get_player_details",
                args_model,
                False,
                "Error: Player character does not exist.",
            )

        player = self.player_character
        details = player.model_dump()
        details["present_in_scenario"] = player.present_in_scenario or "None"
        pretty_details = "\n"+"\n".join(_format_nested_dict(details))
        return self._log_and_summarize(
            "get_player_details",
            args_model,
            True,
            pretty_details,
        )

    def get_character_details(self, args_model: GetCharacterDetailsArgs) -> str:
        """(QUERY tool) Returns detailed information for a character."""
        if self.player_character and self.player_character.id == args_model.character_id:
            char = self.player_character
        else:
            char = self.simulated_characters.get(args_model.character_id)
        if not char:
            return self._log_and_summarize(
                "get_character_details",
                args_model,
                False,
                f"Error: Character ID '{args_model.character_id}' not found.",
            )

        details = char.model_dump()
        details["present_in_scenario"] = char.present_in_scenario or "None"
        pretty_details = "\n"+"\n".join(_format_nested_dict(details))
        return self._log_and_summarize(
            "get_character_details",
            args_model,
            True,
            pretty_details,
        )



