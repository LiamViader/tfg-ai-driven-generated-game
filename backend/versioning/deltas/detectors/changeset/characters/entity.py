from typing import Dict, Any, List

from core_game.character.schemas import CharacterBaseModel, NonPlayerCharacterModel
from versioning.deltas.detectors.base import ChangeDetector
from versioning.deltas.detectors.changeset.characters.attributes import (
    IdentityDetector, 
    PhysicalDetector, 
    PsychologicalDetector, 
    KnowledgeDetector,
    DynamicStateDetector,
    NarrativeWeightDetector,
)
from versioning.deltas.detectors.field_detector import FieldChangeDetector


class CharacterDetector(ChangeDetector[CharacterBaseModel]):
    """
    Aggregates all changes for a single character entity by orchestrating
    detectors for its various components and attributes.
    """
    def __init__(self):
        """
        Initializes the detector by composing it with detectors for each
        of the character's main components.
        """
        # Detectors for attributes common to ALL characters
        self.common_attribute_detectors: Dict[str, ChangeDetector] = {
            "identity": IdentityDetector(),
            "physical": PhysicalDetector(),
            "psychological": PsychologicalDetector(),
            "knowledge": KnowledgeDetector(),
        }

        # Detectors for attributes specific ONLY to NPCs
        self.npc_attribute_detectors: Dict[str, ChangeDetector] = {
            "dynamic_state": DynamicStateDetector(),
            "narrative": NarrativeWeightDetector(),
        }

        # Detectors for simple fields at the top level of CharacterBaseModel
        self.top_level_field_detectors: List[ChangeDetector] = [
            FieldChangeDetector("present_in_scenario"),
            FieldChangeDetector("image_path"),
            FieldChangeDetector("type"),
        ]

    def detect(self, old: CharacterBaseModel, new: CharacterBaseModel) -> Dict[str, Any] | None:
        """
        Detects changes by delegating to component-specific detectors and
        aggregates the results into a single nested dictionary.
        """
        full_changes: Dict[str, Any] = {}

        # 1. Process common attributes (identity, physical, etc.)
        for attr_name, detector in self.common_attribute_detectors.items():
            old_attribute = getattr(old, attr_name)
            new_attribute = getattr(new, attr_name)
            
            attribute_changes = detector.detect(old_attribute, new_attribute)
            if attribute_changes:
                full_changes[attr_name] = attribute_changes

        # 2. Process simple, top-level fields
        for detector in self.top_level_field_detectors:
            field_changes = detector.detect(old, new)
            if field_changes:
                full_changes.update(field_changes)
        
        # 3. Process NPC-specific attributes ONLY if the character is an NPC
        if isinstance(new, NonPlayerCharacterModel) and isinstance(old, NonPlayerCharacterModel):
            for attr_name, detector in self.npc_attribute_detectors.items():
                old_attribute = getattr(old, attr_name)
                new_attribute = getattr(new, attr_name)
                
                attribute_changes = detector.detect(old_attribute, new_attribute)
                if attribute_changes:
                    full_changes[attr_name] = attribute_changes

        return full_changes if full_changes else None