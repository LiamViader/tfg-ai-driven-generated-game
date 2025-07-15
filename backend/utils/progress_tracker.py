from typing import Callable, Optional

class ProgressTracker:
    """
    A stateful class to track and report hierarchical progress for
    long-running, nested tasks.
    """
    def __init__(
        self,
        # The update_fn is only needed on the root tracker.
        update_fn: Optional[Callable[[float, str], None]] = None,
        # These are for the internal use of sub-trackers.
        weight: float = 1.0,
        offset: float = 0.0,
        parent: Optional["ProgressTracker"] = None,
    ):
        self.update_fn = update_fn
        self.weight = weight
        self.offset = offset
        self.parent = parent
        self.local_progress: float = 0.0 # We store the local progress

    def _report_progress(self, global_progress: float, message: str):
        """Internal method to propagate progress upwards to the root."""
        if self.parent:
            self.parent._report_progress(global_progress, message)
        elif self.update_fn:
            # Only the root tracker calls the final callback function.
            self.update_fn(global_progress, message)

    def update(self, local_progress: float, message: str = ""):
        """
        Updates the progress of THIS tracker (a value from 0.0 to 1.0).
        """
        # We ensure the local progress is clamped between 0 and 1.
        self.local_progress = max(0.0, min(1.0, local_progress))
        
        # We calculate the global progress contributed by this tracker plus its offset.
        global_progress = self.offset + self.local_progress * self.weight
        
        # We report the new global progress upwards.
        self._report_progress(global_progress, message)

    def subtracker(self, sub_weight: float) -> "ProgressTracker":
        """
        Creates a sub-tracker for a sub-task.

        This sub-task represents a fraction (`sub_weight`) of this tracker's
        total weight, starting from its current progress point.
        """
        if not (0.0 <= sub_weight <= 1.0):
            raise ValueError("Sub-tracker weight must be between 0.0 and 1.0")

        # The child's offset starts from this tracker's current global progress.
        current_global_offset = self.offset + self.local_progress * self.weight
        
        # The child's absolute weight is a fraction of this tracker's weight.
        child_weight = self.weight * sub_weight
        
        return ProgressTracker(
            weight=child_weight,
            offset=current_global_offset,
            parent=self # The parent of the sub-tracker is always `self`.
        )