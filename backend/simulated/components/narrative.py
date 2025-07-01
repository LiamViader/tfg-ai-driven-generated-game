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

    # ---- Main goal helpers ----
    def set_main_goal(self, goal: str) -> None:
        self._working_state.set_main_goal(goal)

    def get_main_goal(self) -> str | None:
        return self._working_state.get_main_goal()
    
    def set_narrative_structure(self, structure_type: NarrativeStructureTypeModel) -> None:
        self._working_state.set_narrative_structure(structure_type)

    # ---- Narrative beat management ----
    def add_narrative_beat(self, stage_index: int, beat: NarrativeBeatModel) -> None:
        self._working_state.add_narrative_beat(stage_index, beat)

    def add_failure_condition(self, failure_condition: FailureConditionModel) -> None:
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
