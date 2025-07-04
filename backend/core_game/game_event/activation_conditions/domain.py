from abc import ABC, abstractmethod
from typing import Dict, Any

# Assuming this is the path to your Singleton. Adjust if necessary!
from simulated.game_state import SimulatedGameState

# Import all the data models (schemas) that the domain classes will need
from .schemas import *


class ActivationCondition(ABC):
    """
    Abstract domain class for all activation contition for events.
    It encapsulates the logic to determine if an event should be activated.
    """

    def __init__(self, model: ActivationConditionModel):
        self._model = model

    @property
    def model_data(self) -> ActivationConditionModel:
        """Returns the underlying Pydantic data model."""
        return self._model

    @abstractmethod
    def is_met(self, game_state: SimulatedGameState, **kwargs: Any) -> bool:
        """
        Checks if this trigger's condition is met in the current game state.

        Args:
            game_state: The instance of the simulated game state.
            **kwargs: Additional context-specific arguments (e.g., player action).

        Returns:
            True if the associated event should be activated, False otherwise.
        """
        pass


class AreaEntryCondition(ActivationCondition):
    """Logic for the condition that activates when the player enters a scenario."""

    def __init__(self, model: AreaEntryConditionModel):
        super().__init__(model)
        self._model: AreaEntryConditionModel 

    def is_met(self, game_state: SimulatedGameState, **kwargs: Any) -> bool:
        player = game_state.get_player()
        if not player:
            return False
        return player.id == self._model.scenario_id


class EventCompletionCondition(ActivationCondition):
    """Logic for the trigger that activates when another event has been completed."""

    def __init__(self, model: EventCompletionConditionModel):
        super().__init__(model)
        self._model: EventCompletionConditionModel

    def is_met(self, game_state: SimulatedGameState, **kwargs: Any) -> bool:
        completed_ids = game_state.read_only_events.get_completed_event_ids()
        return self._model.source_event_id in completed_ids


class CharacterInteractionOption(ActivationCondition):
    """Logic for triggers that populate a character's dialogue catalog."""

    def __init__(self, model: CharacterInteractionOptionModel):
        super().__init__(model)
        self._model: CharacterInteractionOptionModel

    @property
    def character_id(self) -> str:
        return self._model.character_id

    @property
    def menu_label(self) -> str:
        return self._model.menu_label

    @property
    def is_repeatable(self) -> bool:
        return self._model.is_repeatable

    def is_met(self, game_state: SimulatedGameState, **kwargs: Any) -> bool:
        # This trigger is REACTIVE. Its main logic is not in this passive check,
        # but in the manager method that fetches dialogue options.
        # This method would be used if the manager delegated the final check.
        return False


class ImmediateActivation(ActivationCondition):
    """Represents an event that should execute immediately upon becoming available."""

    def __init__(self, model: ImmediateActivationModel):
        super().__init__(model)

    def is_met(self, game_state: SimulatedGameState, **kwargs: Any) -> bool:
        # This trigger is automatic.
        # If the event is 'AVAILABLE', this method returns True,
        # causing it to be executed on the next game cycle.
        return True


# --- Wrapper Map ---
# This dictionary is crucial for the GameEventsManager to instantiate
# the correct domain class based on the data model's 'type' field.

WRAPPER_MAP: Dict[str, type[ActivationCondition]] = {
    "area_entry": AreaEntryCondition,
    "event_completion": EventCompletionCondition,
    "character_interaction": CharacterInteractionOption,
    "immediate": ImmediateActivation,
}