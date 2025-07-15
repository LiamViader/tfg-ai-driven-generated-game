from simulated.versioning.deltas.detectors.base import ChangeDetector
from simulated.versioning.deltas.schemas import ChangeDetailModel
from core_game.character.schemas import CharacterBaseModel

class InternalCharacterVisualsDetector(ChangeDetector[CharacterBaseModel]):
    """ Detects changes for visual recompute. """
    def detect(self, old_c: CharacterBaseModel, new_c: CharacterBaseModel) -> dict | None:
        visual_attributes = ["identity", "physical"]
        visual_changes = {}
        for attr in visual_attributes:
            old_val = getattr(old_c, attr)
            new_val = getattr(new_c, attr)
            if old_val.model_dump() != new_val.model_dump():
                visual_changes[attr] = ChangeDetailModel(
                    old=old_val.model_dump(), new=new_val.model_dump()
                )
        
        return {"modified_visual_info": visual_changes} if visual_changes else None

class InternalCharacterLocationDetector(ChangeDetector[CharacterBaseModel]):
    """ Detects changes in location. """
    def detect(self, old_c: CharacterBaseModel, new_c: CharacterBaseModel) -> dict | None:
        if old_c.present_in_scenario != new_c.present_in_scenario:
            change = ChangeDetailModel(old=old_c.present_in_scenario, new=new_c.present_in_scenario)
            return {"modified_location": change}
        return None