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


class ModifyCharacterArgs(BaseModel):
    character_id: str = PydanticField(..., description="ID of the character to modify")
    new_full_name: Optional[str] = PydanticField(None, description="New full name")
    new_personality_summary: Optional[str] = PydanticField(None, description="New personality summary")


class DeleteCharacterArgs(BaseModel):
    character_id: str = PydanticField(..., description="ID of the character to delete")


class SimulatedCharactersModel(BaseModel):
    """In-memory representation of characters cast manipulated by the agent."""

    simulated_characters: Dict[str, CharacterBaseModel] = PydanticField(default_factory=dict)
    deleted_characters: Dict[str, CharacterBaseModel] = PydanticField(default_factory=dict)
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

