"""Domain classes for working with game event models."""
from __future__ import annotations
from .schemas import (
    NPCConversationEventModel,
    PlayerNPCConversationEventModel,
    NarratorInterventionEventModel,
    CutsceneFrameModel,
    CutsceneEventModel,
    NPCMessage,
    NarratorMessage,
    ConversationMessage,
    GameEventModel,
    GameEventsManagerModel,
)
from typing import Optional, Dict, List, Set, TYPE_CHECKING
from collections import defaultdict
from .constants import EVENT_STATUSES, EVENT_STATUS_LITERAL
from core_game.game_event.activation_conditions.domain import (
    ActivationCondition,
    CharacterInteractionOption,
    WRAPPER_MAP as CONDITION_WRAPPER_MAP
)
from core_game.game_event.schemas import RunningEventInfo
from core_game.game_event.activation_conditions.schemas import ActivationConditionModel, CharacterInteractionOptionModel


from core_game.character.domain import PlayerCharacter, BaseCharacter
from core_game.character.schemas import CharacterBaseModel, IdentityModel, PhysicalAttributesModel, PsychologicalAttributesModel, KnowledgeModel

import json
from typing import AsyncGenerator

if TYPE_CHECKING:
    from simulated.game_state import SimulatedGameState


class BaseGameEvent:
    """Common functionality for domain event wrappers.
    """

    def __init__(self, model: GameEventModel):
        self._data = model
        self._activation_conditions: List[ActivationCondition] = [] # Initialize here
        self._build_condition_wrappers()
        self.triggered_by: Optional[ActivationCondition]

    def _build_condition_wrappers(self):
        """Instantiates domain objects for the activation conditions."""
        # Always clear before rebuilding to avoid duplicates if called multiple times
        self._activation_conditions = []
        for condition_model in self._data.activation_conditions:
            wrapper_class = CONDITION_WRAPPER_MAP.get(condition_model.type)
            if wrapper_class:
                self._activation_conditions.append(wrapper_class(model=condition_model))

    @property
    def id(self) -> str:
        """Return the unique identifier of the underlying event model."""
        return self._data.id

    @property
    def status(self) -> str:
        """Returns the status"""
        return self._data.status
    
    @property
    def title(self) -> str:
        """Returns the title"""
        return self._data.title
    
    @property
    def description(self) -> str:
        """Returns the description"""
        return self._data.description
    
    @property
    def source_beat_id(self) -> Optional[str]:
        """Returns the source beat id"""
        return self._data.source_beat_id
    
    @property
    def type(self) -> Optional[str]:
        """Returns the source beat id"""
        return self._data.type
    
    @property
    def activation_conditions(self) -> List[ActivationCondition]:
        return self._activation_conditions
    

    @activation_conditions.setter
    def activation_conditions(self, value: List[ActivationCondition]) -> None:
        self._activation_conditions = value


    def get_model(self) -> GameEventModel:
        """Return the underlying Pydantic model."""
        return self._data

