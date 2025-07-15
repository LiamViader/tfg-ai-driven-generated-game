from abc import ABC, abstractmethod
from typing import Any, Dict


class ChangeDetector(ABC):
    """
    The universal interface for anything that can detect a change.
    It returns a dictionary with the changes, or None if there are none.
    """
    @abstractmethod
    def detect(self, old: Any, new: Any) -> Dict[str, Any] | None:
        pass