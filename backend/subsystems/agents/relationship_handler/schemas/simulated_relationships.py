from typing import Dict, Optional, List, Any, Literal
from pydantic import BaseModel, Field as PydanticField
from core_game.character.schemas import RelationshipType, CharacterRelationship


class GetRelationshipDetailsArgs(BaseModel):
    source_character_id: str = PydanticField(..., description="ID of the source character")
    target_character_id: str = PydanticField(..., description="ID of the target character")


class FinalizeSimulationArgs(BaseModel):
    justification: str = PydanticField(..., description="Explanation of why the objective is met")


class CreateRelationshipTypeArgs(BaseModel):
    name: str = PydanticField(..., description="Name of the relationship type")
    explanation: Optional[str] = PydanticField(
        default=None,
        description="Detailed explanation of the relationship type",
    )


class CreateUndirectedRelationshipArgs(BaseModel):
    character_a_id: str = PydanticField(..., description="ID of the first character")
    character_b_id: str = PydanticField(..., description="ID of the second character")
    relationship_type: str = PydanticField(..., description="Name of the relationship type")
    intensity: Optional[int] = PydanticField(
        None, description="Intensity of the relationship if applicable"
    )


class CreateDirectedRelationshipArgs(BaseModel):
    source_character_id: str = PydanticField(..., description="ID of the character initiating the relationship")
    target_character_id: str = PydanticField(..., description="ID of the target character")
    relationship_type: str = PydanticField(..., description="Name of the relationship type")
    intensity: Optional[int] = PydanticField(None, description="Intensity of the relationship if applicable")


class ModifyRelationshipIntensityArgs(BaseModel):
    source_character_id: str = PydanticField(..., description="ID of the source character")
    target_character_id: str = PydanticField(..., description="ID of the target character")
    relationship_type: str = PydanticField(..., description="Name of the relationship type")
    new_intensity: int = PydanticField(..., ge=0, le=10, description="New intensity value")


class SimulatedRelationshipsModel(BaseModel):
    relationship_types: Dict[str, RelationshipType] = PydanticField(default_factory=dict)
    relationships_matrix: Dict[str, Dict[str, Dict[str, CharacterRelationship]]] = PydanticField(default_factory=dict)
    executor_applied_operations_log: List[Dict[str, Any]] = PydanticField(default_factory=list)
    task_finalized_by_agent: bool = PydanticField(default=False)
    task_finalized_justification: Optional[str] = PydanticField(default=None)
    executor_or_validator: Literal["executor", "validator"] = PydanticField(default="executor")

    def _log_and_summarize(self, tool_name: str, args: BaseModel, success: bool, message: str) -> str:
        self.executor_applied_operations_log.append({
            "tool_called": tool_name,
            "args": args.model_dump(),
            "success": success,
            "message": message,
        })
        observation = f"Result of '{tool_name}': {message}"
        print(observation)
        return observation


    def get_relationship_details(self, args_model: GetRelationshipDetailsArgs) -> str:
        rels = self.relationships_matrix.get(args_model.source_character_id, {}).get(
            args_model.target_character_id, {}
        )
        if not rels:
            return self._log_and_summarize(
                "get_relationship_details", args_model, True, "No relationships found."
            )
        details = ", ".join(
            f"{name}: {rel.intensity if rel.intensity is not None else 'N/A'}" for name, rel in rels.items()
        )
        return self._log_and_summarize(
            "get_relationship_details", args_model, True, details
        )

    def finalize_simulation(self, args_model: FinalizeSimulationArgs) -> Dict[str, Any]:
        self.task_finalized_by_agent = True
        self.task_finalized_justification = args_model.justification
        self.executor_applied_operations_log.append({
            "tool_called": "finalize_simulation",
            "args": args_model.model_dump(),
            "success": True,
            "message": args_model.justification,
        })
        return {
            "final_justification": args_model.justification,
            "final_relationships": self.relationships_matrix,
        }

