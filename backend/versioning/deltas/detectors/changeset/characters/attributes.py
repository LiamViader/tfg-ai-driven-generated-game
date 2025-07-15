from versioning.deltas.detectors.base import ChangeDetector
from core_game.character.schemas import IdentityModel, PhysicalAttributesModel, PsychologicalAttributesModel, KnowledgeModel
from versioning.deltas.detectors.field_detector import FieldChangeDetector
from typing import Any, Dict, List

from core_game.character.schemas import (
    IdentityModel,
    PhysicalAttributesModel,
    PsychologicalAttributesModel,
    KnowledgeModel,
    DynamicStateModel,
    NarrativeWeightModel,
)

class IdentityDetector(ChangeDetector[IdentityModel]):
    """Aggregates changes within the IdentityModel."""
    def __init__(self):
        self.leaf_detectors: List[ChangeDetector] = [
            FieldChangeDetector("full_name"),
            FieldChangeDetector("alias"),
            FieldChangeDetector("age"),
            FieldChangeDetector("gender"),
            FieldChangeDetector("profession"),
            FieldChangeDetector("species"),
            FieldChangeDetector("alignment"),
        ]
    
    def detect(self, old: IdentityModel, new: IdentityModel) -> Dict[str, Any] | None:
        full_changes = {}
        for detector in self.leaf_detectors:
            changes = detector.detect(old, new)
            if changes:
                full_changes.update(changes)
        return full_changes if full_changes else None

class PhysicalDetector(ChangeDetector[PhysicalAttributesModel]):
    """Aggregates changes within the PhysicalAttributesModel."""
    def __init__(self):
        self.leaf_detectors: List[ChangeDetector] = [
            FieldChangeDetector("appearance"),
            FieldChangeDetector("visual_prompt"),
            FieldChangeDetector("distinctive_features"),
            FieldChangeDetector("clothing_style"),
            FieldChangeDetector("characteristic_items"),
        ]
    
    def detect(self, old: PhysicalAttributesModel, new: PhysicalAttributesModel) -> Dict[str, Any] | None:
        # The aggregation logic is identical to the detectors above
        full_changes = {}
        for detector in self.leaf_detectors:
            changes = detector.detect(old, new)
            if changes:
                full_changes.update(changes)
        return full_changes if full_changes else None

class PsychologicalDetector(ChangeDetector[PsychologicalAttributesModel]):
    """Aggregates changes within the PsychologicalAttributesModel."""
    def __init__(self):
        self.leaf_detectors: List[ChangeDetector] = [
            FieldChangeDetector("personality_summary"),
            FieldChangeDetector("personality_tags"),
            FieldChangeDetector("motivations"),
            FieldChangeDetector("values"),
            FieldChangeDetector("fears_and_weaknesses"),
            FieldChangeDetector("communication_style"),
            FieldChangeDetector("backstory"),
            FieldChangeDetector("quirks"),
        ]
    
    def detect(self, old: PsychologicalAttributesModel, new: PsychologicalAttributesModel) -> Dict[str, Any] | None:
        # The aggregation logic is identical
        full_changes = {}
        for detector in self.leaf_detectors:
            changes = detector.detect(old, new)
            if changes:
                full_changes.update(changes)
        return full_changes if full_changes else None

class KnowledgeDetector(ChangeDetector[KnowledgeModel]):
    """Aggregates changes within the KnowledgeModel."""
    def __init__(self):
        self.leaf_detectors: List[ChangeDetector] = [
            FieldChangeDetector("background_knowledge"),
            FieldChangeDetector("acquired_knowledge"),
        ]
    
    def detect(self, old: KnowledgeModel, new: KnowledgeModel) -> Dict[str, Any] | None:
        # The aggregation logic is identical
        full_changes = {}
        for detector in self.leaf_detectors:
            changes = detector.detect(old, new)
            if changes:
                full_changes.update(changes)
        return full_changes if full_changes else None

# --------------------------------------------------------------------------
# Detectors for NPC-Specific Attributes
# --------------------------------------------------------------------------

class DynamicStateDetector(ChangeDetector[DynamicStateModel]):
    """Aggregates changes within the NPC's DynamicStateModel."""
    def __init__(self):
        self.leaf_detectors: List[ChangeDetector] = [
            FieldChangeDetector("current_emotion"),
            FieldChangeDetector("immediate_goal"),
        ]

    def detect(self, old: DynamicStateModel, new: DynamicStateModel) -> Dict[str, Any] | None:
        # The aggregation logic is identical
        full_changes = {}
        for detector in self.leaf_detectors:
            changes = detector.detect(old, new)
            if changes:
                full_changes.update(changes)
        return full_changes if full_changes else None

class NarrativeWeightDetector(ChangeDetector[NarrativeWeightModel]):
    """Aggregates changes within the NPC's NarrativeWeightModel."""
    def __init__(self):
        self.leaf_detectors: List[ChangeDetector] = [
            FieldChangeDetector("narrative_role"),
            FieldChangeDetector("current_narrative_importance"),
            FieldChangeDetector("narrative_purposes"),
        ]

    def detect(self, old: NarrativeWeightModel, new: NarrativeWeightModel) -> Dict[str, Any] | None:
        # The aggregation logic is identical
        full_changes = {}
        for detector in self.leaf_detectors:
            changes = detector.detect(old, new)
            if changes:
                full_changes.update(changes)
        return full_changes if full_changes else None
    
