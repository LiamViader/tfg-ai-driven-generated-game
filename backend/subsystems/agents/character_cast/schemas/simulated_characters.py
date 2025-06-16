"""Pydantic models used by the character creation agent."""

from typing import Dict, List, Any, Optional, Annotated, Literal
from pydantic import BaseModel, Field as PydanticField, model_validator


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
    _generate_character_id,
)


class CreateNPCArgs(BaseModel):
    """Arguments required to create a NPC."""
    identity: IdentityModel = PydanticField(..., description="Full identity information")
    physical: PhysicalAttributesModel = PydanticField(..., description="Full physical description")
    psychological: PsychologicalAttributesModel = PydanticField(..., description="Detailed psychological profile")
    knowledge: KnowledgeModel = PydanticField(default_factory=KnowledgeModel, description="Initial knowledge state, aquired knowledge should be empty")
    dynamic_state: DynamicStateModel = PydanticField(default_factory=DynamicStateModel, description="Initial dynamic state")
    narrative: NarrativeWeightModel = PydanticField(..., description="Narrative role and importance")


class CreatePlayerArgs(BaseModel):
    """Arguments required to create the player character."""
    identity: IdentityModel = PydanticField(..., description="Full identity information")
    physical: PhysicalAttributesModel = PydanticField(..., description="Full physical description")
    psychological: PsychologicalAttributesModel = PydanticField(..., description="Detailed psychological profile")
    knowledge: KnowledgeModel = PydanticField(default_factory=KnowledgeModel, description="Initial knowledge state")
    present_in_scenario: str = PydanticField(..., description="ID of the scenario where the player starts")


class ModifyCharacterArgs(BaseModel):
    """Arguments for basic modifications valid for NPCs and the player."""

    character_id: str = PydanticField(
        ...,
        description="ID of the character (NPC or player) to modify",
    )
    new_full_name: Optional[str] = PydanticField(
        None, description="New full name"
    )
    new_personality_summary: Optional[str] = PydanticField(
        None, description="New personality summary"
    )


class ModifyIdentityArgs(BaseModel):
    """Arguments for updating identity attributes on NPCs or the player."""

    character_id: str = PydanticField(
        ...,
        description="ID of the character (NPC or player) to modify",
    )
    new_full_name: Optional[str] = PydanticField(None, description="New full name")
    new_alias: Optional[str] = PydanticField(None, description="New alias")
    new_age: Optional[int] = PydanticField(None, description="New age")
    new_gender: Optional[Literal["male", "female", "non-binary", "undefined", "other"]] = PydanticField(
        None, description="New gender"
    )
    new_profession: Optional[str] = PydanticField(None, description="New profession")
    new_species: Optional[str] = PydanticField(None, description="New species")
    new_alignment: Optional[str] = PydanticField(None, description="New alignment")


class ModifyPhysicalArgs(BaseModel):
    """Arguments for updating physical attributes on NPCs or the player."""

    character_id: str = PydanticField(
        ...,
        description="ID of the character (NPC or player) to modify",
    )
    new_appearance: Optional[str] = PydanticField(None, description="New appearance")
    new_distinctive_features: Optional[List[str]] = PydanticField(
        None, description="New distinctive features list"
    )
    new_clothing_style: Optional[str] = PydanticField(None, description="New clothing style")
    new_characteristic_items: Optional[List[str]] = PydanticField(
        None, description="New characteristic items list"
    )


class ModifyPsychologicalArgs(BaseModel):
    """Arguments for updating psychological traits on NPCs or the player."""

    character_id: str = PydanticField(
        ...,
        description="ID of the character (NPC or player) to modify",
    )
    new_personality_summary: Optional[str] = PydanticField(None, description="New personality summary")
    new_personality_tags: Optional[List[str]] = PydanticField(None, description="New personality tags")
    new_motivations: Optional[List[str]] = PydanticField(None, description="New motivations")
    new_values: Optional[List[str]] = PydanticField(None, description="New values")
    new_fears_and_weaknesses: Optional[List[str]] = PydanticField(
        None, description="New fears and weaknesses"
    )
    new_communication_style: Optional[str] = PydanticField(None, description="New communication style")
    new_backstory: Optional[str] = PydanticField(None, description="New backstory")
    new_quirks: Optional[List[str]] = PydanticField(None, description="New quirks list")


