from versioning.deltas.detectors.base import ChangeDetector
from versioning.deltas.detectors.changeset.characters.entity import CharacterDetector
from core_game.character.schemas import CharactersModel
from typing import Dict, Any, List

class CharactersDetector(ChangeDetector[CharactersModel]):
    """Detects changes in the entire characters component."""
    def __init__(self, character_detector: CharacterDetector):
        self.character_detector = character_detector

    def detect(self, old: CharactersModel, new: CharactersModel) -> Dict[str, Any] | None:
        final_changes: Dict[str, Any] = {}
        
        # 1. Detects if player id has changed
        if old.player_character_id != new.player_character_id and new.player_character_id:
            final_changes["player_character_id"] = new.player_character_id

        registry_ops: List[Dict[str, Any]] = []

        # 2. Player registry logic
        old_chars, new_chars = old.registry, new.registry
        old_ids, new_ids = set(old_chars), set(new_chars)
        
        for id in sorted(new_ids - old_ids):
            model = new_chars[id]
            
            public_fields = self.character_detector.get_public_fields_for(model)
            
            dumped_data = model.model_dump(include=public_fields)
            
            registry_ops.append({"op": "add", "id": id, **dumped_data})
        
        for id in sorted(old_ids - new_ids):
            registry_ops.append({"op": "remove", "id": id})
            
        for id in sorted(old_ids & new_ids):
            char_changes = self.character_detector.detect(old_chars[id], new_chars[id])
            if char_changes:
                registry_ops.append({"op": "update", "id": id, **char_changes})
                
        if registry_ops:
            final_changes["registry"] = registry_ops
            
        return final_changes if final_changes else None