class NPCConversationEvent(BaseGameEvent):
    """Domain logic for an NPC-only conversation."""

    def __init__(self, model: NPCConversationEventModel):
        super().__init__(model)
        self._data = model

    def add_message(self, message: ConversationMessage) -> None:
        self._data.messages.append(message)
    
    @property
    def npc_ids(self) -> List[str]:
        return self._data.npc_ids
    
    @property
    def messages(self) -> List[ConversationMessage]:
        return self._data.messages
    
    
    async def run(self, game_state: 'SimulatedGameState') -> AsyncGenerator[str, None]:
        """
        Runs the flow of an NPC-to-NPC conversation.
        """
        from subsystems.game_events.dialog_engine.turn_manager.npc import decide_next_npc_speaker
        from subsystems.game_events.dialog_engine.dialog_generator.npc import generate_npc_message_stream
        from subsystems.game_events.dialog_engine.parser import parse_and_stream_messages, InvalidTagError
        MAX_RETRIES_PER_TURN = 3
        conversation_ended_naturally = False

        # --- Bucle de Conversación Principal ---
        # Este bucle continúa mientras haya alguien que hablar.
        while True:
            speaker = decide_next_npc_speaker(self, self.triggered_by, game_state)

            if not speaker:
                print(f"[Event: {self.id}] Conversation concluded naturally.")
                conversation_ended_naturally = True
                break # Sale del bucle de conversación

            turn_successful = False
            # --- Bucle de Reintentos por Turno ---
            # Intenta generar el turno de este hablante hasta MAX_RETRIES veces.
            for attempt in range(MAX_RETRIES_PER_TURN):
                print(f"[Event: {self.id}] Attempt {attempt + 1}/{MAX_RETRIES_PER_TURN} for speaker {speaker.id}...")
                
                raw_llm_stream = generate_npc_message_stream(
                    speaker=speaker,
                    event=self,
                    game_state=game_state
                )

                try:
                    # Intenta parsear y streamear el turno completo.
                    async for message_json in parse_and_stream_messages(raw_llm_stream, speaker, self):
                        yield message_json
                    
                    # Si el bucle 'async for' termina sin lanzar una excepción, el turno fue exitoso.
                    turn_successful = True
                    print(f"[Event: {self.id}] Turn for {speaker.id} completed successfully.")
                    break # Sale del bucle de reintentos y pasa al siguiente turno.

                except InvalidTagError as e:
                    print(f"[ERROR in Event {self.id}] Parser failed on attempt {attempt + 1}: {e}")
                    # Si este no es el último intento, el bucle continuará para reintentar.
                    if attempt == MAX_RETRIES_PER_TURN - 1:
                        print(f"[Event: {self.id}] All retries failed for speaker {speaker.id}. Stopping event.")

            if not turn_successful:
                # Si después de todos los reintentos el turno no fue exitoso,
                # rompemos el bucle de conversación principal para evitar quedarnos atascados.
                print(f"[Event: {self.id}] Event failed due to repeated errors.")
                conversation_ended_naturally = False
                break
        
        # --- Lógica de Finalización del Evento ---
        # Esta sección se ejecuta después de que el bucle 'while' termina.
        if conversation_ended_naturally:
            # Si la conversación terminó porque no había más turnos, se considera completada.
            print(f"[Event: {self.id}] Marking event as COMPLETED.")
            game_state.events.get_state().complete_current_event()
        else:
            # Si la conversación terminó por un fallo, se podría marcar como fallida.
            # (Aquí podrías añadir una lógica para cambiar el estado a "FAILED" si lo tuvieras)
            print(f"[Event: {self.id}] Event finished due to failure. Not marking as completed.")
            # Por ejemplo: game_state.events.get_state().fail_current_event()