class ModifyKnowledgeArgs(BaseModel):
    """Arguments for updating knowledge on NPCs or the player."""

    character_id: str = PydanticField(
        ...,
        description="ID of the character (NPC or player) to modify",
    )
    new_background_knowledge: Optional[List[str]] = PydanticField(None, description="New background knowledge")
    new_acquired_knowledge: Optional[List[str]] = PydanticField(None, description="New acquired knowledge")


class ModifyDynamicStateArgs(BaseModel):
    """Arguments for updating an NPC's dynamic state. Does not work on the player."""

    character_id: str = PydanticField(
        ...,
        description="ID of the NPC to modify; the player cannot be modified",
    )
    new_current_emotion: Optional[str] = PydanticField(None, description="New current emotion")
    new_immediate_goal: Optional[str] = PydanticField(None, description="New immediate goal")


class ModifyNarrativeArgs(BaseModel):
    """Arguments for updating an NPC's narrative role. Does not work on the player."""

    character_id: str = PydanticField(
        ...,
        description="ID of the NPC to modify; the player cannot be modified",
    )
    new_narrative_role: Optional[Literal["protagonist", "secondary", "extra", "antagonist", "ally", "informational figure"]] = PydanticField(
        None, description="New narrative role"
    )
    new_current_narrative_importance: Optional[Literal["important", "secondary", "minor", "inactive"]] = PydanticField(
        None, description="New narrative importance"
    )
    new_narrative_purposes: Optional[List[NarrativePurposeModel]] = PydanticField(
        None, description="New narrative purposes"
    )


class DeleteCharacterArgs(BaseModel):
    """Arguments for deleting an NPC. The player cannot be deleted."""

    character_id: str = PydanticField(
        ...,
        description="ID of the NPC to delete. The player character cannot be deleted.",
    )


class PlaceCharacterArgs(BaseModel):
    """Arguments for placing a character in a scenario.

    If the character is already in another scenario, it will be moved to the
    specified one. This works for both NPCs and the player.
    """

    character_id: str = PydanticField(
        ..., description="ID of the character to place or move"
    )
    new_scene_id: str = PydanticField(
        ...,
        description=(
            "ID of the destination scenario. If the character was already in a"
            " scene, it will be relocated here"
        ),
    )


class RemoveCharacterFromScenarioArgs(BaseModel):
    """Arguments for removing a character from its current scenario.

    Only NPCs can be unplaced; the player must always belong to a scenario.
    """

    character_id: str = PydanticField(
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
    ]] = PydanticField(
        default=None,
        description="Optional attribute to filter by",
    )
    value_to_match: Optional[str] = PydanticField(
        default=None,
        description="Value that the attribute should match or contain",
    )
    max_results: Optional[int] = PydanticField(
        default=10,
        description="Maximum number of characters to list when filtering",
    )
    list_identity: bool = PydanticField(
        default=False,
        description="Include full identity fields when listing",
    )
    list_physical: bool = PydanticField(
        default=False,
        description="Include physical attributes when listing",
    )
    list_psychological: bool = PydanticField(
        default=False,
        description="Include psychological traits when listing",
    )
    list_knowledge: bool = PydanticField(
        default=False,
        description="Include knowledge fields when listing",
    )
    list_dynamic_state: bool = PydanticField(
        default=False,
        description="Include dynamic state when listing",
    )
    list_narrative: bool = PydanticField(
        default=False,
        description="Include narrative attributes when listing",
    )


class GetCharacterDetailsArgs(BaseModel):
    """Arguments for retrieving a character's full details."""
    character_id: str = PydanticField(..., description="ID of the character")


class GetPlayerDetailsArgs(BaseModel):
    """Arguments for retrieving details of the player character."""
    pass


