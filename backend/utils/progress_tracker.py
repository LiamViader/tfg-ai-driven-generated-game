from typing import Callable, Optional

class ProgressTracker:
    """
    A stateful class to track and report hierarchical progress for
    long-running, nested tasks.
    """
    def __init__(
        self,
        update_fn: Optional[Callable[[float, str], None]] = None,
        weight: float = 1.0,
        offset: float = 0.0,
        parent: Optional["ProgressTracker"] = None,
        debug: bool = False  # 👈 NUEVO parámetro opcional
    ):
        self.update_fn = update_fn
        self.weight = weight
        self.offset = offset
        self.parent = parent
        self.debug = debug  # 👈 Guardamos si queremos modo debug
        self.local_progress: float = 0.0

    def _report_progress(self, global_progress: float, message: str):
        """Internal method to propagate progress upwards to the root."""
        if self.parent:
            self.parent._report_progress(global_progress, message)
        elif self.update_fn:
            if self.debug:
                print(f"[ProgressTracker] {global_progress:.1%} - {message}")  # 👈 Logging en modo debug
            self.update_fn(global_progress, message)

    def update(self, local_progress: float, message: str = ""):
        """
        Updates the progress of THIS tracker (a value from 0.0 to 1.0).
        """
        self.local_progress = max(0.0, min(1.0, local_progress))
        global_progress = self.offset + self.local_progress * self.weight
        self._report_progress(global_progress, message)

    def subtracker(self, sub_weight: float) -> "ProgressTracker":
        """
        Creates a sub-tracker for a sub-task.
        """
        if not (0.0 <= sub_weight <= 1.0):
            raise ValueError("Sub-tracker weight must be between 0.0 and 1.0")

        current_global_offset = self.offset + self.local_progress * self.weight
        child_weight = self.weight * sub_weight

        return ProgressTracker(
            weight=child_weight,
            offset=current_global_offset,
            parent=self,
            debug=self.debug  # 👈 Hereda el modo debug del padre
        )
