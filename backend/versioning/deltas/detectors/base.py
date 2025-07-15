from abc import ABC, abstractmethod
from typing import Any, Dict, TypeVar, Generic
T_Model = TypeVar("T_Model")

class ChangeDetector(Generic[T_Model], ABC):
    """
    The universal interface for anything that can detect a change.
    It returns a dictionary with the changes, or None if there are none.
    """
    @abstractmethod
    def detect(self, old: T_Model, new: T_Model) -> Dict[str, Any] | None:
        pass