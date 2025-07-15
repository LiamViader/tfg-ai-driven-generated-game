from simulated.versioning.deltas.detectors.base import ChangeDetector
from typing import Any, Dict

class FieldChangeDetector(ChangeDetector):
    """A generic detector that checks for changes in a specific attribute."""
    def __init__(self, field_name: str):
        self.field_name = field_name

    def detect(self, old: Any, new: Any) -> Dict[str, Any] | None:
        if not hasattr(old, self.field_name) or not hasattr(new, self.field_name):
            return None

        old_val = getattr(old, self.field_name)
        new_val = getattr(new, self.field_name)

        if old_val != new_val:
            return {self.field_name: new_val}
        return None