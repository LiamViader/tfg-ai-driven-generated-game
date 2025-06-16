"""Pydantic models used by the character creation agent."""

from typing import Dict, List, Any, Optional, Annotated
from pydantic import BaseModel, Field as PydanticField, model_validator

from core_game.character.schemas import (
    IdentityModel,
    PhysicalAttributesModel,
    PsychologicalAttributesModel,
    KnowledgeModel,
    DynamicStateModel,
    NarrativeWeightModel,
    NonPlayerCharacterModel,
    CharacterBaseModel,
    _generate_character_id,
)


class CreateFullNPCArgs(BaseModel):
    """Arguments required to create a fully detailed NPC."""

    identity: IdentityModel = PydanticField(..., description="Full identity information")
    physical: PhysicalAttributesModel = PydanticField(..., description="Full physical description")
    psychological: PsychologicalAttributesModel = PydanticField(..., description="Detailed psychological profile")
    knowledge: KnowledgeModel = PydanticField(default_factory=KnowledgeModel, description="Initial knowledge state")
    dynamic_state: DynamicStateModel = PydanticField(default_factory=DynamicStateModel, description="Initial dynamic state")
    narrative: NarrativeWeightModel = PydanticField(..., description="Narrative role and importance")


class ModifyCharacterArgs(BaseModel):
    character_id: str = PydanticField(..., description="ID of the character to modify")
    new_full_name: Optional[str] = PydanticField(None, description="New full name")
    new_personality_summary: Optional[str] = PydanticField(None, description="New personality summary")


class DeleteCharacterArgs(BaseModel):
    character_id: str = PydanticField(..., description="ID of the character to delete")


class SimulatedCharactersModel(BaseModel):
    """In-memory representation of characters manipulated by the agent."""

    simulated_characters: Dict[str, CharacterBaseModel] = PydanticField(default_factory=dict)
    deleted_characters: Dict[str, CharacterBaseModel] = PydanticField(default_factory=dict)
    operations_log: List[Dict[str, Any]] = PydanticField(default_factory=list)

    task_finalized_by_agent: bool = PydanticField(default=False)
    task_finalized_justification: Optional[str] = PydanticField(default=None)
    agent_validated: bool = PydanticField(default=False)
    agent_validation_conclusion_flag: bool = PydanticField(default=False)
    agent_validation_assessment_reasoning: str = PydanticField(default="")
    agent_validation_suggested_improvements: str = PydanticField(default="")

    @staticmethod
    def generate_sequential_character_id(existing_ids: List[str]) -> str:
        """Generate a unique sequential character id."""
        new_id = _generate_character_id()
        while new_id in existing_ids:
            new_id = _generate_character_id()
        return new_id

    def _log_and_summarize(self, tool_name: str, args: BaseModel, success: bool, message: str) -> str:
        self.operations_log.append({
            "tool_called": tool_name,
            "args": args.model_dump(),
            "success": success,
            "message": message,
        })
        return f"Result of '{tool_name}': {message} | Characters: {len(self.simulated_characters)}"

    def get_summary(self) -> str:
        if not self.simulated_characters:
            return "No characters created yet."
        return "Characters: " + ", ".join(f"{c.identity.full_name}({cid})" for cid, c in self.simulated_characters.items())

