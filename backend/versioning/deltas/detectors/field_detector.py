from versioning.deltas.detectors.base import ChangeDetector
from typing import Any, Dict

# Un objeto único que usaremos como valor por defecto para saber si un atributo no se encontró.
_SENTINEL = object()

class FieldChangeDetector(ChangeDetector):
    """
    A generic detector that checks for changes in a specific attribute,
    correctly handling addition, modification, and removal of the attribute.
    """
    def __init__(self, field_name: str):
        self.field_name = field_name

    def detect(self, old: Any, new: Any) -> Dict[str, Any] | None:

        old_val = getattr(old, self.field_name, _SENTINEL)
        new_val = getattr(new, self.field_name, _SENTINEL)


        if old_val == new_val:
            return None


        if new_val is _SENTINEL:
            return {self.field_name: None}
        

        return {self.field_name: new_val}