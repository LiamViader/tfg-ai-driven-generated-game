from simulated.versioning.deltas.detectors.base import ChangeDetector
from core_game.character.schemas import CharacterBaseModel, CharactersModel
from simulated.versioning.deltas.schemas import CharacterDiffModel

class InternalCharacterDetector(ChangeDetector[CharacterBaseModel]):
    """ Aggregates the changes for a single character in the report format. """
    def __init__(self, leaf_detectors: list[ChangeDetector[CharacterBaseModel]]):
        self.leaf_detectors = leaf_detectors

    def detect(self, old_c: CharacterBaseModel, new_c: CharacterBaseModel) -> dict:
        aggregated_changes = {}
        for detector in self.leaf_detectors:
            changes = detector.detect(old_c, new_c)
            if changes:
                aggregated_changes.update(changes)
        return aggregated_changes

class InternalCharactersCollectionDetector(ChangeDetector[CharactersModel]):
    """ Replicates the logic of `diff_characters_against`, returning a CharacterDiffModel. """
    def __init__(self, character_detector: InternalCharacterDetector):
        self.character_detector = character_detector

    def detect(self, old_chars_model: CharactersModel, new_chars_model: CharactersModel) -> CharacterDiffModel:
        old_chars = old_chars_model.registry
        new_chars = new_chars_model.registry
        old_ids, new_ids = set(old_chars.keys()), set(new_chars.keys())

        diff_dict = {
            "added": sorted(list(new_ids - old_ids)),
            "removed": sorted(list(old_ids - new_ids)),
            "modified": [],
            "modified_visual_info": {},
            "modified_location": {},
        }

        for id in sorted(old_ids & new_ids):
            if old_chars[id].model_dump() == new_chars[id].model_dump():
                continue
            
            diff_dict["modified"].append(id)
            details = self.character_detector.detect(old_chars[id], new_chars[id])
            
            if details:
                if "modified_visual_info" in details:
                    diff_dict["modified_visual_info"][id] = details["modified_visual_info"]
                if "modified_location" in details:
                    diff_dict["modified_location"][id] = details["modified_location"]

        return CharacterDiffModel(**diff_dict)