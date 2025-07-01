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

    def set_narrative_structure(self, structure_type: NarrativeStructureTypeModel) -> None:
        self._working_state.set_narrative_structure(structure_type)

    # ---- Narrative beat management ----
    def add_narrative_beat(self, stage_index: int, beat: NarrativeBeatModel) -> None:
        self._working_state.add_narrative_beat(stage_index, beat)

    def add_failure_condition(self, failure_condition: FailureConditionModel) -> None:
        self._working_state.add_failure_condition(failure_condition)

    def add_risk_triggered_beats(
        self,
        condition_id: str,
        risk_triggered: RiskTriggeredBeats,
    ) -> None:
        self._working_state.add_risk_triggered_beats(condition_id, risk_triggered)

    def set_failure_risk_level(self, condition_id: str, risk_level: int) -> None:
        self._working_state.set_failure_risk_level(condition_id, risk_level)
