from typing import Callable, Optional

class ProgressTracker:
    def __init__(
        self,
        weight: float = 1.0,
        offset: float = 0.0,
        parent: Optional["ProgressTracker"] = None,
        update_fn: Optional[Callable[[float, str], None]] = None
    ):
        self.weight = weight
        self.offset = offset
        self.parent = parent
        self.update_fn = update_fn

    def update(self, local_progress: float, message: str = ""):
        global_progress = self.offset + local_progress * self.weight
        if self.parent:
            self.parent.update(global_progress, message)
        elif self.update_fn:
            self.update_fn(global_progress, message)

    def subtracker(self, subweight: float) -> "ProgressTracker":
        return ProgressTracker(
            weight=subweight,
            offset=self.offset,
            parent=self.parent or self,
            update_fn=self.update_fn
        )