class PlayerNPCConversationEvent(BaseGameEvent):
    """Domain logic for a conversation involving the player and NPCs."""

    def __init__(self, model: PlayerNPCConversationEventModel):
        super().__init__(model)
        self._data = model

    def add_message(self, message: ConversationMessage) -> None:
        self._data.messages.append(message)
    
    @property
    def npc_ids(self) -> List[str]:
        return self._data.npc_ids
    
    @property
    def messages(self) -> List[ConversationMessage]:
        return self._data.messages
    
    async def run(self, game_state: 'SimulatedGameState') -> AsyncGenerator[str, None]:
        """
        Runs the flow of a conversation involving the player, with retry logic.
        """
    
        from subsystems.game_events.dialog_engine.turn_manager.player_npc import decide_next_player_npc_speaker
        from subsystems.game_events.dialog_engine.dialog_generator.npc import generate_npc_message_stream
        from subsystems.game_events.dialog_engine.dialog_generator.player import generate_player_message_stream
        from subsystems.game_events.dialog_engine.parser import parse_and_stream_messages, InvalidTagError
        print(f"[Event: {self.id}] Running Player-NPC Conversation...")
        
        MAX_RETRIES_PER_TURN = 3
        conversation_ended_naturally = False

        # --- Main Conversation Loop ---
        while True:
            speaker = decide_next_player_npc_speaker(self, self.triggered_by, game_state)

            if not speaker:
                print(f"[Event: {self.id}] Conversation concluded naturally.")
                conversation_ended_naturally = True
                break

            turn_successful = False
            is_player_turn = isinstance(speaker, PlayerCharacter)

            # --- Turn Retry Loop ---
            for attempt in range(MAX_RETRIES_PER_TURN):
                print(f"[Event: {self.id}] Attempt {attempt + 1}/{MAX_RETRIES_PER_TURN} for speaker {speaker.id}...")
                
                # Select the correct generator based on the speaker's type
                if is_player_turn:
                    raw_llm_stream = generate_player_message_stream(
                        speaker=speaker, event=self, game_state=game_state
                    )
                else: # NPC

                    raw_llm_stream = generate_npc_message_stream(
                        speaker=speaker, event=self, game_state=game_state
                    )

                try:
                    # Parse and stream the complete turn
                    async for message_json in parse_and_stream_messages(raw_llm_stream, speaker, self):
                        yield message_json
                    
                    turn_successful = True
                    print(f"[Event: {self.id}] Turn for {speaker.id} completed successfully.")
                    break # Exit retry loop

                except InvalidTagError as e:
                    print(f"[ERROR in Event {self.id}] Parser failed on attempt {attempt + 1}: {e}")
                    if attempt == MAX_RETRIES_PER_TURN - 1:
                        print(f"[Event: {self.id}] All retries failed for speaker {speaker.id}. Stopping event.")

            if not turn_successful:
                print(f"[Event: {self.id}] Event failed due to repeated errors.")
                conversation_ended_naturally = False
                break

            # If the successful turn was the player's, it must have ended in a choice.
            # The stream must pause and wait for the player's next action.
            if is_player_turn:
                print(f"[Event: {self.id}] Player choice presented. Pausing stream.")
                return # IMPORTANT: Exit the generator. The stream is over for now.

        # --- Event Finalization Logic ---
        if conversation_ended_naturally:
            print(f"[Event: {self.id}] Marking event as COMPLETED.")
            game_state.events.get_state().complete_current_event()
        else:
            print(f"[Event: {self.id}] Event finished due to failure. Not marking as completed.")
            # For example: game_state.events.get_state().fail_current_event()
        
    async def process_player_choice(self, game_state: 'SimulatedGameState', choice_label: str) -> AsyncGenerator[str, None]:
        """
        Generates the player's intervention based on their choice, and then continues the event flow.
        """

        from subsystems.game_events.dialog_engine.dialog_generator.choice_driven import generate_choice_driven_message_stream
        from subsystems.game_events.dialog_engine.parser import parse_and_stream_messages, InvalidTagError
        print(f"[Event: {self.id}] Processing player choice: '{choice_label}'")
        
        player = game_state.read_only_characters.get_player()
        if not player:
            raise ValueError("Player character not found in game state.")

        MAX_RETRIES = 3
        player_turn_successful = False

        # --- Part 1: Generate and stream the Player's intervention ---
        for attempt in range(MAX_RETRIES):
            print(f"[Event: {self.id}] Attempt {attempt + 1}/{MAX_RETRIES} to generate player intervention...")
            
            raw_llm_stream = generate_choice_driven_message_stream(
                player_choice=choice_label,
                speaker=player,
                event=self,
                game_state=game_state
            )

            try:
                async for message_json in parse_and_stream_messages(raw_llm_stream, player, self):
                    yield message_json
                
                player_turn_successful = True
                print(f"[Event: {self.id}] Player intervention generated successfully.")
                break

            except InvalidTagError as e:
                print(f"[ERROR in Event {self.id}] Parser failed on attempt {attempt + 1}: {e}")
                if attempt == MAX_RETRIES - 1:
                    print(f"[Event: {self.id}] All retries failed for player intervention.")
        
        if not player_turn_successful:
            print(f"[Event: {self.id}] Event failed during player intervention. Stopping.")
            # Optionally fail the event
            # game_state.events.get_state().fail_current_event()
            return

        # --- Part 2: Continue the rest of the conversation ---
        print(f"[Event: {self.id}] Player turn complete. Resuming conversation...")
        # This loop takes over and continues the event from where it left off.
        async for subsequent_message_json in self.run(game_state):
            yield subsequent_message_json

