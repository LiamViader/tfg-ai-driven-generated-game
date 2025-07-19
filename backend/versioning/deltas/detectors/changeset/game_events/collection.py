# En versioning/deltas/detectors/changeset/events/collection.py

from typing import Dict, Any, List, Set, Tuple
from versioning.deltas.detectors.base import ChangeDetector
# Import all necessary models
from core_game.game_event.schemas import GameEventsManagerModel, GameEventModel
from core_game.game_event.activation_conditions.schemas import (
    ActivationConditionModel,
    CharacterInteractionOptionModel
)
from core_game.game_event.constants import EVENT_STATUS_LITERAL

# --- Helper function to extract and INDEX interaction options from a GameEventsManagerModel ---
# La clave aquí es que el diccionario más interno se indexará por el ID de la condición de activación.
def _extract_and_index_character_interaction_options_from_model(
    events_manager_model: GameEventsManagerModel
) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Extracts available character interaction options from a GameEventsManagerModel
    and indexes them by character_id and then by activation_condition_id.
    """
    # { character_id: { condition_id: { event_id: ..., title: ..., description: ..., menu_label: ..., is_repeatable: ... } } }
    indexed_character_options: Dict[str, Dict[str, Dict[str, str]]] = {}

    for event_id, event_model in events_manager_model.all_events.items():
        if event_model.status == "AVAILABLE":
            for condition_model in event_model.activation_conditions:
                if condition_model.type == "character_interaction":
                    try:
                        char_interaction_condition: CharacterInteractionOptionModel = \
                            CharacterInteractionOptionModel.model_validate(condition_model.model_dump())

                        char_id = char_interaction_condition.character_id
                        condition_id = char_interaction_condition.id # Use the condition's ID for indexing
                        menu_label = char_interaction_condition.menu_label
                        is_repeatable = char_interaction_condition.is_repeatable

                        if char_id not in indexed_character_options:
                            indexed_character_options[char_id] = {}

                        # Store the option data, indexed by condition_id
                        option_data = {
                            "event_id": event_id,
                            "title": event_model.title,
                            "description": event_model.description,
                            "menu_label": menu_label,
                            "is_repeatable": is_repeatable
                        }
                        indexed_character_options[char_id][condition_id] = option_data
                        
                    except Exception as e:
                        print(f"Warning: Could not validate condition {condition_model.id} "
                              f"of event {event_id} as CharacterInteractionOptionModel: {e}")
                        continue

    return indexed_character_options

# --- The EventsDetector class ---
class GameEventsDetector(ChangeDetector[GameEventsManagerModel]):
    """
    Detects relevant changes in game events, particularly character interaction options.
    This detector operates exclusively on GameEventsManagerModel instances from checkpoints.
    It generates 'add', 'update', and 'delete' deltas based on activation condition IDs.
    """
    def detect(self, old: GameEventsManagerModel, new: GameEventsManagerModel) -> Dict[str, Any] | None:
        """
        Compares the old and new GameEventsManagerModels to identify
        changes in character interaction options and generates deltas.
        """
        all_changes: Dict[str, Any] = {}
        
        # Extract and index options from both old and new states
        old_indexed_options = _extract_and_index_character_interaction_options_from_model(old)
        new_indexed_options = _extract_and_index_character_interaction_options_from_model(new)

        character_deltas: Dict[str, List[Dict[str, Any]]] = {}

        # Get all unique character IDs involved in either old or new states
        all_character_ids: Set[str] = set(old_indexed_options.keys()) | set(new_indexed_options.keys())

        for char_id in sorted(list(all_character_ids)): # Sort for consistent output
            old_char_options = old_indexed_options.get(char_id, {})
            new_char_options = new_indexed_options.get(char_id, {})

            char_ops: List[Dict[str, Any]] = []

            old_condition_ids: Set[str] = set(old_char_options.keys())
            new_condition_ids: Set[str] = set(new_char_options.keys())

            # 1. Detect Removed Options
            for cond_id in sorted(list(old_condition_ids - new_condition_ids)):
                char_ops.append({"op": "remove", "condition_id": cond_id})

            # 2. Detect Added and Updated Options
            for cond_id in sorted(list(new_condition_ids)):
                new_option_data = new_char_options[cond_id]

                if cond_id not in old_condition_ids:
                    # New option added
                    char_ops.append({
                        "op": "add",
                        "condition_id": cond_id,
                        **new_option_data # Unpack the data fields
                    })
                else:
                    # Option might be updated
                    old_option_data = old_char_options[cond_id]
                    
                    # Convert dicts to tuples of sorted items for comparison
                    # This handles potential key order differences if data structure is large/complex
                    if tuple(sorted(old_option_data.items())) != tuple(sorted(new_option_data.items())):
                        # Option updated
                        char_ops.append({
                            "op": "update",
                            "condition_id": cond_id,
                            **new_option_data # Send the full new data for update
                        })
            
            if char_ops:
                character_deltas[char_id] = char_ops

        if character_deltas:
            all_changes["character_interaction_options_delta"] = character_deltas

        return all_changes if all_changes else None