class SimulatedCharactersModel(BaseModel):
    """In-memory representation of characters cast manipulated by the agent."""

    simulated_characters: Dict[str, CharacterBaseModel] = PydanticField(default_factory=dict)
    deleted_characters: Dict[str, CharacterBaseModel] = PydanticField(default_factory=dict)
    player_character: Optional[PlayerCharacterModel] = PydanticField(default=None)
    executor_applied_operations_log: List[Dict[str, Any]] = PydanticField(default_factory=list)

    validator_applied_operations_log: List[Dict[str, Any]] = PydanticField(default_factory=list)

    task_finalized_by_agent: bool = PydanticField(default=False)
    task_finalized_justification: Optional[str] = PydanticField(default=None)
    agent_validated: bool = PydanticField(default=False)
    agent_validation_conclusion_flag: bool = PydanticField(default=False)
    agent_validation_assessment_reasoning: str = PydanticField(default="")
    agent_validation_suggested_improvements: str = PydanticField(default="")
    executor_or_validator: Literal["executor", "validator"] = PydanticField(default="executor", description="Whether the cast is currently being used by the executor agent or the validator agent.")

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

            summary = f"- ID: {char.id}, Name: '{char.identity.full_name}', Type: {char.type}"
            role = (
                char.narrative.narrative_role
                if isinstance(char, NonPlayerCharacterModel)
                else "N/A"
            )
            summary += f", Role: {role}"
            if args_model.list_identity:
                summary += f", identity={char.identity.model_dump()}"
            if args_model.list_physical:
                summary += f", physical={char.physical.model_dump()}"
            if args_model.list_psychological:
                summary += f", psychological={char.psychological.model_dump()}"
            if args_model.list_knowledge:
                summary += f", knowledge={char.knowledge.model_dump()}"
            if isinstance(char, NonPlayerCharacterModel) and args_model.list_dynamic_state:
                summary += f", dynamic_state={char.dynamic_state.model_dump()}"
            if isinstance(char, NonPlayerCharacterModel) and args_model.list_narrative:
                summary += f", narrative={char.narrative.model_dump()}"

            matches.append(summary)
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

    def create_player(self, args_model: CreatePlayerArgs) -> str:
        """(MODIFICATION tool) Create the player character."""
        if self.player_character is not None:
            return self._log_and_summarize(
                "create_player",
                args_model,
                False,
                "Error: Player already exists.",
            )

        new_id = self.generate_sequential_character_id(list(self.simulated_characters.keys()))
        player = PlayerCharacterModel(
            id=new_id,
            identity=args_model.identity,
            physical=args_model.physical,
            psychological=args_model.psychological,
            knowledge=args_model.knowledge,
            present_in_scenario=args_model.present_in_scenario,
        )

        self.player_character = player
        self.simulated_characters[new_id] = player

        return self._log_and_summarize(
            "create_player",
            args_model,
            True,
            f"Player '{player.identity.full_name}' created with id {new_id} in scene {args_model.present_in_scenario}.",
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
        details = [
            f"ID: {player.id}",
            f"Name: {player.identity.full_name}",
            f"Scene: {player.present_in_scenario}",
            f"Profession: {player.identity.profession}",
            f"Species: {player.identity.species}",
        ]
        return self._log_and_summarize(
            "get_player_details",
            args_model,
            True,
            "\n".join(details),
        )

    def get_character_details(self, args_model: GetCharacterDetailsArgs) -> str:
        """(QUERY tool) Returns detailed information for a character."""
        char = self.simulated_characters.get(args_model.character_id)
        if not char:
            return self._log_and_summarize(
                "get_character_details",
                args_model,
                False,
                f"Error: Character ID '{args_model.character_id}' not found.",
            )

        role = (
            char.narrative.narrative_role
            if isinstance(char, NonPlayerCharacterModel)
            else "N/A"
        )
        details = [
            f"ID: {char.id}",
            f"Name: {char.identity.full_name}",
            f"Species: {char.identity.species}",
            f"Profession: {char.identity.profession}",
            f"Narrative Role: {role}",
            f"Personality: {char.psychological.personality_summary}",
        ]
        return self._log_and_summarize(
            "get_character_details",
            args_model,
            True,
            "\n".join(details),
        )