class NarratorInterventionEvent(BaseGameEvent):
    """Domain logic for narrator interventions."""

    def __init__(self, model: NarratorInterventionEventModel):
        super().__init__(model)
        self._data = model

    def add_message(self, message: ConversationMessage) -> None:
        self._data.messages.append(message)

    @property
    def messages(self) -> List[ConversationMessage]:
        return self._data.messages
    
    async def run(self, game_state: 'SimulatedGameState') -> AsyncGenerator[str, None]:
        """
        Runs the flow of a Narrator Intervention. This is a single turn event.
        """
        from subsystems.game_events.dialog_engine.dialog_generator.narrator import generate_narrator_message_stream
        from subsystems.game_events.dialog_engine.parser import parse_and_stream_messages, InvalidTagError
        print(f"[Event: {self.id}] Running Narrator Intervention...")
        
        MAX_RETRIES = 3
        turn_successful = False
        narrator_speaker = BaseCharacter(
            data=CharacterBaseModel(
                id="narrator",
                identity=IdentityModel(
                    full_name="",
                    alias="",
                    age=1,
                    gender="female",
                    profession="",
                    species="",
                    alignment="",
                ),
                physical=PhysicalAttributesModel(
                    appearance="",
                    visual_prompt="",
                    distinctive_features=[],
                    clothing_style="",
                    characteristic_items=[]
                ),
                psychological=PsychologicalAttributesModel(
                    personality_summary="",
                    personality_tags=[],
                    motivations=[],
                    values=[],
                    fears_and_weaknesses=[],
                    communication_style="",
                    backstory="",
                    quirks=[]
                ),
                knowledge=KnowledgeModel(
                    background_knowledge=[],
                    acquired_knowledge=[]
                )
            )
        )
        for attempt in range(MAX_RETRIES):
            print(f"[Event: {self.id}] Attempt {attempt + 1}/{MAX_RETRIES} for narrator...")
            
            raw_llm_stream = generate_narrator_message_stream(
                event=self,
                game_state=game_state
            )

            try:
                async for message_json in parse_and_stream_messages(raw_llm_stream, narrator_speaker, self):
                    yield message_json
                
                turn_successful = True
                print(f"[Event: {self.id}] Narrator turn completed successfully.")
                break # Exit retry loop

            except InvalidTagError as e:
                print(f"[ERROR in Event {self.id}] Parser failed on attempt {attempt + 1}: {e}")
                if attempt == MAX_RETRIES - 1:
                    print(f"[Event: {self.id}] All retries failed for narrator. Stopping event.")

        # --- Event Finalization Logic ---
        if turn_successful:
            print(f"[Event: {self.id}] Marking event as COMPLETED.")
            game_state.events.get_state().complete_current_event()
        else:
            print(f"[Event: {self.id}] Event finished due to failure. Not marking as completed.")


class CutsceneFrame:
    """Domain wrapper around :class:`CutsceneFrameModel`."""

    def __init__(self, model: CutsceneFrameModel):
        self._data: CutsceneFrameModel = model

    def add_narrator_message(self, message: NarratorMessage) -> None:
        self._data.narrator_messages.append(message)

    def add_npc_message(self, message: NPCMessage) -> None:
        self._data.npc_messages.append(message)


class CutsceneEvent(BaseGameEvent):
    """Domain logic for cutscene events."""

    def __init__(self, model: CutsceneEventModel):
        super().__init__(model)
        self._data = model

    def add_frame(self, frame: CutsceneFrameModel) -> None:
        self._data.frames.append(frame)


WRAPPER_MAP: Dict[str, type[BaseGameEvent]] = {
    "npc_conversation": NPCConversationEvent,
    "player_npc_conversation": PlayerNPCConversationEvent,
    "narrator_intervention": NarratorInterventionEvent,
    "cutscene": CutsceneEvent,
}

