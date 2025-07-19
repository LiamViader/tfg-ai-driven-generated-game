from typing import List, Tuple

# The facade through which we interact with the versioned state
from simulated.game_state import SimulatedGameState

# Domain classes needed for type checking
from core_game.game_event.domain import BaseGameEvent
from core_game.game_event.activation_conditions.domain import (
    AreaEntryCondition,
    EventCompletionCondition,
    ImmediateActivation,
)

class GameLoopManager:
    """
    Orchestrates the main game flow, tick by tick.
    
    Responsibilities:
    - On each tick, check if new passive events should be activated and process the currently active event.
    - Provide an interface for external systems (Player Input) to activate events reactively or proactively.
    """
    def __init__(self, game_state: SimulatedGameState):
        """
        Initializes the manager with a reference to the game state.
        """
        self.game_state = game_state
    
    def update(self):
        """
        The main game loop method. It should be called on every frame or "tick".
        It manages the flow between processing an active event and looking for a new one.
        """
        self._check_passive_conditions()
        current_active_event = self.game_state.events.get_current_running_event()
        if current_active_event:
            self._process_active_event(current_active_event)

    # --- Private Internal Logic Methods ---

    def _process_active_event(self, event: BaseGameEvent):
        """
        Contains the logic to execute the content of an active event.
        """
        print(f"--- Processing active event: {event.id} ({event.title}) ---")
        # Your specific logic would go here:
        # - If it's a dialogue, display the next line.
        # - If it's a cutscene, advance the animation.
        # - If it's a quest, check if the objectives have been met.
        
        # Placeholder for completion logic
        if self._is_event_logic_complete(event):
            self.events_manager.complete_current_event()

    def _is_event_logic_complete(self, event: BaseGameEvent) -> bool:
        """
        Placeholder: Checks if an event's logic has finished.
        In a real game, this would query the event's state.
        """
        # Simple example: for now, we make all events last for a single tick.
        print(f"Event '{event.id}' logic is complete.")
        return True

    def _check_passive_conditions(self):
        """
        Searches for and activates events based on passive/automatic conditions
        (entering an area, completing another event, immediate activation).
        """
        available_events = self.game_state.get_events_by_status("AVAILABLE")

        for event in available_events:
            for condition in event.activation_conditions():                    
                if condition.is_met(self.game_state):
                    print(f"Passive condition met for event '{event.id}'. Starting event.")
                    self.events_manager.start_event(event.id)
                    #hauria d'establir algun ordre segons regles

    # --- Public API for External Systems (Input, AI Director) ---

    def on_player_interacts_with_character(self, character_id: str) -> List[Tuple[str, str]]:
        """
        API for the input system. Called when the player clicks on an NPC.
        Returns the dialogue options to be displayed in the UI.
        """
        return self.events_manager.get_dialogue_options_for_character(character_id)

    def on_player_selects_interaction_option(self, event_id: str):
        """
        API for the input system. Called when the player chooses an option from the menu.
        Starts the event associated with that option.
        """
        event = self.events_manager.get_event_by_id(event_id)
        if event and event.status == "AVAILABLE":
            print(f"Player selected an option. Starting event '{event.id}'.")
            self.events_manager.start_event(event_id)
        else:
            status = event.status if event else "Not Found"
            print(f"Warning: Cannot start event '{event_id}' from player interaction. Status is '{status}'.")
