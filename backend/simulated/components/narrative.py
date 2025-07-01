from copy import deepcopy
from typing import List
from core_game.narrative.schemas import (
    NarrativeBeatModel,
    FailureConditionModel,
    RiskTriggeredBeats,
    NarrativeStructureTypeModel,
)
from core_game.narrative.domain import NarrativeState

class SimulatedNarrative:
    """Lightweight wrapper around :class:`NarrativeState`."""

    def __init__(self, narrative_state: NarrativeState) -> None:
        self._working_state: NarrativeState = narrative_state

    def __deepcopy__(self, memo):
        copied_state = NarrativeState(model=deepcopy(self._working_state.to_model()))
        return SimulatedNarrative(copied_state)

    def get_state(self) -> NarrativeState:
        return self._working_state

    def get_initial_summary(self) -> str:
        """Return summary info about the current narrative stage."""
        return self._working_state.get_initial_summary()

    def get_structure_details(self) -> str:
        """Return details of the narrative structure with beats and current stage."""
        return self._working_state.get_structure_details()

    # ---- Main goal helpers ----
    def set_main_goal(self, goal: str) -> None:
        self._working_state.set_main_goal(goal)

    def get_main_goal(self) -> str | None:
        return self._working_state.get_main_goal()
    
    def set_narrative_structure(self, structure_type: NarrativeStructureTypeModel) -> None:
        self._working_state.set_narrative_structure(structure_type)

    # ---- Stage index helpers ----
    def get_current_stage_index(self) -> int:
        """Return the index of the currently active narrative stage."""
        index = self._working_state.to_model().current_stage_index
        return index or 0

    def get_next_stage_index(self) -> int:
        """Return the index of the next narrative stage if available."""
        if self._working_state.narrative_structure is None:
            raise ValueError("No narrative structure selected")
        next_index = self.get_current_stage_index() + 1
        if next_index >= len(self._working_state.narrative_structure.stages):
            raise IndexError("No next stage exists")
        return next_index

    # ---- Narrative beat management ----
    def add_narrative_beat(self, stage_index: int, beat: NarrativeBeatModel) -> None:
        """Add a beat ensuring the stage exists and avoiding duplicates."""
        if self._working_state.narrative_structure is None:
            raise ValueError("No narrative structure selected")

        stages = self._working_state.narrative_structure.stages
        if stage_index < 0 or stage_index >= len(stages):
            raise IndexError("Stage index out of range")

        stage = stages[stage_index]
        if any(existing.id == beat.id for existing in stage.stage_beats):
            raise ValueError(
                f"Beat with ID '{beat.id}' already exists in stage {stage_index}"
            )

        stage.stage_beats.append(beat)

    def add_failure_condition(self, failure_condition: FailureConditionModel) -> None:
        """Add a new failure condition ensuring unique ids."""
        if any(fc.id == failure_condition.id for fc in self._working_state.failure_conditions):
            raise ValueError(f"Failure condition '{failure_condition.id}' already exists")
        self._working_state.failure_conditions.append(failure_condition)

    def _find_failure(self, condition_id: str) -> FailureConditionModel:
        for cond in self._working_state.failure_conditions:
            if cond.id == condition_id:
                return cond
        raise KeyError(f"Failure condition '{condition_id}' not found")

    def add_risk_triggered_beats(
        self,
        condition_id: str,
        risk_triggered: RiskTriggeredBeats,
    ) -> None:
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