class GameEventsManager:
    """Domain class for managing and storing events"""
    def __init__(self, model: Optional[GameEventsManagerModel] = None):
        self._all_events: Dict[str, BaseGameEvent] = {}
        # The stack now stores RunningEventInfo objects instead of just strings
        self._running_event_stack: List[RunningEventInfo] = []

        self._status_indexes: Dict[str, Set[str]] = {status: set() for status in EVENT_STATUSES}
        self._events_by_beat_id: Dict[str, Set[str]] = defaultdict(set)
        self._beatless_event_ids: Set[str] = set()
        self._interaction_options_by_character: Dict[str, Set[str]] = defaultdict(set)
        
        if model:
            self._populate_and_reindex(model)

    def _populate_and_reindex(self, model: GameEventsManagerModel):
        """
        Populates the manager from the data model and REBUILDS all
        indexes from the primary data source (`all_events`).
        """
        # The stack is now a list of Pydantic models
        self._running_event_stack = model.running_event_stack.copy()
        
        self._status_indexes = {status: set() for status in EVENT_STATUSES}
        self._events_by_beat_id = defaultdict(set)
        self._beatless_event_ids = set()
        self._interaction_options_by_character = defaultdict(set)
        self._all_events = {}

        for event_id, event_model in model.all_events.items():
            wrapper_class = WRAPPER_MAP.get(event_model.type)
            if not wrapper_class: continue
            
            domain_event = wrapper_class(model=event_model)
            self._all_events[event_id] = domain_event

            self._status_indexes[event_model.status].add(event_id)

            if event_model.source_beat_id:
                self._events_by_beat_id[event_model.source_beat_id].add(event_id)
            else:
                self._beatless_event_ids.add(event_id)

            for condition in domain_event.activation_conditions:
                if isinstance(condition, CharacterInteractionOption):
                    self._interaction_options_by_character[condition.character_id].add(event_id)



    def to_model(self) -> GameEventsManagerModel:
        return GameEventsManagerModel(
            all_events={eid: ev.get_model() for eid, ev in self._all_events.items()},
            running_event_stack=self._running_event_stack
        )

    def start_event(self, event_id: str, activating_condition_id: Optional[str] = None):
        """
        Activates an event, sets its status to RUNNING, and pushes it onto the top of the stack
        along with the ID of the condition that triggered it.
        """
        if event_id not in self._all_events:
            raise KeyError(f"Error: Cannot start non-existent event '{event_id}'.")
            
        event = self._all_events[event_id]
        if event.status != "AVAILABLE":
            return

        self.set_event_status(event_id, "RUNNING")
        activating_condition = None
        for cond in event.activation_conditions:
            if activating_condition_id == cond:
                activating_condition = cond
                break

        event.triggered_by = activating_condition
        # Push the new info object onto the stack
        self._running_event_stack.append(
            RunningEventInfo(event_id=event_id, activating_condition_id=activating_condition_id)
        )

    def complete_current_event(self):
        """
        Completes the event that is currently at the top of the stack,
        pops it, and updates its status to COMPLETED.
        """
        if not self._running_event_stack:
            print("Warning: Tried to complete an event, but the running stack is empty.")
            return

        event_info_to_complete = self._running_event_stack.pop()
        self.set_event_status(event_info_to_complete.event_id, "COMPLETED")
        
        # Optional: What happens to the event that was underneath? Does it resume?
        # The logic for resuming would be in the GameLoopManager.

    # --- METHODS TO QUERY THE STACK ---

    def get_current_running_event_info(self) -> Optional[RunningEventInfo]:
        """
        Returns the info object for the event that is currently active (at the top of the stack).
        Returns None if no event is running.
        """
        if not self.is_any_event_running():
            return None
        return self._running_event_stack[-1]

    def get_current_running_event(self) -> Optional[BaseGameEvent]:
        """
        Returns the event domain object that is currently active (at the top of the stack).
        Returns None if no event is running.
        """
        current_info = self.get_current_running_event_info()
        if not current_info:
            return None
        
        return self._all_events.get(current_info.event_id)

    def is_any_event_running(self) -> bool:
        """Returns True if the running event stack is not empty."""
        return len(self._running_event_stack) > 0

    def set_event_status(self, event_id: str, new_status: EVENT_STATUS_LITERAL):
        """
        Updates an event's status and correctly maintains the indexes.
        This is the ONLY method you should use to change an event's status.
        """
        if new_status not in EVENT_STATUSES:
            print(f"Error: Attempted to set invalid status '{new_status}'.")
            return

        if event_id in self._all_events:
            event = self._all_events[event_id]
            old_status = event.status

            if old_status == new_status:
                return 

            if old_status in self._status_indexes:
                self._status_indexes[old_status].discard(event_id)

            self._status_indexes[new_status].add(event_id)

            event.get_model().status = new_status
            print(f"Event '{event_id}' status changed from '{old_status}' to '{new_status}'.")

    def get_events_by_status(self, status: str) -> List[BaseGameEvent]:
        """
        Efficiently retrieves all events with a given status using the index.
        """
        if status not in self._status_indexes:
            return []
        
        event_ids = self._status_indexes[status]
        return [self._all_events[eid] for eid in event_ids]

    def get_completed_event_ids(self) -> Set[str]:
        """
        Directly and efficiently returns the set of completed event IDs.
        """
        return self._status_indexes.get("COMPLETED", set())
    
    def find_event(self, event_id: str) -> Optional[BaseGameEvent]:
        """
        Returns the event associated with event id or None if it doesnt exist
        """
        return self._all_events.get(event_id)
    
    def add_and_index_event(self, event_model: GameEventModel) -> BaseGameEvent:
        """
        (Internal Logic) Adds a pre-validated event model to the internal state
        and updates all necessary indexes. This is the final step.
        """
        print("ADDING AND INDEXING EVENT")
        wrapper_class = WRAPPER_MAP.get(event_model.type)
        if not wrapper_class:
            raise TypeError(f"Internal Error: Event type '{event_model.type}' is unknown and cannot be processed.")

        domain_event = wrapper_class(model=event_model)
        self._all_events[event_model.id] = domain_event

        self._status_indexes[domain_event.status].add(domain_event.id)

        if domain_event.source_beat_id:
            self._events_by_beat_id[domain_event.source_beat_id].add(domain_event.id)
        else:
            self._beatless_event_ids.add(domain_event.id)

        for condition in domain_event.activation_conditions:
            if isinstance(condition, CharacterInteractionOption):
                self._interaction_options_by_character[condition.character_id].add(domain_event.id)
        print("RETURNING DOMAIN EVENT")
        return domain_event
    
    def link_conditions_to_event(self, event_id: str, conditions: List[ActivationConditionModel]):
        """
        (Core Logic) Adds new activation conditions to an existing event's data model
        and updates all relevant indexes.
        """
        event = self._all_events[event_id] # Assumes event existence is pre-validated

        # Add the new conditions to the underlying Pydantic model
        event.get_model().activation_conditions.extend(conditions)
        
        # Rebuild the domain wrappers for the event so it's aware of the new conditions
        event._build_condition_wrappers()

        # Update indexes with the new information
        for condition in conditions:
            if isinstance(condition, CharacterInteractionOptionModel):
                self._interaction_options_by_character[condition.character_id].add(event_id)

    def unlink_condition_from_event(self, event_id: str, condition_id: str) -> ActivationConditionModel:
        """Remove a specific activation condition from an event and update indexes."""
        event = self._all_events.get(event_id)
        if not event:
            raise KeyError(f"Event with ID '{event_id}' not found.")

        conditions = event.get_model().activation_conditions
        idx_to_remove = next((i for i, cond in enumerate(conditions) if cond.id == condition_id), None)
        if idx_to_remove is None:
            raise KeyError(
                f"Activation condition '{condition_id}' not found for event '{event_id}'."
            )

        removed_condition = conditions.pop(idx_to_remove)

        # Rebuild the wrappers list
        event.activation_conditions = []
        event._build_condition_wrappers()

        if isinstance(removed_condition, CharacterInteractionOptionModel):
            char_set = self._interaction_options_by_character.get(removed_condition.character_id)
            if char_set:
                char_set.discard(event_id)
                if not char_set:
                    self._interaction_options_by_character.pop(removed_condition.character_id, None)

        return removed_condition

    def list_events(self, status: Optional[str] = None) -> List[BaseGameEvent]:
        """
        Lists full event domain objects, optionally filtered by status.
        """
        events_to_list: List[BaseGameEvent] = []
        if status:
            if status not in self._status_indexes:
                raise ValueError(f"Invalid status filter: '{status}'.")
            event_ids = self._status_indexes[status]
            events_to_list = [self._all_events[eid] for eid in event_ids]
        else:
            events_to_list = list(self._all_events.values())
        
        return events_to_list

    def delete_event(self, event_id: str) -> BaseGameEvent:
        """Remove an event completely from the manager and all indexes."""
        event = self._all_events.pop(event_id, None)
        if not event:
            raise KeyError(f"Event with ID '{event_id}' not found.")

        # Remove from running stack if present
        self._running_event_stack = [eid for eid in self._running_event_stack if eid != event_id]

        # Clean status index
        if event.status in self._status_indexes:
            self._status_indexes[event.status].discard(event_id)

        # Clean beat indexes
        if event.source_beat_id:
            beat_set = self._events_by_beat_id.get(event.source_beat_id)
            if beat_set:
                beat_set.discard(event_id)
                if not beat_set:
                    self._events_by_beat_id.pop(event.source_beat_id, None)
        else:
            self._beatless_event_ids.discard(event_id)

        # Clean interaction indexes
        for condition in event.activation_conditions:
            if isinstance(condition, CharacterInteractionOption):
                char_set = self._interaction_options_by_character.get(condition.character_id)
                if char_set:
                    char_set.discard(event_id)
                    if not char_set:
                        self._interaction_options_by_character.pop(condition.character_id, None)

        return event

    def update_event_description(self, event_id: str, new_description: str) -> BaseGameEvent:
        """Update the description of an existing event."""
        event = self._all_events.get(event_id)
        if not event:
            raise KeyError(f"Event with ID '{event_id}' not found.")
        event.get_model().description = new_description
        return event

    def update_event_title(self, event_id: str, new_title: str) -> BaseGameEvent:
        """Update the title of an existing event."""
        event = self._all_events.get(event_id)
        if not event:
            raise KeyError(f"Event with ID '{event_id}' not found.")
        event.get_model().title = new_title
        return event

    def disable_event(self, event_id: str) -> BaseGameEvent:
        """Set the event status to DISABLED if currently AVAILABLE."""
        event = self._all_events.get(event_id)
        if not event:
            raise KeyError(f"Event with ID '{event_id}' not found.")
        if event.status != "AVAILABLE":
            raise ValueError(
                f"Cannot disable event '{event_id}' because it is in '{event.status}' status."
            )

        self.set_event_status(event_id, "DISABLED")
        return event

    def enable_event(self, event_id: str) -> BaseGameEvent:
        """Set the event status back to AVAILABLE if currently DISABLED."""
        event = self._all_events.get(event_id)
        if not event:
            raise KeyError(f"Event with ID '{event_id}' not found.")
        if event.status != "DISABLED":
            raise ValueError(
                f"Cannot enable event '{event_id}' because it is in '{event.status}' status."
            )

        self.set_event_status(event_id, "AVAILABLE")
        return event

    def get_all_events_grouped(self) -> Dict[str, Dict[str, List[BaseGameEvent]]]:
        """
        Returns all full event domain objects, grouped by beat and then by status.
        """

        grouped_events: Dict[str, Dict[str, List[BaseGameEvent]]] = defaultdict(lambda: defaultdict(list))

        for event in self._all_events.values():
            beat_key = event.source_beat_id or "BEATLESS"
            status_key = event.status
            
            grouped_events[beat_key][status_key].append(event)

        return grouped_events
        
