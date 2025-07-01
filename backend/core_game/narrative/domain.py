from __future__ import annotations
from typing import Optional
from core_game.narrative.schemas import (
    NarrativeStateModel,
    NarrativeBeatModel,
    FailureConditionModel,
    RiskTriggeredBeats,
    NarrativeStageModel,
    NarrativeStructureModel,
    NarrativeStructureTypeModel,
    GoalModel,
)
from core_game.narrative.structures import AVAILABLE_NARRATIVE_STRUCTURES

class NarrativeState:
    """Domain wrapper around :class:`NarrativeStateModel`."""

    def __init__(self, model: Optional[NarrativeStateModel] = None) -> None:
        if model:
            self._data = model
        else:
            # create an empty narrative state with no structure selected yet
            self._data = NarrativeStateModel(
                main_goal=None,
                failure_conditions=[],
                current_stage_index=0,
                narrative_structure=None,
            )

    # ------------------------------------------------------------------
    # Conversion helpers
    # ------------------------------------------------------------------
    def to_model(self) -> NarrativeStateModel:
        return self._data

    # ------------------------------------------------------------------
    # Accessor properties
    # ------------------------------------------------------------------
    @property
    def narrative_structure(self) -> Optional[NarrativeStructureModel]:
        return self._data.narrative_structure

    @property
    def failure_conditions(self) -> list[FailureConditionModel]:
        return self._data.failure_conditions

    # ------------------------------------------------------------------
    # Main goal helpers
    # ------------------------------------------------------------------
    def set_main_goal(self, goal: str) -> None:
        """Define the main goal of the narrative."""
        self._data.main_goal = GoalModel(description=goal)

    def get_main_goal(self) -> Optional[str]:
        """Return the main goal description if defined."""
        if self._data.main_goal is None:
            return None
        return self._data.main_goal.description

    # ------------------------------------------------------------------
    # Configuration methods
    # ------------------------------------------------------------------
    def set_narrative_structure(self, structure_type: NarrativeStructureTypeModel) -> None:
        """Initialize the narrative structure from a type model."""
        stages = [
            NarrativeStageModel(**stage.model_dump(), stage_beats=[])
            for stage in structure_type.stages
        ]
        self._data.narrative_structure = NarrativeStructureModel(
            structure_type=structure_type, stages=stages
        )
        self._data.current_stage_index = 0

    # ------------------------------------------------------------------
    # Modification methods
    # ------------------------------------------------------------------
    def add_narrative_beat(self, stage_index: int, beat: NarrativeBeatModel) -> None:
        if self._data.narrative_structure is None:
            raise ValueError("No narrative structure selected")
        stages = self._data.narrative_structure.stages
        if stage_index < 0 or stage_index >= len(stages):
            raise IndexError("Stage index out of range")
        stages[stage_index].stage_beats.append(beat)

    def add_failure_condition(self, failure_condition: FailureConditionModel) -> None:
        self._data.failure_conditions.append(failure_condition)

    def _find_failure(self, condition_id: str) -> FailureConditionModel:
        for cond in self._data.failure_conditions:
            if cond.id == condition_id:
                return cond
        raise KeyError(f"Failure condition '{condition_id}' not found")

    def add_risk_triggered_beats(self, condition_id: str, risk_triggered: RiskTriggeredBeats) -> None:
        cond = self._find_failure(condition_id)
        cond.risk_triggered_beats.append(risk_triggered)

    def set_failure_risk_level(self, condition_id: str, risk_level: int) -> None:
        cond = self._find_failure(condition_id)
        risk_level = max(0, min(100, risk_level))
        cond.risk_level = risk_level
        cond.is_active = risk_level >= 100
        for rtb in cond.risk_triggered_beats:
            for beat in rtb.beats:
                if risk_level >= rtb.trigger_risk_level:
                    beat.status = "ACTIVE"
                if risk_level <= rtb.deactivate_risk_level:
                    beat.status = "PENDING"

    # ------------------------------------------------------------------
    # Summary helpers
    # ------------------------------------------------------------------
    def get_initial_summary(self) -> str:
        """Return the current stage and beats summary."""
        if self._data.narrative_structure is None:
            return "No narrative structure selected"
        stage_index = self._data.current_stage_index or 0
        stages = self._data.narrative_structure.stages
        if stage_index < 0 or stage_index >= len(stages):
            return "No current narrative stage"
        stage = stages[stage_index]
        if stage.stage_beats:
            beats_summary = ", ".join(
                f"{b.id} [{b.status}]" for b in stage.stage_beats
            )
        else:
            beats_summary = "No beats yet"
        return f"Current stage: {stage.name}. Beats: {beats_summary}"
